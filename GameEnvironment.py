from typing import Any, SupportsFloat

import gymnasium as gym
import numpy as np


class GameEnv(gym.Env):
    def __init__(self) -> None:
        self.map: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self.next: np.ndarray = np.zeros([2], dtype=np.int32)
        self.game_level: int = 0
        self.move_count: int = 0

        self._map_merges: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self._last_move_column: int = 0

        self.observation_space: gym.Space = gym.spaces.Box(
            shape=[37],
            low=np.array([1, 1] + [0] * 35, dtype=np.int32),
            high=np.array([6, 6] + [11] * 35, dtype=np.int32),
            dtype=np.int32,
        )

        self.action_space: gym.Space = gym.spaces.Discrete(5)

    def _get_obs(self) -> np.ndarray:
        return np.concatenate([self.next, self.map.flatten()]).reshape(1, -1)

    def _get_info(self) -> dict[str, int]:
        return {"game_level": self.game_level, "move_count": self.move_count}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)

        self.map: np.ndarray = np.zeros([5, 7], dtype=np.int32)
        self.next: np.ndarray = self.np_random.integers(1, 6, size=[2], dtype=np.int32)
        self.game_level: int = 0
        self.move_count: int = 0

        return self._get_obs(), self._get_info()

    def step(
        self, action
    ) -> tuple[np.ndarray, SupportsFloat, bool, bool, dict[str, int]]:
        self._last_move_column = action
        reward = 0

        canMergeOnTop: bool = self.map[action, 6] == self.next[0]
        if self.map[action, 6] == 0 or canMergeOnTop:
            self.move_count += 1
            reward = 0.01

            if canMergeOnTop:
                self.map[action, 6] = self.next[0] + 1
            else:
                self.map[action, 6] = self.next[0]

            self.new_next()

            self.fall_move_loop()
        else:
            reward = -0.1

        truncated = False
        return (
            self._get_obs(),
            reward,
            self.detect_termination(),
            truncated,
            self._get_info(),
        )

    def new_next(self) -> None:
        self.next[0] = self.next[1]
        self.next[1] = self.np_random.integers(1, 6, dtype=np.int32)

    def fall_move_loop(self) -> None:
        merged: bool = True

        while merged:
            self.fall()
            merged = self.merge()

    def fall(self) -> None:
        for col in range(self.map.shape[0]):
            values: np.ndarray = self.map[col][self.map[col] != 0]
            self.map[col].fill(0)
            self.map[col, : len(values)] = values

    def merge(self) -> bool:
        for col in range(5):
            for row in range(7):
                c = self.map[col, row]
                if c == 0:
                    self._map_merges[col, row] = 0
                    continue
                same_tiles: int = 0
                if col > 0:
                    same_tiles += self.map[col - 1, row] == c
                if col < 4:
                    same_tiles += self.map[col + 1, row] == c
                if row > 0:
                    same_tiles += self.map[col, row - 1] == c
                if row < 6:
                    same_tiles += self.map[col, row + 1] == c
                self._map_merges[col, row] = same_tiles

        # przez wszystkie elementy policzyć ile można połączyć
        # jeżeli jest więcej niż 1 max, priorytezować
        # kolumnę ostztbiego ruchu
        # znajdź największy index dla każdej kolumny, sprawdź który jest największy, jeżeli remis to

        best_pos: tuple[int, int] | None = None
        best_score = -1

        for col in range(5):
            for row in range(7):
                score = self._map_merges[col, row]

                if score > best_score:
                    best_score = score
                    best_pos = (col, row)
                elif (
                    score == best_score
                    and best_pos is not None
                    and col == self._last_move_column
                    and best_pos[0] != self._last_move_column
                ):
                    best_pos = (col, row)

        if best_score > 0 and best_pos is not None:
            self.merge_single(best_pos)
            self.check_game_level()
            return True

        return False

    def merge_single(self, pos: tuple[int, int]) -> None:
        amount: int = 0
        c = self.map[pos]
        if pos[0] > 0:
            if self.map[pos[0] - 1, pos[1]] == c:
                amount += 1
                self.map[pos[0] - 1, pos[1]] = 0
        if pos[0] < 4:
            if self.map[pos[0] + 1, pos[1]] == c:
                amount += 1
                self.map[pos[0] + 1, pos[1]] = 0
        if pos[1] > 0:
            if self.map[pos[0], pos[1] - 1] == c:
                amount += 1
                self.map[pos[0], pos[1] - 1] = 0
        if pos[1] < 6:
            if self.map[pos[0], pos[1] + 1] == c:
                amount += 1
                self.map[pos[0], pos[1] + 1] = 0

        self.map[pos] += amount

    def check_game_level(self) -> None:
        diff: int = self.map.max() - 11

        if diff > 0:
            np.subtract(self.map, diff, out=self.map)
            np.maximum(self.map, 0, out=self.map)
            self.game_level += diff

    def detect_termination(self) -> bool:
        return not any(
            self.map[i, 6] == 0 or self.map[i, 6] == self.next[0] for i in range(5)
        )


if __name__ == "__main__":
    env = GameEnv()
    env.reset()
    env.next[0] = 1
    env.next[1] = 1
    for i in range(20):
        print(env.step(1))
