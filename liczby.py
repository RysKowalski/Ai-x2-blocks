import numpy as np
from PIL import Image

def podziel_obraz(obrazek, wielkosc_czesci):
  """
  Dzieli obraz na części z przeskokiem i nakładaniem.

  Argumenty:
    obrazek_path: Ścieżka do pliku obrazu PNG.
    wielkosc_czesci: Rozmiar części (szerokość x wysokość).

  Zwracany wartość:
    Lista zawierająca wszystkie wycięte fragmenty obrazu.
  """

  # Wczytaj obraz
  szerokosc, wysokosc = obrazek.size

  # Inicjalizuj listę wycinków
  wycinki = []

  # Iteruj po wierszach obrazu
  for y in range(0, wysokosc - wielkosc_czesci[1] + 1):
    # Zwiększ przeskok pikseli o 1 po każdym wierszu
    przeskok_pikseli = 1 + y

    # Iteruj po kolumnach obrazu
    for x in range(0, szerokosc - wielkosc_czesci[0] + 1, przeskok_pikseli):
      # Wykonaj wycięcie części
      wycinek = obrazek.crop((x, y, x + wielkosc_czesci[0], y + wielkosc_czesci[1]))

      # Konwertuj wycinek na format numpy
      wycinek_numpy = np.array(wycinek)

      # Dodaj wycinek do listy
      wycinki.append(wycinek_numpy)

  return wycinki

# Odczytaj obraz za pomocą modułu PIL
obrazek = Image.open('obraz.png')

print(podziel_obraz(obrazek, (5, 15)))