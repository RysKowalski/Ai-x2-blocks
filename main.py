import gymnasium as gym
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from GameEnvironment import GameEnv

print("\nloading modules finished\n")

env = GameEnv()

state_size: int = 0
if env.observation_space.shape is not None:
    state_size = env.observation_space.shape[0]

action_size = 5

print("State Size:", state_size)
print("Action Size:", action_size)

model: Sequential = Sequential(
    [
        tf.keras.Input((37,)),
        Dense(32, activation="relu"),
        Dense(32, activation="relu"),
        Dense(5),
    ]
)

model.compile(optimizer="adam", loss="mse")

gamma = 0.95
epsilon = 1.0
epsilon_decay = 0.99
epsilon_min = 0.01
episodes = 100

for episode in range(episodes):
    state, _ = env.reset()

    done = False
    total_reward: float = 0

    while not done:
        if np.random.rand() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(model.predict(state, verbose=0))

        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated
        total_reward += reward

        target = reward
        if not done:
            target += gamma * np.max(model.predict(next_state, verbose=0))

        q_values = model.predict(
            state,
            verbose=0,
        )
        q_values[0][action] = target

        model.fit(state, q_values, epochs=1, verbose=0)
        state = next_state

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print(
        f"Episode {episode + 1} completed, reward: {total_reward}, moves: {env.move_count}"
    )

state, _ = env.reset()

done = False
total_reward = 0

while not done:
    action = np.argmax(model.predict(state, verbose=0))

    next_state, reward, terminated, truncated, _ = env.step(action)

    total_reward += reward
    done = terminated or truncated

print("Total Reward:", total_reward)
