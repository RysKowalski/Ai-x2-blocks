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
        self.points: list[tuple[int, int]] = []

    def add_points(self: Self, new_points: tuple[int, int]):
        self.points.append(new_points)

state: State = State()

app: FastAPI = FastAPI()
app.mount("/t", StaticFiles(directory=os.path.join('public')))

@app.get('/')
def index():
    return FileResponse(path='public/index/index.html')

@app.post('/points')
def points(data: dict[str, list[int]]):
    new_points: tuple[int, int] = data['points'][0], data['points'][1]
    state.add_points(new_points)
    return {"status": "ok"}

@app.get('/get_points')
async def get_points():
    return state.points

@app.get("/plot")
def plot_points():
    """Generuje nowy wykres na każde żądanie i czyści pamięć"""
    plt.close('all')  # Zamknięcie wszystkich otwartych wykresów przed stworzeniem nowego
    fig, ax = plt.subplots()

    if state.points:
        x_vals, y_vals = zip(*state.points)
        ax.scatter(x_vals, y_vals)

        ax.set_xlim(min(x_vals) - 10, max(x_vals) + 10)
        ax.set_ylim(min(y_vals) - 10, max(y_vals) + 10)
    else:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

    ax.set_title("Visualization of Points")
    ax.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)

    buf.seek(0)

    # StreamingResponse automatycznie zamknie buf po przesłaniu danych
    return StreamingResponse(buf, media_type="image/png", headers={"Connection": "close"})
