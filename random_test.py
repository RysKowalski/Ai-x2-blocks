import gymnasium as gym
from GameEnvironment import GameEnv

env = GameEnv()

episodes = 100

for episode in range(episodes):
    obs, info = env.reset()

    total_reward = 0.0
    terminated = False
    truncated = False

    while not (terminated or truncated):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

    print(
        f"Episode {episode + 1}: "
        f"reward={total_reward:.2f}, "
        f"moves={info['move_count']}, "
        f"level={info['game_level']}"
    )
