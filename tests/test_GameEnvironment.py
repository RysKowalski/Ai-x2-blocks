import gymnasium as gym
import numpy as np

from GameEnvironment import GameEnv


def test_initiation_creates_spaces() -> None:
    env = GameEnv()

    assert env.action_space == gym.spaces.Discrete(5)
    assert env.observation_space == gym.spaces.Dict(
        {
            "moves": gym.spaces.Box(low=1, high=6, shape=[2], dtype=np.int32),
            "map": gym.spaces.Box(low=0, high=11, shape=[5, 7], dtype=np.int32),
        }
    )


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

    map = np.ones([5, 7], dtype=np.int32)
    env.map = map
    next = np.array([7, 7], dtype=np.int32)
    env.next = next

    assert env._get_obs() == {"moves": next, "map": map}


def test__get_info_returns_correct_data() -> None:
    env = GameEnv()
    env.game_level = 2
    env.move_count = 2

    assert env._get_info() == {"game_level": 2, "move_count": 2}
