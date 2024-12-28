import torch
import sys
import os

# Добавляем корневую директорию проекта в пути
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from BrickBreaker.game.brick_breaker import BrickBreakerGame
from ai_model import AIModel

# Загрузка обученной модели
MODEL_PATH = "checkpoints/model.pth"

# Настройка игры
game = BrickBreakerGame()
state_size = len(game.get_state())
action_size = 3  # -1, 0, 1 (влево, стоять, вправо)

# Используем статический метод с корректными параметрами
model = AIModel.load_model(MODEL_PATH, state_size, action_size)

# Игровой цикл
state = game.reset()
running = True

while running:
    # Предсказание действия модели
    action = model.predict(state)

    # Выполнение действия в игре
    next_state, reward, done = game.step(action - 1)  # Смещение для соответствия -1, 0, 1

    # Отрисовка игры
    game.render()

    # Проверка завершения игры
    if done:
        running = False

    # Переход к следующему состоянию
    state = next_state

print("Игра завершена!")
