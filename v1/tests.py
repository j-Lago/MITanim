import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from time import time

import matplotlib.pyplot as plt

from tools import denorm_base, rotate, translate, rotate_flat_list, norm_points, denorm_points
from Vec import gVec, NormCanvas
import numpy as np


from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


WIDTH = 700
HEIGHT = 700

fonts = {'default': ('Cambria', 12),
         'fps': ('Poor Richard', 14),
         }


colors = {'bg': '#ffffff',
          'airgap': '#ffffff',
          'outline': '#666666',
          'a': '#2a7db7',
          'b': '#33a333',
          'c': '#ff8419',
          'x': '#5d86a6',
          'y': '#5ba680',
          'z': '#f08e6b',
          'core': '#cccccc',
          'shaft': '#999999'
          }


def key_binds(window, anim):
    DELTA_FREQ = .1
    window.bind('<Right>', lambda event: anim.change_rotor_speed(DELTA_FREQ))
    window.bind('<Left>',  lambda event: anim.change_rotor_speed(-DELTA_FREQ))
    window.bind('<Up>',    lambda event: anim.change_freq(DELTA_FREQ))
    window.bind('<Down>',  lambda event: anim.change_freq(-DELTA_FREQ))
    window.bind('-',       lambda event: anim.change_delay(-1))
    window.bind('+',       lambda event: anim.change_delay(1))
    window.bind('<space>', lambda event: anim.toggle_run())
    window.bind('a',       lambda event: anim.toggle_visibility(0))
    window.bind('b',       lambda event: anim.toggle_visibility(1))
    window.bind('c',       lambda event: anim.toggle_visibility(2))
    window.bind('e',       lambda event: anim.toggle_visibility(3))
    window.bind('s',       lambda event: anim.toggle_stator_visibility())
    window.bind('r',       lambda event: anim.toggle_rotor_visibility())

def esp_positions(radius, ang):
    return (
    (radius * sin(0 + ang),                radius * cos(0 + ang)               ),
    (radius * sin(pi + ang),               radius * cos(pi + ang)              ),
    (radius * sin(2 * pi / 3 + ang),       radius * cos(2 * pi / 3 + ang)      ),
    (radius * sin(2 * pi / 3 + pi + ang),  radius * cos(2 * pi / 3 + pi + ang) ),
    (radius * sin(-2 * pi / 3 + ang),      radius * cos(-2 * pi / 3 + ang)     ),
    (radius * sin(-2 * pi / 3 + pi + ang), radius * cos(-2 * pi / 3 + pi + ang))
    )

def draw_ranhura(canvas: tk.Canvas, radius: float, orientation=0.0, center: tuple[float, float]=(0, 0), outline='#000000',width=1, fill='#ffffff', **args):
    x0, y0, base = denorm_base(canvas, center)
    r = int(radius*base)

    ps = [(-r, -r),
         (-r,  r),
         (r,  r),
         (r, -r)
         ]

    ps = rotate(ps, orientation)
    ps = [(e[0] + x0, e[1] + y0) for e in ps]

    return (canvas.create_polygon(ps, width=0, fill=fill, **args),
            canvas.create_line(ps[0][0], ps[0][1], ps[1][0], ps[1][1], width=width, fill=outline, **args),
            canvas.create_line(ps[1][0], ps[1][1], ps[2][0], ps[2][1], width=width, fill=outline, **args),
            canvas.create_line(ps[2][0], ps[2][1], ps[3][0], ps[3][1], width=width, fill=outline, **args),
            )

def draw_keyway(canvas: NormCanvas, size: tuple[float, float], radius: float, orientation=0.0, center = (0.0, 0.0), width=1, fill='#ffffff', **args):

    dx2, dy2 = size[0] / 2, size[1] / 2
    ps = ((-dx2, -radius+dy2),
          (-dx2, -radius-dy2),
          ( dx2, -radius-dy2),
          ( dx2, -radius+dy2)
          )

    ps = np.array(rotate(ps, orientation)).flatten().tolist()

    return canvas.draw_polygon(ps, fill=fill, **args)


