import numpy as np

from GameEnvironment import GameEnv


def test_reset_resets_data() -> None:
    env = GameEnv()
    env.map[1, 5] = 1
    env.next[0] = 10  # impossible value after reset
    env.game_level = 1
    env.move_count = 1

    env.reset()

    assert env.map.all() == 0
    assert env.next[0] != 10
    assert env.game_level == 0
    assert env.move_count == 0


def test__get_obs_returns_correct_data() -> None:
    env = GameEnv()

    map = np.ones(shape=[5, 7], dtype=np.int32)
    env.map = map
    next = np.array([7, 7], dtype=np.int32)
    env.next = next

    assert np.equal(env._get_obs(), np.array(([1] * 35 + [7, 7]), dtype=np.int32))


def test__get_info_returns_correct_data() -> None:
    env = GameEnv()
    env.game_level = 2
    env.move_count = 2

    assert env._get_info() == {"game_level": 2, "move_count": 2}


def test_step_falls_block() -> None:
    env = GameEnv()
    env.reset()
    env.next[0] = 2

    env.step(0)

    print(env.map)
    assert np.array_equal(
        env.map,
        np.array(
            [
                [2, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_merge_on_top() -> None:
    env = GameEnv()
    env.reset()
    env.next = np.array([1, 1], dtype=np.int32)

    env.step(0)
    env.step(0)

    print(env.map)
    assert np.array_equal(
        env.map,
        np.array(
            [
                [2, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_merge_three() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    env.next[0] = 1

    env.step(1)

    assert np.array_equal(
        env.map,
        np.array(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [3, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_merge_four() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [5, 1, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0],
            [5, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    env.next[0] = 1

    env.step(1)

    assert np.array_equal(
        env.map,
        np.array(
            [
                [5, 0, 0, 0, 0, 0, 0],
                [4, 0, 0, 0, 0, 0, 0],
                [5, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_chain_merging() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [5, 4, 3, 2, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    env.next[0] = 1

    env.step(0)

    assert np.array_equal(
        env.map,
        np.array(
            [
                [6, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_biggest_merge_first() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [1, 3, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 3, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    env.next[0] = 1

    env.step(1)

    assert np.array_equal(
        env.map,
        np.array(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [5, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_merge_from_side() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [1, 3, 4, 3, 4, 3, 4],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
    )
    env.next[0] = 1

    env.step(1)

    assert np.array_equal(
        env.map,
        np.array(
            [
                [3, 4, 3, 4, 3, 4, 0],
                [2, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    )


def test_step_consumes_next_move() -> None:
    env = GameEnv()
    env.reset()
    env.next[0] = 10  # larger than max random

    env.step(0)

    assert env.next[0] != 10


def test_step_game_level_increases() -> None:
    env = GameEnv()
    env.reset()
    env.next[0] = 11
    env.next[1] = 11
    env.map[1, 0] = 2

    env.step(0)
    env.step(0)

    assert env.game_level == 1
    assert env.map[0, 0] == 11
    assert env.map[1, 0] == 1


def test_step_move_count_increases() -> None:
    env = GameEnv()
    env.reset()

    env.step(0)

    assert env.move_count == 1


def test_step_termination_detection() -> None:
    env = GameEnv()
    env.reset()
    env.map = np.array(
        [
            [1, 2, 3, 4, 5, 6, 0],
            [8, 7, 8, 7, 8, 7, 8],
            [1, 8, 7, 8, 7, 8, 7],
            [8, 7, 8, 7, 8, 7, 8],
            [7, 8, 7, 8, 7, 8, 7],
        ]
    )
    env.next = np.array([1, 2])

    _, _, terminated, _, _ = env.step(0)
    assert terminated
