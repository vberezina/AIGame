import pygame
import math

# Настройки экрана
WIDTH, HEIGHT = 800, 600
FPS = 60

class Agent:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 3
        self.radius = 15

    def update(self, target_pos):
        # 1. Вычисляем вектор к цели
        target = pygame.Vector2(target_pos)
        direction = target - self.pos
        
        # 2. Двигаемся, только если мы не в самой цели
        if direction.length() > 0:
            direction = direction.normalize() # Нормализация
            self.pos += direction * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, (0, 255, 0), (int(self.pos.x), int(self.pos.y)), self.radius)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    agent = Agent(WIDTH // 2, HEIGHT // 2)
    
    running = True
    while running:
        screen.fill((30, 30, 30)) # Темный фон
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Цель — курсор мыши
        mouse_pos = pygame.mouse.get_pos()
        
        # Отрисовка цели
        pygame.draw.circle(screen, (255, 0, 0), mouse_pos, 5)
        
        # Обновление и отрисовка агента
        agent.update(mouse_pos)
        agent.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()