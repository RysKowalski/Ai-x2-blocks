from collections import deque

import random
import keras
import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential

from GameEnvironment import GameEnv

print("\nloading modules finished\n")

TRAINING_NAME: str = "DDQN-5"
log_writer = tf.summary.create_file_writer(f"logs/{TRAINING_NAME}")

env = GameEnv()

episode = 7000
episodes_to_do = episode + 1000
save_model_every_episodes = 50

gamma = 0.98
epsilon_decay = 0.995
epsilon = epsilon_decay**episode
epsilon_min = 0.005

copy_network_every_steps: int = 600
train_every_steps: int = 100
batch_size: int = 128
memory_size = 10000
warmup = 1000
memory: deque[tuple[np.ndarray, int, float, np.ndarray, list[bool], bool]] = deque(
    maxlen=memory_size
)


def create_net(new: bool) -> Sequential:
    if new:
        model: Sequential = Sequential(
            [
                keras.Input((432,)),
                Dense(256, activation="relu"),
                Dense(128, activation="relu"),
                Dense(128, activation="relu"),
                Dense(64, activation="relu"),
                Dense(5, activation="linear"),
            ]
        )
        model.compile("Adam", "Huber")
        return model
    else:
        _model = keras.saving.load_model("model.keras")
        if isinstance(_model, Sequential):
            if _model.loss is None or _model.optimizer is None:
                _model.compile("Adam", "Huber")

            return _model
        raise


online_net: Sequential = create_net(False)
target_net: Sequential = create_net(False)
target_net.set_weights(online_net.get_weights())

last_log_episode = -1


def get_action(env: GameEnv, state, epsilon: float) -> int:
    legal_actions = np.flatnonzero(env.available_moves)

    if np.random.rand() < epsilon:
        return int(np.random.choice(legal_actions))

    state_tensor = tf.convert_to_tensor(state[None, :], dtype=tf.float32)
    q_values = online_net(state_tensor)[0]

    q_values = np.where(tf.convert_to_tensor(env.available_moves), q_values, -np.inf)

    return int(tf.argmax(q_values).numpy())


def train(episode: int) -> None:
    if len(memory) < batch_size or len(memory) < warmup:
        return
    batch = random.sample(memory, batch_size)

    states, actions, rewards, next_states, next_available_moves, dones = zip(*batch)

    states = tf.convert_to_tensor(states, dtype=tf.int32)
    actions = tf.convert_to_tensor(actions, dtype=tf.int32)
    rewards = tf.convert_to_tensor(rewards, dtype=tf.float32)
    next_states = tf.convert_to_tensor(next_states, dtype=tf.int32)
    next_available_moves = tf.convert_to_tensor(next_available_moves, dtype=tf.bool)
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

        next_online_q_values = online_net(next_states)
        next_online_q_values = tf.where(
            next_available_moves,
            next_online_q_values,
            tf.constant(-np.inf, dtype=tf.float32),
        )

        next_actions = tf.argmax(next_online_q_values, axis=1, output_type=tf.int32)

        next_target_q_values = target_net(next_states)

        next_indicies = tf.stack(
            [tf.range(tf.shape(next_actions)[0], dtype=tf.int32), next_actions], axis=1
        )

        next_q = tf.gather_nd(next_target_q_values, next_indicies)

        target_q = rewards + gamma * next_q * (1.0 - dones)

        loss = online_net.loss(target_q, current_q)

    gradients = tape.gradient(loss, online_net.trainable_variables)
    online_net.optimizer.apply_gradients(zip(gradients, online_net.trainable_variables))

    global last_log_episode
    if last_log_episode != episode:
        last_log_episode = episode
        with log_writer.as_default():
            tf.summary.scalar("training/loss", loss, step=episode)
            tf.summary.scalar(
                "training/mean_reward", tf.reduce_mean(rewards), step=episode
            )
            tf.summary.scalar(
                "training/mean_q", tf.reduce_mean(current_q), step=episode
            )
            tf.summary.scalar(
                "training/mean_target_q", tf.reduce_mean(target_q), step=episode
            )
            tf.summary.scalar(
                "training/mean_next_q", tf.reduce_mean(next_q), step=episode
            )


try:
    global_steps: int = 0
    for episode in range(episode, episodes_to_do):
        state, _ = env.reset()

        done: bool = False
        total_reward: float = 0

        while not done:
            global_steps += 1
            action = get_action(env, state, epsilon)

            next_state, reward, terminated, truncated, _ = env.step(action)
            reward = float(reward)
            done = bool(terminated or truncated)
            total_reward += reward

            memory.append(
                (state, action, reward, next_state, env.available_moves.copy(), done)
            )

            state = next_state

            if global_steps % copy_network_every_steps == 0:
                target_net.set_weights(online_net.get_weights())
            if global_steps % train_every_steps == 0:
                train(episode)

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        print(
            f"Episode {episode + 1} completed, reward: {total_reward}, moves: {env.move_count}"
        )
        with log_writer.as_default():
            tf.summary.scalar("training/reward", total_reward, step=episode)
            tf.summary.scalar("training/moves", env.move_count, step=episode)
            tf.summary.scalar("training/level", env.game_level, step=episode)
            tf.summary.scalar("training/epsilon", epsilon, step=episode)

        log_writer.flush()

        if (episode + 1) % save_model_every_episodes == 0:
            online_net.save(f"logs/{TRAINING_NAME}/{TRAINING_NAME}-{episode}.keras")

except KeyboardInterrupt:
    target_net.save("interrupt_model.keras")
    exit()


online_net.save("model.keras")

for _ in range(10):
    state, _ = env.reset()

    done = False
    total_reward = 0

    while not done:
        action = get_action(env, state, 0)

        state, reward, terminated, truncated, _ = env.step(action)

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