def draw_3phase_stator(canvas: NormCanvas,
                       scale: float = 1.0,
                       orientation: float = 0.0,
                       width: float = 1.0):

    _, _, base = denorm_base(canvas.canvas)
    OUTER_RADIUS = .98 * scale
    INNER_RADIUS = .77 * scale
    SLOT_RADIUS = 0.073 * scale
    ESP_RADIUS = .067 * scale
    ESP_DISTANCE_E = 0.83 * scale
    pe_dir = tuple(v*scale for v in (.52, .65, .7, .98, .35, .98, .25, .7))
    pe_esq = tuple(v * (-1, 1)[k % 2] for k, v in enumerate(pe_dir))

    pe_dir = rotate_flat_list(pe_dir, orientation)
    pe_esq = rotate_flat_list(pe_esq, orientation)

    positions = esp_positions(ESP_DISTANCE_E, orientation)
    orientations = (0 - orientation,
                    pi - orientation,
                    2 * pi / 6 + pi - orientation,
                    2 * pi / 6 - orientation,
                    -2 * pi / 6 + pi - orientation,
                    -2 * pi / 6 - orientation
                    )

    return ( canvas.draw_polygon(pe_dir, width=width, fill=colors['core'], outline=colors['outline']),
             canvas.draw_polygon(pe_esq, width=width, fill=colors['core'], outline=colors['outline']),
             canvas.draw_circle(OUTER_RADIUS, width=width, fill=colors['core'], outline=colors['outline']),
             canvas.draw_circle(INNER_RADIUS, width=width, fill=colors['airgap'], outline=colors['outline']),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[0], outline=colors['outline'], fill=colors['airgap'], center=positions[0]),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[1], outline=colors['outline'], fill=colors['airgap'], center=positions[1]),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[2], outline=colors['outline'], fill=colors['airgap'], center=positions[2]),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[3], outline=colors['outline'], fill=colors['airgap'], center=positions[3]),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[4], outline=colors['outline'], fill=colors['airgap'], center=positions[4]),
             *draw_ranhura(widgets['canvas'], SLOT_RADIUS, width=width, orientation=orientations[5], outline=colors['outline'], fill=colors['airgap'], center=positions[5]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['a'], center=positions[0]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['a'], center=positions[1]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['b'], center=positions[2]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['b'], center=positions[3]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['c'], center=positions[4]),
             canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['c'], center=positions[5]),
             canvas.draw_circle((INNER_RADIUS*base-1.02*width)/base, width=width, fill=colors['airgap'], outline=colors['airgap']),
    )

def draw_3phase_induction_rotor(canvas: NormCanvas,
                                scale: float = 1.0,
                                orientation: float = 0.0,
                                width: float = 1.0):

    _, _, base = denorm_base(canvas.canvas)
    OUTER_RADIUS = .74 * scale
    ESP_RADIUS = .067 * scale
    ESP_DISTANCE_R = 0.83 * scale
    SHAFT_RADIUS = 0.15 * scale
    KEYWAY_SIZE = (.1 * scale, .1 * scale)

    pos_r = esp_positions(ESP_DISTANCE_R, orientation)
    core = canvas.draw_circle( OUTER_RADIUS, width=width, fill=colors['core'], outline=colors['outline'])
    esps_r = [canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['x'], center=pos_r[0]),
              canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['x'], center=pos_r[1]),
              canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['y'], center=pos_r[2]),
              canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['y'], center=pos_r[3]),
              canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['z'], center=pos_r[4]),
              canvas.draw_circle(ESP_RADIUS, width=0, fill=colors['z'], center=pos_r[5])]

    shaft = canvas.draw_circle(SHAFT_RADIUS, width=1, fill=colors['shaft'], outline=colors['core'])
    keyway = draw_keyway(canvas, KEYWAY_SIZE, SHAFT_RADIUS, orientation=orientation, fill=colors['core']),

    return ( core, *esps_r, shaft, keyway), esps_r, keyway


