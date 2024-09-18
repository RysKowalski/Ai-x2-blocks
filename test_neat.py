import neat
import os
import pickle
from gra import gra

# Funkcja fitness dla NEAT

max_map = None
max_points = 0
def eval_genomes(genomes, config):
    global max_map
    global max_points
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = gra()  # Tworzymy nową instancję gry dla każdego organizmu
        fitness = 0
        
        # Dopóki gra nie jest przegrana, sieć podejmuje decyzje
        while not game.lose:
            game_state = game.get_raw()  # Pobieramy stan gry w formacie raw
            
            # Sieć podejmuje decyzję na podstawie stanu gry
            output = net.activate(game_state)

            moves = {}
            for i in range(len(game.moves)):
                if game.moves[i]:
                    moves[output[i]] = i

            game.ruch(moves[max(moves.keys())])

            # Fitness opieramy na liczbie punktów w grze
            fitness = game.get_reward()
        
        genome.fitness = fitness  # Przypisujemy wynik fitness do genomu
        if fitness > max_points:
            max_map = game.history

# Funkcja do zapisywania stanu populacji
def save_population(population, filename):
    with open(filename, "wb") as f:
        pickle.dump(population, f)

# Funkcja do ładowania stanu populacji
def load_population(config, filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

# Funkcja czyszcząca reporterów przed ich ponownym dodaniem
def reset_reporters(population):
    population.reporters.reporters.clear()

# Funkcja konfigurująca i uruchamiająca NEAT
def run_neat(config_file):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file  
    )

    # Pytanie o załadowanie sieci
    load_network = input("Czy załadować istniejącą populację? (tak/nie): ")
    if load_network.lower() == "tak":
        try:
            filename = input("Podaj nazwę pliku z populacją: ")
            population = load_population(config, filename)
            print(f"Populacja załadowana z pliku {filename}.")
        except FileNotFoundError:
            print("Plik z populacją nie istnieje. Tworzona nowa populacja.")
            population = neat.Population(config)
    else:
        population = neat.Population(config)

    # Reset reporterów przed ich ponownym dodaniem
    reset_reporters(population)

    # Dodanie reporterów tylko raz
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Trening NEAT
    winner = population.run(eval_genomes, 20)

    # Wyświetlanie najlepszego wyniku
    for i in max_map:
        for j in i:
            print(j)

    # Zapisywanie populacji z możliwością wyboru nazwy
    save_network = input("Czy zapisać wytrenowaną populację? (tak/nie): ")
    if save_network.lower() == "tak":
        filename = input("Podaj nazwę pliku do zapisu: ")
        save_population(population, filename)
        print(f"Populacja zapisana do pliku {filename}.")

if __name__ == "__main__":
    # Poprawa obsługi ścieżki do pliku konfiguracji
    config_path = os.path.join(os.path.dirname(__file__), "neat-config.txt")
    if not os.path.exists(config_path):
        print(f"Plik konfiguracji {config_path} nie istnieje.")
        exit()

    run_neat(config_path)
