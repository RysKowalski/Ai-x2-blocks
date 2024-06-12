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

def replace_non_matching_pixels(image_array, target_rgb):
  """Replaces non-matching pixels with black in a NumPy image array.

  Args:
    image_array (numpy.ndarray): The NumPy array representing the image.
    target_rgb (tuple): The target RGB color values (247, 243, 247).

  Returns:
    numpy.ndarray: The modified image array with non-matching pixels replaced by black.
  """
  # Check if the array has an alpha channel (fourth dimension)
  if image_array.ndim == 4:
    # Extract RGB values, ignoring the alpha channel
    rgb_array = image_array[..., :3]
  else:
    rgb_array = image_array

  # Replace non-matching pixels with black
  modified_image = np.where(np.all(rgb_array[:, :, :3] == target_rgb, axis=2), image_array, np.zeros_like(image_array))
  return modified_image

# Odczytaj obraz za pomocą modułu PIL
obrazek = Image.open('obraz.png')

obrazki = podziel_obraz(obrazek, (5, 15))

szablon = Image.open('szablon.png')
szablon = np.array(szablon)

obrazek = np.array(obrazek)

obrazek = obrazki[0][:, :, :3]


print(replace_non_matching_pixels(obrazek, (247, 243, 247)))