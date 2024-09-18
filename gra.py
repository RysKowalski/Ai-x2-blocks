import random

class gra:
	def __init__(self):
		map = [[0] * 5 for _ in range(8)]
		self.map = map
		
		liczba = [random.randint(1, 6), random.randint(1, 6)]
		self.liczba = liczba
		self.state = 0
		self.lose = False
		self.maxi = 10
		self.points = 0
		self.history = []
		self.last_move = None
		self.moves = [True] * 5
		self.max_number = 0

	def ruch(self, move):
	
		if self.map[6][move] != 0:
			self.sprawdz()
			return None

		def spadanie(lista, data, changes = True):
			
			def fall(list):
				for col, coli in enumerate(list):
					for row, num in enumerate(list[col]):
						if num != 0:
							for i in range(col - 1, -1, -1):  
								if list[i][row] == 0:
									list[i][row] = num
									data[i][row] = 0
									data[col][row] = 999
									list[col][row] = 0
									break
				return list
			
			def fallen(list):
				for col, coli in enumerate(list):
					for row, num in enumerate(list[col]):
						if num != 0:
							for i in range(col - 1, -1, -1):  
								if list[i][row] == 0:
									return True
				return False
			
			for col, coli in enumerate(data):
				for row, num in enumerate(data[col]):
					data[col][row] += 1
			
			while fallen(lista):
				map = fall(lista)
			
			if changes:
				return lista, data
			else:
				return lista
		
		def lacz(map, data, changes = True):
			points = self.points
			pos = []
			pos_ = {}
			for col, coli in enumerate(data):
				for row, num in enumerate(data[col]):
					num *= 10
					while num in pos_:
						num += 1
					pos_[num] = [col, row]
			_pos = sorted(pos_.keys())
			for i in _pos:
				pos.append(pos_[i])
			
			for i, poz in enumerate(pos):
				col = poz[0]
				row = poz[1]
				special = [False, False, False]
				if row == 0:
					special[0] = True
				if col == 0:
					special[1] = True
				if row == 4:
					special[2] = True
				
				if map[col][row] != 0:
					inc = 0
					if not special[0]:
						if map[col][row] == map[col][row - 1]:
							map[col][row - 1] = 0
							inc += 1
							data[col][row] = 0
							data[col][row - 1] = 999
					if not special[1]:
						if map[col][row] == map[col - 1][row]:
							map[col - 1][row] = 0
							inc += 1
							data[col][row] = 0
							data[col][row] = 999
					if not special[2]:
						if map[col][row] == map[col][row + 1]:
							map[col][row + 1] = 0
							inc += 1
							data[col][row] = 0
							data[col][row + 1] = 999
					map[col][row] += inc
					points += 2 ** map[col][row] * inc
				self.points = points
				if changes:
					return map, data
				else:
					return map
				
			
		map_ = [[999] * 5 for _ in range(8)]
		liczba = self.liczba[0]
		self.liczba[0] = self.liczba[1]
		self.liczba[1] = random.randint(1 + self.state, 6 + self.state)
		map = self.map
		map[7][move] = liczba
		
		t = 0
		while True:
			map, map_ = spadanie(map, map_)
			map, map_ = lacz(map, map_)
			map, map_ = spadanie(map, map_)
			map, map_ = lacz(map, map_)
			if str(map) == str(lacz(map, map_, False)) and str(map) == str(spadanie(map, map_, False)):
					break
		self.sprawdz()
		self.map = map
		self.history.append(self.get_ui())
		self.last_move = move

	def sprawdz(self):
		map = self.map
		maxi = self.maxi
		lose = self.lose
		state = self.state
		moves = [True] * 5  # Zakładamy, że wszystkie kolumny są początkowo dostępne
		max_number = self.max_number


		# Sprawdzenie, czy kolumny są pełne i zablokowanie ruchów w pełnych kolumnach
		for i in range(5):
			if map[6][i] != 0:  # Jeśli na pozycji (6, i) w kolumnie jest liczba, to kolumna jest pełna
				moves[i] = False

		lose_ = True
		for i in moves:
			if i:
				lose_ = False
		lose = lose_
		
		# Aktualizacja maksymalnej liczby na planszy i stanu gry
		max_number = max(max(row) for row in map)
		if max_number >= maxi:
			maxi = max_number
			state += 1
		
		# Aktualizacja zmiennych klasy
		self.maxi = maxi
		self.lose = lose
		self.state = state
		self.moves = moves  # Aktualizacja dostępnych ruchów
		self.max_number = max_number
	
	def get(self):
		map = self.map
		liczba = self.liczba
		state = self.state
		lose = self.lose
		points = self.points
		
		ret = {'map':map, 'next_num':liczba, 'max':state, 'lose':lose, 'points':points}
		return ret
	
	def get_raw(self):
		map = self.map
		liczba = self.liczba
		lose = self.lose
		points = self.points
		
		ret = []
		for col, coli in enumerate(map):
			for raw, num in enumerate(map[col]):
				if num == 0:
					ret.append(num)
				else:
					ret.append(num - self.state)
		for i in liczba:
			ret.append(i)
		
		return ret
	
	def human(self):
		import os
		map = self.map
		liczba = self.liczba
		points = self.points
		
		while not self.lose:
			map = self.map
			liczba = self.liczba
			points = self.points
			

			os.system('cls')


			print(f'liczba punktów: {points}\n')

			wmap = map.copy()
			
			mapmax = []
			newmap = [[''] * 5 for _ in range(7)]
			
			for i, col in enumerate(wmap):
				for j, num in enumerate(wmap[i]):
					mapmax.append(2 ** num)
			maxlen = len(str(max(mapmax)))

			
			for i, col in enumerate(wmap):
				for j, num in enumerate(wmap[i]):
					if i == 7:
						break
					spaces = maxlen - len(str(2 ** num))
					if num != 0:
						space = [0, 0]
					
						s = True
						for k in range(0, spaces):
							if s:
								space[0] += 1
							else:
								space[1] += 1
							s = not s
					
						newmap[i][j] = f"{' ' * space[0]}{2 ** num}{' ' * space[1]}"
					else:
						newmap[i][j] = ' ' * maxlen
			
			for i in range(0, len(newmap)):
				print('_' * (len('|'.join(newmap[i])) + 2))
				print(f"|{'|'.join(newmap[i])}|")
			print('_' * (len('|'.join(newmap[i])) + 2))
	
			




			print(f'\nobecna liczba: {2 ** liczba[0]}\nnastępna liczba: {2 ** liczba[1]}\n')
			
			ruh = input('podaj liczbę od 1 do 5: ')
			while True:
				try:
					int(ruh)
					if int(ruh) >= 6 or int(ruh) <= 0:
						raise
					else:
						break
				except:
					ruh = input('nie udało się wykonać ruchu, musisz podać liczbę od 1 do 5: ')
			self.ruch(int(ruh) - 1)
			
			
	def get_ui(self):
		ui = []
		
		map = self.map
		liczba = self.liczba
		points = self.points
		last_move = self.last_move
		
		ui.append(f'liczba punktów: {points}\n')

		wmap = map.copy()
			
		mapmax = []
		newmap = [[''] * 5 for _ in range(7)]
			
		for i, col in enumerate(wmap):
			for j, num in enumerate(wmap[i]):
				mapmax.append(2 ** num)
		maxlen = len(str(max(mapmax)))

			
		for i, col in enumerate(wmap):
			for j, num in enumerate(wmap[i]):
				if i == 7:
					break
				spaces = maxlen - len(str(2 ** num))
				if num != 0:
					space = [0, 0]
					
					s = True
					for k in range(0, spaces):
						if s:
							space[0] += 1
						else:
							space[1] += 1
						s = not s
					
					newmap[i][j] = f"{' ' * space[0]}{2 ** num}{' ' * space[1]}"
				else:
					newmap[i][j] = ' ' * maxlen
			
		for i in range(0, len(newmap)):
			ui.append('_' * (len('|'.join(newmap[i])) + 2))
			ui.append(f"|{'|'.join(newmap[i])}|")
		ui.append('_' * (len('|'.join(newmap[i])) + 2))
	
		ui.append(f'\nobecna liczba: {2 ** liczba[0]}\nnastępna liczba: {2 ** liczba[1]}\n')
		ui.append(f'ostatni_ruch:{last_move}\n\n\n')
		return ui


	def get_reward(self):
		# Bazowe zmienne
		map = self.map
		points = self.points
		max_number = self.max_number
		
		# Nagroda za maksymalną liczbę na planszy
		reward = 0
		reward += max_number * 100  # Wzmocniona nagroda za większe liczby

		# Kara za sytuacje, gdy mniejsza liczba jest pod większą
		penalty = 0
		for col in range(len(map[0])):  # Przechodzimy przez każdą kolumnę
			for row in range(1, len(map)):  # Sprawdzamy od drugiego rzędu w dół
				if map[row][col] > 0 and map[row - 1][col] > 0:  # Tylko, jeśli obie liczby są różne od 0
					if map[row][col] < map[row - 1][col]:  # Mniejsza liczba pod większą
						penalty += (map[row - 1][col] - map[row][col]) * 10  # Kara zależna od różnicy liczb
		
		# Nagroda lub kara zależna od liczby punktów (zwiększamy jej znaczenie)
		reward += points * 10  # Zwiększamy wpływ liczby punktów na końcową nagrodę
		
		# Kara za przegraną
		if self.lose:
			reward -= 1000  # Duża kara za przegraną, by unikać kończenia gry
		
		# Ostateczny wynik
		final_reward = reward - penalty
		return final_reward
