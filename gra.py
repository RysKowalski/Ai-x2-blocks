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
        
	def ruch(self, move):
	
		def spadanie(lista, data):
            
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
			
			return lista, data
		
		def lacz(map, data):
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
				return map, data
				
			
		map_ = [[999] * 5 for _ in range(8)]
		liczba = self.liczba[0]
		self.liczba[0] = self.liczba[1]
		self.liczba[1] = random.randint(1 + self.state, 6 + self.state)
		map = self.map
		map[7][move] = liczba
		
		t = 0
		while True:
			maps = map.copy()
			map, map_ = spadanie(map, map_)
			map, map_ = lacz(map, map_)
			map, map_ = spadanie(map, map_)
			if map != lacz(map, map_) and map != spadanie(map, map_):
				t += 1
				if t == 3:
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
		ret.append(points)
		
		return [ret, lose, points]
	
	def human(self):
		import os
		map = self.map
		liczba = self.liczba
		lose = self.lose
		points = self.points
		
		while not lose:
			map = self.map
			liczba = self.liczba
			lose = self.lose
			points = self.points
			
			os.system('clear')
			print(f'liczba punktów: {points}\n')

			wmap = map.copy()
			del wmap[7]
			
			mapmax = []
			newmap = []
			
			for i, col in enumerate(wmap):
				for j, num in enumerate(wmap[i]):
					mapmax.append(2 ** num)
			maxlen = len(str(max(mapmax)))

			
			for i, col in enumerate(wmap):
				for j, num in enumerate(wmap[i]):
					spaces = maxlen - len(str(num))
					space = [0, 0]
					
					s = True
					for k in range(0, spaces):
						if s:
							space[0] += 1
						else:
							space[1] += 1
						s = not s
					
					wmap[i][j] = f"{' ' * space[0]}{2 ** num}{' ' * space[1]}"
			
			for i in wmap:
				print(i)




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





t = gra()
t.human()