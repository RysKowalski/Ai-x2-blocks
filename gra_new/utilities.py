import numpy as np
from .gra import Gra

def get_max_number(map: np.ndarray) -> int:
	return np.max(map)

def get_avalible_moves(map: np.ndarray) -> list[bool]:
	return [map[6, i] == 0 for i in range(5)]

def get_revard(self: Gra):
	return type(self)

if __name__ == '__main__':
	import timeit
	get_revard()