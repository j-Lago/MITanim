import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from NormCanvas import NormCanvas
from primitive import Primitive
from transforms import translate, rotate, scale, rgb_to_hex
from time import time
from assets import mosca, primitives, cl
from Animation import Animation
from collections import deque
from statistics import mean


WIDTH = 700
HEIGHT = 700

fonts = {'default': ('Cambria', 12),
         'fps': ('Poor Richard', 14),
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
    window.bind('a',       lambda event: anim.toggle_visibility)
    # window.bind('b',       lambda event: anim.toggle_visibility(1))
    # window.bind('c',       lambda event: anim.toggle_visibility(2))
    # window.bind('e',       lambda event: anim.toggle_visibility(3))


class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas):
        super().__init__(canvas)

        self.dt_filter_buffer = deque(maxlen=10)

        self.stator_core = [
            Primitive(self.canvas, **primitives['stator_outer']),
            Primitive(self.canvas, **primitives['stator_inner']),
            *(Primitive(self.canvas, **primitives['stator_cutout']).rotate(2*pi/6*i) for i in range(6)),
        ]

        self.rotor_core = [
            Primitive(self.canvas, **primitives['rotor_outer']),
            *(Primitive(self.canvas, **primitives['rotor_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]

        self.stator_esp = [
            *(Primitive(self.canvas, **primitives['stator_esp']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.stator_esp):
            p.fill = cl[('a', 'b', 'c')[i % 3]]

        self.rotor_esp = [
            *(Primitive(self.canvas, **primitives['rotor_esp']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.rotor_esp):
            p.fill = cl[('x', 'y', 'z')[i % 3]]



        for p in (*self.stator_core, *self.rotor_core, *self.stator_esp, *self.rotor_esp):
            p.draw()

        coords = translate(mosca['polygon']['coords'], (350, 350))
        self.mosca = canvas.create_polygon(coords, fill='#cccccc', outline='#000000')





    def loop_update(self, t, dt):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        widgets['fps'].config(text=f"fps: {fps:.0f}")

        offset = (350 + 300 * sin(0.47896541 * t), 350 + 300 * cos(1.1357 * t))
        coords = translate(mosca['polygon']['coords'], offset)
        coords = rotate(coords, 4.87*cos(t*0.8)*(sin(t*1.8)+0.8), offset)
        canvas.coords(self.mosca, coords)

        for p in (*self.rotor_core, *self.rotor_esp):
            p.rotate(dt*1.1)
            p.draw()



if __name__ == '__main__':
    window = tk.Tk()
    window.title("Motor de Indução Trifásico")
    canvas = NormCanvas(window, bg='#ffffff', height=HEIGHT, width=WIDTH)


    widgets = {
               'fps': tk.Label(window, text="fps:", font=fonts['fps'], fg='#bb5533'),
               'label': tk.Label(window, text="use UP/DOWN para alterar w", font=fonts['default'])
               }

    widgets['fps'].pack(anchor="w")
    canvas.pack()
    widgets['label'].pack()
    window.update()


    anim = CustomAnim(canvas)


    # key_binds(window)

    anim.loop()
    window.mainloop()
