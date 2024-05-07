import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from time import time


WIDTH = 701
HEIGHT = 701

fonts = {'default': ('Cambria', 12),
         'fps': ('Poor Richard', 14),
         }


colors = {'bg': '#ffffff',
          'airgap': '#ffffff',
          'outline': '#666666',
          'a': '#aa4422',
          'b': '#2244aa',
          'c': '#44aa22',
          'x': '#cc6633',
          'y': '#3366cc',
          'z': '#33cc66',
          'Fe': '#cccccc',
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


def deorm_canvas_coords(canvas: tk.Canvas, normalized_center: tuple[float, float] = (0, 0)) -> (float, float, float):
    base = min(canvas.winfo_width(), canvas.winfo_height()) // 2
    x0 = int(canvas.winfo_width() / 2 + base * normalized_center[0])
    y0 = int(canvas.winfo_height() / 2 + base * normalized_center[1])
    return (x0, y0, base)


class Vec:
    def __init__(self, canvas: tk.Canvas, amp, th, width=7, color='#000000', arrowshape=(.083, .09, .025)):
        self.canvas = canvas
        self.x0, self.y0, self.base = deorm_canvas_coords(canvas)
        self.abs = amp
        self.th = th
        # self.width = width
        # self.color = color
        self.arrowshape = tuple(v * self.base for v in arrowshape)
        self.line = canvas.create_line(self.x0, self.y0, self.x0, self.y0,
                                       width=width,
                                       arrow='last',
                                       arrowshape=self.arrowshape,
                                       fill=color,
                                       )

    @property
    def x(self):
        return self.abs * cos(self.th)

    @property
    def y(self):
        return self.abs * sin(self.th)

    @property
    def xy(self):
        ret = (self.x, self.y)
        return ret

    @xy.setter
    def xy(self, value: tuple[float]):
        self.abs = sqrt(value[0]**2 + value[1]**2)
        self.th = atan2(value[1], value[0])


    def refresh(self):
        amp = self.abs * self.base
        self.canvas.coords(self.line,
                           self.x0, self.y0,
                           self.x0+amp*cos(self.th), self.y0-amp*sin(self.th))

        THRESHOLD = .25
        if abs(self.abs) < THRESHOLD:
            arrowshape = [e*abs(self.abs)/THRESHOLD for e in self.arrowshape]
            self.canvas.itemconfig(self.line, arrowshape=arrowshape)

    def set_visibility(self, visible):
        if visible:
            self.canvas.itemconfig(self.line, state='normal')
        else:
            self.canvas.itemconfig(self.line, state='hidden')


def draw_circle(canvas: tk.Canvas, radius: float, center: tuple[float, float] = (0.0, 0.0), **args):
    x0, y0, base = deorm_canvas_coords(canvas, center)
    r = int(radius*base)
    return canvas.create_oval(x0 - r, y0 - r, x0 + r, y0 + r, **args)


def draw_polygon(canvas: tk.Canvas, points: list | tuple, center: tuple[float, float] = (0.0, 0.0), **args):
    x0, y0, base = deorm_canvas_coords(canvas, center)
    p0 = (x0, y0)
    pts = tuple( int(v*base + p0[k % 2]) for k, v in enumerate(points))
    return canvas.create_polygon(pts, **args)


def draw_rectangle_centered(canvas: tk.Canvas, radius: float, center: tuple[float, float] = (0.0, 0.0), **args):
    x0, y0, base = deorm_canvas_coords(canvas, center)
    r = int(radius*base)
    return canvas.create_rectangle(x0-r, y0-r, x0+r, y0+r, **args)


def rotate(pairs: list, ang: float) -> list:
    c = cos(ang)
    s = sin(ang)
    return [(x*c - y*s, x*s + y*c) for x, y in pairs]


def draw_ranhura(canvas: tk.Canvas, radius: float, orientation=0.0, center: tuple[float, float]=(0, 0), outline='#000000',width=1, fill='#ffffff', **args):
    x0, y0, base = deorm_canvas_coords(canvas, center)
    r = int(radius*base)


    ps = [(-r, -r),
         (-r,  r),
         (r,  r),
         (r, -r)
         ]

    ps = rotate(ps, orientation)
    ps = [(e[0] + x0, e[1] + y0) for e in ps]

    canvas.create_polygon(ps, width=0, fill=fill, **args)

    canvas.create_line(ps[0][0], ps[0][1], ps[1][0], ps[1][1], width=width, fill=outline, **args)
    canvas.create_line(ps[1][0], ps[1][1], ps[2][0], ps[2][1], width=width, fill=outline, **args)
    canvas.create_line(ps[2][0], ps[2][1], ps[3][0], ps[3][1], width=width, fill=outline, **args)


def draw_line(canvas: tk.Canvas, start: tuple[float, float], end: tuple[float, float], **args):
    x0, y0, _ = deorm_canvas_coords(canvas, start)
    x1, y1, _ = deorm_canvas_coords(canvas, end)
    return canvas.create_line(x0, y0, x1, y1, **args)


class Anim():
    def __init__(self, window, widgets):

        self.frames_filter_fps = 0
        self.t_filter_fps = time()
        self.t = time()
        self.window = window
        self.widgets = widgets

        self.run = True

        self.thr = .6
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

        self.visibles = [True] * 4

        self.SLOT_RADIUS = 0.0715
        self.ESP_RADIUS = .067
        self.ESP_DISTANCE_E = 0.83
        self.ESP_DISTANCE_R = 0.67


        dash = (10, 5)
        pe_dir = (.52, .65, .7, .98, .35, .98, .25, .7)
        pe_esq = tuple(v * (-1, 1)[k % 2] for k, v in enumerate(pe_dir))
        draw_polygon(widgets['canvas'], pe_dir, width=1, fill=colors['Fe'], outline=colors['outline'])
        draw_polygon(widgets['canvas'], pe_esq, width=1, fill=colors['Fe'], outline=colors['outline'])
        draw_circle(widgets['canvas'], .98, width=1, fill=colors['Fe'], outline=colors['outline'])
        draw_circle(widgets['canvas'], .77, width=1, fill=colors['airgap'], outline=colors['outline'])
        draw_circle(widgets['canvas'], .74, width=1, fill=colors['Fe'], outline=colors['outline'])


        pos_e = self.esp_positions(self.ESP_DISTANCE_E, 0)
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=0.0,            outline=colors['outline'], fill=colors['airgap'], center=pos_e[0])
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=pi,             outline=colors['outline'], fill=colors['airgap'], center=pos_e[1])
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=2 * pi / 6+pi,  outline=colors['outline'], fill=colors['airgap'], center=pos_e[2])
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=2 * pi / 6,     outline=colors['outline'], fill=colors['airgap'], center=pos_e[3])
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=-2 * pi / 6+pi, outline=colors['outline'], fill=colors['airgap'], center=pos_e[4])
        draw_ranhura(widgets['canvas'], self.SLOT_RADIUS, orientation=-2 * pi / 6,    outline=colors['outline'], fill=colors['airgap'], center=pos_e[5])

        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['a'], center=pos_e[0])
        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['a'], center=pos_e[1])
        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['b'], center=pos_e[2])
        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['b'], center=pos_e[3])
        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['c'], center=pos_e[4])
        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['c'], center=pos_e[5])

        pos_r = self.esp_positions(self.ESP_DISTANCE_R, self.thr)
        self.esps_r = [ draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['x'], center=pos_r[0]),
                        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['x'], center=pos_r[1]),
                        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['y'], center=pos_r[2]),
                        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['y'], center=pos_r[3]),
                        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['z'], center=pos_r[4]),
                        draw_circle(widgets['canvas'], self.ESP_RADIUS, width=0, fill=colors['z'], center=pos_r[5])
                        ]


        draw_line(widgets['canvas'], width=1, fill=colors['a'], dash=dash, start=(self.ESP_DISTANCE_E * sin(0 + pi / 2), self.ESP_DISTANCE_E * cos(0 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(pi + pi / 2), self.ESP_DISTANCE_E * cos(pi + pi / 2)))
        draw_line(widgets['canvas'], width=1, fill=colors['b'], dash=dash, start=(self.ESP_DISTANCE_E * sin(2 * pi / 3 + pi / 2), self.ESP_DISTANCE_E * cos(2 * pi / 3 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(2 * pi / 3 + pi + pi / 2), self.ESP_DISTANCE_E * cos(2 * pi / 3 + pi + pi / 2)))
        draw_line(widgets['canvas'], width=1, fill=colors['c'], dash=dash, start=(self.ESP_DISTANCE_E * sin(-2 * pi / 3 + pi / 2), self.ESP_DISTANCE_E * cos(-2 * pi / 3 + pi / 2)), end=(self.ESP_DISTANCE_E * sin(-2 * pi / 3 + pi + pi / 2), self.ESP_DISTANCE_E * cos(-2 * pi / 3 + pi + pi / 2)))

        self.vecs = []
        self.vecs.append(Vec(widgets['canvas'], amp=self.vamp[0], th=0, color=colors['a']))
        self.vecs.append(Vec(widgets['canvas'], amp=self.vamp[1], th=2 * pi / 3, color=colors['b']))
        self.vecs.append(Vec(widgets['canvas'], amp=self.vamp[2], th=-2 * pi / 3, color=colors['c']))
        self.vecs.append(Vec(widgets['canvas'], amp=0, th=0))

        draw_circle(widgets['canvas'], .02, width=1, fill='#ffffff')


    def esp_positions(self, radius, ang):
        return (
        (radius * sin(0 + ang),                radius * cos(0 + ang)               ),
        (radius * sin(pi + ang),               radius * cos(pi + ang)              ),
        (radius * sin(2 * pi / 3 + ang),       radius * cos(2 * pi / 3 + ang)      ),
        (radius * sin(2 * pi / 3 + pi + ang),  radius * cos(2 * pi / 3 + pi + ang) ),
        (radius * sin(-2 * pi / 3 + ang),      radius * cos(-2 * pi / 3 + ang)     ),
        (radius * sin(-2 * pi / 3 + pi + ang), radius * cos(-2 * pi / 3 + pi + ang))
        )

    def circle_to_denormalized_oval_coords(self, r, x, y):
        x0, y0, base = deorm_canvas_coords(self.widgets['canvas'], (x, y))
        return x0 - r*base, y0 - r*base, x0 + r*base, y0 + r*base


    def toggle_run(self):
        self.run = not self.run

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
                self.vecs[k].abs = self.vamp[k] * sin(self.vth[k])
                x += self.vecs[k].x
                y += self.vecs[k].y

            self.vecs[3].xy = (x, y)

            pos_r = self.esp_positions(self.ESP_DISTANCE_R, self.thr)
            for k in range(len(pos_r)):
                self.widgets['canvas'].coords(self.esps_r[k], self.circle_to_denormalized_oval_coords(self.ESP_RADIUS, *pos_r[k]))

            # draw_circle(widgets['canvas'], .067, width=0, fill=colors['x'], center=pos_r[1]),
            # draw_circle(widgets['canvas'], .067, width=0, fill=colors['y'], center=pos_r[2]),
            # draw_circle(widgets['canvas'], .067, width=0, fill=colors['y'], center=pos_r[3]),
            # draw_circle(widgets['canvas'], .067, width=0, fill=colors['z'], center=pos_r[4]),
            # draw_circle(widgets['canvas'], .067, width=0, fill=colors['z'], center=pos_r[5])

            for v in self.vecs:
                v.refresh()

        self.window.after(self.delay, self.loop)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Motor de Indução Trifásico")

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
