from collections import deque

import numpy as np
import tensorflow as tf
import keras
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential

from GameEnvironment import GameEnv

print("\nloading modules finished\n")

env = GameEnv()

state_size: int = 0
if env.observation_space.shape is not None:
    state_size = env.observation_space.shape[0]

action_size = 5

print("State Size:", state_size)
print("Action Size:", action_size)


gamma = 0.95
epsilon = 0.5
epsilon_decay = 0.995
epsilon_min = 0.01
episodes = 400
memory_size = 10000

memory: deque = deque(maxlen=memory_size)


def create_net(new: bool) -> Sequential:
    if new:
        model = Sequential(
            [
                keras.Input((37,)),
                Dense(32, activation="relu"),
                Dense(32, activation="relu"),
                Dense(5, activation="linear"),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model
    else:
        return keras.saving.load_model("model.keras")


policy_net: Sequential = create_net(False)
target_net: Sequential = create_net(False)


def get_action(env, state, epsilon: float) -> int:
    legal_actions = np.flatnonzero(env.avalible_moves)

    if np.random.rand() < epsilon:
        return int(np.random.choice(legal_actions))

    q_values = policy_net.predict(state, verbose=0)[0]
    q_values = np.where(env.avalible_moves, q_values, -np.inf)

    return int(np.argmax(q_values))


try:
    for episode in range(episodes):
        state, _ = env.reset()

        done = False
        total_reward: float = 0

        while not done:
            action = get_action(env, state, epsilon)

            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            total_reward += float(reward)

            target = reward
            if not done:
                target += gamma * np.max(target_net.predict(next_state, verbose=0))

            q_values = target_net.predict(
                state,
                verbose=0,
            )
            q_values[0][action] = target

            target_net.fit(state, q_values, epochs=1, verbose=0)
            state = next_state

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        print(
            f"Episode {episode + 1} completed, reward: {total_reward}, moves: {env.move_count}"
        )
except KeyboardInterrupt:
    target_net.save("interrupt_model.keras")


for _ in range(10):
    state, _ = env.reset()

    done = False
    total_reward = 0

    while not done:
        action = get_action(env, state, 0)

        next_state, reward, terminated, truncated, _ = env.step(action)

        total_reward += float(reward)
        done = terminated or truncated

    print(
        "Total Reward:",
        round(total_reward, 4),
        " moves: ",
        env.move_count,
        " level: ",
        env.game_level,
    )
target_net.save("model.keras")
