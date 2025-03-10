import neat
import pickle
import requests
from typing import Any, List, Tuple

from game import Game

def filtruj_i_znajdz_index(lista1: list[float], lista2: list[bool]) -> int:
    """
    Filtruje listę lista1, znajdując indeks największej wartości,
    dla której odpowiadający element w lista2 jest True.
    """
    return max((i for i, (val, flag) in enumerate(zip(lista1, lista2)) if flag),
               key=lambda x: lista1[x])

number = 0
def visualize(points: float) -> None:
    """
    Funkcja wizualizująca wynik – przyjmuje liczbę punktów najlepszego genomu.
    """
    global number
    number += 1
    requests.post('http://localhost:8000/points', json={'points': [number, points]})

def eval_genomes(genomes: List[Tuple[int, neat.DefaultGenome]], config: neat.Config) -> None:
    """
    Funkcja oceny genomów.
    Dla każdego genomu tworzy sieć, uruchamia grę i przypisuje fitness.
    Po ocenie wszystkich genomów wyłaniany jest najlepszy wynik,
    który jest przekazywany do funkcji wizualizującej.
    """
    best_fitness: float = float('-inf')
    for genome_id, genome in genomes:
        # Utwórz sieć dla danego genomu
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game: Game = Game()
        genome.fitness = 0.0

        # Pętla gry
        while game.game_running():
            state = game.get_data_ai()  # pobierz stan gry
            output: list[float] = net.activate(state)  # oblicz wyjście sieci

            # Mapowanie wyjścia sieci na akcję gry
            action = filtruj_i_znajdz_index(output, game.get_possible_moves())
            game.move(action)  # wykonaj akcję w grze

            reward = game.points
            genome.fitness = reward  # aktualizuj fitness genomu

        # Aktualizuj najlepszy wynik generacji
        if genome.fitness > best_fitness:
            best_fitness = genome.fitness

    # Po ocenie wszystkich genomów, wywołaj funkcję wizualizacji
    visualize(best_fitness)

def run_neat(config_file: str) -> None:
    """
    Funkcja inicjalizująca konfigurację NEAT, tworząca populację,
    uruchamiająca ewolucję oraz zapisująca najlepszy genom.
    """
    # Wczytanie konfiguracji
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Inicjalizacja populacji
    pop = neat.Population(config)

    # Dodanie reporterów dla podglądu postępu treningu
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    # Uruchomienie ewolucji przez określoną liczbę pokoleń (np. 500)
    best_genome = pop.run(eval_genomes, 500)

    # Zapisz najlepszy genom do pliku
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(best_genome, f)

if __name__ == "__main__":
    # Ścieżka do pliku konfiguracyjnego NEAT
    run_neat("config")

