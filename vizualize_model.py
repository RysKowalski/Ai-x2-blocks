import pickle
import neat
import visualize

def load_model(filepath: str) -> dict:
    """Wczytuje model NEAT z pliku .pkl."""
    with open(filepath, 'rb') as file:
        data: dict = pickle.load(file)
    return data

def main(model_filename: str) -> None:
    """Wczytuje model NEAT i wizualizuje strukturę najlepszego genomu."""
    # Wczytaj model z pliku
    model_data: dict = load_model(model_filename)
    best_genome: neat.DefaultGenome = model_data["best_genome"]

    # Wczytaj konfigurację NEAT; upewnij się, że plik konfiguracyjny 'config-feedforward' jest poprawny
    config: neat.Config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        'config-feedforward'
    )

    # Użyj innej nazwy pliku dla wizualizacji, aby nie nadpisywać oryginalnego pliku modelu
    output_filename: str = "best_genome.gv"
    visualize.draw_net(
        config,
        best_genome,
        view=True,
        filename=output_filename,
        node_names=None,
        show_disabled=True,
        prune_unused=False,
    )

if __name__ == '__main__':
    model_filename: str = 'population.pkl'
    main(model_filename)
