import neat
import pickle
import requests
import os
import math
from typing import Any, List, Tuple, Dict
from concurrent.futures import ProcessPoolExecutor

from game import Game

def filtruj_i_znajdz_index(lista1: List[float], lista2: List[int]) -> int:
    """
    Filtruje listę `lista1`, znajdując indeks największej wartości,
    dla której odpowiadający element w `lista2` jest True.
    """
    return max((i for i, (val, flag) in enumerate(zip(lista1, lista2)) if flag),
               key=lambda x: lista1[x])

number: int = 0
def visualize(points: float) -> None:
    """
    Funkcja wizualizująca wynik – przyjmuje liczbę punktów najlepszego genomu.
    """
    global number
    number += 1
    requests.post('http://localhost:8000/points', json={'points': [number, points]})

def eval_single_genome(genome_data: Tuple[int, neat.DefaultGenome], config: neat.Config) -> Tuple[int, float]:
    """
    Ocena pojedynczego genomu.
    Tworzy sieć, uruchamia grę, wykonuje symulację i zwraca krotkę (id, fitness).
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

    return (genome_id, fitness)

def eval_genome_chunk(genome_chunk: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> List[Tuple[int, float]]:
    """
    Ocena wszystkich genomów z jednego chunka.
    """
    results: List[Tuple[int, float]] = []
    for genome_data in genome_chunk:
        result = eval_single_genome(genome_data, config)
        results.append(result)
    return results

def chunk_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], num_chunks: int) -> List[List[Tuple[int, neat.DefaultGenome]]]:
    """
    Dzieli listę genomów na `num_chunks` części.
    """
    chunk_size: int = math.ceil(len(genomes) / num_chunks)
    return [genomes[i:i + chunk_size] for i in range(0, len(genomes), chunk_size)]

def process_chunk_wrapper(args: Tuple[List[Tuple[int, neat.DefaultGenome]], neat.Config]) -> List[Tuple[int, float]]:
    """
    Funkcja pomocnicza przetwarzająca chunk genomów.
    Używana jest jako funkcja globalna do mapowania w ProcessPoolExecutor.
    """
    genome_chunk, config = args
    return eval_genome_chunk(genome_chunk, config)

def eval_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> None:
    """
    Ocena genomów przy użyciu wieloprocesowości.
    Populacja jest dzielona na chunki według liczby dostępnych rdzeni,
    a każdy proces ocenia swój chunk, omijając ograniczenie GIL.
    Po zebraniu wyników aktualizujemy wartość fitness dla każdego genomu.
    """
    num_cores: int = os.cpu_count() or 1  # liczba dostępnych rdzeni
    num_workers: int = min(num_cores, len(genomes))
    
    # Podziel genomy na chunki – np. dla 800 genomów i 8 rdzeni każdy chunk to ok. 100 genomów.
    genome_chunks: List[List[Tuple[int, neat.DefaultGenome]]] = chunk_genomes(genomes, num_workers)
    
    fitness_results: List[Tuple[int, float]] = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Tworzymy listę argumentów jako krotki (chunk, config)
        chunk_args: List[Tuple[List[Tuple[int, neat.DefaultGenome]], neat.Config]] = [(chunk, config) for chunk in genome_chunks]
        # Używamy funkcji globalnej process_chunk_wrapper zamiast lambdy
        chunk_results = list(executor.map(process_chunk_wrapper, chunk_args))
    
    # Spłaszcz listę wyników
    for sublist in chunk_results:
        fitness_results.extend(sublist)
    
    # Aktualizujemy oryginalne obiekty genomów na podstawie wyników oceny
    genome_dict: Dict[int, neat.DefaultGenome] = {genome_id: genome for genome_id, genome in genomes}
    for genome_id, fitness in fitness_results:
        genome_dict[genome_id].fitness = fitness

    best_fitness: float = max((fitness for _, fitness in fitness_results), default=float('-inf'))
    visualize(best_fitness)

def run_neat(config_file: str) -> None:
    """
    Inicjalizuje konfigurację NEAT, tworzy populację,
    uruchamia ewolucję z wieloprocesową oceną oraz zapisuje najlepszy genom.
    """
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    best_genome = pop.run(eval_genomes, 1500)

    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best_genome, f)

if __name__ == "__main__":
    run_neat("config")
