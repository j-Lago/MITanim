import tkinter as tk
from NormCanvas import NormCanvas
from custom_animation import CustomAnim
from assets import cl
import numpy as np
from math import sin, cos, sqrt, pi, atan2, fabs

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)




def main():

    WIDTH, HEIGHT = 700, 700

    window = tk.Tk()
    window.title("Motor de Indução Trifásico")
    window.configure(background=cl['bg'])
    canvas = NormCanvas(window, bg=cl['bg'], height=HEIGHT, width=WIDTH, highlightbackground=cl['bg'])

    fig0, _ = plt.subplots(1, 1, figsize=(6, 3), dpi=100)
    fig1, _ = plt.subplots(1, 1, figsize=(6, 3), dpi=100)


    fonts = {
        'default': ('Courier', 16),
        'fps': ('Poor Richard', 14),
    }

    infos = tk.Frame(window, bg=cl['bg'])
    controls = tk.Frame(window, bg=cl['bg'])

    # teste = tk.Checkbutton(controls, text='Use Metric')
    # teste.state()

    widgets = {
        'fps': tk.Label(window, text='fps:', font=fonts['fps'], fg='#bb5533', bg=cl['bg']),
        'canvas_fig0': FigureCanvasTkAgg(fig0, master=infos),
        'canvas_fig1': FigureCanvasTkAgg(fig1, master=infos),
        'w_stator': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'w_rotor': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'w_grid': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'slip': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'time_factor': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'frame_delay': tk.Label(infos, text='...', font=fonts['default'], bg=cl['bg']),
        'Tcarga': tk.Checkbutton(controls, text='windings dynamic colors', bg=cl['bg']),
        'figs': [fig0, fig1],
    }

    widgets['canvas_fig0'].get_tk_widget().pack(anchor='ne', side='top', expand=0)
    widgets['canvas_fig1'].get_tk_widget().pack(anchor='ne', side='top', expand=0)
    widgets['fps'].pack(anchor='w', fill='none', side='top')
    widgets['w_stator'].pack(anchor='w', fill='none', side='top')
    widgets['w_grid'].pack(anchor='w', fill='none', side='top')
    widgets['w_rotor'].pack(anchor='w', fill='none', side='top')
    widgets['slip'].pack(anchor='w', fill='none', side='top')
    widgets['time_factor'].pack(anchor='w', fill='none', side='top', expand=0)
    widgets['frame_delay'].pack(anchor='w', fill='none', side='top')

    widgets['Tcarga'].pack(anchor='w', fill='none', side='bottom')
    controls.pack(side='right')
    infos.pack(side='right')

    canvas.pack()
    window.update()

    anim = CustomAnim(canvas, widgets)
    anim.loop()
    window.mainloop()


if __name__ == '__main__':
    main()
