import tkinter as tk
from math import sin, cos, pi, atan2, sqrt
from tools import denorm_base, denorm_points
from NormCanvas import NormCanvas


class Vec:
    def __init__(self, x=0.0, y=0.0):
        self._x = x
        self._y = y

    @property
    def x(self): return self._x

    @property
    def y(self): return self._y

    @property
    def abs(self):
        return sqrt(self._x ** 2 + self._y ** 2)

    # @abs.setter
    # def abs(self, value):
    #     th = self.th
    #     self._x = value * cos(th)
    #     self._y = value * sin(th)

    @property
    def th(self):
        return atan2(self._y, self._x)

    @th.setter
    def th(self, value):
        amp = self.abs
        self._x = amp * cos(value)
        self._x = amp * sin(value)

    @property
    def rect(self): return self._x, self._y

    @rect.setter
    def rect(self, value: tuple[float, float]):
        self._x = value[0]
        self._y = value[1]

    @property
    def polar(self): return self.abs, self.th

    @polar.setter
    def polar(self, value: tuple[float, float]):
        self._x = value[0] * cos(value[1])
        self._y = value[0] * sin(value[1])



class gVec(Vec):
    def __init__(self, canvas: NormCanvas, amp, th, x0=0.0, y0=0.0, width=7, color='#000000', arrowshape=(.083, .09, .025)):
        self.canvas = canvas
        self.x0, self.y0 = (x0, y0)
        self.polar = amp, th
        self.arrowshape = arrowshape

        self.line = self.canvas.create_line(self.x0, self.y0, self.x, self.y, width=width, arrow='last', arrowshape=self.arrowshape, fill=color)


    def refresh(self):
        # print('refresh ', self.rect)
        self.canvas.coords(self.line,
                           self.x0, self.y0,
                           self.x0+self._x, self.y0+self._y)

        THRESHOLD = .25
        if abs(self.abs) < THRESHOLD:
            arrowshape = tuple(float(e*abs(self.abs)/THRESHOLD) for e in self.arrowshape)
            self.canvas.itemconfig(self.line, arrowshape=arrowshape)

    def set_visibility(self, visible):
        if visible:
            self.canvas.itemconfig(self.line, state='normal')
        else:
            self.canvas.itemconfig(self.line, state='hidden')


        
