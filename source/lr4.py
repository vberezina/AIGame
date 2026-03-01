import pygame
import math

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета для визуализации
WHITE = (255, 255, 255)
BLUE = (0, 150, 255)    # Цвет еды
YELLOW = (255, 255, 0)  # Цвет текста активного узла

# --- БАЗОВАЯ АРХИТЕКТУРА ДЕРЕВА ПОВЕДЕНИЯ (CORE) ---

class Node:
    """
    Абстрактный базовый класс для любого узла дерева.
    Метод tick() — это пульс дерева. Он вызывается каждый кадр.
    """
    def tick(self, blackboard):
        raise NotImplementedError

class Sequence(Node):
    """
    Композитный узел 'ПОСЛЕДОВАТЕЛЬНОСТЬ' (Логическое И).
    Выполняет чаилдов по порядку. Если хотя бы один чаилд вернет FAILURE, 
    вся последовательность прерывается и возвращает FAILURE.
    """
    def __init__(self, children):
        self.children = children

    def tick(self, blackboard):
        for child in self.children:
            status = child.tick(blackboard)
            # Если хотя бы одно действие не удалось или еще выполняется,
            # мы не идем к следующему чаилду.
            if status != "SUCCESS":
                return status
        return "SUCCESS" # Все дети выполнились успешно

class Selector(Node):
    """
    Композитный узел 'СЕЛЕКТОР' (Логическое ИЛИ / Fallback).
    Пытается выполнить чаилдов по порядку. Если чаилд вернул SUCCESS или RUNNING,
    селектор останавливается и возвращает этот статус. К следующему чаилду 
    он переходит только если текущий вернул FAILURE.
    """
    def __init__(self, children):
        self.children = children

    def tick(self, blackboard):
        for child in self.children:
            status = child.tick(blackboard)
            # Если нашли хотя бы одно успешное или выполняющееся действие — выходим.
            if status != "FAILURE":
                return status
        return "FAILURE" # Ни один чаилд не смог выполниться

# --- УЗЛЫ-ЛИСТЬЯ  ---

class IsHungry(Node):
    """Узел-условие: проверяет данные в Blackboard."""
    def tick(self, blackboard):
        if blackboard["hunger"] > 70:
            return "SUCCESS" # Да, мы голодны, можно идти к следующему узлу в Sequence
        return "FAILURE" # Нет, прерываем Sequence, идем к следующему узлу в Selector

class FindFood(Node):
    """Узел-действие: управление движением NPC к цели."""
    def tick(self, blackboard):
        npc = blackboard["npc"]
        food_pos = blackboard["food_pos"]
        
        dist = npc.pos.distance_to(food_pos)
        
        # Проверка достижения цели
        if dist < 10:
            blackboard["hunger"] = 0 # Сброс параметра
            blackboard["active_node"] = "Поел!"
            return "SUCCESS" # Сообщаем дереву, что задача завершена
        
        # Логика перемещения
        direction = (food_pos - npc.pos).normalize()
        npc.pos += direction * 3 # Двигаемся со скоростью 3 пикс/кадр
        
        blackboard["active_node"] = "Иду к еде (Поиск пути)"
        return "RUNNING" # Сообщаем дереву, что действие еще в процессе

class Wander(Node):
    """Узел-действие: фоновое поведение (блуждание)."""
    def tick(self, blackboard):
        npc = blackboard["npc"]
        
        # Математическое "ленивое" движение по синусоиде
        t = pygame.time.get_ticks() * 0.002
        npc.pos.x += math.sin(t) * 1.5
        npc.pos.y += math.cos(t * 0.7) * 1.5
        
        blackboard["active_node"] = "Патрулирование / Блуждание"
        return "SUCCESS" # Это действие всегда считается успешным (фоновое)

# --- ИГРОВЫЕ ОБЪЕКТЫ ---

class NPC:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.radius = 15

    def draw(self, screen, hunger):
        # Визуализация состояния голода через цвет: от зеленого к красному
        # hunger 0 -> (0, 255, 0), hunger 100 -> (250, 5, 0)
        r = min(255, int(hunger * 2.5))
        g = max(0, int(255 - hunger * 2.5))
        pygame.draw.circle(screen, (r, g, 0), (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius, 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Лабораторная №4: Дерево Поведения (Behavior Tree)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20, bold=True)

    # 1. Blackboard (Черная доска) — единое хранилище данных для всех узлов.
    # Это позволяет узлам быть "глупыми" и просто читать/писать общие переменные.
    npc_obj = NPC(WIDTH // 2, HEIGHT // 2)
    blackboard = {
        "npc": npc_obj,
        "food_pos": pygame.Vector2(600, 400),
        "hunger": 0.0,
        "active_node": ""
    }

    # 2. Сборка структуры дерева. 
    # Читается так: Пытаемся (Если Голоден ТО Иди кушать). Если не вышло — просто Гуляй.
    behavior_tree = Selector([
        Sequence([
            IsHungry(), 
            FindFood()
        ]),
        Wander()
    ])

    running = True
    while running:
        screen.fill((35, 35, 35))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Возможность перемещать еду кликом мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                blackboard["food_pos"] = pygame.Vector2(event.pos)

        # 3. Обновление мира
        blackboard["hunger"] = min(100, blackboard["hunger"] + 0.15) # Голод растет
        
        # 4. Тик дерева (Запуск процесса принятия решений)
        behavior_tree.tick(blackboard)

        # 5. Отрисовка
        # Рисуем еду
        pygame.draw.circle(screen, BLUE, (int(blackboard["food_pos"].x), int(blackboard["food_pos"].y)), 12)
        pygame.draw.circle(screen, WHITE, (int(blackboard["food_pos"].x), int(blackboard["food_pos"].y)), 12, 1)
        
        # Рисуем NPC
        npc_obj.draw(screen, blackboard["hunger"])

        # Вывод HUD
        h_val = int(blackboard["hunger"])
        h_text = font.render(f"Уровень голода: {h_val}%", True, WHITE)
        n_text = font.render(f"Активный узел BT: {blackboard['active_node']}", True, YELLOW)
        
        screen.blit(h_text, (20, 20))
        screen.blit(n_text, (20, 50))
        
        instr = font.render("Кликните ЛКМ, чтобы переложить еду", True, (150, 150, 150))
        screen.blit(instr, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()