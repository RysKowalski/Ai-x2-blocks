import cv2
import numpy as np
from PIL import Image


def podziel_obraz(obrazek, wielkosc_czasci):
  """
  Dzieli obraz na mniejsze części o określonej wielkości i zwraca listę tych części.

  Argumenty:
    obrazek (obiekt cv2.Mat): Obraz, który ma zostać podzielony.
    wielkosc_czasci (tuple): Rozmiar (szerokość, wysokość) każdej części obrazu.

  Zwracany wartość:
    lista: Lista obiektów cv2.Mat, zawierająca wszystkie części obrazu.
  """

  # Sprawdź, czy obraz jest prawidłowy
  if not isinstance(obrazek, cv2.Mat):
    raise TypeError("Argument 'obrazek' musi być obiektem cv2.Mat")

  # Pobierz wymiary obrazu
  wysokosc, szerokosc, kanaly = obrazek.shape

  # Określ liczbę części w poziomie i pionie
  liczba_czesc_w_poziomie = szerokosc // wielkosc_czasci[0]
  liczba_czesc_w_pionie = wysokosc // wielkosc_czasci[1]

  # Utwórz pustą listę na części obrazu
  czesci_obrazu = []

  # Podziel obraz na części i dodaj je do listy
  for i in range(liczba_czesc_w_pionie):
    for j in range(liczba_czesc_w_poziomie):
      # Wyodrębnij część obrazu
      x = j * wielkosc_czasci[0]
      y = i * wielkosc_czasci[1]
      czesc = obrazek[y:y + wielkosc_czasci[1], x:x + wielkosc_czasci[0]]

      # Dodaj część do listy
      czesci_obrazu.append(czesc)

  return czesci_obrazu

# Odczytaj obraz za pomocą modułu PIL
obraz_pil = Image.open('obraz.png')

# Konwertuj obraz PIL na obiekt cv2.Mat
obrazek = cv2.cvtColor(np.array(obraz_pil), cv2.COLOR_RGB2BGR)
print(type(obrazek))

podziel_obraz(obrazek=obrazek, wielkosc_czasci=(3, 3))