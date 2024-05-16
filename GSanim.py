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
from custom_graphics import synchronous_generator_draw, create_circular_pattern, ThreePhaseIndexIterator


class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=0)

        self.widgets = widgets

        # para média móvel da exibição do FPS
        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.time_factor = 140
        self.plot_downsample_factor = 1
        self.run = True

        self.select_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.select_stator_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3), '8': (8, 3)})  # versão do estator com n espiras por fase

        self.ths = 0.0     # angulo mecânico do estador
        self.thr = 0.0     # angulo mecânico do rotor
        self.fs = 0.0
        self.fr = 0.0

        self._fs_inc = 0.0
        self._fr_inc = 0.0


        # para plots
        self.ax_npt = 150
        self.plt_t = deque(maxlen=self.ax_npt)

        self.prims = PrimitivesGroup('root', [])


        synchronous_generator_draw(self.canvas, self.prims, *self.select_stator_turns.current_value)


        print('--------------------------------')
        self.prims.print_tree()
        print('--------------------------------')




        self.prims.draw(consolidate_transforms_to_original=True)
        self.binds()


    def update_fps_info(self, dt:float):
        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

    def refresh(self, _, dt, frame_count):
        dt /= self.time_factor     # time scaled dt for animation
        redraw_plt = frame_count % self.plot_downsample_factor == 0

        if self.run:
            pass


        self.prims.draw()

        if redraw_plt:
            for fig in self.widgets['figs']:
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

    def update_info(self):
        um_name = self.select_unit.current_key
        um_factor = self.select_unit[um_name]
        um_name_g = um_name if um_name != 'rpm' else 'Hz'
        um_factor_g = self.select_unit[um_name_g]
        um_max_len = 0
        for um in self.select_unit:
            um_max_len = max(len(um), um_max_len)

        self.widgets['w_stator']   .config(text=f"  vel. estator: {self.fs*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['w_grid'].config(
            text=f"----------------------------")
        self.widgets['w_rotor']    .config(text=f"    vel. rotor: {self.fr*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['slip'].config(text=f"----------------------------")
        self.widgets['time_factor'].config(text=f"time reduction: {self.time_factor:>5.1f} x")
        self.widgets['frame_delay'].config(text=f"   frame delay: {self.frame_delay:>5} ms")



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
                    self._s_inc = clip(self.fr + increment, v_min, v_max) - self.fr
                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                case 'time_factor':
                    last = self.time_factor
                    self.time_factor = clip(self.time_factor + increment, v_min, v_max)
                    t_max = max(self.plt_t)
                    for k in range(len(self.plt_t)):
                        self.plt_t[k] = (self.plt_t[k] - t_max) * last / self.time_factor + t_max

            self.update_info()


        def reset_time(reset_and_stop=False):
            self._t_init = time.time()
            self._t_start = 0.0
            self.thr = 0.0
            self.ths = 0.0

            if reset_and_stop:
                self.run = False
                self.draw_all()

        def change_display_mu():
            next(self.select_unit)
            self.update_info()

        def change_slots():

            destroy()
            next(self.select_stator_turns)
            create()



        def destroy():
            prims = self.prims
            canvas = self.canvas

            prims['stator']['core']['slots'].delete_descendant_primitives()
            prims['stator']['coil'].delete_descendant_primitives()
            # prims['stator']['coil_front'].delete_descendant_primitives()

            print('\n')
            self.prims.print_tree()

        def create():
            prims = self.prims
            canvas = self.canvas

            coils_per_phase, phases = self.select_stator_turns.current_value

            prims['stator']['core']['slots'] = create_circular_pattern(canvas,['stator_cutout','stator_cutout_outline'],pattern=phases*coils_per_phase)

            prims['stator']['coil'] = []
            prims['stator']['coil']['a'] = create_circular_pattern(canvas, ['stator_esp'],
                                                                   pattern=ThreePhaseIndexIterator(
                                                                       phases * coils_per_phase, 0))
            prims['stator']['coil']['a'].stroke = cl['a']
            prims['stator']['coil']['a'].fill = cl['a']
            prims['stator']['coil']['b'] = create_circular_pattern(canvas, ['stator_esp'],
                                                                   pattern=ThreePhaseIndexIterator(
                                                                       phases * coils_per_phase, 1))
            prims['stator']['coil']['b'].stroke = cl['b']
            prims['stator']['coil']['b'].fill = cl['b']
            prims['stator']['coil']['c'] = create_circular_pattern(canvas, ['stator_esp'],
                                                                   pattern=ThreePhaseIndexIterator(
                                                                       phases * coils_per_phase, 2))
            prims['stator']['coil']['c'].stroke = cl['c']
            prims['stator']['coil']['c'].fill = cl['c']

            print('\n')
            self.prims.print_tree()



        f_max = 70
        self.canvas.window.bind('+', lambda event: inc_value('fs', 1, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('fs', -1, -f_max, f_max))
        self.canvas.window.bind('<Right>', lambda event: inc_value('s', -1, -f_max, f_max))
        self.canvas.window.bind('<Left>',  lambda event: inc_value('s', 1, -f_max, f_max))

        self.canvas.window.bind('.', lambda event: inc_value('time_factor', self.time_factor*.2, 32.45273575943723503208293147346, 1492.992))
        self.canvas.window.bind(',', lambda event: inc_value('time_factor', -self.time_factor*.16666666666666666666666666666667, 32.45273575943723503208293147346, 1492.992))

        self.canvas.window.bind('m', lambda event: change_display_mu() )
        self.canvas.window.bind('*',       lambda event: inc_value('delay', 1, 0, 30))
        self.canvas.window.bind('/',       lambda event: inc_value('delay', -1, 0, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())

        self.canvas.window.bind('<F1>', lambda event: show_binds())
        self.canvas.window.bind('<Escape>', lambda event: reset_time(reset_and_stop=True))
        self.canvas.window.bind('<0>',     lambda event: reset_time())

        self.canvas.window.bind('v', lambda event: change_slots())
        self.canvas.window.bind('d', lambda event: destroy())
        self.canvas.window.bind('c', lambda event: create())




