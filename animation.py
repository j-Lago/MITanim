import tkinter
from abc import ABC, abstractmethod
from NormCanvas import NormCanvas
from time import time
from primitive import Primitive


class Animation(ABC):
    def __init__(self, canvas: NormCanvas, frame_delay: int = 10):
        self._t_init = time()
        self._t_start = 0.0
        self._frame_count = 0

        self.canvas = canvas
        self.frame_delay = frame_delay
        self.canvas.window.protocol("WM_DELETE_WINDOW", self.window_close_button)
        self._task = None

    def create_primitive(self, *args, **kwargs) -> Primitive:
        return Primitive(self.canvas,  *args, **kwargs)

    def _start_frame_time_counter(self) -> (float, float, int):
        t = time() - self._t_init
        dt = t - self._t_start

        self._t_start = t
        self._frame_count += 1
        return t, dt, self._frame_count


    def window_close_button(self):
        if self._task is not None:
            self.canvas.window.after_cancel(self._task)
        self.canvas.window.destroy()


    def loop(self):
        t, dt, frame_count = self._start_frame_time_counter()
        self.refresh(t, dt, frame_count)

        self._task = self.canvas.window.after(self.frame_delay, self.loop)

    # @abstractmethod
    # def binds(self):
    #     pass
    #     window.bind('<Right>', lambda event: call_function_1())
    #     window.bind('<Left>',  lambda event: call_function_2())

    @abstractmethod
    def refresh(self, t: float, dt: float, frame_count: int):
        pass







