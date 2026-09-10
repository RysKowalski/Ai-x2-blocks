import gymnasium as gym
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

from GameEnvironment import GameEnv

print("\nloading modules finished\n")

env: GameEnv = GameEnv()

state_size = int(env.observation_space.shape[0])
action_size = int(env.action_space.n)

print("State Size:", state_size)
print("Action Size:", action_size)
