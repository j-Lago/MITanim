import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from time import time
from tools import denorm_base
from Vec import gVec, NormCanvas


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



    # key_binds(window)

    loop()
    window.mainloop()
