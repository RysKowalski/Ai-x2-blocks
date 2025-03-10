def filtruj_i_znajdz_index(lista1: list[float], lista2: list[bool]) -> int:
    return max((i for i, (val, flag) in enumerate(zip(lista1, lista2)) if flag), key=lambda x: lista1[x])
