import neat
import os
import pickle
import tkinter as tk
from tkinter import messagebox
import threading  # Dodajemy threading do obsługi wątków
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from gra import gra
import visualize

# Funkcja fitness dla NEAT
max_map = None
max_points = 0
history_all_games = {}  # Przechowywanie historii gier dla każdej generacji

def eval_genomes(genomes, config):
    global max_map, max_points, history_all_games
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        game = gra()  # Tworzymy nową instancję gry dla każdego organizmu
        fitness = 0
        history = []
        
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
        
        # Zapisujemy historię gry dla danego genomu
        history_all_games[genome_id] = game.history
        history_all_games[genome_id].append(['ruchy: ' + str(len(game.history))])
        history_all_games[genome_id].append(['fitness: ' + str(fitness)])

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

# Funkcja do uruchamiania NEAT
def run_neat(config_file, generations_callback):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file  
    )

    # Tworzenie nowej populacji
    population = neat.Population(config)
    
    # Reset reporterów przed ich ponownym dodaniem
    reset_reporters(population)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)


    for i in range(2000):
    # Trening z wywołaniem callbacku po każdej generacji
        winner = population.run(eval_genomes, 1)
        
        # Wywołanie callbacku po zakończeniu treningu
        generations_callback(stats)

# Tworzenie GUI
class NEATApp:
    def __init__(self, root, config_file):
        self.root = root
        self.root.title("NEAT GUI")

        # Tworzenie widżetów GUI
        self.label = tk.Label(root, text="Wybierz generację do wyświetlenia gry:")
        self.label.pack()

        self.generation_listbox = tk.Listbox(root)
        self.generation_listbox.pack()

        self.show_game_button = tk.Button(root, text="Pokaż grę", command=self.show_game)
        self.show_game_button.pack()

        self.figure, self.ax = plt.subplots()
        
        # Dodaj canvas
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.canvas.get_tk_widget().pack()

        # Dodaj toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, root)
        self.toolbar.update()
        self.toolbar.pack()

        # Konfiguracja NEAT
        self.config_file = config_file
        self.history = []

        # Przechowuje statystyki dla wykresu
        self.generations = []
        self.fitness_values = []

        # Flaga do zatrzymania treningu
        self.training_active = False

        # Uruchamianie NEAT w tle
        self.start_training()

    def start_training(self):
        self.training_active = True

        # Uruchomienie treningu w osobnym wątku
        training_thread = threading.Thread(target=self.run_neat)
        training_thread.start()

    def run_neat(self):
        def callback(stats):
            # Zbieranie statystyk do późniejszej aktualizacji GUI
            self.generations = list(range(len(stats.most_fit_genomes)))
            self.fitness_values = [g.fitness for g in stats.most_fit_genomes]

            # Aktualizowanie GUI po każdej generacji
            self.update_gui()

        # Uruchomienie NEAT z callbackiem
        run_neat(self.config_file, callback)

    def update_gui(self):
        # Aktualizacja wykresu
        self.ax.clear()
        self.ax.plot(self.generations, self.fitness_values)
        self.ax.set_title("Fitness w generacjach")
        self.ax.set_xlabel("Generacja")
        self.ax.set_ylabel("Fitness")
        self.ax.grid(True)
        self.canvas.draw()

        # Aktualizacja listy generacji w listboxie
        self.generation_listbox.delete(0, tk.END)
        for i in self.generations:
            self.generation_listbox.insert(tk.END, f"Generacja {i}")

    def show_game(self):
        try:
            # Pobieramy wybraną generację
            selected_index = self.generation_listbox.curselection()[0]
            generation_id = int(selected_index)

            # Pobieramy historię gier dla wybranej generacji
            history = history_all_games.get(generation_id)
            
            if history:
                for state in history:
                    for i in state:
                        print(i)
            else:
                messagebox.showinfo("Brak danych", f"Brak historii dla generacji {generation_id}")
        except IndexError:
            messagebox.showinfo("Błąd", "Wybierz generację z listy.")

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "neat-config.txt")
    if not os.path.exists(config_path):
        print(f"Plik konfiguracji {config_path} nie istnieje.")
        exit()

    root = tk.Tk()
    app = NEATApp(root, config_path)
    root.mainloop()
