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
		self.last_points = 0

	def ruch(self, move):
	
		def spadanie(lista, data):
			# Optymalizacja algorytmu spadania - jedno przejście przez kolumny i wiersze
			for col in range(7, 0, -1):
				for row in range(5):
					if lista[col][row] == 0 and lista[col - 1][row] != 0:
						lista[col][row], lista[col - 1][row] = lista[col - 1][row], 0
						data[col][row] = 0
						data[col - 1][row] = 999
			return lista, data
		
		def lacz(map, data):
			points = self.points
			for col in range(7):
				for row in range(5):
					if map[col][row] != 0:
						# Optymalizacja sprawdzenia sąsiadów i scalanie
						for d_col, d_row in [(-1, 0), (0, -1), (0, 1)]:
							new_col, new_row = col + d_col, row + d_row
							if 0 <= new_col < 8 and 0 <= new_row < 5 and map[new_col][new_row] == map[col][row]:
								map[new_col][new_row] = 0
								map[col][row] += 1
								points += 2 ** map[col][row]
								break
			self.points = points
			return map, data
				
			
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

	def sprawdz(self):
		map = self.map
		maxi = self.maxi
		lose = self.lose
		state = self.state
		
		if any(num != 0 for num in map[7]):
			lose = True
		
		mmax = []
		for col, coli in enumerate(map):
			for row, num in enumerate(map[col]):
				mmax.append(num)
		if max(mmax) >= maxi:
			maxi = max(mmax)
			state += 1
		
		self.maxi = maxi
		self.lose = lose
		self.state = state
	
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
				ret.append(num)
		for i in liczba:
			ret.append(i)
		
		return ret
	
	def get_points(self, all=False):
		points = self.points
		last_points = self.last_points
		return points - last_points

	def human(self):
		import os
		map = self.map
		liczba = self.liczba
		points = self.points
		
		while not self.lose:
			map = self.map
			liczba = self.liczba
			points = self.points
			
			os.system('clear')
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