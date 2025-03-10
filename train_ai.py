import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
import torch as th
import torch.nn as nn
import requests

from stable_baselines3 import DQN
from stable_baselines3.dqn.policies import DQNPolicy
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

from game import Game  # Twoja klasa gry

number: int = 0
async def render_ui(points: int):
    number += 1
    requests.post('http://localhost:8000/points', json={'points': [number, points]})

def show_map(game: Game):
    print()
    for row in game.convert_map(game.map):
        print(row)

# Niestandardowy ekstraktor cech – przetwarza tylko dane gry (pierwsze 37 elementów)
class GameDataExtractor(BaseFeaturesExtractor):
    def __init__(self, observation_space: spaces.Box, features_dim: int = 64):
        # observation_space ma kształt (42,), ale wykorzystamy tylko pierwsze 37 elementów
        super().__init__(observation_space, features_dim)
        self.extractor = nn.Sequential(
            nn.Linear(37, features_dim),
            nn.ReLU()
        )
    
    def forward(self, observations: th.Tensor) -> th.Tensor:
        # Pierwsze 37 elementów to dane gry
        game_data = observations[:, :37]
        return self.extractor(game_data)

# Niestandardowa polityka DQN z maskowaniem niedozwolonych ruchów.
# Obserwacja ma kształt (42,):
#   - Pierwsze 37 elementów to dane gry (przetwarzane przez ekstraktor),
#   - Ostatnie 5 elementów to maska (1.0 = dozwolony, 0.0 = niedozwolony)
class MaskedDQNPolicy(DQNPolicy):
    def forward(self, obs: th.Tensor, deterministic: bool = False):
        # Wyodrębniamy maskę z oryginalnej obserwacji (ostatnie 5 elementów)
        legal_moves = obs[:, 37:]
        # Przetwarzamy obserwację przez niestandardowy ekstraktor (wykorzystując tylko pierwsze 37 elementów)
        features = self.extract_features(obs)
        # Obliczamy Q-wartości na podstawie wyekstrahowanych cech
        q_values = self.q_net(features)  # kształt: (batch, 5)
        # Maskujemy niedozwolone ruchy: dla akcji, gdzie maska == 0, ustawiamy bardzo niską wartość
        masked_q_values = legal_moves * q_values + (1 - legal_moves) * (-1e8)
        if deterministic:
            actions = th.argmax(masked_q_values, dim=1)
        else:
            probs = nn.functional.softmax(masked_q_values, dim=1)
            actions = th.multinomial(probs, num_samples=1).squeeze(dim=1)
        return actions, None

    def _predict(self, observation: th.Tensor, deterministic: bool = True) -> th.Tensor:
        actions, _ = self.forward(observation, deterministic)
        return actions.cpu().numpy()

# Środowisko gry w Gymnasium.
# Obserwacja to konkatenacja danych gry (37 elementów) i maski ruchów (5 elementów), czyli łącznie 42 elementy.
class GameEnv(gym.Env):
    metadata = {"render.modes": ["human"]}
    
    def __init__(self, game_class):
        super(GameEnv, self).__init__()
        self.game_class: Game = game_class
        self.game: Game = None
        # Obserwacja: 37 elementów danych gry + 5 elementów maski = 42 elementy
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(40,), dtype=np.float32)
        # Przestrzeń akcji: 5 ruchów (indeksy 0-4)
        self.action_space = spaces.Discrete(5)
    
    def reset(self, seed=None, options=None):
        render_ui(self.game.points) if self.game else ...
        self.game = self.game_class()  # Inicjalizacja nowej gry
        game_data = np.array(self.game.get_data_ai(), dtype=np.float32)  # 37 elementów
        legal_moves = np.array(self.game.get_possible_moves(), dtype=np.float32)  # 5 elementów (0 lub 1)
        obs = np.concatenate([game_data, legal_moves])
        return obs, {}  # Gymnasium reset() zwraca (obs, info)
    
    def step(self, action):
        # Wykonujemy ruch – zakładamy, że metoda move() przyjmuje akcję jako int (0-4)
        self.game.move(action)
        reward = self.game.reward()
        terminated = not self.game.game_running()  # gra zakończona naturalnie
        truncated = False  # przyjmujemy, że nie nastąpiło przerywanie
        game_data = np.array(self.game.get_data_ai(), dtype=np.float32)
        legal_moves = np.array(self.game.get_possible_moves(), dtype=np.float32)
        obs = np.concatenate([game_data, legal_moves])
        return obs, reward, terminated, truncated, {}
    
    def render(self, mode="human", action=None):
        os.system('clear')
        print("Wybrany ruch:", action)
        print("Punkty:", self.game.points)
        show_map(self.game)
        print("Następne liczby:", self.game.next_numbers)

# Ustawienia dla polityki – przekazujemy nasz niestandardowy ekstraktor cech.
policy_kwargs = dict(
    features_extractor_class=GameDataExtractor,
    features_extractor_kwargs=dict(features_dim=64),
)

# Inicjalizacja środowiska (Gymnasium)
env = GameEnv(Game)

# Inicjalizacja modelu DQN z niestandardową polityką maskującą niedozwolone ruchy
model = DQN(MaskedDQNPolicy, env, verbose=1, policy_kwargs=policy_kwargs)

# Trenowanie modelu – przykładowo 10 000 kroków
model.learn(total_timesteps=10000)

# Zapis modelu
model.save("my_masked_dqn_model")

# Przykładowa rozgrywka z wytrenowanym modelem
obs, _ = env.reset()
done = False
while not done:
    # Model przewiduje akcję – dzięki maskowaniu wybierze tylko dozwolone ruchy
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    env.render(action=action)
    done = terminated or truncated

print("Gra zakończona, nagroda:", reward)

