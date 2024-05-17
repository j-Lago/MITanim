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
from threading import Thread, Event


def plot_thread(event_redraw: Event, figs):
    while True:
        event_redraw.wait(.2)
        for fig in figs:
            # fig.axes.clear()
            fig.canvas.draw()
        event_redraw.clear()

class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=0)

        self._fs_inc = None
        self.plt_lines = None
        self.widgets = widgets

        self._fr_inc = None
        self._fg_inc = None
        self._s_inc = None
        self.fs = None
        self.s = None
        self.fg = None
        self.ths = None
        self.thr = None
        self.thg = None
        self.t = None
        self.time_factor = None
        self.reset_time()

        self.run = True


        # para média móvel da exibição do FPS
        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.plot_downsample_factor = 1

        self.fig1_show = CircularDict({ '': 20, 'I2': 20, 'I1': 20})  #  'atributo': ylim
        self.fig0_show = CircularDict({'V1_abc': 500, 'Ir_xyz': 500, 'I1_abc': 12, 'Im_abc': 1})  # 'atributo': ylim
        self.select_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.select_stator_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3), '8': (8, 3)})  # versão do estator com n espiras por fase
        self.select_rotor_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3)})  # versão do estator com n espiras por fase

        self.mit = MITsim(R1=14.7000 * 0.0,
                          X1=14.9862 * 0.0,
                          R2=10.5445 * 0.7,
                          X2=22.4793 * 1.5,
                          Rc=1.6261e+03,
                          Xm=419.2075,
                          V1nom=380.0,
                          fnom=60.0,
                          p=2,
                          Ns_Nr=80)


        # para plots
        self.ax_npt = 150
        self.plt_t = deque(maxlen=self.ax_npt)
        self.plt_y = (deque(maxlen=self.ax_npt), deque(maxlen=self.ax_npt), deque(maxlen=self.ax_npt))
        self.plot_fig0()
        self.plot_fig1()

        self.prims = PrimitivesGroup('root', [])
        self.create()

        self.prims.draw(consolidate_transforms_to_original=True)

        self.plt_thread_redraw = Event()
        self.plt_thread = Thread(target=plot_thread, args=(self.plt_thread_redraw, self.widgets['figs']), daemon=True)
        self.plt_thread.start()

        self.binds()

    def plot_fig0(self):
        marker_size = 8
        ax = self.widgets['figs'][0].axes[0]
        ax.axhline(0, linestyle='--', color=cl['grid'], linewidth=1)


        self.plt_t.extend(np.linspace(-0.04, 0.00, self.ax_npt))
        self.invalidate_fig0_data(self.time_factor)

        ax.set_ylim(-1.2, 1.2)
        ax.set_xticks([])

        self.plt_lines = {}
        for i, ph in enumerate('abc'):
            self.plt_lines[ph] = (ax.plot(self.plt_t, self.plt_y[i], color=cl[ph], lw=2))[0]
            self.plt_lines[ph+'_marker'] = (ax.plot((0.0,), (0.0,), color=cl[ph], marker='o', markersize=marker_size))[0]


    def plot_fig1(self):
        marker_size = 8
        cursor_lw = 1.5
        nmax = 3800

        ax = self.widgets['figs'][1].axes[0]
        ax.axhline(0, linestyle='--', color=cl['grid'], linewidth=1)
        ax.axvline(0, linestyle='--', color=cl['grid'], linewidth=1)

        wmax = nmax * pi / 30.0
        self.mit.V1 = 1.0 * self.mit.V1nom
        self.mit.f = self.fg
        mit_curves = self.mit.solve_range(-wmax*0.05, wmax, self.ax_npt, ['I1', 'Tind'])
        y1s = abs(mit_curves['I1'])
        y0s = mit_curves['Tind']
        nrs = mit_curves['nr']

        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)
        self.mit.wr = (1.0 - self.s) * self.fg * 2 * pi * 2 / self.mit.p
        self.mit.f = self.fg
        self.mit.solve()

        self.plt_lines['ws_cursor'] = ax.axvline(self.mit.ns, linestyle='-.', color=cl['ws_cursor'], lw=cursor_lw)
        self.plt_lines['wr_cursor'] = ax.axvline(self.mit.nr, linestyle='-.', color=cl['wr_cursor'], lw=cursor_lw)
        self.plt_lines['Tind'] = (ax.plot(nrs, y0s, color=cl['Tind'], lw=2))[0]
        self.plt_lines['Ix'] = (ax.plot(nrs, y1s, color=cl['I1'], lw=2))[0]
        self.plt_lines['Tind_marker'] = (ax.plot(self.mit.nr, self.mit.Tind, color=cl['Tind'], marker='o', markersize=marker_size, lw=2))[0]
        self.plt_lines['Ix_marker'] = (ax.plot(self.mit.nr, self.mit.I1, color=cl['I1'], marker='o', markersize=marker_size, lw=2))[0]
        ax.set_xlim(min(nrs), max(nrs))




    def refresh(self, _, dt, frame_count):
            self.update_fps_info(dt)

            dt /= self.time_factor     # time scaled dt for animation
            redraw_plt = frame_count % self.plot_downsample_factor == 0

            if redraw_plt and self.run:
                self.update_fig1()



            # plot resample
            self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)
            self.mit.wr = (1.0 - self.s) * self.fg * 2 * pi * 2 / self.mit.p
            self.mit.f = self.fg
            self.mit.solve()

            th_er = self.thg - self.thr - pi
            V1_abc = tuple(abs(self.mit.V1) * sin(self.thg - i * 2 * pi / 3) for i in range(3))
            Im_abc = tuple(abs(self.mit.Im) * sin(self.thg + phase(self.mit.Im) - i * 2 * pi / 3) for i in range(3))
            I1_abc = tuple(abs(self.mit.I1) * sin(self.thg + phase(self.mit.I1) - i * 2 * pi / 3) for i in range(3))
            Ir_xyz = tuple(abs(self.mit.I2) * self.mit.Ns_Nr * sin(th_er + phase(self.mit.I2) - i * 2 * pi / 3) for i in range(3))

            mit_t = {'V1_abc': V1_abc, 'Im_abc': Im_abc, 'Ir_xyz': Ir_xyz, 'I1_abc': I1_abc}


            if redraw_plt and self.run:
                self.update_fig0(mit_t)

            self.update_fields(mit_t)

            self.prims['rotor'].rotate(self.thr)
            self.prims['stator'].rotate(self.ths)

            self.prims.draw()




            if self._fs_inc:
                self.fs += self._fs_inc
                self._fs_inc = 0.0

            # previous_fg = self.fg
            if self._fg_inc:
                self.fg += self._fg_inc
                self._fg_inc = 0.0

            if self._s_inc:
                self.s += self._s_inc
                self._s_inc = 0.0


            
            

                
            # if previous_fg * self.fg < 0:  # inversão campo girante
            #     self.s = - self.s


            if self.run:
                self.ths = (self.ths + dt * self.fs * 2 * pi) % (2 * pi)
                self.thr = (self.thr + dt * (1.0-self.s) * self.fg * 2 * pi) % (2 * pi)
                self.thg = (self.thg + dt * self.fg * 2 * pi) % (2 * pi)
                self.t += dt

            if redraw_plt:
                self.plt_thread_redraw.set()
                for fig in self.widgets['figs']:
                    fig.canvas.flush_events()

            self.update_info()
    # ------------------------------- end of refresh -------------------------------------

    def update_fields(self, mit_t):
        for i, ph in enumerate('abc'):
            self.prims['stator']['field']['vec'][ph].scale(mit_t['Im_abc'][i])

        self.prims['stator']['field']['vec']['s'][0].from_complex(self.prims['stator']['field']['vec']['a'][0].to_complex() +
                                                                  self.prims['stator']['field']['vec']['b'][0].to_complex() +
                                                                  self.prims['stator']['field']['vec']['c'][0].to_complex())

        for i, ph in enumerate('xyz'):
            self.prims['rotor']['field']['vec'][ph].scale(mit_t['Ir_xyz'][i] / self.mit.Ns_Nr * 0.5)

        self.prims['rotor']['field']['vec']['r'][0].from_complex(self.prims['rotor']['field']['vec']['x'][0].to_complex() +
                                                                 self.prims['rotor']['field']['vec']['y'][0].to_complex() +
                                                                 self.prims['rotor']['field']['vec']['z'][0].to_complex())


    def update_fig0(self, mit_t):
        ax = self.widgets['figs'][0].axes[0]
        Y_show = mit_t[self.fig0_show.current_key]

        self.plt_t.append(self.t)
        for i, ph in enumerate(self.fig0_show.current_key[3:6]):
            self.plt_y[i].append(Y_show[i])    #amp * sin(self.thg + phi + alpha * i))
            self.plt_lines[('abc')[i]].set_ydata(self.plt_y[i])
            self.plt_lines[('abc')[i]].set_xdata(self.plt_t)
            self.plt_lines[('abc')[i] + '_marker'].set_ydata((self.plt_y[i][-1],))
            self.plt_lines[('abc')[i] + '_marker'].set_xdata((self.plt_t[-1],))
            self.plt_lines[('abc')[i]].set_color(cl[ph])
            self.plt_lines[('abc')[i] + '_marker'].set_color(cl[ph])
        pad = 0.1 / self.time_factor
        t_max = max(self.plt_t)
        t_min = min(self.plt_t)
        y_max = self.fig0_show.current_value
        ax.set_xlim(t_min + pad, t_max + pad)
        ax.set_ylim(-y_max, y_max)
        ax.set_ylabel(self.fig0_show.current_key)



    def update_fig1(self):
        ax = self.widgets['figs'][1].axes[0]
        
        lim_max = 4200.0
        lim_min = 200.0

        nmax = lim_max
        nmin = -lim_min

        if self.fg < 0:
            nmax = lim_min
            nmin = -lim_max
        if self.s > 1:
            dx = self.mit.nr
            nmax += dx
            nmin += dx
        if self.s <= 0 and self.fg > 0:
            dx = self.mit.nr -lim_max +lim_min
            nmax = max(nmax+dx, nmax)
            nmin = max(nmin+dx, nmin)
        if self.s < 0 and self.fg < 0:
            dx = self.mit.nr + lim_max -lim_min
            nmax = min(nmax + dx, nmax)
            nmin = min(nmin + dx, nmin)

        wmax = nmax * pi / 30.0
        wmin = nmin * pi / 30.0

        self.mit.wr = (1.0 - self.s) * self.fg * 2 * pi * 2 / self.mit.p
        self.mit.f = self.fg
        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)

        mit_curves = self.mit.solve_range(wmin, wmax, self.ax_npt, [self.fig1_show.current_key, 'Tind'])
        ixs = abs(mit_curves[self.fig1_show.current_key])
        tinds = mit_curves['Tind']
        nrs = mit_curves['nr']

        self.mit.wr = (1.0 - self.s) * self.fg * 2 * pi * 2 / self.mit.p
        self.mit.f = self.fg
        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)
        self.mit.solve()

        self.plt_lines['ws_cursor'].set_xdata((self.mit.ns, ))
        self.plt_lines['wr_cursor'].set_xdata((self.mit.nr, ))
        self.plt_lines['Tind'].set_ydata(tinds)
        self.plt_lines['Tind'].set_xdata(nrs)
        self.plt_lines['Ix'].set_ydata(ixs)
        self.plt_lines['Ix'].set_xdata(nrs)
        self.plt_lines['Tind_marker'].set_ydata((self.mit.Tind,))
        self.plt_lines['Tind_marker'].set_xdata((self.mit.nr,))
        self.plt_lines['Ix_marker'].set_ydata((abs(self.mit[self.fig1_show.current_key]), ))
        self.plt_lines['Ix_marker'].set_xdata((self.mit.nr,))
        ax.set_xlim(min(nrs), max(nrs))

        ypad = 1.1
        ymax = self.fig1_show.current_value       #np.max(tinds) * ypad
        ymin = -self.fig1_show.current_value       #np.min(tinds) * ypad

        # ymax = np.max(tinds) * ypad
        # ymin = np.min(tinds) * ypad

        sat = 0.12
        if self.s < 0:
            sat = 1.0

        if self.fg > 0:
            ymin = -sat*ymax

        # if self.fg < 0:
        #     ymax = -sat*ymin

        ax.set_ylim(ymin, ymax)
        ax.set_ylabel('Tind' + ((', ' + self.fig1_show.current_key) if self.fig1_show.current_key else '') )




    def update_fps_info(self, dt:float):
        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

    def destroy(self):

        del self.prims['stator']
        del self.prims['rotor']
        self.canvas.delete('all')

        # print('\n')
        # self.prims.print_tree()

    def create(self):
        synchronous_generator_draw(self.canvas, self.prims, self.select_stator_turns.current_value[0], self.select_rotor_turns.current_value[0])
        # print('\n')
        # self.prims.print_tree()


    def update_info(self):
        um_name = self.select_unit.current_key
        um_factor = self.select_unit[um_name]
        um_name_g = um_name if um_name != 'rpm' else 'Hz'
        um_factor_g = self.select_unit[um_name_g]
        um_max_len = 0
        for um in self.select_unit:
            um_max_len = max(len(um), um_max_len)

        self.widgets['w_stator'].config(text=f"  vel. estator: {self.fs * um_factor  :>5.1f} {um_name}{' ' * (um_max_len - len(um_name))}")
        self.widgets['w_grid'].config(
            text=f"    vel. alim.: {self.fg * um_factor_g:>5.1f} {um_name_g}{' ' * (um_max_len - len(um_name_g))}")
        self.widgets['w_rotor'].config(text=f"    vel. rotor: {(1.0-self.s)*self.fg * um_factor  :>5.1f} {um_name}{' ' * (um_max_len - len(um_name))}")
        self.widgets['slip'].config(text=f"         slip: {self.mit.s  :>6.2f} pu{' ' * um_max_len}")
        self.widgets['time_factor'].config(text=f"time reduction: {self.time_factor:>5.1f} x")
        self.widgets['frame_delay'].config(text=f"   frame delay: {self.frame_delay:>5} ms")

    def reset_time(self, reset_and_stop=False):
        if self.t is not None:
            self.invalidate_fig0_data()

        self._t_init = time.time()
        self.time_factor = 140
        self._t_start = 0.0
        self.thg = 0.0
        self.thr = 0.0
        self.ths = 0.0
        self.t = 0.0
        self.s = 0.05
        self.fs = 0.0
        self.fg = 60.0
        self._fs_inc = 0.0
        self._fg_inc = 0.0
        self._s_inc = 0.0

        if reset_and_stop:
            self.run = False
            # self.draw_all()

    def invalidate_fig0_data(self, previous_time_factor=None):

        if not previous_time_factor:
            previous_time_factor = self.time_factor

        t_max = max(self.plt_t)
        for k in range(len(self.plt_t)):
            self.plt_t[k] = (self.plt_t[k] - t_max) * previous_time_factor / self.time_factor + t_max

        nans = np.empty(self.ax_npt, float)
        nans.fill(np.nan)
        for arr in (self.plt_y):
            arr.extend(nans)



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
                case 's':
                    if self.fg < 0:
                        increment = - increment
                    self._s_inc = clip(self.s + increment, v_min, v_max) - self.s
                case 'fg':
                    self._fg_inc = clip(self.fg + increment, v_min, v_max) - self.fg
                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                case 'time_factor':
                    last = self.time_factor
                    self.time_factor = clip(self.time_factor + increment, v_min, v_max)
                    self.invalidate_fig0_data(last)

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


        def choose_fig0_show():
            next(self.fig0_show)
            self.invalidate_fig0_data()

        def choose_fig1_show():
            next(self.fig1_show)

        dw_inc = 0.89   #0.83333333333333333333333333
        f_max = 70
        self.canvas.window.bind('+', lambda event: inc_value('fs', 1, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('fs', -1, -f_max, f_max))
        self.canvas.window.bind('<Right>', lambda event: inc_value('s', -0.01, -0.2, 2.2))
        self.canvas.window.bind('<Left>', lambda event: inc_value('s', 0.01, -0.2, 2.2))
        self.canvas.window.bind('<Up>', lambda event: inc_value('fg', dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Down>', lambda event: inc_value('fg', -dw_inc, -f_max, f_max))

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
        self.widgets['canvas_fig0'].get_tk_widget().bind('<Button-1>', lambda event: choose_fig0_show())
        self.widgets['canvas_fig1'].get_tk_widget().bind('<Button-1>', lambda event: choose_fig1_show())