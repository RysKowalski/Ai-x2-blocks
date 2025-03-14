import neat
import pickle
import requests
import os
import math
from typing import Any, List, Tuple, Dict, Optional
from concurrent.futures import ProcessPoolExecutor

from game import Game

def save_population(pop: neat.Population, best_genome: neat.DefaultGenome, filename: str = "population.pkl") -> None:
	"""
	Zapisuje całą populację NEAT oraz najlepszy genom do pliku.
	
	Przed zapisaniem usuwa reporterów, aby uniknąć problemów z serializacją.
	
	:param pop: Obiekt populacji NEAT.
	:param best_genome: Najlepszy genom uzyskany w trakcie ewolucji.
	:param filename: Nazwa pliku, do którego zapisywane są dane.
	"""
	global number
	data = {"population": pop, "best_genome": best_genome, 'gen': number}
	with open(filename, "wb") as f:
		pickle.dump(data, f)

def load_population(new: bool = False, config_file: str = "config-feedforward", filename: str = "population.pkl") -> Tuple[neat.Population, Optional[neat.DefaultGenome], neat.Config]:
	"""
	Ładuje populację NEAT oraz najlepszy genom z pliku, lub tworzy nową populację jeśli new jest True.
	
	:param new: Jeśli True, tworzy nową populację; jeśli False, ładuje populację z pliku.
	:param config_file: Ścieżka do pliku konfiguracyjnego NEAT.
	:param filename: Nazwa pliku, z którego wczytywane są dane.
	:return: Krotka zawierająca populację, najlepszy genom (lub None przy nowej populacji) oraz konfigurację.
	"""
	global number
	if new:
		config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
							 neat.DefaultSpeciesSet, neat.DefaultStagnation,
							 config_file)
		pop = neat.Population(config)
		pop.add_reporter(neat.StdOutReporter(True))
		stats = neat.StatisticsReporter()
		pop.add_reporter(stats)
		best_genome = None
	else:
		with open(filename, "rb") as f:
			data = pickle.load(f)
		pop = data["population"]
		best_genome = data["best_genome"]
		number = data['gen']
		config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
							 neat.DefaultSpeciesSet, neat.DefaultStagnation,
							 config_file)
		# pop.add_reporter(neat.StdOutReporter(True))
		# stats = neat.StatisticsReporter()
		# pop.add_reporter(stats)
	return pop, best_genome, config

def filtruj_i_znajdz_index(lista1: List[float], lista2: List[int]) -> int:
	"""
	Filtruje listę `lista1`, znajdując indeks największej wartości,
	dla której odpowiadający element w `lista2` jest True.
	"""
	return max((i for i, (val, flag) in enumerate(zip(lista1, lista2)) if flag),
			   key=lambda x: lista1[x])

number: int = 0
def visualize(points: float, game_over: bool) -> None:
	"""
	Funkcja wizualizująca wynik - przyjmuje liczbę punktów najlepszego genomu
	oraz stan gry (game_over) z najlepszego genomu.
	
	:param points: Liczba punktów najlepszego genomu.
	:param game_over: Wartość game.game_over z najlepszego genomu.
	"""
	global number
	number += 1
	try:
		requests.post('http://localhost:8000/points', json={'points': [number, points], 'limit': game_over})
	except:
		pass

def eval_single_genome(genome_data: Tuple[int, neat.DefaultGenome], config: neat.Config) -> Tuple[int, float, bool]:
	"""
	Ocena pojedynczego genomu.
	Tworzy sieć, uruchamia grę, wykonuje symulację i zwraca krotkę (id, fitness, game_over).
	
	:param genome_data: Krotka zawierająca identyfikator genomu oraz sam genom.
	:param config: Konfiguracja NEAT.
	:return: Krotka zawierająca id genomu, wartość fitness oraz stan gry (game_over).
	"""
	genome_id, genome = genome_data
	net = neat.nn.FeedForwardNetwork.create(genome, config)
	game: Game = Game()
	fitness: float = 0.0

	while game.game_running():
		state = game.get_data_ai()              # pobierz stan gry
		output: List[float] = net.activate(state) # oblicz wyjście sieci
		action = filtruj_i_znajdz_index(output, game.get_possible_moves())
		game.move(action)
		fitness = game.points
	
	fitness = game.points

	return (genome_id, fitness, game.game_over)

