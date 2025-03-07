import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

import matplotlib.pyplot as plt
import io
import asyncio

from typing import Self

class State:
    def __init__(self: Self):
        self.points: list[tuple[int, int]] = []
    def add_points(self: Self, new_points: tuple[int, int]):
        self.points.append(new_points)


state: State = State()

app: FastAPI = FastAPI()
app.mount("/nauka_web", StaticFiles(directory=os.path.join('public')))

@app.get('/')
def index():
    return FileResponse(path='index/index.html')

@app.post('/points')
def points(data: dict[str, list[int]]):
    state.add_points(tuple(data['points']))
    return 200

@app.get('/get_points')
async def get_points():
    return state.points

@app.get("/plot")
def plot_points():
    """Generuje nowy wykres na każde żądanie"""
    fig, ax = plt.subplots()

    if state.points:
        x_vals, y_vals = zip(*state.points)
        ax.scatter(x_vals, y_vals)

        # Dynamiczne ustawienie zakresów osi
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

    return StreamingResponse(buf, media_type="image/png")