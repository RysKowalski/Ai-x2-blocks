import pickle
import neat
import random

from game import Game

# Wczytanie modelu NEAT
with open("best_genome.pkl", "rb") as f:
    winner = pickle.load(f)

# Załadowanie konfiguracji NEAT (upewnij się, że masz plik konfiguracyjny)
config_path = "config"
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

# Utworzenie sieci neuronowej z wytrenowanego modelu
net = neat.nn.FeedForwardNetwork.create(winner, config)

# Inicjalizacja gry
game: Game = Game()

while game.game_running():
    # Pobranie danych wejściowych dla modelu
    inputs = game.get_data_ai()
    
    # Przekazanie danych do sieci neuronowej i pobranie wyjść
    outputs = net.activate(inputs)
    
    game.process_ai_input(outputs, True)

    # Możesz dodać wyświetlanie mapy lub wyników, jeśli chcesz obserwować postęp
    print(f"Score: {game.points}")
