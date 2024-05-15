import tkinter as tk
from cmath import polar, rect, phase
import numpy as np
from tkinter import messagebox
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas, BoolVar
from primitive import Primitive
from transformations import translate, rotate, scale, reverse, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip
import time
from assets import assets, cl, binds_message
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal
from MITsim import MITsim
from gvec import GraphicVec2

class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=0)

        self.widgets = widgets
        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)

        self.t = 0.0
        self.ths = 0.0     # angulo mecanico do estador
        self.thr = 0.0     # angulo mecânico do rotor
        # self.thir = 0.0    # fase da corrente do rotor
        self.thg = 0.0     # fase das tensões de alimentação
        self.fs = 0.0
        self.fg = 60
        self.s = 0.05

        self.Ns_Nr = 100 #relação entre n espiras do estator e do rotor

        self._fs_inc = 0.0   # incrementos a ser aplicado no próximo frame
        self._s_inc = 0.0    # incrementos a ser aplicado no próximo frame
        self._fg_inc = 0.0   # incrementos a ser aplicado no próximo frame

        self.fr = (1-self.s) * self.fg
        self.time_factor = 140

        self.V1nom = 380.0




        self.display_mu = CircularDict({'Hz': 1.0, 'rad/s': 2*pi, 'rpm': 60})  # 'um': fator de conversão
        self.display_mit_ax0 = CircularDict({'V1': 500, 'Ir': 500, 'I1': 12, 'Im': 1})   # 'atributo': ylim
        self.display_mit_ax1 = CircularDict({'I2': 1, 'I1': 1, 'nan': 0})      # value não utilizado
        self.esp_front_opacity = CircularDict({'': 0, 'gray75': 1, 'gray50': 2, 'gray25': 3})  # value não utilizado
        self.dynamic_colors = BoolVar(True)




        self.ax_npt = 100
        marker_size = 8
        markers = ('o', 'o', 'o')

        self.plt_t_range = .05  #(2 * pi * 3) / self.fg
        axs = (self.widgets['figs'][0].axes[0],
               self.widgets['figs'][1].axes[0],
               )

        nans = np.empty(self.ax_npt, float)
        nans.fill(np.nan)


        t = np.arange(-self.plt_t_range, 0.0, self.plt_t_range / self.ax_npt)
        self.plt_vgs = (deque(maxlen=self.ax_npt), deque(maxlen=self.ax_npt), deque(maxlen=self.ax_npt))
        for ys in self.plt_vgs:
            ys.extend(nans)
        self.plt_t = deque(maxlen=self.ax_npt)
        self.plt_t.extend(t)

        Zbase = 1
        self.mit = MITsim(R1=14.7000 * Zbase * 0.0,
                          X1=14.9862 * Zbase * 0.0,
                          R2=10.5445 * Zbase * 0.7,
                          X2=22.4793 * Zbase * 1.5,
                          Rc=1.6261e+03 * Zbase,
                          Xm=419.2075 * Zbase,
                          V1=380.0,
                          fnom=60.0,
                          p=2
                          )

        wmax = (2 * pi * 70) * 1.2
        self.mit.V1 = 1.0 * self.V1nom
        self.mit.f = self.fg
        mit_curves = self.mit.solve_range(-wmax, wmax, self.ax_npt, ['I1', 'Tind'])
        y1s = abs(mit_curves['I1'])
        y0s = mit_curves['Tind']
        nrs = mit_curves['nr']

        axs[0].axhline(0, linestyle='--', color=cl['grid'], linewidth=1)
        axs[1].axhline(0, linestyle='--', color=cl['grid'], linewidth=1)
        axs[1].axvline(0, linestyle='--', color=cl['grid'], linewidth=1)
        self.plt_lines = {
            # 'vg_line': (axs[0].plot((0, 0), (-2, 2), '-.k', lw=1.5))[0],
            'vg_a': (axs[0].plot(self.plt_t, self.plt_vgs[0], color=cl['a'], lw=2))[0],
            'vg_b': (axs[0].plot(self.plt_t, self.plt_vgs[1], color=cl['b'], lw=2))[0],
            'vg_c': (axs[0].plot(self.plt_t, self.plt_vgs[2], color=cl['c'], lw=2))[0],
            'vg_a_marker': (axs[0].plot(0, 0, color=cl['a'], marker=markers[0], markersize=marker_size, lw=2))[0],
            'vg_b_marker': (axs[0].plot(0, 0, color=cl['b'], marker=markers[1], markersize=marker_size, lw=2))[0],
            'vg_c_marker': (axs[0].plot(0, 0, color=cl['c'], marker=markers[2], markersize=marker_size, lw=2))[0],

            # 'grid_x0': (axs[1].plot((0, 0), (-10000, 10000), '--', color=cl['grid'], lw=1))[0],
            # 'grid_y0': (axs[1].plot((-10000, 10000), (0, 0), '--', color=cl['grid'], lw=1))[0],
            # 'ws_cursor': (axs[1].plot((self.mit.ws, self.mit.ws), (-10000, 10000), '--', color=cl['ws_cursor'], lw=1))[0],
            # 'wr_cursor': (axs[1].plot((wrs[0], wrs[0]), (-10000, 10000), '-.', color=cl['wr_cursor'], lw=1))[0],

            'ws_cursor': (axs[1].axvline(self.mit.ws, linestyle='-.', color=cl['ws_cursor'], lw=1)),
            'wr_cursor': (axs[1].axvline(self.mit.wr, linestyle='-.', color=cl['wr_cursor'], lw=1)),
            'Tind': (axs[1].plot(nrs, y0s, color=cl['Tind'], lw=2))[0],
            'I1': (axs[1].plot(nrs, y1s, color=cl['I1'], lw=2))[0],
            'Tind_marker': (axs[1].plot(nrs[0], y0s[0], color=cl['Tind'], marker=markers[2], markersize=marker_size, lw=2))[0],
            'I1_marker': (axs[1].plot(nrs[0], y1s[0], color=cl['I1'], marker=markers[2], markersize=marker_size, lw=2))[0],
        }

        axs[0].set_ylim(-1.2, 1.2)
        axs[0].set_xlim(-self.plt_t_range, 0.0)
        axs[0].set_xticks([])


        # axs[1].set_ylim(-0, 11)
        axs[1].set_xlim(0, self.mit.ws)


        widgets['canvas_fig0'].draw()
        widgets['canvas_fig1'].draw()

        self.run = False

        self.slots_ns_alt = 3  # todo: so funciona para 3 e 1
        self.slots_nr_alt = 3  # todo: so funciona para 3 e 1
        self.slots_ns = 1
        self.slots_nr = 1
        self.prims = {'stator': {},
                      'rotor': {},
                      'extra_s': {},
                      'extra_r': {},
                      }



        self.create_original_draw()
        self.draw_all(consolidate_transforms_to_original=True)
        self.binds()


    def create_original_draw(self):

        # stator outer core
        self.prims['stator']['core'] = [
            self.create_primitive(**assets['mount']),
            self.create_primitive(**assets['mount'], transforms=(scale, (-1.0, 1.0))),
            self.create_primitive(**assets['stator_outer']),
            self.create_primitive(**assets['stator_inner']),
        ]

        # stator slots
        n_prims = self.slots_ns_alt * 6
        self.prims['stator']['cutout'] = [
            *(self.create_primitive(**assets['stator_cutout'], transforms=(rotate, -2 * pi * (i - 1) / n_prims))
              for i in range(n_prims)),
        ]
        self.prims['stator']['cutout_outline'] = [
            *(self.create_primitive(**assets['stator_cutout_outline'], transforms=(rotate, -2 * pi * (i - 1) / n_prims))
              for i in range(n_prims)),
        ]


        # rotor outer core
        self.prims['rotor']['core'] = [
            self.create_primitive(**assets['rotor_outer']),
        ]

        # roto slots
        n_prims = self.slots_nr_alt * 6
        self.prims['rotor']['cutout'] = [
            *(self.create_primitive(**assets['rotor_cutout'], transforms=(rotate, -2 * pi * (i - 1) / n_prims))
              for i in range(n_prims)),
        ]
        self.prims['rotor']['cutout_outline'] = [
            *(self.create_primitive(**assets['rotor_cutout_outline'], transforms=(rotate, -2 * pi * (i - 1) / n_prims))
              for i in range(n_prims)),
        ]


        # roto shaft
        self.prims['rotor']['core'].append(self.create_primitive(**assets['shaft']))
        self.prims['rotor']['core'].append(self.create_primitive(**assets['keyway']))
        self.prims['rotor']['core'].append(self.create_primitive(**assets['keyway_outline']))

        # stator magnetic axis
        self.prims['stator']['axis'] = [
            *(self.create_primitive(**assets['stator_axis'], transforms=(rotate, 2 * pi / 3 * i)) for i in
              range(3)),
        ]
        for i, p in enumerate(self.prims['stator']['axis']):
            p.stroke = cl[('a', 'b', 'c')[i % 3]]

        # rotor magnetic axis
        self.prims['rotor']['axis'] = [
            *(self.create_primitive(**assets['rotor_axis']).rotate(2 * pi / 3 * i) for i in range(3)),
        ]
        for i, p in enumerate(self.prims['rotor']['axis']):
            p.stroke = cl[('x', 'y', 'z')[i % 3]]


        # stator flux
        self.prims['extra_s']['flux_a'] = self.create_flux_from_quarter(orientation=0.0, color=cl['a'])
        self.prims['extra_s']['flux_b'] = self.create_flux_from_quarter(orientation=2 * pi / 3, color=cl['b'])
        self.prims['extra_s']['flux_c'] = self.create_flux_from_quarter(orientation=-2 * pi / 3, color=cl['c'])
        self.prims['extra_s']['flux_s'] = self.create_flux_from_quarter(orientation=0.0, color=cl['s'])


        # stator windings
        n_prims = 6 * self.slots_ns_alt
        self.prims['stator']['esp'] = [
            *(self.create_primitive(**assets['stator_esp'], transforms=(rotate, (-2 * pi * (i - 1)) / n_prims))
              for i in range(n_prims)),
        ]
        for i, p in enumerate(self.prims['stator']['esp']):
            p.fill = cl[('a', 'b', 'c')[i // self.slots_ns_alt % 3]]

        # rotor windings
        n_prims = self.slots_nr_alt * 6
        self.prims['rotor']['esp'] = [
            *(self.create_primitive(**assets['rotor_esp'], transforms=(rotate, (-2 * pi * (i - 1)) / n_prims))
              for i in range(n_prims)),
        ]
        for i, p in enumerate(self.prims['rotor']['esp']):
            p.fill = cl[('x', 'y', 'z')[i // self.slots_nr_alt % 3]]

        # rotor windings front
        n_prims = self.slots_nr_alt * 3
        self.prims['extra_r']['esp_front'] = [
            *(self.create_primitive(**assets['rotor_esp_front'], transforms=(rotate, 2 * pi * (i-1) / n_prims))
              for i in range(n_prims)),
        ]
        for i, p in enumerate(self.prims['extra_r']['esp_front']):
            p.fill = cl[('x', 'y', 'z')[i // self.slots_nr_alt % 3]]

        # stator windings front
        n_prims = self.slots_ns_alt * 3
        self.prims['extra_s']['esp_front'] = [
            *(self.create_primitive(**assets['stator_esp_front'], transforms=(rotate, 2 * pi * (i - 1) / n_prims))
              for i in range(n_prims)),
        ]
        for i, p in enumerate(self.prims['extra_s']['esp_front']):
            p.fill = cl[('a', 'b', 'c')[i // self.slots_ns_alt % 3]]

        self.prims['rotor']['vec'] = [
            *(GraphicVec2(0.4, 0.0, self.canvas, stroke=cl[('x', 'y', 'z', 'r')[i]], transforms=(rotate, 2 * pi / 3 * i))
              for i in range(4))
        ]

        self.prims['stator']['vec'] = [
            *(GraphicVec2(0.4, 0.0, self.canvas, stroke=cl[('a', 'b', 'c', 's')[i]], transforms=(rotate, 2*pi/3 * i))
              for i in range(4))
        ]

        # self.prims['stator']['vec'][0].scale(1.2)

        self.create_primitive('circle', (0.0, 0.0, 0.01), fill=cl['airgap'], stroke=cl['outline'])

        self.update_esp_and_cutout_visibility()



    def create_flux_from_quarter(self, orientation=0.0, color: str | None = None):
        orientation += pi
        prims = [
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse, ), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, 1)), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, -1)), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse, ), (scale, (1, -1)), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse, ), (scale, {'factor': (0.8, 0.77), 'center': (0.0, -0.50571428571428571428571428571429)}    ), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, 1)), (scale, {'factor': (0.8, 0.77), 'center': (0.0, -0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, -1)), (scale, {'factor': (0.8, 0.77), 'center': (0.0, 0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse, ), (scale, (1, -1)), (scale, {'factor': (0.8, 0.77), 'center': (0.0, 0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse, ), (scale, {'factor': (.65, .5), 'center': (0.0, -0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, 1)), (scale, {'factor': (.65, .5), 'center': (0.0, -0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(scale, (-1, -1)), (scale, {'factor': (.65, .5), 'center': (0.0, 0.50571428571428571428571428571429)}), (rotate, orientation)])),
            (self.create_primitive(**assets['quarter_flux'], transforms=[(reverse,), (scale, (1, -1)), (scale, {'factor': (.65, .5), 'center': (0.0, 0.50571428571428571428571428571429)}), (rotate, orientation)])),
        ]
        if color:
            for p in prims:
                p.stroke = color

        return prims

    def refresh(self, _, dt, frame_count):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

        # animation clock
        dt /= self.time_factor
        self.fr = (1.0 - self.s) * self.fg

        # todo: deletar esse valor e usar resultado da sim
        currents_s = tuple(sin(self.thg - pi / 2 - 2 * pi / 3 * k) for k in range(3))

        # plot resample
        m = self.mit.m_comp(compensate_Z1 = self.mit.R1 != 0.0 )

        #Tind vs wr curve
        wmax = 4600
        nrs = np.linspace(-wmax, wmax, 200)
        y0s = np.empty_like(nrs)
        y1s = np.empty_like(nrs)
        for k, nr in enumerate(nrs):
            wr = nr / 30.0 * pi
            self.mit.V1 = m * self.V1nom
            self.mit.wr = wr
            self.mit.f = self.fg
            self.mit.solve()
            y1s[k] = abs(self.mit[self.display_mit_ax1.current_key])
            y0s[k] = self.mit.Tind

        self.plt_lines['I1'].set_ydata(y1s)
        self.plt_lines['I1'].set_xdata(nrs)
        self.plt_lines['Tind'].set_ydata(y0s)
        self.plt_lines['Tind'].set_xdata(nrs)

        # markers
        try:
            s = (self.fg - self.fr) / self.fg
        except ZeroDivisionError:
            s = float('nan')

        m0 = 0.008
        self.mit.V1 = max(m, m0) * self.V1nom
        self.mit.wr = self.fr * 2 * pi * 2 / self.mit.p
        self.mit.f = self.fg
        self.mit.solve()

        th_er = (self.thg) - self.thr - pi
        Im_abc = tuple(abs(self.mit.Im) * sin(self.thg + phase(self.mit.Im) - i * 2 * pi / 3) for i in range(3))
        I2_abc = tuple(abs(self.mit.I2) * sin(th_er + phase(self.mit.I2) - i*2*pi/3) for i in range(3))


        self.plt_lines['I1_marker'].set_ydata((abs(self.mit[self.display_mit_ax1.current_key]), abs(self.mit[self.display_mit_ax1.current_key])))
        self.plt_lines['Tind_marker'].set_ydata((self.mit.Tind, self.mit.Tind))
        nr = self.mit.wr * 30.0 / pi
        ns = self.mit.ws * 30.0 / pi
        self.plt_lines['I1_marker'].set_xdata((nr, nr))
        self.plt_lines['Tind_marker'].set_xdata((nr, nr))
        self.plt_lines['ws_cursor'].set_xdata((ns, ns))
        self.plt_lines['wr_cursor'].set_xdata((nr, nr))

        y_pad = 2
        y_min = min(min(min(y0s), min(y1s)) + 22, -y_pad)
        y_max = max(max(y0s), max(y1s)) + y_pad
        xpad = 300
        ws = self.mit.f * 2 * pi * 2 / self.mit.p
        x_min = min(-xpad, min(self.mit.wr, ws) * 30.0 / pi - xpad)
        x_max = max(3600, max(self.mit.wr, ws) * 30.0 / pi + xpad)
        if (s < 0 and ws > 0) or (s >= 0 and ws <= 0):
            # self.widgets['figs'][1].axes[0].set_xlim(-0.03*self.mit.ws, 1.2*self.mit.ws)
            self.widgets['figs'][1].axes[0].set_xlim(x_min, x_max)
            self.widgets['figs'][1].axes[0].autoscale(enable=True, axis="y", tight=False)
            # self.widgets['figs'][1].axes[0].set_ylim(y_min - 28, y_max+6)
        elif (s > 1 and ws > 0) or (s < 1 and ws < 0):
            # self.widgets['figs'][1].axes[0].set_xlim(-0.2*self.mit.ws, 1.03*self.mit.ws)
            self.widgets['figs'][1].axes[0].set_xlim(x_min, x_max)
            # self.widgets['figs'][1].axes[0].set_ylim(y_min, y_max)
            self.widgets['figs'][1].axes[0].autoscale(enable=True, axis="y", tight=False)
        else:
            # self.widgets['figs'][1].axes[0].set_xlim(-0.03*self.mit.ws, 1.03*self.mit.ws)
            self.widgets['figs'][1].axes[0].set_xlim(x_min, x_max)
            self.widgets['figs'][1].axes[0].set_ylim(y_min, y_max)
            # self.widgets['figs'][1].axes[0].autoscale(enable=True, axis="y", tight=False)

        self.widgets['figs'][1].axes[0].set_ylabel(f'Tind {', ' + self.display_mit_ax1.current_key if self.display_mit_ax1.current_key != 'nan' else ''}')


        if self.run:

            # plot ax0
            self.plt_t.append(self.t)


            if self.display_mit_ax0.current_key == 'Ir':
                key = 'I2'
                th = th_er
                amp = abs(self.mit[key]) * self.Ns_Nr
            else:
                key = self.display_mit_ax0.current_key
                th = self.thg
                amp = abs(self.mit[key])

            phi = phase(self.mit[key])

            for phase_id in range(3):

                ax0_curves = tuple(amp * sin(th + phi - k * 2 * pi / 3) for k in range(3))
                self.plt_vgs[phase_id].append(ax0_curves[phase_id])

        redraw_plt = frame_count % 2 == 0
        phases = ('a', 'b', 'c')
        if redraw_plt:
            for k, phase_id in enumerate(phases):
                self.plt_lines['vg_' + phase_id].set_ydata(self.plt_vgs[k])
                self.plt_lines['vg_' + phase_id].set_xdata(self.plt_t)
                self.plt_lines['vg_' + phase_id + '_marker'].set_ydata((self.plt_vgs[k][-1], self.plt_vgs[k][-1]))
                self.plt_lines['vg_' + phase_id + '_marker'].set_xdata((self.plt_t[-1], self.plt_t[-1]))
            # self.plt_lines['vg_line'].set_ydata((-2, 2))
            # self.plt_lines['vg_line'].set_xdata((self.plt_t[-1], self.plt_t[-1]))
            pad = 0.1 / self.time_factor
            t_max = max(self.plt_t)+pad
            t_min = min(self.plt_t)+pad
            y_max = self.display_mit_ax0.current_value

            self.widgets['figs'][0].axes[0].set_xlim(t_min, t_max)
            self.widgets['figs'][0].axes[0].set_ylim(-y_max, y_max)
            self.widgets['figs'][0].axes[0].set_ylabel(f'{self.display_mit_ax0.current_key if self.display_mit_ax0.current_key != 'nan' else ''}')



        # cores dinâmicas baseadas nas correntes do estator
        colors_s =[]
        for k, v in enumerate(currents_s):
            rgb = hex_to_rgb((cl['a'], cl['b'], cl['c'])[k % 3])

            f = abs(currents_s[k % 3]) if self.dynamic_colors else 1.0
            colors_s.append(rgb_to_hex(scale_hsl(rgb, hue=1, sat=(1-f)*0.05+0.95, lum=sqrt(f) * 1.2)))

        # stator
        for part in ['stator', 'extra_s']:
            for group in self.prims[part]:
                for prims in self.prims[part][group]:
                    prims.rotate(self.ths)


        # TODO: restaurar
        for k, prims in enumerate(self.prims['stator']['esp']):
            prims.fill = colors_s[k // self.slots_ns_alt % 3]

        for k, prims in enumerate(self.prims['extra_s']['esp_front']):
            prims.fill = colors_s[k // self.slots_ns_alt % 3]

        # rotor
        for part in ['rotor', 'extra_r']:
            for group in self.prims[part]:
                for prims in self.prims[part][group]:
                    prims.rotate(self.thr+self.ths)



        # xyz flux animation
        # groups = ['flux_x', 'flux_y', 'flux_z']
        # tip = assets['quarter_flux']['arrowshape']
        # max_width = 6
        for phase_id in range(3):
            s = I2_abc[phase_id]
            self.prims['rotor']['vec'][phase_id].scale(s * 0.4)
            # if self.prims['extra_s'][groups[phase_id]][0].visible:
            #     for prims in *self.prims['extra_s'][groups[phase_id]],:
            #         prims.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
            #         prims.width = max_width * fabs(s / abs(self.mit.Im))
            #         prims.fill = colors_s[phase_id]

        self.prims['rotor']['vec'][3].from_complex(self.prims['rotor']['vec'][0].to_complex() +
                                                   self.prims['rotor']['vec'][1].to_complex() +
                                                   self.prims['rotor']['vec'][2].to_complex()
                                                   )


        # abc flux animation



        groups = ['flux_a', 'flux_b', 'flux_c']
        tip = assets['quarter_flux']['arrowshape']
        max_width = 6
        for phase_id in range(3):
            s = Im_abc[phase_id]
            self.prims['stator']['vec'][phase_id].scale(s * 1.48)
            if self.prims['extra_s'][groups[phase_id]][0].visible:
                for prims in *self.prims['extra_s'][groups[phase_id]],:
                    prims.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
                    prims.width = max_width * fabs(s / abs(self.mit.Im))
                    prims.fill = colors_s[phase_id]

        self.prims['stator']['vec'][3].from_complex(self.prims['stator']['vec'][0].to_complex() +
                                                    self.prims['stator']['vec'][1].to_complex() +
                                                    self.prims['stator']['vec'][2].to_complex()
                                                    )

        if self.prims['extra_s']['flux_s'][0].visible:
            for p in *self.prims['extra_s']['flux_s'],:
                p.rotate(phase(self.prims['stator']['vec'][3].to_complex()))


        # self.prims['stator']['vec'][0].coords = (0,0,-1,-1)

        self.draw_all()

        if redraw_plt:
            for fig in self.widgets['figs']:
                fig.canvas.draw()
                fig.canvas.flush_events()

        if self._fs_inc:
            self.fs += self._fs_inc
            self._fs_inc = 0.0

        if self._fg_inc:
            self.fg += self._fg_inc
            self._fg_inc = 0.0

        if self._s_inc:
            self.s += self._s_inc
            self.fr = (1.0-self.s) * self.fg
            self._s_inc = 0.0

        if self.run:
            self.thg = (self.thg + dt * self.fg * 2 * pi) % (2 * pi)
            self.ths = (self.ths + dt * self.fs * 2 * pi) % (2 * pi)
            self.thr = (self.thr + dt * self.fr * 2 * pi) % (2 * pi)
            self.t += dt

        self.update_info()


    # ------------------------------- end of refresh -------------------------------------


    def draw_all(self, *args, **kwargs):
        for part in self.prims:
            for group in self.prims[part]:
                for prim in self.prims[part][group]:
                    prim.draw( *args, **kwargs)

    def update_info(self):
        um_name = self.display_mu.current_key
        um_factor = self.display_mu[um_name]
        um_name_g = um_name if um_name != 'rpm' else 'Hz'
        um_factor_g = self.display_mu[um_name_g]
        um_max_len = 0
        for um in self.display_mu:
            um_max_len = max(len(um), um_max_len)

        self.widgets['w_stator']   .config(text=f"  vel. estator: {self.fs*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['w_grid'].config(
            text=f"    vel. alim.: {self.fg * um_factor_g:>5.1f} {um_name_g}{' ' * (um_max_len - len(um_name_g))}")
        self.widgets['w_rotor']    .config(text=f"    vel. rotor: {self.fr*um_factor  :>5.1f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['slip'].config(text=f"         slip: {self.mit.s  :>6.2f} pu{' ' * (um_max_len)}")
        self.widgets['time_factor'].config(text=f"time reduction: {self.time_factor:>5.1f} x")
        self.widgets['frame_delay'].config(text=f"   frame delay: {self.frame_delay:>5} ms")

    def update_esp_and_cutout_visibility(self):
        parts = ['stator', 'rotor']
        groups = ['esp', 'cutout', 'cutout_outline']
        n = {'stator': self.slots_ns, 'rotor': self.slots_nr, 'extra_s': self.slots_ns, 'extra_r': self.slots_nr}
        if self.slots_ns == 1:
            for part in parts:
                for group in groups:
                    for k, prims in enumerate(self.prims[part][group]):
                        if ((k + 1) // n[part] % 3) != 2:
                            self.prims[part][group][k].visible = False
        else:
            for part in parts:
                for group in groups:
                    for k, prims in enumerate(self.prims[part][group]):
                        self.prims[part][group][k].visible = True

        parts = ['extra_s', 'extra_r']
        groups = ['esp_front']
        if self.slots_ns == 1:
            for part in parts:
                for group in groups:
                    for k, prims in enumerate(self.prims[part][group]):
                        if ((k + 1) // n[part] % 3) != 2:
                            self.prims[part][group][k].visible = False
        else:
            for part in parts:
                for group in groups:
                    visible = False
                    for k, prims in enumerate(self.prims[part][group]):
                        visible |= self.prims[part][group][k].visible
                    for k, prims in enumerate(self.prims[part][group]):
                        self.prims[part][group][k].visible = visible

    def binds(self) -> None:

        def show_binds():
            current_state = self.run
            self.run = False
            messagebox.showinfo("binds", binds_message)
            self.run = current_state

        def toggle_run():
            self.run = not self.run

        def inc_value(var_name: Literal['ws', 'wr', 'we'],  increment: float,  v_min= -9.9, v_max= 9.9):
            match var_name:
                case 'fs':
                    self._fs_inc = clip(self.fs + increment, v_min, v_max) - self.fs
                case 's':
                    self._s_inc = clip(self.s + increment, v_min, v_max) - self.s
                case 'fg':
                    self._fg_inc = clip(self.fg + increment, v_min, v_max) - self.fg
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
            self.thg = 0.0
            self.thr = 0.0
            self.ths = 0.0

            if reset_and_stop:
                self.run = False
                self.draw_all()

        def change_display_mu():
            next(self.display_mu)
            self.update_info()

        def change_display(ax=1):
            match ax:
                case 0:
                    next(self.display_mit_ax0)
                    nans = np.empty(self.ax_npt, float)
                    nans.fill(np.nan)
                    for ys in self.plt_vgs:
                        ys.extend(nans)

                case 1:
                    next(self.display_mit_ax1)
                case _: raise ValueError('valor inválido para ax')

        def toggle_visibility(parts: Literal['stator', 'rotor'], groups: str | None = None):

            # todo: naão funciona 'e'->'n'->'e'
            # if parts in ['extra_s', 'extra_r']:
            #     if groups in ['esp_front']:
            #         update_esp_and_cutout_visibility()
            #         return




            if isinstance(parts, str):
                parts = [parts]
            if isinstance(groups, str):
                groups = [groups]

            # print(parts,groups )

            first_visibility = False
            for part in parts:
                if groups:
                    for group in groups:
                        for p in self.prims[part][group]:
                            if p.visible:
                                first_visibility = True or first_visibility
                else:
                    for group in self.prims[part]:
                        for p in self.prims[part][group]:
                            if p.visible:
                                first_visibility = True or first_visibility

                # print(first_visibility)

            # first_visibility = None
            # if isinstance(parts, str):
            #     parts = [parts]
            for part in parts:
                if groups:
                    # if isinstance(groups, str):
                        # groups = [groups]
                    for group in groups:
                        for p in self.prims[part][group]:
                            # if first_visibility == None:
                                # first_visibility = not p.visible
                            p.visible = not first_visibility
                else:
                    for group in self.prims[part]:
                        for p in self.prims[part][group]:
                            # if first_visibility == None:
                            #     first_visibility = not p.visible
                            p.visible = not first_visibility

            self.update_esp_and_cutout_visibility()




        def change_nesp():
            self.slots_ns = self.slots_ns_alt if self.slots_ns == 1 else 1
            self.slots_nr = self.slots_nr_alt if self.slots_nr == 1 else 1
            # print(self.ns, self.nr, )
            self.update_esp_and_cutout_visibility()

        def change_esp_front_opacity():
            next(self.esp_front_opacity)

            parts = ['extra_s', 'extra_r']
            groups = ['esp_front']
            for part in parts:
                for group in groups:
                    for k, prims in enumerate(self.prims[part][group]):
                        self.prims[part][group][k].stipple = self.esp_front_opacity.current_key



        dw_inc = 0.83333333333333333333333333
        f_max = 70
        self.widgets['Tcarga'].configure(variable=self.dynamic_colors)
        self.canvas.window.bind('o', lambda event: change_esp_front_opacity())
        self.canvas.window.bind('+', lambda event: inc_value('fs', 1, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('fs', -1, -f_max, f_max))
        self.canvas.window.bind('<Right>', lambda event: inc_value('s', -0.01, -0.2, 2.2))
        self.canvas.window.bind('<Left>',  lambda event: inc_value('s', 0.01, -0.2, 2.2))
        self.canvas.window.bind('<Up>',    lambda event: inc_value('fg', dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Down>',  lambda event: inc_value('fg', -dw_inc, -f_max, f_max))
        self.canvas.window.bind('n', lambda event: change_nesp())

        self.canvas.window.bind('.', lambda event: inc_value('time_factor', self.time_factor*.2, 32.45273575943723503208293147346, 1492.992))
        self.canvas.window.bind(',', lambda event: inc_value('time_factor', -self.time_factor*.16666666666666666666666666666667, 32.45273575943723503208293147346, 1492.992))

        self.canvas.window.bind('m', lambda event: change_display_mu() )
        self.canvas.window.bind('*',       lambda event: inc_value('delay', 1, 0, 30))
        self.canvas.window.bind('/',       lambda event: inc_value('delay', -1, 0, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())

        self.widgets['canvas_fig0'].get_tk_widget().bind('<Button-1>', lambda event: change_display(0))
        self.widgets['canvas_fig1'].get_tk_widget().bind('<Button-1>', lambda event: change_display(1))
        # self.canvas.window.bind('<Button-1>', lambda event: toggle_run())
        # self.canvas.window.bind('<Button-3>', lambda event: show_binds())

        # self.canvas.window.bind('<Return>', lambda event: toggle_run())
        self.canvas.window.bind('<F1>', lambda event: show_binds())
        self.canvas.window.bind('<Escape>', lambda event: reset_time(reset_and_stop=True))
        self.canvas.window.bind('<0>',     lambda event: reset_time())
        self.canvas.window.bind('r',       lambda event: toggle_visibility('rotor'))
        self.canvas.window.bind('s',       lambda event: toggle_visibility('stator'))
        self.canvas.window.bind('[', lambda event: toggle_visibility('stator', 'axis'))
        self.canvas.window.bind(']', lambda event: toggle_visibility('rotor', 'axis'))
        self.canvas.window.bind('f',       lambda event: toggle_visibility('extra_s', 'flux_s'))
        self.canvas.window.bind('a',       lambda event: toggle_visibility('extra_s', 'flux_a'))
        self.canvas.window.bind('b',       lambda event: toggle_visibility('extra_s', 'flux_b'))
        self.canvas.window.bind('c',       lambda event: toggle_visibility('extra_s', 'flux_c'))
        self.canvas.window.bind('e',       lambda event: toggle_visibility('extra_s', 'esp_front'))
        self.canvas.window.bind('x',       lambda event: toggle_visibility(['extra_s', 'extra_r']))
        self.canvas.window.bind('g',       lambda event: toggle_visibility('extra_r', 'esp_front'))

class CircularDict(dict):
    def __init__(self, *args):
        dict()
        super().__init__(*args)
        keys = list(self.keys())
        self._current_key = keys[0]

    @property
    def current_key(self):
        return self._current_key

    @current_key.setter
    def current_key(self, value):
        if value not in list(self.keys()):
            raise ValueError(f"a 'key' fornecida não faz parte do dicionário. São chaves válidas {list(self.keys())}")
        self._current_key = value


    @property
    def current_value(self):
        return self[self._current_key]

    def __next__(self):
        keys = list(self.keys())
        self._current_key = keys[(keys.index(self._current_key) + 1) % len(keys)]
        return self._current_key



