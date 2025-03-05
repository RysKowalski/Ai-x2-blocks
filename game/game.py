from typing import Self

import random

class Game:
	def __init__(self: Self, state = None):
		"""inicjacja

		Args:
			state (_type_, optional): TODO. Defaults to None.
		"""
		self.points: int = 0
		self.map: list[list[int]] = [[0 for _ in range(5)] for _ in range(7)] # self.map[col][row]
		self.number_range: list[int] = [1, 6]
		self.moves: int = 0
		self.next_numbers: list[int] = [random.randint(*self.number_range), random.randint(*self.number_range)]
		self.last_drop: list[int] = [0, 0]
	
	def merge_two_cells(self: Self, cell_1_coords: tuple[int, int], cell_2_coords: tuple[int, int], succeed: int) -> bool:
		"""jeżeli komurki są takie same, łączy komurkę 1 z komurką 2, usuwając komurkę 2, i zwiększając wartość komurki 1 o 1.

		Args:
			cell_1_coords (tuple[int, int]): koordynaty col, row pierwszej komurki
			cell_2_coords (tuple[int, int]): koordynaty col, row drugiej komurki
			succeed (int): ilość wcześniejszych połączeń

		Returns:
			bool: True, jeżeli łączenie się powiodło, inaczej False
		"""
		cell_1: int = self.map[cell_1_coords[0]][cell_1_coords[1]]
		cell_2: int = self.map[cell_2_coords[0]][cell_2_coords[1]]

		if cell_1 - succeed != cell_2:
			return False
		
		self.map[cell_2_coords[0]][cell_2_coords[1]] = 0
		self.map[cell_1_coords[0]][cell_1_coords[1]] += 1

		return True
	
	def check_possible_merges(self: Self, column_i: int, row_i: int) -> tuple[bool, bool, bool, bool]:
		"""sprawdza, czy komurka jest na bokach, jeżeli tak, to ustawia zwracaną wartość na False

		Args:
			column_i (_type_): numer kolumny komurki
			row_i (_type_): numer żędu komurki

		Returns:
			tuple[bool, bool, bool, bool]
		[0]: row_i + 1,
		[1]: row_i - 1,
		[2]: column_i + 1,
		[3]: column_i - 1,
		"""

		ret: list[bool] = [True, True, True, True]

		if row_i == len(self.map[0]) - 1:
			ret[0] = False
		
		if row_i == 0:
			ret[1] = False
		
		if column_i == len(self.map) - 1:
			ret[2] = False
		
		if column_i == 0:
			ret[3] = False
		
		return tuple(ret)

	def new_next_numbers(self: Self) -> None:
		"""generuje next_numbers"""
		self.next_numbers = random.randint(*self.number_range), random.randint(*self.number_range)
	
	def check_empty_column(self: Self, column: int) -> int:
		"""przyjmuje mapę oraz kolumnę, i zwraca najniższe puste pole

		Args:
			column (int): kolumna do sprawdzenia

		Returns:
			int: najniższa pusta kolumna
		"""
		map_col: list[int] = [row[column] for row in self.map]
		
		empty: int = len(map_col)
		
		for i, num in enumerate(map_col):
			if num != 0:
				empty = i + 1
		
		return empty
	
	def convert_map(self: Self, map: list[list[int]]) -> list[list[int]]:
		"""przyjmuje mapę, zwraca mape z zamienionymi kolumnami i żądami

		Args:
			map (list[list[int]]): mapa do zamiany

		Returns:
			list[list[int]]: zamieniona mapa
		"""
		return [list(row) for row in zip(*map)]
	
	def fall_map(self: Self) -> None:
		"""generuje mapę po spadnięciu"""
		map_columns: list[list[int]] = self.convert_map(self.map)
		
		column_length: int = len(map_columns[0])

		fallen_map_collumns: list[list[int]] = []

		for column in map_columns:
			fallen_column: list[int] = [x for x in column if x != 0] # usuwa wszystkie elementy 0
			fallen_column.extend([0] * (column_length - len(fallen_column))) # wydłuża listę do pierwotnej długości, z domyślną wartością 0

			fallen_map_collumns.append(fallen_column)
		
		self.map = self.convert_map(fallen_map_collumns)

	def get_possible_moves(self: Self) -> list[bool]:
		"""Zwraca listę booli, reprezentujących możliwość wykonania ruchu w kolumnach.

		Returns:
			list[bool]: Lista o długości liczby kolumn w self.map. True jeśli ruch jest możliwy (ostatni element w kolumnie == 0), inaczej False.
		"""
		last_row = self.map[-1]  # Pobranie ostatniego wiersza planszy
		possible_moves = [cell == 0 for cell in last_row]  # Sprawdzenie, które kolumny są wolne
		return possible_moves
	
	def merge(self: Self) -> None:
		"""łączy komurki mapy z sąsiadami"""

		for _ in [False]:

			column_i = self.last_drop[0]
			row_i = self.last_drop[1]

			if self.map[column_i][row_i] == 0:
				continue

			avalible_merges: tuple[bool, bool, bool, bool] = self.check_possible_merges(column_i, row_i)
			succeed: int = 0

			if avalible_merges[0]:
				succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i + 1), succeed)
			
			if avalible_merges[1]:
				succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i - 1), succeed)

			if avalible_merges[2]:
				succeed += self.merge_two_cells((column_i, row_i), (column_i + 1, row_i), succeed)
			
			if avalible_merges[3]:
				self.merge_two_cells((column_i, row_i), (column_i - 1, row_i), succeed)


		for column_i, column in enumerate(self.map):
			for row_i, cell in enumerate(column):

				if cell == 0:
					continue

				avalible_merges: tuple[bool, bool, bool, bool] = self.check_possible_merges(column_i, row_i)
				succeed: int = 0

				if avalible_merges[0]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i + 1), succeed)
				
				if avalible_merges[1]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i - 1), succeed)

				if avalible_merges[2]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i + 1, row_i), succeed)
				
				if avalible_merges[3]:
					self.merge_two_cells((column_i, row_i), (column_i - 1, row_i), succeed)

	def move(self: Self, move: int):
		...


if __name__ == '__main__':

	def show_map(game: Game):
		print()
		for row in reversed(game.map):
			print((row))
	
	def set_map(game: Game, new_map: list[list[int]]):
		for row_i, row in enumerate(reversed(new_map)):  # Usuń reversed
			for col_i, col in enumerate(row):
				game.map[row_i][col_i] += col  # Indeksy w game.map to row_i, col_i


	t = Game()

	new_map: list[list[int]] = [[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 2, 0, 2],
								[0, 0, 1, 2, 1]]
	
	set_map(t, new_map)

	show_map(t)

	t.fall_map()

	show_map(t)

	new_map: list[list[int]] = [[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 2, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0]]
	t.last_drop = [1, 3]
	set_map(t, new_map)
	
	show_map(t)

	t.fall_map()

	show_map(t)

	t.merge()

	show_map(t)