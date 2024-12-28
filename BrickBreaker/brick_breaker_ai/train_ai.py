import numpy as np
import torch
import sys
import os

from BrickBreaker.brick_breaker_ai.start_learning_strategy import get_next_action

# Добавляем корневую директорию проекта в пути
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from BrickBreaker.game.brick_breaker import BrickBreakerGame
from ai_model import AIModel
from replay_buffer import ReplayBuffer

# Настройка
EPISODES = 100
GAMMA = 0.99
EPSILON = 1.0  # Начальное значение
EPSILON_DECAY = 0.995  # Скорость уменьшения
EPSILON_MIN = 0.05  # Минимальное значение
LEARNING_RATE = 0.001
BATCH_SIZE = 64
MAX_BUFFER_SIZE = 10000

# Создание игры, модели и буфера
game = BrickBreakerGame()
state_size = len(game.get_state())
action_size = 3  # -1, 0, 1 (влево, стоять, вправо)

model = AIModel(state_size, action_size, learning_rate=LEARNING_RATE)
replay_buffer = ReplayBuffer(max_size=MAX_BUFFER_SIZE)

# Обучение
for episode in range(EPISODES):
    state = game.reset()
    total_reward = 0
    done = False

    while not done:
        # Выбор действия: исследование или использование модели
        if np.random.random() < EPSILON:
            action = np.random.choice(action_size)  # Случайное действие
        else:
            action = model.predict(state)  # Предсказание модели

        action = get_next_action(EPSILON, game, model)

        # Выполнение действия и сохранение перехода
        next_state, reward, done = game.step(action - 1)  # Смещение для соответствия -1, 0, 1
        replay_buffer.add(state, action, reward, next_state, done)

        total_reward += reward
        state = next_state

        # Тренировка модели, если достаточно данных
        if replay_buffer.size() >= BATCH_SIZE:
            batch = replay_buffer.sample(BATCH_SIZE)
            model.train(batch, GAMMA)

        # Отрисовка игры для визуализации
        game.render()

    # Уменьшение epsilon
    if EPSILON > EPSILON_MIN:
        EPSILON *= EPSILON_DECAY

    print(f"Episode: {episode}, Action: {action}, Reward: {reward}, Total Reward: {total_reward}")
    print(f"Episode {episode + 1}, Total Reward: {total_reward}")

# Сохранение модели
model.save_model("checkpoints/model.pth")
print("Обучение завершено, модель сохранена как 'model.pth'")
