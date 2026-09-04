from typing import Any, SupportsFloat

from gymnasium.core import ActType, ObsType
import numpy as np
import gymnasium as gym


class GameEnv(gym.Env):
    def __init__(self) -> None:
        self.map: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self.next: np.ndarray = np.zeros([2], dtype=np.int32)
        self.game_level: int = 0
        self.move_count: int = 0

        self.observation_space = gym.spaces.Dict(
            {
                "moves": gym.spaces.Box(low=1, high=6, shape=[2], dtype=np.int32),
                "map": gym.spaces.Box(low=0, high=11, shape=[5, 7], dtype=np.int32),
            }
        )
        self.action_space = gym.spaces.Discrete(5)

    def _get_obs(self) -> dict:
        return {"moves": self.next, "map": self.map}

    def _get_info(self) -> dict:
        return {"game_level": self.game_level, "move_count": self.move_count}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)

        self.map: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self.next: np.ndarray = self.np_random.integers(1, 6, size=[2], dtype=np.int32)
        self.game_level: int = 0
        self.move_count: int = 0

        return self._get_obs(), self._get_info()

    def step(self, action) -> tuple[object, SupportsFloat, bool, bool, dict[str, Any]]:

        terminated = False
        if self.map[action, 6] == 0 or self.map[action, 6] == self.next[0]:
            pass  # TODO: move logic
        else:
            terminated = True

        reward = 0
        truncated = False
        return self._get_obs(), reward, terminated, truncated, self._get_info()


if __name__ == "__main__":
    env = GameEnv()
    env.reset()
    env.map[1, 6] = 1
    env.next[0] = 1
    for i in range(20):
        print(env.step(1))
