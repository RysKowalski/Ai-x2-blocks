import keras
import numpy as np

from GameEnvironment import GameEnv


MODEL_PATH: str = "model.keras"


model = keras.saving.load_model(MODEL_PATH)


def print_state(env: GameEnv) -> None:
    map_view: np.ndarray = env.map.T[::-1]

    print("┌" + "─" * (map_view.shape[1] * 4 - 1) + "┐")

    for row in map_view:
        print("│", end="")
        for value in row:
            print(f" {int(value):2}", end="│")
        print()

    print("└" + "─" * (map_view.shape[1] * 4 - 1) + "┘")
    print(f"Next: {env.next.tolist()}, reward: {round(env._reward, 4)}")
    print(f"Move: {env.move_count}  Level: {env.game_level}")


def get_action(env, state, epsilon: float) -> int:
    legal_actions = np.flatnonzero(env.avalible_moves)

    if np.random.rand() < epsilon:
        return int(np.random.choice(legal_actions))

    q_values = model.predict(state, verbose=0)[0]
    q_values = np.where(env.avalible_moves, q_values, -np.inf)

    return int(np.argmax(q_values))


def play_game() -> None:
    env: GameEnv = GameEnv()

    state, _ = env.reset()

    done: bool = False
    total_reward: float = 0.0

    print_state(env)

    while not done:
        action: int = get_action(env, state, 0.0)

        next_state, reward, terminated, truncated, _ = env.step(action)

        total_reward += float(reward)
        state = next_state
        done = terminated or truncated

        print_state(env)
        print(f"Action: {action}")
        print(f"Step reward: {float(reward):.4f}")

    print()
    print("=" * 40)
    print("GAME OVER")
    print("=" * 40)
    print(
        "Total Reward:",
        round(total_reward, 4),
        " moves: ",
        env.move_count,
        " level: ",
        env.game_level,
    )


if __name__ == "__main__":
    play_game()
