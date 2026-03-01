import pygame
import math

# --- НАСТРОЙКИ И КОНСТАНТЫ ---
WIDTH = 600           # Ширина окна
ROWS = 30             # Количество клеток в сетке (30x30)
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Алгоритм поиска пути A*")

# Цветовая схема для визуализации состояний узлов
WHITE = (255, 255, 255)   # Чистая клетка (проходимая)
BLACK = (0, 0, 0)       # Препятствие (стена)
GRAY = (128, 128, 128)    # Сетка
RED = (255, 0, 0)         # "Закрытый список" (узлы, которые уже проверили)
GREEN = (0, 255, 0)       # "Открытый список" (узлы на границе поиска)
BLUE = (0, 0, 255)        # Финальный кратчайший путь
ORANGE = (255, 165, 0)    # Точка старта
PURPLE = (128, 0, 128)    # Точка финиша

class Node:
    """Класс отдельной клетки (узла) графа."""
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        # Координаты для отрисовки в пикселях
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        
        # Параметры алгоритма:
        self.g = float("inf") # Стоимость пути от старта до этой клетки
        self.f = float("inf") # Общая оценка (g + h)
        self.parent = None    # Ссылка на предыдущий узел для восстановления пути

    def get_pos(self): return self.row, self.col
    def is_barrier(self): return self.color == BLACK
    
    # Методы смены состояния (цвета)
    def make_start(self): self.color = ORANGE
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = PURPLE
    def make_closed(self): 
        if self.color not in [ORANGE, PURPLE]: self.color = RED
    def make_open(self): 
        if self.color not in [ORANGE, PURPLE]: self.color = GREEN
    def make_path(self): 
        if self.color not in [ORANGE, PURPLE]: self.color = BLUE
    def reset(self): self.color = WHITE

    def draw(self, win):
        """Рисует квадрат клетки."""
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        """Проверяет соседние клетки и добавляет их в список, если они не стены."""
        self.neighbors = []
        # Сосед снизу
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Сосед сверху
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Сосед справа
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Сосед слева
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

def h(p1, p2):
    """
    Эвристическая функция. 
    Используем Манхэттенское расстояние (сумма разностей координат).
    """
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(current, draw):
    """Восстанавливает путь, идя от финиша к старту по ссылкам parent."""
    while current.parent:
        current = current.parent
        current.make_path()
        draw() # Отрисовываем каждый шаг восстановления пути

def algorithm(draw, grid, start, end):
    """Сердце лабораторной — реализация алгоритма A*."""
    open_set = {start} # Список узлов для проверки
    start.g = 0
    start.f = h(start.get_pos(), end.get_pos())

    while open_set:
        # Позволяет закрыть окно во время работы алгоритма
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Выбираем из списка узел с минимальным значением f (самый перспективный)
        current = min(open_set, key=lambda node: node.f)
        
        # Если текущий узел — это цель, строим путь и завершаем работу
        if current == end:
            reconstruct_path(end, draw)
            end.make_end()
            return True

        open_set.remove(current)

        for neighbor in current.neighbors:
            # Предполагаем, что шаг в любую сторону стоит 1
            temp_g_score = current.g + 1

            # Если нашли путь до соседа короче, чем был известен ранее
            if temp_g_score < neighbor.g:
                neighbor.parent = current
                neighbor.g = temp_g_score
                # f(n) = g(n) + h(n)
                neighbor.f = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set:
                    open_set.add(neighbor)
                    neighbor.make_open()

        draw() # Перерисовываем экран для эффекта анимации поиска
        if current != start:
            current.make_closed() # Помечаем узел как проверенный
            
    return False # Путь не найден

# --- ФУНКЦИИ УПРАВЛЕНИЯ ПОЛЕМ ---

def make_grid(rows, width):
    """Создает двумерный массив объектов Node."""
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw(win, grid, rows, width):
    """Главная функция отрисовки кадра."""
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
            
    # Рисуем линии сетки
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRAY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRAY, (j * gap, 0), (j * gap, width))
            
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    """Преобразует координаты мыши в индексы сетки с защитой от выхода за границы."""
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    # Защита IndexError: ограничиваем значения диапазоном [0, rows-1]
    row = max(0, min(row, rows - 1))
    col = max(0, min(col, rows - 1))
    return row, col

def main(win, width):
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # ЛКМ: Установка Старта -> Финиша -> Стен
            if pygame.mouse.get_pressed()[0]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start and node != end:
                    start = node
                    start.make_start()
                elif not end and node != start:
                    end = node
                    end.make_end()
                elif node != end and node != start:
                    node.make_barrier()

            # ПКМ: Сброс клетки
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start: start = None
                elif node == end: end = None

            if event.type == pygame.KEYDOWN:
                # SPACE: Запуск алгоритма
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # C: Полная очистка
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)