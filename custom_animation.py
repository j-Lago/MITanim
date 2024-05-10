import tkinter as tk
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas
from primitive import Primitive
from transforms import translate, rotate, scale, rgb_to_hex, clip
import time
from assets import assets, cl
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal

class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=1)

        self.widgets = widgets

        self.ths = 0.0
        self.thr = 0.0
        self.the = 0.0
        self.w_stator = 0.0
        self.w_rotor = 0.7
        self.w_grid = 1.2

        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.widgets['w_stator'].config(text=f"velocidade estator (unbinded): {self.w_stator:1.1f}")
        self.widgets['w_rotor'].config(text=f"velocidade rotor (left/right): {self.w_rotor:1.1f}")
        self.widgets['w_grid'].config(text=f"velocidade campo girante (up/down): {self.w_grid:1.1f}")
        self.widgets['frame_delay'].config(text=f"frame delay (-/+): {self.frame_delay}")

        self.run = True


        self.prims = {'stator': {},
                      'rotor': {},
                      'extra_s': {},
                      'extra_r': {},
                      }


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
            *(self.create_primitive(**assets['stator_axis']).rotate(2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['stator']['axis']):
            p.stroke = cl[('a', 'b', 'c')[i % 3]]

        self.prims['rotor']['axis'] = [
            *(self.create_primitive(**assets['rotor_axis']).rotate(2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['rotor']['axis']):
            p.stroke = cl[('x', 'y', 'z')[i % 3]]

        th = pi
        self.prims['extra_s']['flux_a'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
        ]

        th = 2 * pi / 3 + pi
        self.prims['extra_s']['flux_b'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
        ]
        for p in self.prims['extra_s']['flux_b']: p.stroke = cl['b']

        th = -2 * pi / 3 + pi
        self.prims['extra_s']['flux_c'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
        ]
        for p in self.prims['extra_s']['flux_c']: p.stroke = cl['c']

        th = pi
        self.prims['extra_s']['flux_s'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(th),
        ]
        for p in self.prims['extra_s']['flux_s']: p.stroke = cl['flux_s']

        self.prims['stator']['esp'] = [
            *(self.create_primitive(**assets['stator_esp']).rotate(-2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.prims['stator']['esp']):
            p.fill = cl[('a', 'b', 'c')[i % 3]]

        self.prims['rotor']['esp'] = [
            *(self.create_primitive(**assets['rotor_esp']).rotate(-2 * pi / 6 * i) for i in range(6)),
        ]
        for i, p in enumerate(self.prims['rotor']['esp']):
            p.fill = cl[('x', 'y', 'z')[i % 3]]

        self.prims['extra_r']['esp_front'] = [
            *(self.create_primitive(**assets['rotor_esp_front']).rotate(2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['extra_r']['esp_front']):
            p.fill = cl[('x', 'y', 'z')[i % 3]]

        self.prims['extra_s']['esp_front'] = [
            *(self.create_primitive(**assets['stator_esp_front']).rotate(2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['extra_s']['esp_front']):
            p.fill = cl[('a', 'b', 'c')[i % 3]]

        self.draw_all(consolidate_transforms_to_original=True)


    def draw_all(self, *args, **kwargs):
        for part in self.prims:
            for group in self.prims[part]:
                for prim in self.prims[part][group]:
                    prim.draw( *args, **kwargs)

    def binds(self) -> None:

        def toggle_run():
            self.run = not self.run

        def change_speed(var_name: Literal['ws', 'wr', 'we'],  increment: float,  v_min= -9.9, v_max= 9.9):
            match var_name:
                case 'ws':
                    self.w_stator = clip(self.w_stator + increment, v_min, v_max)
                    self.widgets['w_stator'].config(text=f"velocidade estator: {self.w_stator:1.1f}")
                case 'wr':
                    self.w_rotor = clip(self.w_rotor + increment, v_min, v_max)
                    self.widgets['w_rotor'].config(text=f"velocidade rotor: {self.w_rotor:1.1f}")
                case 'we':
                    self.w_grid = clip(self.w_grid + increment, v_min, v_max)
                    self.widgets['w_grid'].config(text=f"velocidade campo girante: {self.w_grid:1.1f}")
                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                    self.widgets['frame_delay'].config(text=f"frame delay: {self.frame_delay}")

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

        def reset_time(reset_and_stop=False):
            self._t_init = time.time()
            self._t_start = 0.0
            self.the = 0.0
            self.thr = 0.0
            self.ths = 0.0

            if reset_and_stop:
                self.run = False
                self.draw_all()

        dw_inc = 0.1
        self.canvas.window.bind('+', lambda event: change_speed('ws', dw_inc))
        self.canvas.window.bind('-', lambda event: change_speed('ws', -dw_inc))
        self.canvas.window.bind('<Right>', lambda event: change_speed('wr', dw_inc))
        self.canvas.window.bind('<Left>',  lambda event: change_speed('wr', -dw_inc))
        self.canvas.window.bind('<Up>',    lambda event: change_speed('we', dw_inc))
        self.canvas.window.bind('<Down>',  lambda event: change_speed('we', -dw_inc))
        self.canvas.window.bind('*',       lambda event: change_speed('delay', 1, 1, 30))
        self.canvas.window.bind('/',       lambda event: change_speed('delay', -1, 1, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())
        # self.canvas.window.bind('<Return>', lambda event: toggle_run())
        self.canvas.window.bind('<Escape>', lambda event: reset_time(reset_and_stop=True))
        self.canvas.window.bind('<0>',     lambda event: reset_time())
        self.canvas.window.bind('r',       lambda event: toggle_visibility('rotor'))
        self.canvas.window.bind('s',       lambda event: toggle_visibility('stator'))
        self.canvas.window.bind('f',       lambda event: toggle_visibility('extra_s', 'flux_s'))
        self.canvas.window.bind('a',       lambda event: toggle_visibility('extra_s', 'flux_a'))
        self.canvas.window.bind('b',       lambda event: toggle_visibility('extra_s', 'flux_b'))
        self.canvas.window.bind('c',       lambda event: toggle_visibility('extra_s', 'flux_c'))
        self.canvas.window.bind('e',       lambda event: toggle_visibility('extra_s', 'esp_front'))
        self.canvas.window.bind('x',       lambda event: toggle_visibility(['extra_s', 'extra_r']))
        self.canvas.window.bind('g',       lambda event: toggle_visibility('extra_r', 'esp_front'))

    def loop_update(self, t, dt):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

        if self.run:

            # stator
            self.ths = (self.ths + dt * self.w_stator) % (2 * pi)
            for part in ['stator', 'extra_s']:
                for group in self.prims[part]:
                    for prims in self.prims[part][group]:
                        prims.rotate(self.ths)

            # rotor
            self.thr = (self.thr + dt * self.w_rotor) % (2 * pi)
            for part in ['rotor', 'extra_r']:
                for group in self.prims[part]:
                    for prims in self.prims[part][group]:
                        prims.rotate(self.thr)

            tip = assets['quarter_flux']['arrowshape']
            self.the = (self.the + dt * self.w_grid) % (2 * pi)
            # fase a
            th = self.the
            if self.prims['extra_s']['flux_a'][0].visible:
                for p in *self.prims['extra_s']['flux_a'],:
                    s = sin(th)
                    p.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
                    p.width = 6 * fabs(s)

            # fase b
            if self.prims['extra_s']['flux_b'][0].visible:
                th = self.the - 2 * pi / 3
                for p in *self.prims['extra_s']['flux_b'],:
                    s = sin(th)
                    p.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
                    p.width = 6 * fabs(s)

            # fase c
            if self.prims['extra_s']['flux_c'][0].visible:
                th = self.the + 2 * pi / 3
                for p in *self.prims['extra_s']['flux_c'],:
                    s = sin(th)
                    p.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
                    p.width = 6 * fabs(s)

                    # fase c
            if self.prims['extra_s']['flux_s'][0].visible:
                th = self.the - pi / 2
                for p in *self.prims['extra_s']['flux_s'],:
                    p.rotate(th)

            self.draw_all()

