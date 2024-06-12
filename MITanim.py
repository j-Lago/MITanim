import tkinter as tk
from tkinter import DISABLED, NORMAL
from cmath import polar, rect, phase
import numpy as np
from tkinter import messagebox
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas, BoolVar
from primitive import Primitive, PrimitivesGroup, collision_circle_point
from transformations import norm_coords, denorm_coords, translate, rotate, scale, reverse, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip, CircularDict, hex_bezier, scale_rgb, denorm_coords
import time
from assets import assets, cl, binds_message, contrast_color_scale
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal
from MITsim import MITsim
from gvec import GraphicVec2
import matplotlib.pyplot as plt
from matplotlib import font_manager
from custom_graphics import mit_draw, circular_pattern, IndexFilter3ph, create_stator
from threading import Thread, Event
from functools import partial

def plot_thread(event_redraw: Event, figs):
    while True:
        event_redraw.wait()
        for fig in figs:
            fig.axes.clear()
            fig.canvas.draw()
        event_redraw.clear()

# def plot_thread_fig0(event_redraw: Event, fig):
#     while True:
#         event_redraw.wait(.2)
#         fig.canvas.draw()
#         event_redraw.clear()
#
# def plot_thread_fig1(event_redraw: Event, fig):
#     while True:
#         event_redraw.wait(.2)
#         fig.canvas.draw()
#         event_redraw.clear()

