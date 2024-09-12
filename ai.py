import gra
import random
import threading


gen = 0
max = 0
max_gra = []

def t(running):
	global gen
	global max
	global max_gra
	s = gra.gra()
	while not running.is_set():
		if s.lose:
			gen += 1
			print(s.points, gen, max)
			if s.points > max:
				max = s.points
				max_gra = s.history
			s = gra.gra()
		s.ruch(random.randint(0, 4))

threads = []
running = threading.Event()
for i in range(0, 1):
	threads.append(threading.Thread(target=t, args=(running,)))

for thread in threads:
	thread.start()
	
input('zakończyć? ')
running.set()
for thread in threads:
	thread.join()
print(f'gen:{gen}, max_points:{max}, best_game:\n')
for i in max_gra:
	for j in i:
		print(j)

