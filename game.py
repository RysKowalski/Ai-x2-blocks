from typing import Self

import random
import itertools

class Game:
	def __init__(self: Self, state = None):
		"""inicjacja

		Args:
			state (_type_, optional): TODO. Defaults to None.
		"""
		self.points: int = 0
		self.map: list[list[int]] = [[0 for _ in range(7)] for _ in range(5)] # self.map[col][row]
		self.number_range: list[int] = [1, 6]
		self.moves: int = 0
		self.next_numbers: list[int] = [random.randint(*self.number_range), random.randint(*self.number_range)]
		self.last_drop: list[int] = [0, 0]
		self.last_move: int = 0
		self.level: int = 0

	def show_map(self: Self):
		print()
		for row in self.convert_map(self.map):
			print((row))
	
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
		
		return ret[0], ret[1], ret[2], ret[3]

	def new_next_numbers(self: Self) -> None:
		"""generuje next_numbers"""
		self.next_numbers.pop(0)
		self.next_numbers.append(random.randint(*self.number_range))
	
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
	
	def fall_map(self: Self) -> bool:
		"""generuje mapę po spadnięciu

		Returns:
			bool: czy wystpiła zmiana
		"""
		change: bool = False

		map_columns: list[list[int]] = self.map.copy()
		
		column_length: int = len(map_columns[0])

		fallen_map_collumns: list[list[int]] = []

		for column in map_columns:
			fallen_column: list[int] = [x for x in column if x != 0] # usuwa wszystkie elementy 0
			fallen_column.extend([0] * (column_length - len(fallen_column))) # wydłuża listę do pierwotnej długości, z domyślną wartością 0

			fallen_map_collumns.append(fallen_column)
		
		self.map = fallen_map_collumns.copy()

		if map_columns != fallen_map_collumns:
			change = True
		return change

	def update_points(self: Self, merges: int, number: int) -> None:
		"""przyjmuje ilość udanych połączeń, oraz liczbę po połączeniu

		Args:
			merges (int): ilość udanych połączeń
			number (int): liczba po połączeniu
		"""
		
		self.points += number * merges

	def get_possible_moves(self: Self) -> list[int]:
		"""Zwraca listę booli, reprezentujących możliwość wykonania ruchu w kolumnach.

		Returns:
			list[bool]: Lista o długości liczby kolumn w self.map. True jeśli ruch jest możliwy (ostatni element w kolumnie == 0), inaczej False.
		"""
		last_row = self.convert_map(self.map)[-1]  # Pobranie ostatniego wiersza planszy
		possible_moves = [int(cell == 0) for cell in last_row]  # Sprawdzenie, które kolumny są wolne
		return possible_moves
	
	def merge(self: Self) -> bool:
		"""łączy komurki mapy z sąsiadami

		Returns:
			bool: czy wystąpiła zmiana
		"""
		change: bool = False

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
			
			self.update_points(succeed, self.map[column_i][row_i])

			if succeed > 0:
				change = True


		for column_i, column in enumerate(self.map):
			for row_i, cell in enumerate(column):

				if cell == 0:
					continue

				avalible_merges = self.check_possible_merges(column_i, row_i)
				succeed = 0

				if avalible_merges[0]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i + 1), succeed)
				
				if avalible_merges[1]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i, row_i - 1), succeed)

				if avalible_merges[2]:
					succeed += self.merge_two_cells((column_i, row_i), (column_i + 1, row_i), succeed)
				
				if avalible_merges[3]:
					self.merge_two_cells((column_i, row_i), (column_i - 1, row_i), succeed)
				
				self.update_points(succeed, self.map[column_i][row_i])

				if succeed > 0:
					change = True
		
		return change

	def spawn_element(self: Self) -> None:
		"""spawnuje element na mapie w kolumnie move, oraz aktualizuje next_numbers

		Args:
			move (int): kolumna ruchu, zakres od 0 do 4
		"""
		self.map[self.last_move][len(self.map[0]) - 1] = self.next_numbers[0]
		self.new_next_numbers()

	def set_last_drop(self: Self, move: int) -> None:
		"""przyjmuje move, i ustawia self.last_drop na najniższą wolną pozycję w kolumnie move

		Args:
			move (int): ruch, jako kolumna
		"""
		row: int = len([x for x in self.map[move] if x != 0])
		self.last_drop = [move, row - 1]

	def merge_fall_loop(self: Self) -> None:
		"""pętla spadająca i łącząca mapę"""
		change: bool = True

		while change:
			self.set_last_drop(self.last_move)
			change = False
			if self.fall_map():
				change = True
			
			if self.merge():
				change = True

	def check_game_level(self: Self) -> None:
		"""Updates game level. If any cell in map is greater than 11, 
		self.level is increased by the difference, and each cell in map is reduced by that difference (min 0)."""

		flatten_map: list[int] = list(itertools.chain(*self.map))
		max_flatten_map: int = max(flatten_map)

		if max_flatten_map <= 11:
			return

		difference = max_flatten_map - 11

		for row_index, row in enumerate(self.map):
			for col_index, value in enumerate(row):
				self.map[row_index][col_index] = max(value - difference, 0)

		self.level += difference
		self.points += 100 * difference

	def move(self: Self, move: int):
		"""przyjmue ruh, jako int od 0 do 4, oznaczajce kolumny

		Args:
			move (int): kolumna ruchu, zakres od 0 do 4
		"""
		self.last_move = move
		self.spawn_element()
		self.merge_fall_loop()
		self.check_game_level()
		self.merge_fall_loop()

	def get_data_ai(self: Self) -> list[int]:
		"""zwraca listę z mapą oraz następnymi ruchami

		Returns:
			list[int]: 35 elementów int z mapą, 2 elementy int z następnymi ruchami
		"""
		data:list[int] = []
		
		data.extend(list(itertools.chain(*self.map)))
		data.extend(self.next_numbers)

		return data

	def reward(self: Self) -> float:
		"""zwraca nagrodę jako float

		Returns:
			float: nagroda
		"""
		return self.points

	def game_running(self: Self) -> bool:
		"""jeżeli żaden ruch nie jest dostępny, zwraca False

		Returns:
			bool: _description_
		"""
		return any(self.get_possible_moves())
	
	def process_ai_input(self: Self, input: list[float], human: bool) -> None:
		"""przyjmuje dane, które zwrócił model, jako lista wartości dla opcji

		Args:
			input (list[float]): input ai
		"""
		move = max((i for i, (val, flag) in enumerate(zip(input, self.get_possible_moves())) if flag), key=lambda x: input[x])
		self.move(move)
		if human:
			self.show_map()
			print(self.next_numbers)

if __name__ == '__main__':
	import os
	import requests

	def show_map(game: Game):
		print()
		for row in t.convert_map(game.map):
			print((row))
	
	def set_map(game: Game, new_map: list[list[int]]):
		for row_i, row in enumerate(reversed(new_map)):  # Usuń reversed
			for col_i, col in enumerate(row):
				game.map[row_i][col_i] += col  # Indeksy w game.map to row_i, col_i

	def update_ui(points: int, i: int):
		# requests.post('http://localhost:8000/points', json={'points': [i, points]})
		print(points, i)
		exit()

	t = Game()

	while True:
		print(t.reward())
		show_map(t)
		print(f'{t.next_numbers}')
		t.move(int(input(f'podaj liczbę {t.get_possible_moves()}: ')) - 1)
	# i: int = 0
	# while True:
	# 	game: Game = Game()

	# 	i += 1
	# 	j = 0
	# 	while game.game_running():
	# 		j += 1
	# 		game.move(random.randint(0, 4))
	# 		update_ui(game.points + i, j )
		

	new_map: list[list[int]] = [[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 2, 0],
								[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0]]