class Anim():
    def __init__(self, window, widgets):

        self.stator_visible = True
        self.rotor_visible = True

        self.ncanvas = NormCanvas(widgets['canvas'])

        self.frames_filter_fps = 0
        self.t_filter_fps = time()
        self.t = time()
        self.window = window
        self.widgets = widgets

        self.run = True

        self.thr = .0
        self.dt = .01

        self.w = 2
        self.w_MIN = -5
        self.w_MAX = 5

        self.wr = .8
        self.wr_MIN = self.w_MIN
        self.wr_MAX = self.w_MAX


        self.delay = 10
        self.delay_MIN = 1
        self.delay_MAX = 40

        self.vth = [0, -2 * pi / 3, 2 * pi / 3]
        self.vamp = [.45] * 3
        self.thm_e = [0, 2 * pi / 3, -2 * pi / 3]

        self.visibles = [True] * 4

        self.SLOT_RADIUS = 0.0715
        self.ESP_RADIUS = .067
        self.ESP_DISTANCE_E = 0.83
        self.ESP_DISTANCE_R = 0.67
        self.SHAFT_RADIUS = 0.15


        self.stator = draw_3phase_stator(self.ncanvas)
        self.rotor, self.esps_r, self.keyway = draw_3phase_induction_rotor(self.ncanvas)


        # widgets['canvas']

        dash = (10, 5)
        self.ncanvas.draw_line( width=1, fill=colors['a'], dash=dash, start=(self.ESP_DISTANCE_E * sin(0 + pi / 2), self.ESP_DISTANCE_E * cos(0 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(pi + pi / 2), self.ESP_DISTANCE_E * cos(pi + pi / 2)))
        self.ncanvas.draw_line( width=1, fill=colors['b'], dash=dash, start=(self.ESP_DISTANCE_E * sin(2 * pi / 3 + pi / 2), self.ESP_DISTANCE_E * cos(2 * pi / 3 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(2 * pi / 3 + pi + pi / 2), self.ESP_DISTANCE_E * cos(2 * pi / 3 + pi + pi / 2)))
        self.ncanvas.draw_line( width=1, fill=colors['c'], dash=dash, start=(self.ESP_DISTANCE_E * sin(-2 * pi / 3 + pi / 2), self.ESP_DISTANCE_E * cos(-2 * pi / 3 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(-2 * pi / 3 + pi + pi / 2), self.ESP_DISTANCE_E * cos(-2 * pi / 3 + pi + pi / 2)))

        self.vecs = []
        self.vecs.append(gVec(self.ncanvas, amp=self.vamp[0], th=0, color=colors['a']))
        self.vecs.append(gVec(self.ncanvas, amp=self.vamp[1], th=2 * pi / 3, color=colors['b']))
        self.vecs.append(gVec(self.ncanvas, amp=self.vamp[2], th=-2 * pi / 3, color=colors['c']))
        self.vecs.append(gVec(self.ncanvas, amp=0, th=0))


        self.ncanvas.draw_circle( .012, width=1, fill='#ffffff')

    def circle_to_denormalized_oval_coords(self, r, x, y):
        x0, y0, base = denorm_base(self.widgets['canvas'], (x, y))
        return x0 - r*base, y0 - r*base, x0 + r*base, y0 + r*base


    def toggle_run(self):
        self.run = not self.run

    def toggle_stator_visibility(self):
        self.stator_visible = not self.stator_visible

        for obj in self.stator:
            state = 'normal' if self.stator_visible else 'hidden'
            self.ncanvas.itemconfig(obj, state=state)

    def toggle_rotor_visibility(self):
        self.rotor_visible = not self.rotor_visible

        for obj in self.rotor:
            state = 'normal' if self.rotor_visible else 'hidden'
            self.ncanvas.itemconfig(obj, state=state)

    def toggle_visibility(self, ids):
        if not isinstance(ids, list | tuple):
            ids = [ids]

        for id in ids:
            self.visibles[id] = not self.visibles[id]
            self.vecs[id].set_visibility(self.visibles[id])
    def change_freq(self, delta):
        self.w += delta
        self.w = min(max(self.w, self.w_MIN), self.w_MAX)
        widgets['label'].config(text=f"DOWN/UP -> w: {self.w:1.1f}")

    def change_rotor_speed(self, delta):
        self.wr += delta
        self.wr = min(max(self.wr, self.wr_MIN), self.wr_MAX)
        widgets['label'].config(text=f"LEFT/RIGHT -> wr: {self.wr:1.1f}")

    def change_delay(self, delta):
        self.delay += delta
        self.delay = min(max(self.delay, self.delay_MIN), self.delay_MAX)
        widgets['label'].config(text=f"-/+ -> delay: {self.delay}")


    def loop(self):
        t = time()

        fps_filter = 100 // self.delay
        if self.frames_filter_fps < fps_filter-1:
            self.frames_filter_fps += 1
        else:
            dt_filter_fps = t - self.t_filter_fps
            try:
                fps = fps_filter / dt_filter_fps
            except ZeroDivisionError:
                fps = float('inf')
            self.t_filter_fps = t
            self.frames_filter_fps = 0
            widgets['fps'].config(text=f"fps: {fps:.0f}")

        dt = t - self.t
        self.t = t

        if self.run:

            self.thr += self.wr * dt

            x, y = 0, 0
            for k in range(3):
                self.vth[k] = self.vth[k] + self.w * dt
                self.vecs[k].polar = self.vamp[k] * sin(self.vth[k]), self.thm_e[k]
                x += self.vecs[k].x
                y += self.vecs[k].y

            self.vecs[3].rect = (x, y)

            pos_r = esp_positions(self.ESP_DISTANCE_R, self.thr)
            for k in range(len(pos_r)):
                self.widgets['canvas'].coords(self.esps_r[k], self.circle_to_denormalized_oval_coords(self.ESP_RADIUS, *pos_r[k]))

            coords = self.widgets['canvas'].coords(self.keyway)
            coords = norm_points(self.ncanvas.canvas, coords)
            coords = rotate(coords, self.wr * dt)
            self.widgets['canvas'].coords(self.keyway, denorm_points(self.ncanvas.canvas, coords))

            for v in self.vecs:
                pass
                v.refresh()

        self.window.after(self.delay, self.loop)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Motor de Indução Trifásico")

    fig, axs = plt.subplots(2,1, figsize=(8, 4), dpi=100)
    t = np.arange(0.0, 0.05, .0001)
    w = 2*pi*60
    d = 2*pi/3
    y = 0.8
    axs[0].plot(t, np.sin(w * t), t, np.sin(w * t - d), t, np.sin(w * t + d))
    axs[1].plot(0,0,0,0,0,0,t, np.sin(w * t + y), t, np.sin(w * t - d + y), t, np.sin(w * t + d + y))

    plt_canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    plt_canvas.draw()
    plt_canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)

    widgets = {'canvas': tk.Canvas(window, bg=colors['bg'], height=HEIGHT, width=WIDTH),
               'fps': tk.Label(window, text="fps:", font=fonts['fps'], fg='#bb5533'),
               'label': tk.Label(window, text="use UP/DOWN para alterar w", font=fonts['default'])
               }

    widgets['fps'].pack(anchor="w")
    widgets['canvas'].pack()
    widgets['label'].pack()
    window.update()

    anim = Anim(window, widgets)


    key_binds(window, anim)

    anim.loop()
    window.mainloop()
