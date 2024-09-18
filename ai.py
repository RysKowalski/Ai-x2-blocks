from gra import gra
from random import randint


avalible_moves = [True, True, True, True, False]
output = [1, 4, 3, 2, 444]






moves = []

maks_value = -1
for i in range(len(avalible_moves)):
    if avalible_moves[i]:  # Jeśli wartość bool jest True
        if output[i] > maks_value:
            maks_value = output[i]
            maks_index = i


print(maks_index)