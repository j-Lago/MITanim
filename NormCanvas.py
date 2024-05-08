import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from tools import denorm_base, denorm_points, resize


class NormCanvas():
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas

    def denorm(self, points, denorm_origin=True):
        return denorm_points(self.canvas, points, denorm_origin=denorm_origin)

    def denorm_arrowshape(self, arrowshape):
        _, _, base = denorm_base(self.canvas)
        return resize(arrowshape, base)


    def create_line(self, x0, y0, x1, y1, arrowshape=None, *args, **kwargs):
        if arrowshape:
            kwargs['arrowshape'] = self.denorm_arrowshape(arrowshape)
        return self.canvas.create_line(*self.denorm((x0, y0, x1, y1)), *args, **kwargs)

    def coords(self, line, *args):
        self.canvas.coords(line, self.denorm(args))

    def winfo_width(self):
        return self.canvas.winfo_width()

    def winfo_height(self):
        return self.canvas.winfo_height()

    def itemconfig(self, line, arrowshape: tuple[float, ...] | None = None, *args, **kwargs):
        _, _, base = denorm_base(self.canvas, *args)
        if arrowshape:
            kwargs['arrowshape'] = self.denorm_arrowshape(arrowshape)

        self.canvas.itemconfig(line, *args, **kwargs)

    def pack(self):
        self.canvas.pack()

    def draw_line(self, start: tuple[float, float], end: tuple[float, float], **args):
        x0, y0, _ = denorm_base(self.canvas, start)
        x1, y1, _ = denorm_base(self.canvas, end)
        return self.canvas.create_line(x0, y0, x1, y1, **args)

    def draw_circle(self, radius: float, center: tuple[float, float] = (0.0, 0.0), **args):
        x0, y0, base = denorm_base(self.canvas, center)
        r = int(radius * base)
        return self.canvas.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, **args)

    def draw_polygon(self, points: list | tuple, center: tuple[float, float] = (0.0, 0.0), **args):
        x0, y0, base = denorm_base(self.canvas, center)
        p0 = (x0, y0)
        pts = tuple(int(v * base + p0[k % 2]) for k, v in enumerate(points))
        return self.canvas.create_polygon(pts, **args)

    def draw_square_centered(self, radius: float, center: tuple[float, float] = (0.0, 0.0), **args):
        x0, y0, base = denorm_base(self.canvas, center)
        r = int(radius * base)
        return self.canvas.create_rectangle(x0 - r, y0 - r, x0 + r, y0 + r, **args)