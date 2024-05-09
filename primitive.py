from NormCanvas import NormCanvas
from transforms import Coords, Point, Numeric, denorm_coords
from math import sqrt
import transforms
from typing import Literal


class Primitive:
    def __init__(self, canvas: NormCanvas,
                 shape: Literal['line', 'polygon', 'rectangle', 'square', 'circle', 'oval', 'arc'],
                 coords: Coords,
                 width: int = 1,
                 stroke: str = '#000000',
                 fill: str = '',
                 state: Literal['normal', 'active', 'disabled', 'hidden'] = 'normal'):
        """
        """
        self._canvas = canvas
        self._handle = None
        self.coords = coords
        self.original_coords = coords

        self.shape = shape
        self.stroke = stroke
        self._fill = fill
        self.width = width
        self.state = state

    def reset_itemconfig(self):
        kwargs = {'width': self.width,
                  'state': self.state}

        if self._fill:
            kwargs['fill'] = self._fill
        if self.stroke:
            kwargs['outline'] = self.stroke

        self._canvas.itemconfig(self._handle, **kwargs)


    @property
    def fill(self) -> str:
        return self._fill

    @fill.setter
    def fill(self, fill):
        self._fill = fill
        self._canvas.itemconfig(self._handle, fill=fill)

    def reset_transformations(self):
        self.coords = self.original_coords

    def rotate(self, angle: Numeric, center: Point = (0, 0), from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.rotate(coords, angle, center)
        return self

    def translate(self, offset: Point, from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.translate(coords, offset)
        return self

    def scale(self, factor: Numeric, center: Point = (0, 0), from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.scale(coords, factor, center)
        return self

    def draw(self, coords: Coords | None = None, **kwargs):
        if coords:
            self.coords = coords

        if self._handle:
            self._canvas.coords(self._handle, self.denorm_coords())
        else:
            match self.shape:
                case 'line':
                    raise ValueError(f"'primitive_type' ({self.shape}) inválido")
                case 'polygon':
                    self._handle = self._canvas.create_polygon(self.denorm_coords(), outline=self.stroke,
                                                               fill=self._fill, width=self.width, state=self.state)
                case 'rectangle':
                    raise ValueError(f"'primitive_type' ({self.shape}) inválido")
                case 'oval':
                    raise ValueError(f"'primitive_type' ({self.shape}) inválido")
                case 'circle':
                    self._handle = self._canvas.create_oval(self._denorm_coords_circle_to_oval(), outline=self.stroke,
                                                            fill=self._fill, width=self.width, state=self.state)
                case 'arc':
                    raise ValueError(f"'primitive_type' ({self.shape}) inválido")
                case _:
                    raise ValueError(f"'primitive_type' ({self.shape}) inválido")
        self._canvas.itemconfig(self._handle, **kwargs)

    def denorm_coords(self) -> Coords:
        if self.shape == 'circle' and len(self.coords) == 3:
            ret = self._denorm_coords_circle_to_oval()
            return ret

        return denorm_coords(self._canvas, self.coords)

    def _denorm_coords_circle_to_oval(self) -> Coords:
        oval_coords = transforms.coords_circle_to_oval(self.coords)
        return denorm_coords(self._canvas, oval_coords)
