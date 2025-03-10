import neat
import pickle
import multiprocessing
from typing import List, Tuple

from game import Game

def filtruj_i_znajdz_index(lista1: List[float], lista2: List[bool]) -> int:
    """Zwraca indeks największej wartości z lista1, dla której odpowiadający element w lista2 jest True."""
    return max((i for i, (val, flag) in enumerate(zip(lista1, lista2)) if flag), key=lambda x: lista1[x])

def evaluate_genome(genome_data: Tuple[int, neat.DefaultGenome, neat.Config]) -> Tuple[int, float]:
    """
    Ocena pojedynczego genomu.
    
    Tworzy sieć na podstawie genomu, uruchamia symulację gry oraz oblicza fitness.
    """
    genome_id, genome, config = genome_data
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game: Game = Game()
    # Reset fitness, jeżeli nie jest zerowany w konstruktorze gry
    genome.fitness = 0.0

    # Pętla symulacji gry
    while game.game_running():
        state = game.get_data_ai()  # pobranie stanu gry
        output: List[float] = net.activate(state)  # aktywacja sieci
        action: int = filtruj_i_znajdz_index(output, game.get_possible_moves())
        game.move(action)  # wykonanie ruchu w grze
        genome.fitness = game.points  # aktualizacja fitness na podstawie punktów z gry

    return genome_id, genome.fitness

def eval_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> None:
    """
    Równoległa ocena genomów przy użyciu multiprocessing.
    
    Każdy genom jest oceniany w osobnym procesie. Wynik (genome_id, fitness)
    jest zwracany, a następnie przypisywany do odpowiedniego genomu.
    """
    # Przygotowanie danych do przetwarzania: każdy element to (genome_id, genome, config)
    data = [(genome_id, genome, config) for genome_id, genome in genomes]
    
    with multiprocessing.Pool() as pool:
        results = pool.starmap(evaluate_genome, data)
    
    # Utworzenie mapy genome_id -> genome w celu łatwej aktualizacji fitness
    genome_map = {genome_id: genome for genome_id, genome in genomes}
    for genome_id, fitness in results:
        genome_map[genome_id].fitness = fitness

def run_neat(config_file: str) -> None:
    """
    Inicjalizuje konfigurację NEAT, tworzy populację, uruchamia ewolucję oraz zapisuje najlepszy genom.
    """
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    
    best_genome = pop.run(eval_genomes, 500)  # ewolucja przez 500 pokoleń
    
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best_genome, f)

if __name__ == "__main__":
    run_neat("config")

