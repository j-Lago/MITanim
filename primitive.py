from NormCanvas import NormCanvas
from transforms import Coords, Point, Numeric, denorm_coords
from math import sqrt
import transforms
from typing import Literal
from copy import copy, deepcopy


class Primitive:
    def __init__(self, canvas: NormCanvas,
                 shape: Literal['line', 'polygon', 'rectangle', 'square', 'circle', 'oval', 'arc'],
                 coords: Coords,
                 **kwargs):
        """
        """
        self._canvas = canvas
        self._handle = None
        self.coords = coords
        self.original_coords = coords
        self.shape = shape


        self._create(**kwargs)


    @staticmethod
    def merge(primitives_list, merge_into_id: int = 0):
        coords = []
        merged = primitives_list[merge_into_id]

        first_shape = merged.shape
        for p in primitives_list:
            if p.shape != first_shape:
                raise ValueError(f"só é suportado combinar primitivas de mesmo 'shape': {first_shape=} != {p.shape=}")
            coords.append(p.coords)

        merged.coords = tuple(v for pt in coords for v in pt)

        return merged

    @property
    def arrow(self) -> str:
        return self._canvas.itemcget(self._handle, 'arrow')

    @arrow.setter
    def arrow(self, arrow):
        self._canvas.itemconfig(self._handle, arrow=arrow)

    @property
    def arrowshape(self) -> str:
        return self._canvas.itemcget(self._handle, 'arrowshape')

    @arrowshape.setter
    def arrowshape(self, arrowshape):
        self._canvas.itemconfig(self._handle, arrowshape=arrowshape)

    @property
    def fill(self) -> str:
        return self._canvas.itemcget(self._handle, 'fill')

    @fill.setter
    def fill(self, fill):
        self._canvas.itemconfig(self._handle, fill=fill)

    @property
    def stroke(self) -> str:
        key = 'outline' if self.shape != 'line' else 'fill'
        return self._canvas.itemcget(self._handle, key)

    @stroke.setter
    def stroke(self, stroke):
        if self.shape != 'line':
            self._canvas.itemconfig(self._handle, outline=stroke)
        else:
            self._canvas.itemconfig(self._handle, fill=stroke)

    @property
    def width(self) -> str:
        return self._canvas.itemcget(self._handle, 'width')

    @width.setter
    def width(self, width):
        self._canvas.itemconfig(self._handle, width=width)

    @property
    def visible(self) -> str:
        return self._canvas.itemcget(self._handle, 'state') != 'hidden'

    @visible.setter
    def visible(self, visible):
        self._canvas.itemconfig(self._handle, state='normal' if visible else 'hidden')

    def reset_transformations(self):
        self.coords = self.original_coords

    def reverse(self, from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.reverse(coords)
        return self

    def rotate(self, angle: Numeric, center: Point = (0, 0), from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.rotate(coords, angle, center)
        return self

    def translate(self, offset: Point, from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.translate(coords, offset)
        return self

    def scale(self, factor: Numeric | Point, center: Point = (0, 0), from_original: bool = False):
        coords = self.original_coords if from_original else self.coords
        self.coords = transforms.scale(coords, factor, center)
        return self

    def _create(self, **kwargs):
        # print('... >> ', kwargs)
        kwargs['outline'] = kwargs.pop('stroke', '')
        match self.shape:
            case 'line':
                kwargs['fill'] = kwargs.pop('outline', kwargs.pop('fill', ''))
                # print('line>> ', kwargs)
                self._handle = self._canvas.create_line(self.denorm_coords(), **kwargs)
            case 'polygon':
                self._handle = self._canvas.create_polygon(self.denorm_coords(), **kwargs)
            case 'rectangle':
                self._handle = self._canvas.create_rectangle(self.denorm_coords(), **kwargs)
            case 'oval':
                raise ValueError(f"'primitive_type' ({self.shape}) inválido")
            case 'circle':
                self._handle = self._canvas.create_oval(self._denorm_coords_circle_to_oval(), **kwargs)
            case 'arc':
                raise ValueError(f"'primitive_type' ({self.shape}) inválido")
            case _:
                raise ValueError(f"'primitive_type' ({self.shape}) inválido")
        self.draw()

    def draw(self,
             reset_transforms_to_original_after_draw: bool = True,
             consolidate_transforms_to_original: bool = False,
             **kwargs):

        self._canvas.coords(self._handle, self.denorm_coords())
        self._canvas.itemconfig(self._handle, **kwargs)

        if consolidate_transforms_to_original:
            self.original_coords = self.coords
        else:
            if reset_transforms_to_original_after_draw:
                self.coords = self.original_coords



    def denorm_coords(self) -> Coords:
        if self.shape == 'circle' and len(self.coords) == 3:
            ret = self._denorm_coords_circle_to_oval()
            return ret

        return denorm_coords(self._canvas, self.coords)

    def _denorm_coords_circle_to_oval(self) -> Coords:
        oval_coords = transforms.coords_circle_to_oval(self.coords)
        return denorm_coords(self._canvas, oval_coords)
