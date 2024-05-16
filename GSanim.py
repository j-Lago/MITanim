import tkinter as tk
from cmath import polar, rect, phase
import numpy as np
from tkinter import messagebox
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas, BoolVar
from primitive import Primitive, PrimitivesGroup
from transformations import translate, rotate, scale, reverse, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip, CircularDict
import time
from assets import assets, cl, binds_message
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal
from MITsim import MITsim
from gvec import GraphicVec2
import matplotlib.pyplot as plt
from custom_graphics import synchronous_generator_draw, circular_pattern, IndexFilter3ph, create_stator


class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=0)

        self.widgets = widgets

        self._fr_inc = None
        self._fs_inc = None
        self.fs = None
        self.fr = None
        self.thr = None
        self.ths = None
        self.time_factor = None
        self.reset_time()

        self.run = True




        # para média móvel da exibição do FPS
        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.plot_downsample_factor = 3

        self.select_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.select_stator_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3), '8': (8, 3)})  # versão do estator com n espiras por fase
        self.select_rotor_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3)})  # versão do estator com n espiras por fase




        # para plots
        self.ax_npt = 150
        self.plt_t = deque(maxlen=self.ax_npt)

        self.prims = PrimitivesGroup('root', [])
        self.create()

        self.prims.draw(consolidate_transforms_to_original=True)
        self.binds()

    def refresh(self, _, dt, frame_count):
        self.update_fps_info(dt)

        dt /= self.time_factor     # time scaled dt for animation
        redraw_plt = frame_count % self.plot_downsample_factor == 0


        self.prims['rotor'].rotate(self.thr)
        self.prims['stator'].rotate(self.ths)


        self.prims.draw()


        for fig in self.widgets['figs']:
            if redraw_plt:
                fig.canvas.draw()
            fig.canvas.flush_events()

        if self._fs_inc:
            self.fs += self._fs_inc
            self._fs_inc = 0.0

        if self._fr_inc:
            self.fr += self._fr_inc
            self._fr_inc = 0.0

        if self.run:
            self.ths = (self.ths + dt * self.fs * 2 * pi) % (2 * pi)
            self.thr = (self.thr + dt * self.fr * 2 * pi) % (2 * pi)

        self.update_info()

    # ------------------------------- end of refresh -------------------------------------

    def update_fps_info(self, dt:float):
        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

    def destroy(self):

        del self.prims['stator']
        del self.prims['rotor']
        self.canvas.delete('all')

        print('\n')
        self.prims.print_tree()

    def create(self):
        synchronous_generator_draw(self.canvas, self.prims, self.select_stator_turns.current_value[0], self.select_rotor_turns.current_value[0])
        print('\n')
        self.prims.print_tree()


    def update_info(self):
        um_name = self.select_unit.current_key
        um_factor = self.select_unit[um_name]

        um_max_len = 0
        for um in self.select_unit:
            um_max_len = max(len(um), um_max_len)

        self.widgets['w_stator']   .config(text=f"  vel. estator: {self.fs*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['w_grid'].config(text=f"----------------------------")
        self.widgets['w_rotor']    .config(text=f"    vel. rotor: {self.fr*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['slip'].config(text=f"----------------------------")
        self.widgets['time_factor'].config(text=f"time reduction: {self.time_factor:>5.1f} x")
        self.widgets['frame_delay'].config(text=f"   frame delay: {self.frame_delay:>5} ms")

    def reset_time(self, reset_and_stop=False):
        self._t_init = time.time()
        self.time_factor = 140
        self._t_start = 0.0
        self.thr = 0.0
        self.ths = 0.0
        self.fr = 57.0
        self.fs = 0.0
        self._fs_inc = 0.0
        self._fr_inc = 0.0

        if reset_and_stop:
            self.run = False
            # self.draw_all()



    def binds(self) -> None:

        def show_binds():
            current_state = self.run
            self.run = False
            messagebox.showinfo("binds", binds_message)
            self.run = current_state

        def toggle_run():
            self.run = not self.run

        def inc_value(var_name: Literal['fs', 'fr', 'delay', 'time_factor'],
                      increment: int | float,
                      v_min: int | float,
                      v_max: int | float):

            match var_name:
                case 'fs':
                    self._fs_inc = clip(self.fs + increment, v_min, v_max) - self.fs
                case 'fr':
                    self._fr_inc = clip(self.fr + increment, v_min, v_max) - self.fr
                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                case 'time_factor':
                    last = self.time_factor
                    self.time_factor = clip(self.time_factor + increment, v_min, v_max)
                    t_max = max(self.plt_t)
                    for k in range(len(self.plt_t)):
                        self.plt_t[k] = (self.plt_t[k] - t_max) * last / self.time_factor + t_max

            self.update_info()


        def change_display_mu():
            next(self.select_unit)
            self.update_info()

        def change_slots(parts: Literal['rotor', 'stator']):
            if isinstance(parts, str):
                parts = [parts]

            self.destroy()
            if 'rotor' in parts: next(self.select_rotor_turns)
            if 'stator' in parts: next(self.select_stator_turns)
            self.create()



        f_max = 70
        self.canvas.window.bind('+', lambda event: inc_value('fs', 1, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('fs', -1, -f_max, f_max))
        self.canvas.window.bind('<Right>', lambda event: inc_value('fr', -1, -f_max, f_max))
        self.canvas.window.bind('<Left>',  lambda event: inc_value('fr', 1, -f_max, f_max))

        self.canvas.window.bind('.', lambda event: inc_value('time_factor', self.time_factor*.2, 32.45273575943723503208293147346, 1492.992))
        self.canvas.window.bind(',', lambda event: inc_value('time_factor', -self.time_factor*.16666666666666666666666666666667, 32.45273575943723503208293147346, 1492.992))

        self.canvas.window.bind('u', lambda event: change_display_mu() )
        self.canvas.window.bind('*',       lambda event: inc_value('delay', 1, 0, 30))
        self.canvas.window.bind('/',       lambda event: inc_value('delay', -1, 0, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())

        self.canvas.window.bind('<F1>', lambda event: show_binds())
        self.canvas.window.bind('<Escape>', lambda event: self.reset_time(reset_and_stop=True))
        self.canvas.window.bind('<0>',     lambda event: self.reset_time())

        self.canvas.window.bind('m', lambda event: change_slots('stator'))
        self.canvas.window.bind('n', lambda event: change_slots('rotor'))
        # self.canvas.window.bind('d', lambda event: self.destroy())
        # self.canvas.window.bind('c', lambda event: self.create())




