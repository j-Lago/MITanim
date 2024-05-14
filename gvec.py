from NormCanvas import NormCanvas
from math import sin, cos, pi, atan2, sqrt
from primitive import Primitive


class GraphicVec2(Primitive):
    def __init__(self,
                 real: float, imag: float,
                 canvas: NormCanvas,
                 origin: tuple | complex = complex(0.0, 0.0),
                 arrow_fade_threshold=0.25,
                 arrowshape=(25, 28, 8),
                 stroke='#000000',
                 width=8,
                 **line_kwargs):


        vec = complex(real, imag)

        origin = origin if isinstance(origin, complex) else complex(*origin)

        if line_kwargs.pop('transforms', None):
            raise ValueError("'GraphicVec2' não possui o parâmetro 'transforms'")

        coords = (origin.real, origin.imag, origin.real+vec.real, origin.imag+vec.imag)
        super().__init__(canvas, shape='line', coords=coords, width=width, arrowshape=arrowshape, arrow='last', stroke=stroke, **line_kwargs, dont_draw=True)

        self.vec = vec
        self.origin = origin
        self.arrow_fade_threshold = arrow_fade_threshold
        self._arrowshape = arrowshape

    # @property
    # def _handle(self):
    #     return self.line._handle

    @property
    def coords(self):
        return tuple((self.origin.real, self.origin.imag, self.vec.real, self.vec.imag))

    @coords.setter
    def coords(self, coords):
        match len(coords):
            case 2:
                self.vec = complex(coords[0], coords[1])
            case 4:
                self.origin = complex(coords[0], coords[1])
                self.vec = complex(coords[2]-coords[0], coords[3]-coords[1])
            case _: raise ValueError(f"coord' deve ser 2 (x, y) ou 4 (x0, y0, x, y) elementos" )

        self._canvas.coords(self._handle, self.denorm_coords())



    def draw(self, **kwargs):
        self.coords = (self.origin.real, self.origin.imag, self.origin.real+self.vec.real, self.origin.imag+self.vec.imag)

        if abs(abs(self.vec)) < self.arrow_fade_threshold:
            arrowshape = tuple(float(e * abs(self.vec) / self.arrow_fade_threshold) for e in self._arrowshape)
            self._canvas.itemconfig(self._handle, arrowshape=arrowshape)

        self._canvas.coords(self._handle, self.denorm_coords())
        self._canvas.itemconfig(self._handle, **kwargs)



    # def set_visibility(self, visible):
    #     if visible:
    #         self.canvas.itemconfig(self.line, state='normal')
    #     else:
    #         self.canvas.itemconfig(self.line, state='hidden')
