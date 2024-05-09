import abc
from NormCanvas import NormCanvas
from time import time


class Animation(abc.ABC):
    def __init__(self, canvas: NormCanvas, frame_delay: int = 10):
        self._t_init = time()
        self._t_start = 0.0

        self.canvas = canvas
        self.frame_delay = frame_delay

    # @property
    # def t(self) -> float:
    #     return time() - self._t_init

    def _start_frame_time_counter(self) -> (float, float):
        # t = self.t
        t = time() - self._t_init
        dt = t - self._t_start

        self._t_start = t
        return t, dt

    def loop(self):
        t, dt = self._start_frame_time_counter()
        self.loop_update(t, dt)

        self.canvas.window.after(self.frame_delay, self.loop)

    @abc.abstractmethod
    def loop_update(self, t: float, dt: float, duty_cycle: float):
        pass
