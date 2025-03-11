import os
import gc
import io
import matplotlib
import matplotlib.pyplot as plt

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

from typing import Self

# Użycie bezpieczniejszego backendu dla matplotlib
matplotlib.use('Agg')

class State:
    def __init__(self: Self):
        """Inicjalizuje stan z listą punktów. Każdy punkt to krotka (x, y, is_golden)."""
        self.points: list[tuple[int, int, bool]] = []

    def add_points(self: Self, new_point: tuple[int, int, bool]) -> None:
        """Dodaje nowy punkt do listy punktów."""
        self.points.append(new_point)

state: State = State()

app: FastAPI = FastAPI()
app.mount("/t", StaticFiles(directory=os.path.join('public')))

@app.get('/')
def index():
    """Zwraca stronę główną."""
    return FileResponse(path='public/index/index.html')

@app.post('/points')
def points(data: dict) -> dict:
    """
    Dodaje punkt do stanu.
    
    Oczekuje JSON z kluczami:
      - "points": lista dwóch liczb (x, y)
      - opcjonalnie "limit": jeśli True, punkt będzie oznaczony jako złoty
    """
    x, y = data['points'][0], data['points'][1]
    print(data.get('limit', 'skibidi'))
    is_golden: bool = data.get('limit', False)
    state.add_points((x, y, is_golden))
    return {"status": "ok"}

@app.get('/get_points')
async def get_points():
    """Zwraca listę wszystkich punktów."""
    return state.points

@app.get("/plot")
def plot_points():
    """Generuje nowy wykres na każde żądanie i czyści pamięć."""
    plt.close('all')
    fig, ax = plt.subplots()

    if state.points:
        golden_points = [(x, y) for x, y, is_golden in state.points if is_golden]
        normal_points = [(x, y) for x, y, is_golden in state.points if not is_golden]
        
        if normal_points:
            x_vals, y_vals = zip(*normal_points)
            ax.scatter(x_vals, y_vals, color='blue')
        if golden_points:
            x_vals, y_vals = zip(*golden_points)
            ax.scatter(x_vals, y_vals, color='gold')
        
        all_x = [x for x, _, _ in state.points]
        all_y = [y for _, y, _ in state.points]
        ax.set_xlim(min(all_x) - 10, max(all_x) + 10)
        ax.set_ylim(min(all_y) - 10, max(all_y) + 10)
    else:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

    ax.set_title("Visualization of Points")
    ax.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png", headers={"Connection": "close"})
