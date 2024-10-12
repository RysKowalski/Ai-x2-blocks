from random import randint
import numpy as np
import utilities

class Gra:
	def __init__(self) -> None:
		self.map: np.ndarray = np.zeros((8, 5))
		self.current: int = randint(0, 5)
		self.next: int = randint(0, 5)
		self.lose: bool = False
		self.points: float = 0
		self.history: list[int] = []
		self.last_move: int = -1
	
	def get_max_number(self):
		return utilities.get_max_number(self.map)
	
	def get_avalible_moves(self):
		return utilities.get_avalible_moves(self.map)



if __name__ == '__main__':
	test = Gra()