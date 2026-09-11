from GameEnvironment import GameEnv


def run_tui(env: GameEnv) -> None:
    _, _ = env.reset()
    terminated = False
    truncated = False

    while True:
        print_state(env)
        print()
        print("Choose action [1-5], or q to quit:")

        command: str = input("> ").strip()

        if command.lower() == "q":
            break

        try:
            action: int = int(command)
        except ValueError:
            print("Invalid action.")
            input("Press Enter...")
            continue

        if not 1 <= action <= 5:
            print("Action must be between 1 and 5.")
            input("Press Enter...")
            continue

        _, reward, terminated, truncated, info = env.step(action - 1)

        if terminated or truncated:
            print("\033[2J\033[H", end="")
            print("Map:")
            print(env.map)
            print()
            print(f"Next: {env.next}")
            print()
            print(f"Reward: {reward}")
            print(f"Info: {info}")
            print()
            print("Episode finished.")
            input("Press Enter to reset...")

            env.reset()


def print_state(env: GameEnv) -> None:
    map_view = env.map.T[::-1]

    print("┌" + "─" * (map_view.shape[1] * 4 - 1) + "┐")

    for row in map_view:
        print("│", end="")
        for value in row:
            print(f" {int(value):2}", end="│")
        print()

    print("└" + "─" * (map_view.shape[1] * 4 - 1) + "┘")
    print(f"Next: {env.next.tolist()}, reward: {round(env._reward, 4)}")


if __name__ == "__main__":
    run_tui(GameEnv())
