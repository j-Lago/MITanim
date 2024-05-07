from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import time

x = np.arange(0, 2*np.pi, 0.01)        # x-array


class Animation:
    def __init__(self):
        self.th = 0
        self.t = time()

        self.fig, self.ax = plt.subplots(nrows=1, ncols=1, figsize=(7, 7))
        self.line, = self.ax.plot(x, np.sin(x))

    def __iter__(self):
        return self

    def __next__(self):
        return self

    def step(self, i):
        t = time()
        dt = t-self.t
        self.ax.set_title(f'{1 / dt:.0f} fps')

        self.t = t
        self.th += 0.01

        self.line.set_ydata(np.sin(x+self.th))  # update the data


root = Tk.Tk()

label = Tk.Label(root,text="SHM Simulation").grid(column=0, row=0)

anim = Animation()

canvas = FigureCanvasTkAgg(anim.fig, master=root)
canvas.get_tk_widget().grid(column=0, row=1)



ani = animation.FuncAnimation(anim.fig, anim.step, interval=20, blit=False)

Tk.mainloop()