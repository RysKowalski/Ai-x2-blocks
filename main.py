from collections import deque

import random
import keras
import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential

from GameEnvironment import GameEnv

print("\nloading modules finished\n")

log_writer = tf.summary.create_file_writer("logs")

env = GameEnv()

gamma = 0.95
epsilon = 0.5
epsilon_decay = 0.995
epsilon_min = 0.01
episodes = 350

copy_network_every_episodes: int = 5
batch_size: int = 30
memory_size = 10000
memory: deque[tuple[np.ndarray, int, float, np.ndarray, bool]] = deque(
    maxlen=memory_size
)


Sequential(
    [
        keras.layers.Conv2D((35), (5, 7), activation="relu"),
        keras.layers.Conv2D((35), (5, 7), activation="relu"),
    ]
)


def create_net(new: bool) -> Sequential:
    if new:
        model: Sequential = Sequential(
            [
                keras.Input((37,)),
                Dense(64, activation="relu"),
                Dense(64, activation="relu"),
                Dense(5, activation="linear"),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model
    else:
        _model = keras.saving.load_model("model.keras")
        if isinstance(_model, Sequential):
            return _model
        raise


optimizer_fn = keras.optimizers.Adam()
loss_fn = keras.losses.MeanSquaredError()

online_net: Sequential = create_net(True)
target_net: Sequential = create_net(True)


def get_action(env, state, epsilon: float) -> int:
    legal_actions = np.flatnonzero(env.available_moves)

    if np.random.rand() < epsilon:
        return int(np.random.choice(legal_actions))

    q_values = online_net.predict(state, verbose=0)[0]
    q_values = np.where(env.available_moves, q_values, -np.inf)

    return int(np.argmax(q_values))


def train(episode: int) -> None:
    if len(memory) < batch_size:
        return
    batch = random.sample(memory, batch_size)

    states, actions, rewards, next_states, dones = zip(*batch)

    states = tf.convert_to_tensor(states, dtype=tf.int32)
    states = tf.squeeze(states, axis=1)

    next_states = tf.convert_to_tensor(next_states, dtype=tf.int32)
    next_states = tf.squeeze(next_states, axis=1)

    actions = tf.convert_to_tensor(actions, dtype=tf.int32)
    rewards = tf.convert_to_tensor(rewards, dtype=tf.float32)
    dones = tf.convert_to_tensor(dones, dtype=tf.float32)

    with tf.GradientTape() as tape:
        q_values = online_net(states)
        indices = tf.stack(
            [
                tf.range(tf.shape(actions)[0], dtype=tf.int32),
                actions,
            ],
            axis=1,
        )

        current_q = tf.gather_nd(q_values, indices)
        next_q = tf.reduce_max(target_net(next_states), axis=1)

        target_q = rewards + gamma * next_q * (1.0 - dones)

        loss = loss_fn(target_q, current_q)

    gradients = tape.gradient(loss, online_net.trainable_variables)
    optimizer_fn.apply_gradients(zip(gradients, online_net.trainable_variables))

    with log_writer.as_default():
        tf.summary.scalar("training/loss", loss, step=episode)
        tf.summary.scalar("training/mean_reward", tf.reduce_mean(rewards), step=episode)
        tf.summary.scalar("training/mean_q", tf.reduce_mean(current_q), step=episode)
        tf.summary.scalar(
            "training/mean_target_q", tf.reduce_mean(target_q), step=episode
        )
        tf.summary.scalar("training/mean_next_q", tf.reduce_mean(next_q), step=episode)


try:
    for episode in range(episodes):
        state, _ = env.reset()

        done = False
        total_reward: float = 0

        while not done:
            action = get_action(env, state, epsilon)

            next_state, reward, terminated, truncated, _ = env.step(action)
            reward = float(reward)
            done = terminated or truncated
            total_reward += reward

            memory.append((state, action, reward, next_state, done))

            state = next_state

        epsilon = max(epsilon_min, epsilon * epsilon_decay)
        train(episode)
        if episode % copy_network_every_episodes == 0:
            target_net.set_weights(online_net.get_weights())

        print(
            f"Episode {episode + 1} completed, reward: {total_reward}, moves: {env.move_count}"
        )
        with log_writer.as_default():
            tf.summary.scalar("training/reward", total_reward, step=episode)
            tf.summary.scalar("training/moves", env.move_count, step=episode)
            tf.summary.scalar("training/level", env.game_level, step=episode)

        log_writer.flush()

except KeyboardInterrupt:
    target_net.save("interrupt_model.keras")
    exit()


target_net.save("model.keras")

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
