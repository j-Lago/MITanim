import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from NormCanvas import NormCanvas
from primitive import Primitive
from transforms import translate, rotate, scale, rgb_to_hex
import time
from assets import primitives, cl
from animation import Animation
from collections import deque
from statistics import mean


WIDTH = 700
HEIGHT = 700

fonts = {'default': ('Cambria', 12),
         'fps': ('Poor Richard', 14),
         }


class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas):
        super().__init__(canvas)

        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.ths = 0.0
        self.thr = 0.0
        self.th  = 0.0
        self.run = True

        self.stator_core = [
            Primitive(self.canvas, **primitives['stator_outer']),
            Primitive(self.canvas, **primitives['stator_inner']),
            *(Primitive(self.canvas, **primitives['stator_cutout']).rotate(2*pi/6*i) for i in range(6)),
            *(Primitive(self.canvas, **primitives['stator_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]

        self.rotor_core = [
            Primitive(self.canvas, **primitives['rotor_outer']),
            *(Primitive(self.canvas, **primitives['rotor_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
            *(Primitive(self.canvas, **primitives['rotor_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]


        self.stator_axis = [
            *(Primitive(self.canvas, **primitives['stator_axis']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.stator_axis):
            p.stroke = cl[('a', 'b', 'c')[i % 3]]

        self.rotor_axis = [
            *(Primitive(self.canvas, **primitives['rotor_axis']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.rotor_axis):
            p.stroke = cl[('x', 'y', 'z')[i % 3]]



        self.stator_flux = [
            (Primitive(self.canvas, **primitives['quarter_flux'])),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, 1)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, -1)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((1, -1)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((.8, .77), center=(0.0, -0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(0.0, -0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(0.0, 0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((1, -1)).scale((.8, .77), center=(0.0, 0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((.65, .5), center=(0.0, -0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(0.0, -0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(0.0, 0.50571428571428571428571428571429)),
            (Primitive(self.canvas, **primitives['quarter_flux'])).scale((1, -1)).scale((.65, .5), center=(0.0, 0.50571428571428571428571428571429)),
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

        self.rotor_esp_front = [
            *(Primitive(self.canvas, **primitives['rotor_esp_front']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.rotor_esp_front):
            p.fill = cl[('x', 'y', 'z')[i % 3]]

        self.stator_esp_front = [
            *(Primitive(self.canvas, **primitives['stator_esp_front']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.stator_esp_front):
            p.fill = cl[('a', 'b', 'c')[i % 3]]


        self.rotor = (*self.rotor_core,
                      *self.rotor_esp,
                      *self.rotor_axis,
                      *self.rotor_esp_front
                      )

        self.stator = (*self.stator_core,
                       *self.stator_esp,
                       *self.stator_axis,
                       *self.stator_esp_front
                       )


        for p in (*self.stator, *self.stator_flux, *self.rotor):
            p.draw()

    def binds(self):

        def toggle_run():
            self.run = not self.run

        def toggle_stator_esp_front_visibility():
            for p in self.stator_esp_front:
                p.visible = not p.visible

        def toggle_rotor_esp_front_visibility():
            for p in self.rotor_esp_front:
                p.visible = not p.visible

        def toggle_stator_flux_visibility():
            for p in self.stator_flux:
                p.visible = not p.visible

        DELTA_FREQ = .1
        # window.bind('<Right>', lambda event: anim.change_rotor_speed(DELTA_FREQ))
        # window.bind('<Left>',  lambda event: anim.change_rotor_speed(-DELTA_FREQ))
        # window.bind('<Up>',    lambda event: anim.change_freq(DELTA_FREQ))
        # window.bind('<Down>',  lambda event: anim.change_freq(-DELTA_FREQ))
        # window.bind('-',       lambda event: anim.change_delay(-1))
        # window.bind('+',       lambda event: anim.change_delay(1))
        self.canvas.window.bind('<space>', lambda event: toggle_run())
        # window.bind('a',       lambda event: anim.toggle_visibility)
        # window.bind('b',       lambda event: anim.toggle_visibility(1))
        # window.bind('c',       lambda event: anim.toggle_visibility(2))
        self.canvas.window.bind('e',       lambda event: toggle_stator_esp_front_visibility())
        self.canvas.window.bind('g',       lambda event: toggle_rotor_esp_front_visibility())
        self.canvas.window.bind('f',       lambda event: toggle_stator_flux_visibility())





    def loop_update(self, t, dt):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        widgets['fps'].config(text=f"fps: {fps:.0f}")

        if self.run:
            self.thr = dt * 0.5
            for p in self.rotor:
                p.rotate(self.thr)
                p.draw()

            self.the = dt * 0.8
            for p in self.stator_flux:
                p.rotate(self.the)
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
