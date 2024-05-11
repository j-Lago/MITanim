import tkinter as tk
import numpy as np
from tkinter import messagebox
from math import sin, cos, pi, atan2, sqrt, fabs
from NormCanvas import NormCanvas
from primitive import Primitive
from transforms import translate, rotate, scale, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip
import time
from assets import assets, cl, binds_message
from animation import Animation
from collections import deque
from statistics import mean
from typing import Literal

class CustomAnim(Animation):
    def __init__(self, canvas: NormCanvas, widgets: dict):
        super().__init__(canvas, frame_delay=0)

        self.widgets = widgets

        self.t = 0.0
        self.ths = 0.0
        self.thr = 0.0
        self.the = 0.0
        self.fs = 0.0
        self.fr = 55
        self.fg = 60
        self.time_factor = 140

        self.display_mu = CircularDict({'Hz': 1.0, 'rad/s': 2*pi, 'rpm': 60})
        self.display_mu.current_key = 'rpm'


        self.dt_filter_buffer = deque(maxlen=100)
        self.dc_filter_buffer = deque(maxlen=100)
        self.update_info()

        npt = 150
        marker_size = 8
        markers = ('o', 'o', 'o')

        self.plt_t_range = .05  #(2 * pi * 3) / self.fg
        axs = self.widgets['figs'][0].axes

        nans = np.empty(npt, float)
        nans.fill(np.nan)


        t = np.arange(-self.plt_t_range, 0.0, self.plt_t_range / npt)
        self.plt_vgs = (deque(maxlen=npt), deque(maxlen=npt), deque(maxlen=npt))
        for ys in self.plt_vgs:
            ys.extend(nans)
        self.plt_t = deque(maxlen=npt)
        self.plt_t.extend(t)

        self.plt_lines = {
            # 'vg_line': (axs[0].plot((0, 0), (-2, 2), '-.k', lw=1.5))[0],
            'vg_a': (axs[0].plot(self.plt_t, self.plt_vgs[0], color=cl['a'], lw=2))[0],
            'vg_b': (axs[0].plot(self.plt_t, self.plt_vgs[1], color=cl['b'], lw=2))[0],
            'vg_c': (axs[0].plot(self.plt_t, self.plt_vgs[2], color=cl['c'], lw=2))[0],
            'vg_a_marker': (axs[0].plot(0, 0, color=cl['a'], marker=markers[0], markersize=marker_size, lw=2))[0],
            'vg_b_marker': (axs[0].plot(0, 0, color=cl['b'], marker=markers[1], markersize=marker_size, lw=2))[0],
            'vg_c_marker': (axs[0].plot(0, 0, color=cl['c'], marker=markers[2], markersize=marker_size, lw=2))[0],
        }
        axs[0].set_ylim(-1.2, 1.2)
        axs[0].set_xlim(-self.plt_t_range, 0.0)
        axs[0].set_xticks([])

        widgets['canvas_fig0'].draw()

        self.run = True


        self.prims = {'stator': {},
                      'rotor': {},
                      'extra_s': {},
                      'extra_r': {},
                      }


        self.prims['stator']['core'] = [
            self.create_primitive(**assets['mount']),
            self.create_primitive(**assets['mount']).scale((-1.0,1.0)),
            self.create_primitive(**assets['stator_outer']),
            self.create_primitive(**assets['stator_inner']),
            *(self.create_primitive(**assets['stator_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
            *(self.create_primitive(**assets['stator_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
        ]

        self.prims['rotor']['core'] = [
            self.create_primitive(**assets['rotor_outer']),
            *(self.create_primitive(**assets['rotor_cutout']).rotate(2 * pi / 6 * i) for i in range(6)),
            *(self.create_primitive(**assets['rotor_cutout_outline']).rotate(2 * pi / 6 * i) for i in range(6)),
            self.create_primitive(**assets['shaft']),
            self.create_primitive(**assets['keyway']),
            self.create_primitive(**assets['keyway_outline']),
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

        t = pi
        self.prims['extra_s']['flux_a'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
        ]

        t = 2 * pi / 3 + pi
        self.prims['extra_s']['flux_b'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
        ]
        for p in self.prims['extra_s']['flux_b']: p.stroke = cl['b']

        t = -2 * pi / 3 + pi
        self.prims['extra_s']['flux_c'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
        ]
        for p in self.prims['extra_s']['flux_c']: p.stroke = cl['c']

        t = pi
        self.prims['extra_s']['flux_s'] = [
            (self.create_primitive(**assets['quarter_flux'])).reverse().rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.8, .77), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.8, .77), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, 1)).scale((.65, .5), center=(
            0.0, -0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).scale((-1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
            (self.create_primitive(**assets['quarter_flux'])).reverse().scale((1, -1)).scale((.65, .5), center=(
            0.0, 0.50571428571428571428571428571429)).rotate(t),
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

        # self.prims['rotor']['core'].append(self.create_primitive(**assets['shaft']))
        # self.prims['rotor']['core'].append(self.create_primitive(**assets['keyway']))
        # self.prims['rotor']['core'].append(self.create_primitive(**assets['keyway_outline']))

        self.draw_all(consolidate_transforms_to_original=True)

    def refresh(self, _, dt, frame_count):

        self.dt_filter_buffer.append(dt)
        fps = 1 / mean(self.dt_filter_buffer)
        self.widgets['fps'].config(text=f"fps: {fps:.0f}")

        # animation clock
        dt /= self.time_factor

        currents_s = tuple(sin(self.the - pi / 2 - 2 * pi / 3 * k) for k in range(3))

        # plot resample
        if self.run:
            m = max(min(self.fg / 60, 1.0), -1.0)
            for phases in range(3):
                self.plt_vgs[phases].append(currents_s[phases] * m)
            self.plt_t.append(self.t)


        redraw_plt = frame_count % 2 == 0
        phases = ('a', 'b', 'c')
        if redraw_plt:
            for k, phase in enumerate(phases):
                self.plt_lines['vg_' + phase].set_ydata(self.plt_vgs[k])
                self.plt_lines['vg_' + phase].set_xdata(self.plt_t)
                self.plt_lines['vg_' + phase + '_marker'].set_ydata((self.plt_vgs[k][-1], self.plt_vgs[k][-1]))
                self.plt_lines['vg_' + phase + '_marker'].set_xdata((self.plt_t[-1], self.plt_t[-1]))
            # self.plt_lines['vg_line'].set_ydata((-2, 2))
            # self.plt_lines['vg_line'].set_xdata((self.plt_t[-1], self.plt_t[-1]))
            pad = 0.1 / self.time_factor
            t_max = max(self.plt_t)+pad
            t_min = min(self.plt_t)+pad
            self.widgets['figs'][0].axes[0].set_xlim(t_min, t_max)


        # cores dinâmicas baseadas nas correntes do estator
        colors_s =[]
        for k, v in enumerate(currents_s):
            rgb = hex_to_rgb((cl['a'], cl['b'], cl['c'])[k % 3])
            # f = fabs(currents_s[k % 3])
            f = abs(currents_s[k % 3])
            colors_s.append(rgb_to_hex(scale_hsl(rgb, hue=1, sat=(1-f)*0.05+0.95, lum=sqrt(f) * 1.2)))

        # stator
        for part in ['stator', 'extra_s']:
            for group in self.prims[part]:
                for prims in self.prims[part][group]:
                    prims.rotate(self.ths)

        for k, prims in enumerate(self.prims['stator']['esp']):
            prims.fill = colors_s[k%3]
        for k, prims in enumerate(self.prims['extra_s']['esp_front']):
            prims.fill = colors_s[k % 3]

        # rotor
        for part in ['rotor', 'extra_r']:
            for group in self.prims[part]:
                for prims in self.prims[part][group]:
                    prims.rotate(self.thr)

        # abc flux animation
        groups = ['flux_a', 'flux_b', 'flux_c']
        tip = assets['quarter_flux']['arrowshape']
        max_width = 6
        for phase_id in range(3):
            if self.prims['extra_s'][groups[phase_id]][0].visible:
                th = self.the + 2 * pi / 3
                for prims in *self.prims['extra_s'][groups[phase_id]],:
                    s = currents_s[phase_id]
                    prims.arrowshape = (tip[0] * s, tip[1] * s, tip[2] * fabs(s))
                    prims.width = max_width * fabs(s)
                    prims.fill = colors_s[phase_id]

        # stator flux animation
        if self.prims['extra_s']['flux_s'][0].visible:
            for p in *self.prims['extra_s']['flux_s'],:
                p.rotate(self.the-pi)

        self.draw_all()

        if redraw_plt:
            self.widgets['figs'][0].canvas.draw()
            self.widgets['figs'][0].canvas.flush_events()

        if self.run:
            self.the = (self.the + dt * self.fg * 2 * pi) % (2 * pi)
            self.thr = (self.thr + dt * self.fr * 2 * pi) % (2 * pi)
            self.ths = (self.ths + dt * self.fs * 2 * pi) % (2 * pi)
            self.t += dt



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

        self.widgets['w_stator']   .config(text=f"  vel. estator: {self.fs*um_factor  :>5.0f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['w_rotor']    .config(text=f"    vel. rotor: {self.fr*um_factor  :>5.0f} {um_name}{' '*(um_max_len-len(um_name))}")
        self.widgets['w_grid']     .config(text=f"    vel. alim.: {self.fg*um_factor_g:>5.0f} {um_name_g}{' '*(um_max_len-len(um_name_g))}")
        self.widgets['time_factor'].config(text=f"time reduction: {self.time_factor:>5.0f} x")
        self.widgets['frame_delay'].config(text=f"   frame delay: {self.frame_delay:>5} ms")

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
                case 'ws':
                    self.fs = clip(self.fs + increment, v_min, v_max)
                case 'wr':
                    self.fr = clip(self.fr + increment, v_min, v_max)
                case 'we':
                    self.fg = clip(self.fg + increment, v_min, v_max)
                case 'delay':
                    self.frame_delay = int(clip(self.frame_delay + increment, v_min, v_max))
                case 'time_factor':
                    last = self.time_factor
                    self.time_factor = clip(self.time_factor + increment, v_min, v_max)
                    t_max = max(self.plt_t)
                    for k in range(len(self.plt_t)):
                        self.plt_t[k] = (self.plt_t[k] - t_max) * last / self.time_factor + t_max

            self.update_info()


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

        def change_display_mu():
            next(self.display_mu)
            self.update_info()

        dw_inc = 1
        f_max = 70
        self.canvas.window.bind('+', lambda event: inc_value('ws', dw_inc, -f_max, f_max))
        self.canvas.window.bind('-', lambda event: inc_value('ws', -dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Right>', lambda event: inc_value('wr', dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Left>',  lambda event: inc_value('wr', -dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Up>',    lambda event: inc_value('we', dw_inc, -f_max, f_max))
        self.canvas.window.bind('<Down>',  lambda event: inc_value('we', -dw_inc, -f_max, f_max))

        self.canvas.window.bind('.', lambda event: inc_value('time_factor', self.time_factor*.2, 32.45273575943723503208293147346, 1492.992))
        self.canvas.window.bind(',', lambda event: inc_value('time_factor', -self.time_factor*.16666666666666666666666666666667, 32.45273575943723503208293147346, 1492.992))

        self.canvas.window.bind('m', lambda event: change_display_mu() )
        self.canvas.window.bind('*',       lambda event: inc_value('delay', 1, 0, 30))
        self.canvas.window.bind('/',       lambda event: inc_value('delay', -1, 0, 30))
        self.canvas.window.bind('<space>', lambda event: toggle_run())
        self.canvas.window.bind('<Button-1>', lambda event: toggle_run())
        self.canvas.window.bind('<Button-3>', lambda event: show_binds())
        # self.canvas.window.bind('<Return>', lambda event: toggle_run())
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