class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict = None):
        super().__init__(canvas, frame_delay=0)

        self.th_sync = None
        self._f_ref_inc = None
        self.plt_lines = None
        self.widgets = widgets

        self._fr_inc = None
        self._fg_inc = None
        self._s_inc = None
        self.f_sync = None
        self.f_ref = None
        self.f_rot = None
        self.th_ref = None
        self.th_rot = None
        self.th_grid = None
        self.t = None
        self.time_factor = None
        self.inertia = None
        self.reset_time()

        self.run = True

        self.en_sim_inertia = BoolVar(False)
        self.en_stator_field_lines = BoolVar(False)
        self.en_stator_field_vec = BoolVar(True)
        self.en_rotor_field_lines = BoolVar(False)
        self.en_rotor_field_vec = BoolVar(True)

        self.en_stator_coil_front = BoolVar(False)
        self.en_rotor_coil_front = BoolVar(False)

        self.sel_ref = tk.StringVar(value='stator')



        # para média móvel da exibição do FPS
        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.plot_downsample_factor = 3

        self.sel_dynamic_color = CircularDict({'3phase': False, 'amplitude': True})
        self.sel_dynamic_color.key = '3phase'

        # self.sel_ref = CircularDict({'stator': 0, 'rotor': 1, 'field': 2})
        self.sel_mount = CircularDict({'normal': True, 'hidden': False})
        # self.select_part = CircularDict({'all': 0, 'stator': 1, 'rotor': 2})
        self.sel_stator_field = CircularDict({'abc': 0, 'abcs': 1, 'a': 2, 'b': 3, 'c': 4, 's': 5})
        self.sel_stator_field.key = 's'

        self.sel_rotor_field = CircularDict({'xyz': 0, 'xyzr': 1, 'x': 2, 'y': 3, 'z': 4, 'r': 5})
        self.sel_rotor_field.key = 'r'

        self.sel_fig1 = CircularDict({'nan': 20, 'I2': 20, 'I1': 20, 'Tres': 20})  #  'atributo': ylim
        self.sel_fig1.key = 'Tres'

        self.sel_fig0 = CircularDict({'V1_abc': 500,
                                      'Ir_xyz': 500,
                                      'I1_abc': 12,
                                      'Im_abc': 1,
                                      })  # 'atributo': ylim



        self.sel_stator_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3), '8': (8, 3)})  # versão do estator com n espiras por fase
        self.sel_rotor_turns = CircularDict({'simp': (2, 3), '4': (4, 3), '6': (6, 3)})  # versão do estator com n espiras por fase
        self.sel_coil_opacity = CircularDict({'gray75': 1, 'gray50': 2, 'gray25': 3})  # value não utilizado
        # self.sel_power_unit = CircularDict({'kW': 0.001, 'hp': 0.00134102, 'cv': 0.00135962})  # 'um': fator de conversão
        # self.sel_speed_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.sel_fs_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.sel_fr_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.sel_fg_unit = CircularDict({'Hz': 1.0, 'rad/s': 2 * pi, 'rpm': 60})  # 'um': fator de conversão
        self.sel_Pconv_unit = CircularDict({'kW': 0.001, 'hp': 0.00134102, 'cv': 0.00135962})  # 'um': fator de conversão


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
        self.ax_npt_fig0 = 100
        self.ax_npt_fig1 = 100
        self.plt_t = deque(maxlen=self.ax_npt_fig0)
        self.plt_y = (deque(maxlen=self.ax_npt_fig0), deque(maxlen=self.ax_npt_fig0), deque(maxlen=self.ax_npt_fig0))
        # plt.rcParams['font.family'] = 'sans-serif'
        # plt.rcParams['font.sans-serif'] = 'corbel'

        self.plot_fig0()
        self.plot_fig1()

        self.prims = PrimitivesGroup('root', [])
        self.create()




        self.binds()

        self.thread_figs_redraw = Event()
        self.thread_figs = Thread(target=plot_thread, args=(self.thread_figs_redraw, self.widgets['figs']), daemon=True)
        self.thread_figs.start()
        # self.thread_fig0_redraw = Event()
        # self.thread_fig0 = Thread(target=plot_thread_fig0, args=(self.thread_fig0_redraw, self.widgets['figs'][0]), daemon=True)
        # self.thread_fig1_redraw = Event()
        # self.thread_fig1 = Thread(target=plot_thread_fig1, args=(self.thread_fig1_redraw, self.widgets['figs'][1]), daemon=True)
        # self.thread_fig0.start()
        # self.thread_fig1.start()




    def plot_fig0(self):
        marker_size = 8
        ax = self.widgets['figs'][0].axes[0]
        ax.axhline(0, linestyle='--', color=cl['grid'], linewidth=1)


        self.plt_t.extend(np.linspace(-0.04, 0.00, self.ax_npt_fig0))
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

        self.plt_lines['ws_cursor'] = ax.axvline(0, linestyle='-.', color=cl['ws_cursor'], lw=cursor_lw)
        self.plt_lines['wr_cursor'] = ax.axvline(0, linestyle='-.', color=cl['wr_cursor'], lw=cursor_lw)
        self.plt_lines['Tind'] = (ax.plot(0, 0, color=cl['Tind'], lw=2))[0]
        self.plt_lines['Ix'] = (ax.plot(0, 0, color=cl['I1'], lw=2))[0]
        self.plt_lines['Tind_marker'] = (ax.plot(0, 0, color=cl['Tind'], marker='o', markersize=marker_size, lw=2))[0]
        self.plt_lines['Ix_marker'] = (ax.plot(0,0, color=cl['I1'], marker='o', markersize=marker_size, lw=2))[0]





    def refresh(self, _, dt, frame_count):
        self.update_fps_info(dt)
        redraw_plt = frame_count % self.plot_downsample_factor == 0

        dt /= self.time_factor     # time scaled dt for animation

        if redraw_plt and self.run:
            self.update_fig1()

        # plot resample
        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)
        self.mit.wr = (self.f_rot - self.f_ref) * 2 * pi * 2 / self.mit.p
        self.mit.f = self.f_grid
        self.mit.solve()

        th_er = self.th_sync - self.th_rot - pi
        alpha = 2 * pi / 3
        V1_abc = tuple(abs(self.mit.V1) * sin(self.th_grid - i * alpha) for i in range(3))
        Im_abc = tuple(abs(self.mit.Im) * sin(self.th_grid + phase(self.mit.Im) - i * alpha) for i in range(3))
        I1_abc = tuple(abs(self.mit.I1) * sin(self.th_grid + phase(self.mit.I1) - i * alpha) for i in range(3))
        Ir_xyz = tuple(abs(self.mit.I2) * self.mit.Ns_Nr * sin(th_er + phase(self.mit.I2) - i * alpha) for i in range(3))

        mit_t = {'V1_abc': V1_abc, 'Im_abc': Im_abc, 'Ir_xyz': Ir_xyz, 'I1_abc': I1_abc}


        if redraw_plt and self.run:
            self.update_fig0(mit_t)

        self.update_fields(mit_t)

        self.prims['rotor'].rotate(self.th_rot)
        self.prims['stator'].rotate(self.th_ref)

        self.prims['stator']['core']['mount'].visible = self.sel_mount.value and self.prims['stator']['core']['mount'].parent_visible
        # self.prims['rotor'].visible = self.select_part.key in ('rotor', 'all')
        # self.prims['stator'].visible = self.select_part.key in ('stator', 'all')

        if self.sel_dynamic_color.value:
            self.prims['stator']['coil_front'].visible = False
            self.prims['rotor']['coil_front'].visible = False
            self.color_stator_coils(I1_abc)
            self.color_rotor_coils(Ir_xyz)
        else:
            self.prims['stator']['coil_front'].visible = self.en_stator_coil_front and self.prims['stator'].visible
            self.prims['rotor']['coil_front'].visible = self.en_rotor_coil_front and self.prims['rotor'].visible


        self.prims.draw()
        if redraw_plt:
            if not self.thread_figs_redraw.is_set():
                self.thread_figs_redraw.set()
            for fig in self.widgets['figs']:
                fig.canvas.flush_events()

        self.process_inc()
        self.process_inertia(dt)
        th_ref_inc = 0.0
        match self.sel_ref.get():
            case 'free':
                pass
            case 'stator':
                self._f_ref_inc -= self.f_ref
                th_ref_inc = -self.th_ref
            case 'rotor':
                self._f_ref_inc -= self.f_rot
                th_ref_inc = -self.th_rot
            case 'field':
                self._f_ref_inc -= self.f_sync
                th_ref_inc = -self.th_sync
            case _:
                raise ValueError('assert')
        self.process_inc()


        if self.run:
            self.th_ref = (self.th_ref + dt * self.f_ref * 2 * pi) % (2 * pi) + th_ref_inc
            self.th_rot = (self.th_rot + dt * self.f_rot * 2 * pi) % (2 * pi) + th_ref_inc
            self.th_grid = (self.th_grid + dt * self.f_grid * 2 * pi) % (2 * pi)
            self.th_sync = self.th_grid + self.th_ref
            self.t += dt

        self.update_info()

    def process_inertia(self, dt):
        if self.en_sim_inertia:
            DT = (self.mit.Tind - self.mit.Tres)
            self.f_rot += DT * dt / self.inertia
            self._s_inc = 0.0
        else:
            dfr = self._s_inc * self.f_grid
            self.f_rot += dfr
            self._s_inc = 0.0

    def process_inc(self):
        if self.run:
            s = self.s
            self.f_grid += self._fg_inc
            self.f_rot = (1.0 - s) * self.f_grid + self.f_ref
            self._fg_inc = 0.0

            self.f_ref += self._f_ref_inc
            self.f_sync += self._f_ref_inc
            self.f_rot += self._f_ref_inc
            self._f_ref_inc = 0.0

    # ------------------------------- end of refresh -------------------------------------

    def color_stator_coils(self, I1_abc):
        if self.sel_dynamic_color.value:
            for i, ph in enumerate('abc'):
                amp = clip(I1_abc[i] * 0.33, -1.0, 1.0)
                tp = fabs(amp)
                tn = fabs(-amp)
                clp = hex_bezier('#ff6600', '#aaffaa', '#0066ff', amp * 0.5 + 0.5)
                cln = hex_bezier('#ff6600', '#aaffaa', '#0066ff', -amp * 0.5 + 0.5)

                if amp < 0:
                    clp, cln = cln, clp
                    tp, tn = tn, tp

                self.prims['stator']['coil']['in'][ph].fill = clp
                self.prims['stator']['coil']['in'][ph].stroke = clp
                self.prims['stator']['coil']['out'][ph].fill = cln
                self.prims['stator']['coil']['out'][ph].stroke = cln

                self.prims['stator']['current']['in'][ph].stroke = scale_rgb(clp, contrast_color_scale)
                self.prims['stator']['current']['in'][ph].fill = scale_rgb(clp, contrast_color_scale)
                self.prims['stator']['current']['out'][ph].stroke = scale_rgb(cln, contrast_color_scale)
                self.prims['stator']['current']['out'][ph].fill = scale_rgb(cln, contrast_color_scale)

                for j, _ in enumerate(self.prims['stator']['current']['in'][ph]):
                    self.prims['stator']['current']['in'][ph][j].scale(tp, center=self.prims['stator']['current']['in'][ph][j].anchor)
                    self.prims['stator']['current']['out'][ph][j].scale(tn, center=self.prims['stator']['current']['out'][ph][j].anchor)

                if amp < 0:
                    self.prims['stator']['current']['in'][ph].rotate(pi)
                    self.prims['stator']['current']['out'][ph].rotate(pi)
                    self.prims['stator']['coil']['in'][ph].rotate(pi)
                    self.prims['stator']['coil']['out'][ph].rotate(pi)


    def color_rotor_coils(self, Ir_xyz):
        for i, ph in enumerate('xyz'):
            amp = clip(Ir_xyz[i] / self.mit.Ns_Nr * 0.33, -1.0, 1.0)
            tp = fabs(amp)
            tn = fabs(-amp)
            clp = hex_bezier('#ff6600', '#aaffaa', '#0066ff', amp * 0.5 + 0.5)
            cln = hex_bezier('#ff6600', '#aaffaa', '#0066ff', -amp * 0.5 + 0.5)

            if amp < 0:
                clp, cln = cln, clp
                tp, tn = tn, tp

            self.prims['rotor']['coil']['in'][ph].fill = clp
            self.prims['rotor']['coil']['in'][ph].stroke = clp
            self.prims['rotor']['coil']['out'][ph].fill = cln
            self.prims['rotor']['coil']['out'][ph].stroke = cln

            self.prims['rotor']['current']['in'][ph].stroke = scale_rgb(clp, contrast_color_scale)
            self.prims['rotor']['current']['in'][ph].fill = scale_rgb(clp, contrast_color_scale)
            self.prims['rotor']['current']['out'][ph].stroke = scale_rgb(cln, contrast_color_scale)
            self.prims['rotor']['current']['out'][ph].fill = scale_rgb(cln, contrast_color_scale)

            for j, _ in enumerate(self.prims['rotor']['current']['in'][ph]):
                self.prims['rotor']['current']['in'][ph][j].scale(tp, center=self.prims['rotor']['current']['in'][ph][j].anchor)
                self.prims['rotor']['current']['out'][ph][j].scale(tn, center=self.prims['rotor']['current']['out'][ph][j].anchor)

            if amp < 0:
                self.prims['rotor']['current']['in'][ph].rotate(pi)
                self.prims['rotor']['current']['out'][ph].rotate(pi)
                self.prims['rotor']['coil']['in'][ph].rotate(pi)
                self.prims['rotor']['coil']['out'][ph].rotate(pi)



    def update_fields(self, mit_t):

        stator_width_factor = 9
        rotor_width_factor = 0.04

        for i, ph in enumerate('abc'):
            self.prims['stator']['field']['vec'][ph].scale(mit_t['Im_abc'][i])
            self.prims['stator']['field']['lines'][ph].width = abs(mit_t['Im_abc'][i]) * stator_width_factor
            if mit_t['Im_abc'][i] < 0.0:
                self.prims['stator']['field']['lines'][ph].rotate(pi)

        res_s = self.prims['stator']['field']['vec']['a'][0].to_complex() + self.prims['stator']['field']['vec']['b'][0].to_complex() + self.prims['stator']['field']['vec']['c'][0].to_complex()
        self.prims['stator']['field']['vec']['s'][0].from_complex(res_s)
        self.prims['stator']['field']['lines']['s'].width = abs(res_s) * stator_width_factor
        self.prims['stator']['field']['lines']['s'].rotate(pi + phase(res_s))

        for i, ph in enumerate('xyz'):
            self.prims['rotor']['field']['vec'][ph].scale(mit_t['Ir_xyz'][i] / self.mit.Ns_Nr * 0.5)
            self.prims['rotor']['field']['lines'][ph].width = abs(mit_t['Ir_xyz'][i]) * rotor_width_factor
            if mit_t['Ir_xyz'][i] < 0.0:
                self.prims['rotor']['field']['lines'][ph].rotate(pi)

        res_r = self.prims['rotor']['field']['vec']['x'][0].to_complex() + self.prims['rotor']['field']['vec']['y'][0].to_complex() + self.prims['rotor']['field']['vec']['z'][0].to_complex()
        self.prims['rotor']['field']['vec']['r'][0].from_complex(res_r)
        self.prims['rotor']['field']['lines']['r'].width = abs(res_r) * stator_width_factor   # não é roto_width_factor, pois as correntes do rotor estão em base distinta da das coordenadas do canvas (self.mit.Ns_Nr )
        self.prims['rotor']['field']['lines']['r'].rotate(phase(res_r))



        for ph in 'abcs':
            self.prims['stator']['field']['vec'][ph].visible = self.en_stator_field_vec and (ph in self.sel_stator_field.key)

        for ph in 'xyzr':
            self.prims['rotor']['field']['vec'][ph].visible = self.en_rotor_field_vec and (ph in self.sel_rotor_field.key)

        for ph in 'abcs':
            self.prims['stator']['field']['lines'][ph].visible = self.en_stator_field_lines and (ph in self.sel_stator_field.key)


        for ph in 'xyzr':
            self.prims['rotor']['field']['lines'][ph].visible = self.en_rotor_field_lines and (ph in self.sel_rotor_field.key)



    def update_fig0(self, mit_t):
        ax = self.widgets['figs'][0].axes[0]
        Y_show = mit_t[self.sel_fig0.key]

        self.plt_t.append(self.t)
        for i, ph in enumerate(self.sel_fig0.key[3:6]):
            self.plt_y[i].append(Y_show[i])    #amp * sin(self.thg + phi + alpha * i))
            self.plt_lines[('abc')[i]].set_ydata(self.plt_y[i])
            self.plt_lines[('abc')[i]].set_xdata(self.plt_t)
            self.plt_lines[('abc')[i] + '_marker'].set_ydata((self.plt_y[i][-1],))
            self.plt_lines[('abc')[i] + '_marker'].set_xdata((self.plt_t[-1],))
            self.plt_lines[('abc')[i]].set_color(cl[ph])
            self.plt_lines[('abc')[i] + '_marker'].set_color(cl[ph])
        pad = 0.05 / self.time_factor * self.plot_downsample_factor
        t_max = max(self.plt_t)
        t_min = min(self.plt_t)
        # t_min = t_max -.01
        y_max = self.sel_fig0.value
        ax.set_xlim(t_min + pad, t_max + pad)
        ax.set_ylim(-y_max, y_max)
        ax.set_ylabel(self.sel_fig0.key)



    def update_fig1(self):
        ax = self.widgets['figs'][1].axes[0]
        
        lim_max = 4200.0
        lim_min = 200.0

        nmax = lim_max
        nmin = -lim_min

        if self.f_grid < 0:
            nmax = lim_min
            nmin = -lim_max
        if self.s > 1:
            dx = self.mit.nr
            nmax += dx
            nmin += dx
        if self.s <= 0 and self.f_grid > 0:
            dx = self.mit.nr -lim_max +lim_min
            nmax = max(nmax+dx, nmax)
            nmin = max(nmin+dx, nmin)
        if self.s < 0 and self.f_grid < 0:
            dx = self.mit.nr + lim_max -lim_min
            nmax = min(nmax + dx, nmax)
            nmin = min(nmin + dx, nmin)

        wmax = nmax * pi / 30.0
        wmin = nmin * pi / 30.0

        self.mit.wr = (self.f_rot - self.f_ref) * 2 * pi * 2 / self.mit.p
        self.mit.f = self.f_grid
        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)

        mit_curves = self.mit.solve_range(wmin, wmax, self.ax_npt_fig1, [self.sel_fig1.key, 'Tind'])
        Xs = abs(mit_curves[self.sel_fig1.key]) if self.sel_fig1.key[0] == 'I' else mit_curves[self.sel_fig1.key]
        Tinds = mit_curves['Tind']
        nrs = mit_curves['nr']

        self.mit.wr = (self.f_rot - self.f_ref) * 2 * pi * 2 / self.mit.p
        self.mit.f = self.f_grid
        self.mit.V1 = self.mit.V1nom * self.mit.m_comp(compensate_Z1=self.mit.R1 != 0.0)
        self.mit.solve()

        self.plt_lines['ws_cursor'].set_xdata((self.mit.ns, ))
        self.plt_lines['wr_cursor'].set_xdata((self.mit.nr, ))
        self.plt_lines['Tind'].set_ydata(Tinds)
        self.plt_lines['Tind'].set_xdata(nrs)
        self.plt_lines['Ix'].set_ydata(Xs)
        self.plt_lines['Ix'].set_xdata(nrs)
        self.plt_lines['Tind_marker'].set_ydata((self.mit.Tind,))
        self.plt_lines['Tind_marker'].set_xdata((self.mit.nr,))
        self.plt_lines['Ix_marker'].set_ydata(((abs(self.mit[self.sel_fig1.key]) if self.sel_fig1.key[0] == 'I' else self.mit[self.sel_fig1.key]),))
        self.plt_lines['Ix_marker'].set_xdata((self.mit.nr,))

        self.plt_lines['Ix'].set_color(cl[self.sel_fig1.key])
        self.plt_lines['Ix_marker'].set_color(cl[self.sel_fig1.key])
        ax.set_xlim(min(nrs), max(nrs))

        # ypad = 1.1
        # ymax = np.max(Tinds) * ypad
        # ymin = np.min(Tinds) * ypad
        ymax = 20
        ymin = -ymax

        sat = 0.12
        if self.s < 0:
            sat = 1.0

        if self.f_grid > 0:
            ymin = -sat*ymax

        # if self.fg < 0:
        #     ymax = -sat*ymin

        ax.set_ylim(ymin, ymax)
        ax.set_ylabel('Tind' + ((', ' + self.sel_fig1.key) if self.sel_fig1.key != 'nan' else ''))




    def update_fps_info(self, dt:float):
        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"{fps:.0f} fps")

    def destroy(self):
        del self.prims['stator']
        del self.prims['rotor']
        self.canvas.delete('all')


    def create(self):
        mit_draw(self.canvas, self.prims, self.sel_stator_turns.value[0], self.sel_rotor_turns.value[0])
        self.prims.draw(consolidate_transforms_to_original=True)



    def update_info(self):

        self.widgets['w_stator_um'].config(text=f'[{self.sel_fs_unit.key}]')
        self.widgets['w_rotor_um'] .config(text=f'[{self.sel_fr_unit.key}]')
        self.widgets['w_grid_um']  .config(text=f'[{self.sel_fg_unit.key}]')
        self.widgets['Pconv_um']   .config(text=f'[{self.sel_Pconv_unit.key}]')

        maxlen = len('stator [rad/s]')
        self.widgets['w_stator'].config(text=f'{self.f_ref * self.sel_fs_unit.value        :4.1f}')
        self.widgets['w_rotor'] .config(text=f'{self.f_rot * self.sel_fr_unit.value        :4.1f}')
        self.widgets['w_grid']  .config(text=f'{self.f_sync * self.sel_fg_unit.value       :4.1f}')
        self.widgets['Pconv']   .config(text=f'{self.mit.Pconv * self.sel_Pconv_unit.value :4.2f}')
        self.widgets['slip']    .config(text=f'{self.mit.s                                 :4.2f}')
        self.widgets['Tind']    .config(text=f'{self.mit.Tind                              :4.2f}')
        self.widgets['f']       .config(text=f'{self.mit.f                                 :4.1f}')
        self.widgets['time_factor'].config(text=f"{self.time_factor:>6.1f} x")

    def reset_time(self, reset_and_stop=False):
        if self.t is not None:
            self.invalidate_fig0_data()

        self._t_init = time.time()
        self.time_factor = 140
        self._t_start = 0.0
        self.th_grid = 0.0
        self.th_rot = 0.0
        self.th_ref = 0.0
        self.th_sync = 0.0
        self.t = 0.0
        self.f_rot = 57.0
        self.f_ref = 0.0
        self.f_sync = 60.0
        self._f_ref_inc = 0.0
        self._fg_inc = 0.0
        self._s_inc = 0.0
        self.inertia = 0.008

        if reset_and_stop:
            self.run = False
            # self.draw_all()

    def invalidate_fig0_data(self, previous_time_factor=None):

        if not previous_time_factor:
            previous_time_factor = self.time_factor

        t_max = max(self.plt_t)
        for k in range(len(self.plt_t)):
            self.plt_t[k] = (self.plt_t[k] - t_max) * previous_time_factor / self.time_factor + t_max

        nans = np.empty(self.ax_npt_fig0, float)
        nans.fill(np.nan)
        for arr in (self.plt_y):
            arr.extend(nans)

    @property
    def f_irot(self):
        return self.s * self.f_grid

    @property
    def f_grid(self):
        return self.f_sync - self.f_ref

    @f_grid.setter
    def f_grid(self, value):
        self.f_sync  = value + self.f_ref


    @property
    def s(self):
        if self.f_grid != 0.0:
            return (self.f_sync - self.f_rot) / self.f_grid
        else:
            return 0.0



    def binds(self) -> None:

        def show_binds():
            current_state = self.run
            self.run = False
            messagebox.showinfo('binds', binds_message,)
            self.run = current_state

        def toggle_run():
            self.run = not self.run

        def toggle_sim():
            if self.en_sim_inertia:
                self.en_sim_inertia = False
            else:
                self.en_sim_inertia = True


        def inc_value(var_name: Literal['fg', 'fs', 's', 'delay', 'time_factor', 'Tres'],
                      increment: int | float,
                      v_min: int | float,
                      v_max: int | float):

            match var_name:
                case 'fs':
                    if self.run:
                        self._f_ref_inc = clip(self.f_ref + increment, v_min, v_max) - self.f_ref
                case 's':
                    if self.run:
                        if self.f_sync < 0:
                            increment = - increment
                        self._s_inc = clip(self.s + increment, v_min, v_max) - self.s
                case 'fg':
                    if self.run:
                        self._fg_inc = clip(self.f_sync + increment, v_min, v_max) - self.f_sync
                case 'Tres':
                    if self.run:
                        self.mit.k0 = clip(self.mit.k0 + increment, v_min, v_max)
                        self.mit.k2 = clip(self.mit.k2 + increment*0.00001, v_min*0.00001, v_max*0.00001)

                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                    print(f'(/*) time factor: {self.frame_delay}')
                case 'time_factor':
                    last = self.time_factor
                    self.time_factor = clip(self.time_factor + increment, v_min, v_max)
                    self.invalidate_fig0_data(last)


            # self.update_info()


        def change_slots(parts: Literal['rotor', 'stator']):
            if isinstance(parts, str):
                parts = [parts]

            self.destroy()
            if 'rotor' in parts: next(self.sel_rotor_turns)
            if 'stator' in parts: next(self.sel_stator_turns)
            self.create()


        def reset_colors():
            next(self.sel_dynamic_color)
            if not self.sel_dynamic_color.value:
                self.widgets['stator_coil_front'].config(state=tk.NORMAL)
                self.widgets['rotor_coil_front'].config(state=tk.NORMAL)
                # del self.en_stator_coil_front
                # del self.en_rotor_coil_front
                self.en_stator_coil_front = BoolVar(False)
                self.en_rotor_coil_front = BoolVar(False)
                self.widgets['stator_coil_front'].configure(variable=self.en_stator_coil_front)
                self.widgets['rotor_coil_front'].configure(variable=self.en_rotor_coil_front)
                for ph in 'abc':
                    for direction in ('in', 'out'):
                        self.prims['stator']['coil'][direction][ph].stroke = scale_rgb(cl[ph], contrast_color_scale)
                        self.prims['stator']['coil'][direction][ph].fill = cl[ph]
                    for direction in ('in', 'out'):
                        self.prims['stator']['current'][direction][ph].fill = scale_rgb(cl[ph], contrast_color_scale)
                        self.prims['stator']['current'][direction][ph].stroke = scale_rgb(cl[ph], contrast_color_scale)

                    for ph in 'xyz':
                        for direction in ('in', 'out'):
                            self.prims['rotor']['coil'][direction][ph].stroke = scale_rgb(cl[ph], contrast_color_scale)
                            self.prims['rotor']['coil'][direction][ph].fill = cl[ph]
                        for direction in ('in', 'out'):
                            self.prims['rotor']['current'][direction][ph].fill = scale_rgb(cl[ph], contrast_color_scale)
                            self.prims['rotor']['current'][direction][ph].stroke = scale_rgb(cl[ph], contrast_color_scale)
            else:
                self.en_stator_coil_front = False
                self.en_rotor_coil_front = False
                self.widgets['stator_coil_front'].config(state=tk.DISABLED)
                self.widgets['rotor_coil_front'].config(state=tk.DISABLED)


        def change_coil_opacity():
            next(self.sel_coil_opacity)
            for ph in ('xyz'):
                for node in self.prims['rotor'].filter_matching_keys('coil_front', ph):
                    node.fill = cl[ph]
                    node.stipple = self.sel_coil_opacity.key
            for ph in ('abc'):
                for node in self.prims['stator'].filter_matching_keys('coil_front', ph):
                    node.fill = cl[ph]
                    node.stipple = self.sel_coil_opacity.key



        def change_part_field(event):
            x, y = norm_coords(canvas=self.canvas, coords=(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(),
                                                           self.canvas.winfo_pointery() - self.canvas.winfo_rooty()))
            if collision_circle_point(self.prims['rotor']['core']['outer'][0], (x, y)):
                field_menu(event, self.sel_rotor_field)
            elif collision_circle_point(self.prims['stator']['core']['outer'][0], (x, y)):
                field_menu(event, self.sel_stator_field)

        def change_part_visibility():
            x, y = norm_coords(canvas=self.canvas, coords=(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(),
                                                           self.canvas.winfo_pointery() - self.canvas.winfo_rooty()))
            if collision_circle_point(self.prims['rotor']['core']['outer'][0], (x, y)):
                self.prims['rotor'].toggle_visible()
            elif collision_circle_point(self.prims['stator']['core']['outer'][0], (x, y)):
                self.prims['stator'].toggle_visible()

        def field_menu(event, selection):
            self.run = False
            self._previous_run = False
            menu = tk.Menu(self.canvas.window, tearoff=0)
            if selection.name is not None:
                menu.add_command(label=selection.name, state='disabled')
                menu.add_separator()
            for it in selection:
                menu.add_command(label=it, command=partial(selection.set_current_key, it))
            # if isinstance(selection.value, PlotLimits):
            #     menu.add_separator()
            #     menu.add_command(label='y autoscale', command=partial(toggle_autoscale, selection, 'y'))
            menu.tk_popup(event.x_root, event.y_root)
            self.run = True



        dw_inc = 0.89   #0.83333333333333333333333333
        f_max = 70
        self.canvas.window.bind('=', lambda event: inc_value('fs', 1, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('fs', -1, -f_max, f_max))
        self.canvas.window.bind('.', lambda event: inc_value('s', -0.01, -0.2, 2.2))
        self.canvas.window.bind(',', lambda event: inc_value('s', 0.01, -0.2, 2.2))
        self.canvas.window.bind('<Right>', lambda event: inc_value('fg', dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Left>', lambda event: inc_value('fg', -dw_inc, -f_max, f_max))

        self.canvas.window.bind('<Up>', lambda event: inc_value('Tres', 0.2, -11, 11))
        self.canvas.window.bind('<Down>', lambda event: inc_value('Tres', -0.2, -11, 11))

        self.canvas.window.bind(']', lambda event: inc_value('time_factor', self.time_factor*.2, 32.45273575943723503208293147346, 1492.992))
        self.canvas.window.bind('[', lambda event: inc_value('time_factor', -self.time_factor*.16666666666666666666666666666667, 32.45273575943723503208293147346, 1492.992))

        # self.canvas.window.bind('v', lambda event: next(self.select_speed_unit) )
        # self.canvas.window.bind('p', lambda event: next(self.select_power_unit))
        self.canvas.window.bind('*',       lambda event: inc_value('delay', 1, 0, 30))
        self.canvas.window.bind('/',       lambda event: inc_value('delay', -1, 0, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())
        # self.canvas.window.bind('<Return>', lambda event: toggle_sim())
        self.canvas.window.bind('<F1>', lambda event: show_binds())
        self.canvas.window.bind('<Escape>', lambda event: self.reset_time(reset_and_stop=True))
        self.canvas.window.bind('<0>',     lambda event: self.reset_time())

        self.canvas.window.bind('m', lambda event: change_slots('stator'))
        self.canvas.window.bind('n', lambda event: change_slots('rotor'))
        self.canvas.window.bind('o', lambda event: change_coil_opacity())

        # self.canvas.window.bind('d', lambda event: self.destroy())
        # self.canvas.window.bind('c', lambda event: self.create())
        self.widgets['canvas_fig0'].get_tk_widget().bind('<Button-1>', lambda event: {next(self.sel_fig0), self.invalidate_fig0_data()})
        self.widgets['canvas_fig0'].get_tk_widget().bind('<Button-3>', lambda event: {self.invalidate_fig0_data(), field_menu(event, self.sel_fig0)})
        self.widgets['canvas_fig1'].get_tk_widget().bind('<Button-1>', lambda event: next(self.sel_fig1))
        # self.canvas.bind('<Button-3>', lambda event: {next(self.select_part),self.prims.print_tree(print_leafs=False)})
        self.canvas.bind('<Button-1>', lambda event: change_part_visibility())
        self.canvas.bind('<Button-3>', change_part_field)


        self.canvas.window.bind('T',  lambda event: {print(f'\n\n{'-' * 135}'), self.prims.print_tree()})
        self.canvas.window.bind('t',  lambda event: {print(f'\n\n{'-'*135}'), self.prims.print_tree(False)})
        self.canvas.window.bind('d',  lambda event: reset_colors())
        self.canvas.window.bind('s', lambda event: next(self.sel_stator_field))
        self.canvas.window.bind('r', lambda event: next(self.sel_rotor_field))
        self.canvas.window.bind('\\', lambda event: next(self.sel_mount))
        # self.canvas.window.bind('k',  lambda event: next(self.select_ref))


        self.widgets['sim_inertia']       .configure(variable=self.en_sim_inertia)
        self.widgets['stator_field_lines'].configure(variable=self.en_stator_field_lines)
        self.widgets['stator_field_vec']  .configure(variable=self.en_stator_field_vec)
        self.widgets['rotor_field_lines'] .configure(variable=self.en_rotor_field_lines)
        self.widgets['rotor_field_vec']   .configure(variable=self.en_rotor_field_vec)
        self.widgets['stator_coil_front'] .configure(variable=self.en_stator_coil_front)
        self.widgets['rotor_coil_front']  .configure(variable=self.en_rotor_coil_front)

        self.widgets['w_stator_um'].bind('<Button-1>', lambda event: next(self.sel_fs_unit))
        self.widgets['w_rotor_um'] .bind('<Button-1>', lambda event: next(self.sel_fr_unit))
        self.widgets['w_grid_um']  .bind('<Button-1>', lambda event: next(self.sel_fg_unit))
        self.widgets['Pconv_um']   .bind('<Button-1>', lambda event: next(self.sel_Pconv_unit))

        self.widgets['ref_free'].configure(variable=self.sel_ref, value='free')
        self.widgets['ref_stator'].configure(variable=self.sel_ref, value='stator')
        self.widgets['ref_rotor'] .configure(variable=self.sel_ref, value='rotor')
        self.widgets['ref_field'] .configure(variable=self.sel_ref, value='field')

        # self.canvas.window.bind('<B1-Motion>', lambda event: drag_window())