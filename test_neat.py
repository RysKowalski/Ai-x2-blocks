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
            
            # Wybieramy indeks z największą wartością jako ruch
            move = output.index(max(output))
            
            # Wykonujemy ruch w grze
            game.ruch(move)
            
            # Fitness opieramy na liczbie punktów w grze
            fitness = game.get_revard()
        
        genome.fitness = fitness  # Przypisujemy wynik fitness do genomu
        if fitness > max_points:
            max_map = game.history

# Funkcja konfigurująca i uruchamiająca NEAT
def run_neat(config_file):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file  

    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)  


    # Pytanie o załadowanie sieci
    load_network = input("Czy załadować istniejącą sieć? (tak/nie): ")
    if load_network.lower() == "tak":
        try:
            filename = input("Podaj nazwę pliku: ")
            with open(filename, "rb") as f:
                winner = pickle.load(f)
            print("Sieć załadowana.")
            population.add_member(winner)
        except FileNotFoundError:
            print("Plik z siecią nie istnieje. Tworzona nowa populacja.")

    winner = population.run(eval_genomes, 150)

    for i in max_map:
        for j in i:
            print(j)

    # Zapisywanie sieci z możliwością wyboru nazwy
    save_network = input("Czy zapisać wytrenowaną sieć? (tak/nie): ")
    if save_network.lower() == "tak":
        filename = input("Podaj nazwę pliku do zapisu: ")
        with open(filename, "wb") as f:
            pickle.dump(winner, f)
        print(f"Sieć zapisana do pliku {filename}.")

if __name__ == "__main__":
    # Poprawa obsługi ścieżki do pliku konfiguracji
    config_path = os.path.join(os.path.dirname(__file__), "neat-config.txt")
    if not os.path.exists(config_path):
        print(f"Plik konfiguracji {config_path} nie istnieje.")
        exit()

    run_neat(config_path)