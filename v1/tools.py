import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from time import time
import numpy as np


def denorm_base(canvas: tk.Canvas,
                normalized_center: tuple[float, float] = (0.0, 0.0),
                denorm_base: float | None = None
                ) -> tuple[float, float, float]:
    if not denorm_base:
        denorm_base = min(canvas.winfo_width(), canvas.winfo_height()) // 2
    x = int(canvas.winfo_width() / 2 + denorm_base * normalized_center[0])
    y = int(canvas.winfo_height() / 2 + denorm_base * normalized_center[1])
    return x, y, denorm_base


def denorm_points(canvas, points, denorm_origin=True, *args) -> tuple:
    x0, y0, base = denorm_base(canvas, *args)
    p0 = ((x0, y0) if denorm_origin else (0, 0))
    return tuple(v * base * (1.0, -1.0)[xy_id := k % 2] + p0[xy_id] for k, v in enumerate(points))


def norm_points(canvas, points, *args) -> tuple:
    x0, y0, base = denorm_base(canvas, *args)
    return tuple((v - (x0, y0)[xy_id := k % 2]) / (base, -base)[xy_id] for k, v in enumerate(points))


def resize(arrowshape, amp):
    return tuple(v * amp for v in arrowshape)


def rotate(pairs: list | tuple | np.ndarray, ang: float) -> list:
    c = cos(ang)
    s = sin(ang)
    if isinstance(pairs[0], float | int):
        if (l := len(pairs)) < 2 or l % 2 == 1:
            raise ValueError(f'o tamanho de "pairs" deve ser par e maior ou igual a 2: {type(pairs)=}, {len(pairs)=}')
        pairs = np.array(pairs).reshape(-1, 2)
        return np.array([(x * c - y * s, x * s + y * c) for x, y in pairs]).flatten().tolist()
    elif isinstance(pairs[0], list | tuple | np.ndarray):
        return [(x * c - y * s, x * s + y * c) for x, y in pairs]
    else:
        raise ValueError(f'formato "pairs" não suportado: {type(pairs)=}')


def translate(pairs: list, dx, dy) -> list:
    return [(x + dx, y + dy) for x, y in pairs]


def rotate_flat_list(points: list, ang: float) -> list:
    c = cos(ang)
    s = sin(ang)
    pairs = np.array(points).reshape(-1, 2).tolist()

    return np.array([(x * c - y * s, x * s + y * c) for x, y in pairs]).flatten().tolist()
