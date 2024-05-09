import tkinter as tk
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas
from primitive import Primitive
from transforms import translate, rotate, scale, rgb_to_hex
import time
from assets import assets, cl
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal


WIDTH = 700
HEIGHT = 700

fonts = {'default': ('Cambria', 12),
         'fps': ('Poor Richard', 14),
         }


class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas):
        super().__init__(canvas, frame_delay=1)

        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)

        self.run = True
        self.prims = {'stator': {},
                      'rotor': {},
                      'extra_s': {},
                      'extra_r': {},
                      }


        self.ths = 0.0
        self.thr = 0.0
        self.the  = 0.0



        self.prims['stator']['core'] = [
            self.create_primitive(**assets['stator_outer']),
            self.create_primitive(**assets['stator_inner']),
            *(self.create_primitive(**assets['stator_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
            *(self.create_primitive(**assets['stator_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]

        self.prims['rotor']['core'] = [
            self.create_primitive(**assets['rotor_outer']),
            *(self.create_primitive(**assets['rotor_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
            *(self.create_primitive(**assets['rotor_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]


        self.prims['stator']['axis'] = [
            *(self.create_primitive(**assets['stator_axis']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['stator']['axis']):
            p.stroke = cl[('a', 'b', 'c')[i % 3]]

        self.prims['rotor']['axis'] = [
            *(self.create_primitive(**assets['rotor_axis']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['rotor']['axis']):
            p.stroke = cl[('x', 'y', 'z')[i % 3]]



        # for p in self.stator_flux[::2]:
        self.prims['extra_s']['flux'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse(),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)),

            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(0.0, -0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(0.0, -0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(0.0, 0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(0.0, 0.50571428571428571428571428571429)),

            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(0.0, -0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(0.0, -0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(0.0, 0.50571428571428571428571428571429)),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(0.0, 0.50571428571428571428571428571429)),
        ]


        self.prims['stator']['esp']  = [
            *(self.create_primitive(**assets['stator_esp']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.prims['stator']['esp']):
            p.fill = cl[('a', 'b', 'c')[i % 3]]

        self.prims['rotor']['esp'] = [
            *(self.create_primitive(**assets['rotor_esp']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.prims['rotor']['esp']):
            p.fill = cl[('x', 'y', 'z')[i % 3]]

        self.prims['extra_r']['esp_front'] = [
            *(self.create_primitive(**assets['rotor_esp_front']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['extra_r']['esp_front']):
            p.fill = cl[('x', 'y', 'z')[i % 3]]

        self.prims['extra_s']['esp_front'] = [
            *(self.create_primitive(**assets['stator_esp_front']).rotate(-2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['extra_s']['esp_front']):
            p.fill = cl[('a', 'b', 'c')[i % 3]]


        # self.rotor = (*self.prims['rotor']['core'],
        #               *self.prims['rotor']['esp'],
        #               *self.prims['rotor']['esp_front'],
        #               *self.prims['rotor']['axis'],
        #               )
        #
        # self.stator = (*self.prims['stator']['core'],
        #                *self.prims['stator']['esp'],
        #                *self.prims['stator']['esp_front'],
        #                *self.prims['stator']['axis'],
        #                *self.prims['stator']['flux'],
        #                )

        # for p in (*self.stator, *self.rotor):
        for part in self.prims:
            for group in self.prims[part]:
                for prim in self.prims[part][group]:
                    prim.draw(consolidate_transforms_to_original=True)

    def binds(self):

        def toggle_run():
            self.run = not self.run

        def toggle_visibility(parts: Literal['stator', 'rotor'], groups: str | None = None):

            first_visibility = None
            if isinstance(parts, str):
                parts = [parts]
            for part in parts:
                if groups:
                    if isinstance(groups, str):
                        groups = [groups]
                    for group in groups:
                        for p in self.prims[part][group]:
                            if first_visibility == None:
                                first_visibility = not p.visible
                            p.visible = first_visibility
                else:
                    for group in self.prims[part]:
                        for p in self.prims[part][group]:
                            if first_visibility == None:
                                first_visibility = not p.visible
                            p.visible = first_visibility

        DELTA_FREQ = .1
        # window.bind('<Right>', lambda event: anim.change_rotor_speed(DELTA_FREQ))
        # window.bind('<Left>',  lambda event: anim.change_rotor_speed(-DELTA_FREQ))
        # window.bind('<Up>',    lambda event: anim.change_freq(DELTA_FREQ))
        # window.bind('<Down>',  lambda event: anim.change_freq(-DELTA_FREQ))
        # window.bind('-',       lambda event: anim.change_delay(-1))
        # window.bind('+',       lambda event: anim.change_delay(1))
        self.canvas.window.bind('<space>', lambda event: toggle_run())
        self.canvas.window.bind('r',       lambda event: toggle_visibility('rotor'))
        self.canvas.window.bind('s', lambda event: toggle_visibility('stator'))
        # window.bind('a',       lambda event: anim.toggle_visibility)
        # window.bind('b',       lambda event: anim.toggle_visibility(1))
        # window.bind('c',       lambda event: anim.toggle_visibility(2))
        self.canvas.window.bind('e',       lambda event: toggle_visibility('extra_s', 'esp_front'))
        self.canvas.window.bind('x',       lambda event: toggle_visibility(['extra_s', 'extra_r']))
        self.canvas.window.bind('g',       lambda event: toggle_visibility('extra_r', 'esp_front'))
        self.canvas.window.bind('f',       lambda event: toggle_visibility('extra_s', 'flux'))





    def loop_update(self, t, dt):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        widgets['fps'].config(text=f"fps: {fps:.0f}")

        if self.run:

            # rotor
            self.thr = (self.thr + dt * 0.7) % (2 * pi)
            for part in ['rotor', 'extra_r']:
                for group in self.prims[part]:
                    for prims in self.prims[part][group]:
                        prims.rotate(self.thr)
                        prims.draw()

            self.the = (self.the + dt * 1.8) % (2*pi)
            for p in *self.prims['extra_s']['flux'],:
                # p.rotate(self.the)

                w = sin(self.the)
                p.width = 6*fabs(w)

                tip = assets['quarter_flux']['arrowshape']
                p.arrowshape = (tip[0]*w, tip[1]*w, tip[2]*fabs(w))

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
