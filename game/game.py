from typing import Self

def check_empty_column(map: list[list[int]], column: int) -> int:
	map_row: list[int] = [row[column] for row in map]
	
	empty: int = len(map_row)
	
	for i, num in enumerate(map_row):
		if num != 0:
			empty = i + 1
	
	return empty

class Game:
	
	def __init__(self: Self, state = None):
		self.points: int = 0
		self.map: list[list[int]] = [[0 for _ in range(5)] for _ in range(7)]
		self.number_range: list[int] = [1, 6]
		self.moves: int = 0

	def get_possible_moves(self: Self) -> list[bool]:
		possible_moves: list[bool] = [i == 0 for i in self.map[6]]
		return possible_moves
	
	def move(self: Self, move: int):
		...

if __name__ == '__main__':
	t = Game()
	
	t.map[0][4] = 1
	t.map[1][4] = 1
	t.map[2][4] = 1

	for i, row in enumerate(t.map):
		print(i, row)
	print(check_empty_column(t.map, 4))