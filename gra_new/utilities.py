import numpy as np

class Gra:
	def __init__(self) -> None:
		self.map: np.ndarray = None
		self.current: int = None
		self.next: int = None
		self.lose: bool = None
		self.points: float = None
		self.history: list[int] = None
		self.last_move: int = None
	
	def get_max_number(self) -> int:
		pass
	
	def get_avalible_moves(self) -> list[bool]:
		pass

	def get_revard(self) -> bool:
		pass

	def get_game_data(self) -> list[float]:
		pass

	def move(self, move_index: int) -> None:
		pass

def get_max_number(map: np.ndarray) -> int:
	return np.max(map)

def get_avalible_moves(map: np.ndarray) -> list[bool]:
	return [map[6, i] == 0 for i in range(5)]

def get_revard(points: int) -> float:
	return points

def get_game_data(self: Gra) -> list[float]:
	ret: list[float] = []
	ret += self.map.flatten().tolist()
	ret.append(self.current)
	ret.append(self.next)

	return ret

def move(map: np.ndarray, move_index: int) -> np.ndarray:
	if map[6, move_index] != 0:
		return map
	
	def falling(map: np.ndarray):
		# Dla każdej kolumny osobno
		for col in range(map.shape[1]):
			# Pobieramy niezerowe elementy kolumny
			non_zero_elements = map[:, col][map[:, col] != 0]
			
			# Resetujemy kolumnę do zer
			map[:, col] = 0
			
			# Umieszczamy niezerowe elementy na najwyższych pozycjach, jeśli są jakieś niezerowe elementy
			if len(non_zero_elements) > 0:
				map[:len(non_zero_elements), col] = non_zero_elements


		
	
	falling(map)
	return map
	


if __name__ == '__main__':
	import gra
	import timeit
	test_gra = gra.Gra()

	test_move = 1
	test_gra.map[6, 2] = 2
	test_gra.map[5, 2] = 3
	print(move(test_gra.map, test_move))

	#print(timeit.timeit(lambda: move(test_gra.map, test_move), number=1000))