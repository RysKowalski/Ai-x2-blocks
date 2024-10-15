from random import randint
import numpy as np
import utilities

class Gra:
	def __init__(self) -> None:
		self.map: np.ndarray = np.zeros((8, 5), dtype=int)
		self.current: int = randint(1, 6)
		self.next: int = randint(1, 6)
		self.lose: bool = False
		self.points: float = 0
		self.history: list[int] = []
		self.last_move: int = -1
	
	def get_max_number(self) -> int:
		return utilities.get_max_number(self.map)
	
	def get_avalible_moves(self) -> list[bool]:
		return utilities.get_avalible_moves(self.map)
	
	def get_revard(self) -> float:
		return utilities.get_revard(self.points)
	
	def get_game_data(self) -> list[float]:
		return utilities.get_game_data(self)
	
	def move(self, move_index: int) -> None:
		self.map = utilities.move(self.map, move_index)



if __name__ == '__main__':
	test = Gra()

	print(test.get_game_data())