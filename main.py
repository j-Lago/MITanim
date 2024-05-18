from GSanim import CustomAnim
# from custom_animation import CustomAnim

import tkinter as tk
from NormCanvas import NormCanvas
from assets import cl, fonts
import numpy as np
from math import sin, cos, sqrt, pi, atan2, fabs

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


def main():

    WIDTH, HEIGHT = 700, 700

    window = tk.Tk()
    window.title("Lab. Virtual de Máquinas Elétricas: Motor de Indução Trifásico")
    window.configure(background=cl['bg'])
    canvas = NormCanvas(window, bg=cl['bg'], height=HEIGHT, width=WIDTH, highlightbackground=cl['bg'])

    fig0, _ = plt.subplots(1, 1, figsize=(6, 3), dpi=90)
    fig1, _ = plt.subplots(1, 1, figsize=(6, 3), dpi=90)


    frames = tk.Frame(window, bg=cl['bg'])
    infos = tk.Frame(frames, bg=cl['bg'])
    plots = tk.Frame(frames, bg=cl['bg'])
    controls = tk.Frame(frames, bg=cl['bg'])

    # teste = tk.Checkbutton(controls, text='Use Metric')
    # teste.state()

    widgets = {
        'fps': tk.Label(window, text='fps:', font=fonts['fps'], fg='#bb5533', bg=cl['bg']),
        'canvas_fig0': FigureCanvasTkAgg(fig0, master=plots),
        'canvas_fig1': FigureCanvasTkAgg(fig1, master=plots),

        'w_stator': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'w_rotor': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'w_grid': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'slip': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'time_factor': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'Pconv': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),

        'sim_inertia': tk.Checkbutton(controls, text='Newton 2nd', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'rotor_field_lines': tk.Checkbutton(controls, text='Rotor field lines', font=fonts['default'],  bg=cl['bg'], fg=cl['default_font']),
        'rotor_field_vec': tk.Checkbutton(controls, text='Rotor field vector', font=fonts['default'],  bg=cl['bg'], fg=cl['default_font']),
        'stator_field_lines': tk.Checkbutton(controls, text='Stator field lines', font=fonts['default'],  bg=cl['bg'], fg=cl['default_font']),
        'stator_field_vec': tk.Checkbutton(controls, text='Stator field vector', font=fonts['default'],  bg=cl['bg'], fg=cl['default_font']),
        'stator_coil_front': tk.Checkbutton(controls, text='Stator coil front', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'rotor_coil_front': tk.Checkbutton(controls, text='Rotor coil front', font=fonts['default'], bg=cl['bg'], fg=cl['default_font']),
        'figs': [fig0, fig1],
    }

    widgets['canvas_fig0'].get_tk_widget().pack(anchor='ne', side='top', expand=0)
    widgets['canvas_fig1'].get_tk_widget().pack(anchor='ne', side='top', expand=0)
    widgets['fps'].pack(anchor='w', fill='none', side='top')
    widgets['w_stator'].pack(anchor='w', fill='none', side='top')
    widgets['w_rotor'].pack(anchor='w', fill='none', side='top')
    widgets['w_grid'].pack(anchor='w', fill='none', side='top')
    widgets['slip'].pack(anchor='w', fill='none', side='top')
    widgets['Pconv'].pack(anchor='w', fill='none', side='top')
    widgets['time_factor'].pack(anchor='w', fill='none', side='top', expand=0)

    widgets['sim_inertia'].pack(anchor='w', fill='none', side='bottom')
    widgets['stator_coil_front'].pack(anchor='w', fill='none', side='bottom')
    widgets['rotor_coil_front'].pack(anchor='w', fill='none', side='bottom')
    widgets['rotor_field_lines'].pack(anchor='w', fill='none', side='bottom')
    widgets['stator_field_lines'].pack(anchor='w', fill='none', side='bottom')
    widgets['rotor_field_vec'].pack(anchor='w', fill='none', side='bottom')
    widgets['stator_field_vec'].pack(anchor='w', fill='none', side='bottom')

    plots.pack(side='top')
    frames.pack(side='left')
    controls.pack(side='left')
    infos.pack(side='right')

    canvas.pack()
    window.update()

    anim = CustomAnim(canvas, widgets)
    anim.loop()

    window.mainloop()

if __name__ == '__main__':
    main()
