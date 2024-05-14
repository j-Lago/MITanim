from __future__ import annotations
import tkinter as tk
from transformations import Coords, Point, denorm_coords
from math import sqrt


class NormCanvas(tk.Canvas):
    def __init__(self, window: tk.Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = window

