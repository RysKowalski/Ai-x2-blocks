import neat
import os
import pickle
import yaml  # Dodajemy bibliotekę yaml do zapisu do pliku w formacie YAML
from gra import gra

from concurrent.futures import ThreadPoolExecutor

def eval_genome_threaded(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game = gra()
    fitness = 0
    while not game.lose:
        game_state = game.get_raw()
        output = net.activate(game_state)
        move = output.index(max(output))
        game.ruch(move)
        fitness = game.points
    genome.fitness = fitness

def eval_genomes(genomes, config):
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for genome_id, genome in genomes:
            futures.append(executor.submit(eval_genome_threaded, genome, config))
        for future in futures:
            future.result()


# Funkcja do zapisania przebiegu gry przez najlepszy model i zapisu wyniku get() do YAML
def simulate_and_save_best_game(winner, config):
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    game = gra()  # Nowa instancja gry dla zwycięskiego modelu
    game_outputs = []  # Lista do zapisywania wyników funkcji get()
    
    # Dopóki gra nie jest przegrana, sieć podejmuje decyzje
    while not game.lose:
        game_state = game.get_raw()  # Pobieramy stan gry w formacie raw
        output = net.activate(game_state)  # Sieć podejmuje decyzję
        move = output.index(max(output))  # Wybieramy ruch z największą wartością
        game.ruch(move)  # Wykonujemy ruch
        
        # Zapisujemy wynik funkcji get() po każdym ruchu
        game_outputs.append(str(game.get()))  # Zakładam, że game.get() zwraca stan gry, który chcemy zapisać
    
    # Zapisz przebieg gry do pliku YAML
    with open("game_outputs.yaml", "w") as f:
        yaml.dump(game_outputs, f)

# Funkcja konfigurująca i uruchamiająca NEAT
def run_neat(config_file):
    # Załaduj konfigurację
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file
    )
    
    # Tworzymy populację NEAT
    population = neat.Population(config)
    
    # Dodajemy raportowanie postępów
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    # Uruchamiamy NEAT przez 50 pokoleń
    winner = population.run(eval_genomes, 500)
    
    # Zapisz zwycięską sieć
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
    
    # Uruchom symulację zwycięskiego modelu i zapisz wyniki funkcji get() do pliku YAML
    simulate_and_save_best_game(winner, config)

# Wczytanie konfiguracji i uruchomienie NEAT
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.txt")  # Ścieżka do pliku konfiguracji NEAT
    run_neat(config_path)
