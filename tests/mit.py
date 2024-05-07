import aggdraw
import tkinter as tk
import numpy as np
from numpy import pi, sin, cos, arctan2, sqrt
from typing import Any
import itertools

palette = {'bg': '#eeeeee',
               'a': '#aa4422',
               'b': '#2244aa',
               'c': '#44aa22',
               'x': '#aa1155',
               'y': '#5511aa',
               'z': '#55aa11',
               'Fe': '#cccccc'
               }

class NormalizedDraw:
    def __init__(self, draw):
        self.draw = draw

    def denormalize(self, points) -> tuple:
        nv = [0]*len(points)
        base = 250
        p0 = (250, 250)
        sinal = (1.0, -1.0)
        return tuple( v * base * sinal[xy_id := k % 2] + p0[xy_id] for k, v in enumerate(points))

    def line(self, coords: tuple | list, pen):
        self.draw.line(self.denormalize(coords), pen)

    def polygon(self, coords: tuple | list, pen, brush):
        self.draw.polygon(self.denormalize(coords), pen, brush)

def clip(value, vmin, vmax):
    return max(min(value, vmax), vmin)


def rgb255(rgb: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(int(clip(e*255, vmin=0, vmax=255)) for e in rgb)


def polar_to_rect(amp, theta):
    return amp*cos(theta), amp*sin(theta)

def rect_to_polar(x, y):
    return arctan2(y, x)

def rotate(pairs: list | tuple, ang: float) -> tuple:
    c = cos(ang)
    s = sin(ang)
    return tuple((x*c - y*s, x*s + y*c) for x, y in pairs)


class Vec2():
    def __init__(self, x: float = 0.0, y: float = 0.0,
                 draw: Any | None = None,
                 width=1,
                 line_color=(0.0, 0.0, 0.0),
                 fill_color=None,
                 tip=(-.06, -0.02, -.055),
                 amp: float | None = None, theta: float | None = None,
                 x0: float = 0.0, y0: float = 0.0,
                 **line_args
                 ):

        self.draw = draw
        self.tip = tip
        self.lc_255 = rgb255(line_color)
        self.fc_255 = rgb255(fill_color if fill_color else line_color)

        self.x0, self.y0 = x0, y0

        if isinstance(amp, float) and isinstance(theta, float):
            self.x, self.y = polar_to_rect(amp, theta)
        else:
            self.x, self.y = x, y

        self.pen = aggdraw.Pen(self.lc_255, width)
        self.brush = aggdraw.Brush(self.fc_255)

        if draw:
            draw.line((self.x0, self.y0, self.x, self.y), self.pen)
            if tip:
                self._draw_tip()

    def _draw_tip(self):
            """
            self.tip = (p1.x, p1.y, p2.x)
            fica implícito: p0 = (0, 0), p2.y = 0, p3.x=p1.x e p3.y=-p1.y
               p1
               *
                 *     *
                   *         *
                     *            *
    =================== p2             * p0=(0,0)
                     *            *
                   *         *
                 *     *
               *
              p3
            """
            pts = ( (0.0, 0.0),                      # p0
                    (self.tip[0], self.tip[1]),      # p1
                    (self.tip[2], 0.0),              # p2
                    (self.tip[0], -self.tip[1])      # p3
                    )


            amp = self.amp
            theta = self.theta

            pts_rotate = rotate(pts, theta)
            # pts_scale = tuple( (p[0] * amp, p[1] * amp) for p in pts_rotate)

            pts_ofsset = tuple( (p[0] + self.x, p[1] + self.y) for p in pts_rotate)
            pts_flat = tuple(itertools.chain.from_iterable(pts_ofsset))

            # print(f'{pts=}')
            # print(f'{pts_rotate=}')
            # print(f'{pts_ofsset=}')
            # print(f'{pts_flat=}')
            self.draw.polygon(pts_flat, self.pen, self.brush)

            # print(f'estive aqui: {tuple(zip(*pts_flat))}')


    @property
    def amp(self):
        return sqrt((self.x-self.x0)**2 + (self.y-self.y0)**2)

    @property
    def theta(self):
        return arctan2(self.y-self.y0, self.x-self.x0)

    @property
    def polar(self) -> tuple:
        return self.amp, self.theta

    @polar.setter
    def polar(self, value):
        self.x, self.y = polar_to_rect(value[0], value[1])

    def __str__(self):
        return f'(start=({self.x0:.3f},  {self.y0:.3f}), end=({self.x:.3f},  {self.y:.3f}))'


class Animation():
    def __init__(self, root, norm_draw, delay=1000):
        self.delay = delay
        self.root = root
        self.norm_draw = norm_draw

        self.th = 0
        self.amps = [0.0, .0, 0.0]
        self.ths = [0.0, 2*pi / 3, -2*pi / 3]

        self.vecs = []
        self.vecs.append(Vec2(amp=self.amps[0], theta=self.ths[0], draw=self.norm_draw, width=3, line_color=(1, 0.5, 0)))
        self.vecs.append(Vec2(amp=self.amps[1], theta=self.ths[1], draw=self.norm_draw, width=3, line_color=(0.5, 0, 1)))
        self.vecs.append(Vec2(amp=self.amps[2], theta=self.ths[2], draw=self.norm_draw, x0=0, y0=0, width=3, line_color=(0, 1, 0.5)))
        print(self.vecs)

    def loop(self, dt):
        self.th += 2*dt
        self.amps = [sin(self.th), sin(self.th - 2 * pi / 3), sin(self.th + 2 * pi / 3)]
        self.ths = [0.0, 2 * pi / 3, -2 * pi / 3]

        self.vecs[0].polar = (self.amps[0], self.ths[0])
        self.vecs[1].polar = (self.amps[1], self.ths[1])
        self.vecs[2].polar = (self.amps[2], self.ths[2])

        self.norm_draw.draw.flush()
        print(int(self.th/2/dt))
        self.root.after(self.delay, self.loop, dt)


def main():


    size = (500, 500)
    root = tk.Tk()


    draw = aggdraw.Dib("RGB", size, palette['bg'])
    norm_draw = NormalizedDraw(draw)



    frame = tk.Frame(root, width=size[0], height=size[1], bg="")
    frame.bind("<Expose>", lambda e: draw.expose(hwnd=e.widget.winfo_id()))
    frame.pack()

    anim = Animation(root, norm_draw)
    # DELTA_FREQ = .1
    # window.bind('<Up>', lambda event: anim.change_freq(DELTA_FREQ))
    # window.bind('<Down>', lambda event: anim.change_freq(-DELTA_FREQ))
    # window.bind('<space>', lambda event: anim.toggle_run())
    # window.bind('a', lambda event: anim.toggle_visibility(0))
    # window.bind('b', lambda event: anim.toggle_visibility(1))
    # window.bind('c', lambda event: anim.toggle_visibility(2))
    # window.bind('e', lambda event: anim.toggle_visibility(3))

    anim.loop(.01)
    frame.mainloop()





if __name__ == '__main__':
    main()