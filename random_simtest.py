import numpy as np
from GameEnvironment import GameEnv

env = GameEnv()

episodes = 1000

levels: int = 0
total_move_count: int = 0
total_test_reward: float = 0
episode: int = 0
while True:
    episode += 1
    obs, info = env.reset()

    total_reward = 0.0
    terminated = False
    truncated = False

    while not (terminated or truncated):
        legal_actions = np.flatnonzero(env.avalible_moves)
        action = int(np.random.choice(legal_actions))
        obs, reward, terminated, truncated, info = env.step(action)
        if info["game_level"] > 0:
            print(
                "MORE THEN 0!!!!1!!"
                f"Episode {episode + 1}: "
                f"reward={total_reward:.2f}, "
                f"moves={info['move_count']}, "
                f"level={info['game_level']}"
            )

        total_reward += float(reward)

    levels += info["game_level"]
    total_move_count += info["move_count"]
    total_test_reward += total_reward
    print(
        f"Episode {episode + 1}: "
        f"reward={total_reward:.2f} avg{total_test_reward / (episode + 1)}, "
        f"moves={info['move_count']} avg{total_move_count / (episode + 1)}, "
        f"level={info['game_level']}"
    )

print(levels)