def eval_genome_chunk(genome_chunk: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> List[Tuple[int, float, bool]]:
	"""
	Ocena wszystkich genomów z jednego chunka.
	
	:param genome_chunk: Lista krotek zawierających id genomu oraz genom.
	:param config: Konfiguracja NEAT.
	:return: Lista krotek zawierających id genomu, wartość fitness oraz stan gry (game_over).
	"""
	results: List[Tuple[int, float, bool]] = []
	for genome_data in genome_chunk:
		result = eval_single_genome(genome_data, config)
		results.append(result)
	return results

def chunk_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], num_chunks: int) -> List[List[Tuple[int, neat.DefaultGenome]]]:
	"""
	Dzieli listę genomów na `num_chunks` części.
	
	:param genomes: Lista krotek zawierających id genomu oraz genom.
	:param num_chunks: Liczba części.
	:return: Lista list genomów podzielonych na chunki.
	"""
	chunk_size: int = math.ceil(len(genomes) / num_chunks)
	return [genomes[i:i + chunk_size] for i in range(0, len(genomes), chunk_size)]

def process_chunk_wrapper(args: Tuple[List[Tuple[int, neat.DefaultGenome]], neat.Config]) -> List[Tuple[int, float, bool]]:
	"""
	Funkcja pomocnicza przetwarzająca chunk genomów.
	Używana jest jako funkcja globalna do mapowania w ProcessPoolExecutor.
	
	:param args: Krotka zawierająca chunk genomów oraz konfigurację.
	:return: Lista krotek zawierających id genomu, wartość fitness oraz stan gry (game_over).
	"""
	genome_chunk, config = args
	return eval_genome_chunk(genome_chunk, config)

def eval_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> None:
	"""
	Ocena genomów przy użyciu wieloprocesowości.
	Populacja jest dzielona na chunki według liczby dostępnych rdzeni,
	a każdy proces ocenia swój chunk, omijając ograniczenie GIL.
	Po zebraniu wyników aktualizujemy wartość fitness dla każdego genomu,
	a następnie wizualizujemy wynik najlepszego genomu, przekazując jego stan gry (game_over).
	
	:param genomes: Lista krotek zawierających id genomu oraz genom.
	:param config: Konfiguracja NEAT.
	"""
	num_cores: int = os.cpu_count() or 1
	num_workers: int = min(num_cores, len(genomes))
	
	genome_chunks: List[List[Tuple[int, neat.DefaultGenome]]] = chunk_genomes(genomes, num_workers)
	
	fitness_results: List[Tuple[int, float, bool]] = []
	with ProcessPoolExecutor(max_workers=num_workers) as executor:
		chunk_args: List[Tuple[List[Tuple[int, neat.DefaultGenome]], neat.Config]] = [(chunk, config) for chunk in genome_chunks]
		chunk_results = list(executor.map(process_chunk_wrapper, chunk_args))
	
	for sublist in chunk_results:
		fitness_results.extend(sublist)
	
	genome_dict: Dict[int, neat.DefaultGenome] = {genome_id: genome for genome_id, genome in genomes}
	for genome_id, fitness, _ in fitness_results:
		genome_dict[genome_id].fitness = fitness

	best_tuple: Tuple[int, float, bool] = max(fitness_results, key=lambda x: x[1], default=(-1, float('-inf'), False))
	best_fitness: float = best_tuple[1]
	best_game_over: bool = best_tuple[2]
	visualize(best_fitness, best_game_over)


def run_neat(config_file: str, new: bool = False) -> None:
	"""
	Inicjalizuje konfigurację NEAT, tworzy lub ładuje populację,
	dodaje reportery do śledzenia postępu treningu, uruchamia ewolucję 
	oraz zapisuje populację wraz z najlepszym genomem.
	
	:param config_file: Ścieżka do pliku konfiguracyjnego NEAT.
	:param new: Jeśli True, tworzy nową populację; jeśli False, ładuje populację z pliku 'population.pkl'.
	"""
	pop, _, config = load_population(new=new, config_file=config_file)
	
	best_genome = pop.run(eval_genomes, 500)
	
	save_population(pop, best_genome, "population.pkl")

if __name__ == "__main__":
	run_neat("config-feedforward", False)
