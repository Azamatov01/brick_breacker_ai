import pygame
import random

class BrickBreakerGame:
    def __init__(self):
        # Инициализация Pygame
        pygame.init()

        # Параметры экрана
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Brick Breaker")

        # Цвета
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.COLORS = [self.RED, self.GREEN, self.BLUE]

        # FPS
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # Загрузка фонового изображения и его масштабирование
        try:
            self.background = pygame.image.load("background.png").convert()
            self.background = pygame.transform.scale(self.background, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            # Если не удалось загрузить изображение, используем заливку
            self.background = None

        # Параметры платформы
        self.PADDLE_WIDTH, self.PADDLE_HEIGHT = 100, 10
        self.paddle_x = self.WIDTH // 2 - self.PADDLE_WIDTH // 2
        self.paddle_y = self.HEIGHT - 30
        self.paddle_speed = 10

        # Параметры мяча
        self.BALL_RADIUS = 10
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx, self.ball_dy = 4, -4
        self.ball_color = random.choice(self.COLORS)

        # Параметры блоков
        self.BLOCK_WIDTH, self.BLOCK_HEIGHT = 75, 30
        self.BLOCK_PADDING = 5
        self.blocks = []
        self._create_blocks()

        # Боковые панели
        self.SIDE_PANEL_WIDTH = 10
        self.SIDE_PANEL_HEIGHT = (self.HEIGHT // 4) // 2
        self.SIDE_PANEL_PADDING = 10
        self.SIDE_PANEL_Y_OFFSET = self.HEIGHT // 2

        self.side_panels = [
            pygame.Rect(self.WIDTH - self.SIDE_PANEL_WIDTH - self.SIDE_PANEL_PADDING,
                        self.SIDE_PANEL_Y_OFFSET + self.SIDE_PANEL_HEIGHT * i,
                        self.SIDE_PANEL_WIDTH, self.SIDE_PANEL_HEIGHT)
            for i in range(3)
        ]
        self.side_colors = self.COLORS[:]

        # Шрифт для отображения счёта (кол-во оставшихся блоков)
        self.font = pygame.font.SysFont("arial", 24)

    def _create_blocks(self):
        for row in range(5):
            for col in range(10):
                x = col * (self.BLOCK_WIDTH + self.BLOCK_PADDING) + 10
                y = row * (self.BLOCK_HEIGHT + self.BLOCK_PADDING) + 10
                color = random.choice(self.COLORS)
                block = pygame.Rect(x, y, self.BLOCK_WIDTH, self.BLOCK_HEIGHT)
                self.blocks.append((block, color))

    def check_collision_path(self):
        ball_rect = pygame.Rect(
            self.ball_x - self.BALL_RADIUS,
            self.ball_y - self.BALL_RADIUS,
            self.BALL_RADIUS * 2,
            self.BALL_RADIUS * 2
        )
        for block, color in self.blocks[:]:
            if block.colliderect(ball_rect):
                # Проверка цвета и разрушение блока
                if color == self.ball_color:
                    self.blocks.remove((block, color))

                    # Определяем направление рикошета
                    overlap_left = ball_rect.right - block.left
                    overlap_right = block.right - ball_rect.left
                    overlap_top = ball_rect.bottom - block.top
                    overlap_bottom = block.bottom - ball_rect.top

                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                    if min_overlap == overlap_left:
                        self.ball_dx = -abs(self.ball_dx)
                    elif min_overlap == overlap_right:
                        self.ball_dx = abs(self.ball_dx)
                    elif min_overlap == overlap_top:
                        self.ball_dy = -abs(self.ball_dy)
                    elif min_overlap == overlap_bottom:
                        self.ball_dy = abs(self.ball_dy)
                else:
                    # Рикошет без разрушения блока
                    self.ball_dy = -self.ball_dy
                break

        # Проверка столкновений с боковыми панелями
        for i, panel in enumerate(self.side_panels):
            if panel.colliderect(ball_rect):
                self.ball_color = self.side_colors[i]  # Изменение цвета мяча
                self.ball_dx = -self.ball_dx  # Отражение от боковой панели
                break

    def get_state(self):
        """Возвращает текущее состояние игры."""
        return [
            self.paddle_x / self.WIDTH,  # Нормализованная позиция платформы
            self.ball_x / self.WIDTH,    # Нормализованная позиция мяча
            self.ball_y / self.HEIGHT,   # Нормализованная вертикальная позиция мяча
            self.ball_dx / 10,           # Скорость мяча по X
            self.ball_dy / 10,           # Скорость мяча по Y
            (self.ball_x - self.paddle_x) / self.WIDTH  # Разница между мячом и платформой
        ]

    def reset(self):
        """Сбрасывает игру в начальное состояние и возвращает состояние."""
        # Сбрасываем позицию платформы
        self.paddle_x = self.WIDTH // 2 - self.PADDLE_WIDTH // 2

        # Сбрасываем позицию и скорость мяча
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx, self.ball_dy = 4, -4
        self.ball_color = random.choice(self.COLORS)

        # Пересоздаём блоки
        self.blocks = []
        self._create_blocks()

        # Возвращаем начальное состояние игры
        return self.get_state()

    def step(self, action):
        # Движение платформы
        if action == -1 and self.paddle_x > 0:
            self.paddle_x -= self.paddle_speed
        elif action == 1 and self.paddle_x < self.WIDTH - self.PADDLE_WIDTH:
            self.paddle_x += self.paddle_speed

        # Движение мяча
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Проверка столкновений
        self.check_collision_path()

        # Столкновения с границами
        if self.ball_x - self.BALL_RADIUS <= 0 or self.ball_x + self.BALL_RADIUS >= self.WIDTH:
            self.ball_dx = -self.ball_dx
        if self.ball_y - self.BALL_RADIUS <= 0:
            self.ball_dy = -self.ball_dy

        # Столкновение с платформой
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)
        ball_rect = pygame.Rect(self.ball_x - self.BALL_RADIUS, self.ball_y - self.BALL_RADIUS,
                                self.BALL_RADIUS * 2, self.BALL_RADIUS * 2)

        reward = 0  # Начальная награда

        if paddle_rect.colliderect(ball_rect):
            self.ball_dy = -abs(self.ball_dy)
            reward += 0.5  # Награда за отбивание мяча

        # Возвращаем состояние, награду и статус завершения игры
        done = self.ball_y + self.BALL_RADIUS >= self.HEIGHT
        return self.get_state(), reward, done

        # --- Код ниже не исполнится из-за return выше, но оставлен для справки ---
        # Если хотите использовать расширенную логику наград,
        # то перенесите return выше в конец step(), а код ниже раскомментируйте.
        """
        if paddle_rect.colliderect(ball_rect):
            self.ball_dy = -abs(self.ball_dy)
            reward += 1.0  # Увеличенная награда за успешное отбивание мяча

        # Столкновения с боковыми панелями
        for i, panel in enumerate(self.side_panels):
            if panel.colliderect(ball_rect):
                self.ball_color = self.side_colors[i]  # Изменение цвета мяча
                self.ball_dx = -self.ball_dx
                break

        # Столкновение с блоками
        for block, color in self.blocks[:]:
            if block.colliderect(ball_rect):
                if color == self.ball_color:  # Разрушается только блок такого же цвета
                    self.blocks.remove((block, color))
                    reward += 2.0  # Увеличенная награда за разрушение блока
                else:
                    # Инвертируем только вертикальную скорость, если цвет не совпадает
                    self.ball_dy = -self.ball_dy
                break

        # Штраф за пропуск мяча
        if self.ball_y + self.BALL_RADIUS >= self.HEIGHT:
            reward -= 5.0  # Сильный штраф за пропуск мяча

        # Завершение игры
        done = self.ball_y + self.BALL_RADIUS >= self.HEIGHT or len(self.blocks) == 0

        return self.get_state(), reward, done
        """

    def render(self):
        """Отображает текущее состояние игры на экране."""
        # Если есть фоновое изображение - выводим его, иначе заливаем экран
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        # Рисуем платформу с небольшим градиентом
        # Для примера: сверху - белый, снизу - светло-серый
        paddle_surface = pygame.Surface((self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
        color_top = (200, 200, 200)
        color_bottom = (100, 100, 100)
        for y in range(self.PADDLE_HEIGHT):
            # Интерполяция цвета (простой линейный градиент)
            r = color_top[0] + (color_bottom[0] - color_top[0]) * y / self.PADDLE_HEIGHT
            g = color_top[1] + (color_bottom[1] - color_top[1]) * y / self.PADDLE_HEIGHT
            b = color_top[2] + (color_bottom[2] - color_top[2]) * y / self.PADDLE_HEIGHT
            pygame.draw.line(paddle_surface, (int(r), int(g), int(b)), (0, y), (self.PADDLE_WIDTH, y))
        self.screen.blit(paddle_surface, (self.paddle_x, self.paddle_y))

        # Рисование мяча
        pygame.draw.circle(self.screen, self.ball_color, (int(self.ball_x), int(self.ball_y)), self.BALL_RADIUS)

        # Рисуем блоки с закруглёнными углами
        for block, color in self.blocks:
            # Создаём дополнительную поверхность и рисуем на ней закруглённый прямоугольник
            block_surface = pygame.Surface((self.BLOCK_WIDTH, self.BLOCK_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(block_surface, color, (0, 0, self.BLOCK_WIDTH, self.BLOCK_HEIGHT), border_radius=8)
            self.screen.blit(block_surface, (block.x, block.y))

        # Рисование боковых панелей с полупрозрачностью
        for i, panel in enumerate(self.side_panels):
            panel_surface = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
            # Устанавливаем альфа-канал (прозрачность)
            panel_surface.set_alpha(120)
            panel_surface.fill(self.side_colors[i])
            self.screen.blit(panel_surface, (panel.x, panel.y))

        # Выводим счёт: количество оставшихся блоков
        text_surface = self.font.render(f"Blocks left: {len(self.blocks)}", True, self.WHITE)
        self.screen.blit(text_surface, (10, self.HEIGHT - 30))

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        self.clock.tick(self.FPS)

    def play(self):
        running = True
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Управление платформой
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.paddle_x > 0:
                self.paddle_x -= self.paddle_speed
            if keys[pygame.K_RIGHT] and self.paddle_x < self.WIDTH - self.PADDLE_WIDTH:
                self.paddle_x += self.paddle_speed

            # Движение мяча
            self.check_collision_path()
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy

            # Столкновения с границами
            if self.ball_x - self.BALL_RADIUS <= 0:  # Левая граница
                self.ball_dx = -self.ball_dx
            if self.ball_x + self.BALL_RADIUS >= self.WIDTH:  # Правая граница
                self.ball_dx = -self.ball_dx
            if self.ball_y - self.BALL_RADIUS <= 0:  # Верхняя граница
                self.ball_dy = -self.ball_dy
            if self.ball_y + self.BALL_RADIUS >= self.HEIGHT:  # Нижняя граница (игрок проигрывает)
                print("Game Over!")
                running = False

            # Столкновение с платформой
            paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)
            if paddle_rect.colliderect(
                pygame.Rect(self.ball_x - self.BALL_RADIUS, self.ball_y - self.BALL_RADIUS, self.BALL_RADIUS * 2, self.BALL_RADIUS * 2)
            ):
                self.ball_dy = -abs(self.ball_dy)

            # Столкновения с боковыми панелями
            ball_rect = pygame.Rect(self.ball_x - self.BALL_RADIUS, self.ball_y - self.BALL_RADIUS, self.BALL_RADIUS * 2, self.BALL_RADIUS * 2)
            for i, panel in enumerate(self.side_panels):
                if panel.colliderect(ball_rect):
                    self.ball_color = self.side_colors[i]  # Изменение цвета мяча
                    self.ball_dx = -self.ball_dx
                    break

            # Отрисовка всего на экране
            self.render()

        pygame.quit()

if __name__ == "__main__":
    game = BrickBreakerGame()
    game.play()
