from gra_old import gra
from os import system



t = gra()

while not t.lose:
    system('cls')
    for i in t.get_ui():
        print(i)
    print(len(t.history))
    print(t.get_reward())
    t.ruch(int(input('liczba od 0 do 4: ')) - 1)