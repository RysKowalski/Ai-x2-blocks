from typing import Any

import numpy as np
import gymnasium as gym


class GameEnv(gym.Env):
    def __init__(self) -> None:
        self.map: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self.next: np.ndarray = np.zeros([2], dtype=np.int32)

        self.observation_space = gym.spaces.Dict(
            {
                "moves": gym.spaces.Box(low=1, high=6, shape=[2], dtype=np.int32),
                "map": gym.spaces.Box(low=0, high=11, shape=[5, 7], dtype=np.int32),
            }
        )
        self.action_space = gym.spaces.Discrete(5)

    def _get_obs(self) -> dict:
        return {"moves": self.next, "map": self.map}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        return super().reset(seed=seed, options=options)
