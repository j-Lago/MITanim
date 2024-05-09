import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from time import time
from tools import denorm_base
from Vec import gVec, NormCanvas
import tksvg


WIDTH = 700
HEIGHT = 700

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


def key_binds(window):
    DELTA_FREQ = .1
    # window.bind('<Right>', lambda event: anim.change_rotor_speed(DELTA_FREQ))
    # window.bind('<Left>',  lambda event: anim.change_rotor_speed(-DELTA_FREQ))
    # window.bind('<Up>',    lambda event: anim.change_freq(DELTA_FREQ))
    # window.bind('<Down>',  lambda event: anim.change_freq(-DELTA_FREQ))
    # window.bind('-',       lambda event: anim.change_delay(-1))
    # window.bind('+',       lambda event: anim.change_delay(1))
    # window.bind('<space>', lambda event: anim.toggle_run())
    # window.bind('a',       lambda event: anim.toggle_visibility(0))
    # window.bind('b',       lambda event: anim.toggle_visibility(1))
    # window.bind('c',       lambda event: anim.toggle_visibility(2))
    # window.bind('e',       lambda event: anim.toggle_visibility(3))


def loop():
    global th
    th += 0.01
    v1.polar = sin(th+2*pi/3), -2*pi/3
    v2.polar = sin(th-2*pi/3), 2*pi/3



    v1.refresh()
    v2.refresh()

    window.after(10, loop)


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Motor de Indução Trifásico")
    ocanvas = tk.Canvas(window, bg=colors['bg'], height=HEIGHT, width=WIDTH)
    canvas = NormCanvas(ocanvas)

    widgets = {
               'fps': tk.Label(window, text="fps:", font=fonts['fps'], fg='#bb5533'),
               'label': tk.Label(window, text="use UP/DOWN para alterar w", font=fonts['default'])
               }

    widgets['fps'].pack(anchor="w")
    canvas.pack()
    widgets['label'].pack()
    window.update()

    th = 0.0
    v1 = gVec(canvas, 0.8, th, color='red')
    v2 = gVec(canvas, 1, th, color='blue')

    def offset(path: list | tuple, offset: tuple[float, float]) -> list | tuple:
        new_path = [v + (offset)[i % 2] for i, v in enumerate(path)]
        if isinstance(path, list):
            return new_path
        elif isinstance(path, tuple):
            return tuple(new_path)
        else:
            raise ValueError(f"'path' com tipo incompatível: {type(path)=}")


    polygon = [5, 0, 10, 1, 15, 3, 4, 2, 8, 5, 12, 8, 3, 3, 6, 8, 8, 12, 2, 5, 3, 9, 3, 15, 0, 1, 0, 3, -1, 5, -4, 34, 11, 2, 12, 3, 11, 3, 12, 3, 11, 5, 10, 4, 11, 5, 10, 6, 10, 6, 9, 6, 9, 7, 9, 8, 9, 8, 8, 8, 7, 8, 8, 9, 27, -21, 1, -1, 1, -1, 1, 0, 2, -1, 14, -5, 14, 1, 13, 6, 10, 12, 5, 14, -1, 14, -7, 13, -11, 10, -1, 1, -1, 0, -1, 1, -1, 0, -33, 13, 4, 11, 4, 11, 3, 11, 2, 11, 2, 12, 2, 11, 1, 12, 0, 12, 0, 12, -1, 12, -2, 12, -2, 11, -2, 11, -3, 11, -4, 11, -4, 11, 33, 13, 1, 1, 3, 1, 4, 2, 5, 3, 8, 6, 11, 10, 3, 4, 5, 9, 7, 13, 1, 5, 1, 10, 1, 15, -1, 4, -2, 9, -5, 14, -3, 4, -6, 8, -10, 11, -4, 3, -8, 5, -13, 6, -5, 2, -9, 2, -14, 1, -5, 0, -10, -2, -14, -4, -2, -1, -3, -2, -5, -3, -27, -22, -8, 9, -7, 9, -8, 8, -9, 8, -9, 7, -9, 7, -9, 6, -10, 6, -10, 6, -11, 5, -10, 5, -11, 4, -12, 3, -11, 3, -12, 3, -11, 2, 4, 35, 0, 1, 1, 1, 0, 1, 0, 2, -3, 14, -8, 12, -12, 8, -15, 3, -15, -3, -12, -8, -8, -12, -3, -14, 0, -2, 0, -1, 1, -1, 0, -1, 4, -35, -11, -2, -12, -3, -11, -3, -12, -3, -11, -4, -10, -5, -11, -5, -10, -6, -10, -6, -9, -6, -9, -7, -9, -7, -9, -8, -8, -8, -7, -9, -8, -9, -27, 22, -2, 1, -3, 2, -5, 3, -18, 10, -41, 4, -51, -14, -10, -18, -4, -41, 14, -52, 1, -1, 3, -1, 4, -2, 33, -13, -4, -11, -4, -11, -3, -11, -2, -11, -2, -11, -2, -12, -1, -12, 0, -12, 0, -12, 1, -12, 2, -11, 2, -12, 2, -11, 3, -11, 4, -11, 4, -11, -33, -13, -1, 0, -1, -1, -1, 0, -1, -1, -11, -10, -7, -13, -1, -14, 5, -14, 10, -12, 13, -6, 14, -1, 14, 5, 2, 1, 1, 0, 1, 1, 1, 1, 27, 21, 8, -9, 7, -8, 8, -8, 9, -8, 9, -8, 9, -7, 9, -6, 10, -6, 10, -6, 11, -5, 10, -4, 11, -5, 12, -3, 11, -3, 12, -3, 11, -2, -4, -34, -1, -2, -1, -4, -1, -5, 0, -6, 1, -10, 3, -15, 2, -4, 5, -9, 8, -12, 4, -3, 8, -6, 12, -8, 5, -2, 10, -3, 15, -3]
    polygon = offset(polygon, (350, 350))

    canvas.canvas.create_polygon(polygon, fill='#cccccc', outline='#000000')



    # key_binds(window)

    loop()
    window.mainloop()
