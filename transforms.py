from math import sin, cos, pi, atan2, sqrt
import typing
from copy import copy

type Numeric = float or int
type Coords = list[Numeric, ...] or tuple[Numeric, ...]
type Point = tuple[Numeric, Numeric]


def translate(coords: Coords, offset: Point) -> Coords:
    input_type = type(coords)

    if len(coords) == 3:
        return input_type((coords[0] + offset[0], coords[1] + offset[1], coords[2]))
    else:
        return input_type(v + offset[i % 2] for i, v in enumerate(coords))


def scale(coords: Coords, factor: Numeric | Point, center: Point = (0, 0)) -> Coords:
    input_type = type(coords)

    if len(coords) == 3:
        return input_type(((coords[0]-center[0])*factor+center[0], (coords[1]-center[1])*factor+center[1], coords[2]*factor))
    else:
        if isinstance(factor, float | int):
            print(factor)
            factor = (factor, factor)
        return input_type(factor[i_xy := i % 2] * (v-center[i % 2]) + center[i_xy] for i, v in enumerate(coords))


def reverse(coords: Coords) -> Coords:
    input_type = type(coords)

    original = copy(coords)
    L = len(original)//2
    pairs = (zip(coords[::2], coords[1::2]))  # (x0, y0, x1, y1, ...) -> ((x0, y0), (x1, y1), ...)
    pairs = ( (original[-i*2], original[-i*2-1])  for i in range(L) )
    coords = (v for pt in pairs for v in pt)  # ((x0, y0), (x1, y1), ...) -> (x0, y0, x1, y1, ...)
    return input_type(coords)

def rotate(coords: Coords, angle: Numeric, center: Point = (0, 0)) -> Coords:
    input_type = type(coords)

    c = cos(angle)
    s = sin(angle)
    x0, y0 = center

    if len(coords) == 3:
        x, y, r = coords
        return input_type(( (dx := x-x0) * c - (dy := y-y0) * s + x0,  dx * s + dy * c + y0, r))
    else:
        pairs = (zip(coords[::2], coords[1::2]))    # (x0, y0, x1, y1, ...) -> ((x0, y0), (x1, y1), ...)
        pairs = (((dx := x-x0) * c - (dy := y-y0) * s + x0, dx * s + dy * c + y0) for x, y in pairs)
        coords = (v for pt in pairs for v in pt)    # ((x0, y0), (x1, y1), ...) -> (x0, y0, x1, y1, ...)
        return input_type(coords)

def denorm_coords(canvas, coords) -> tuple:
    input_type = type(coords)
    base = min(canvas.winfo_width(), canvas.winfo_height()) // 2
    center = (canvas.winfo_width() / 2), (canvas.winfo_height() / 2)
    return input_type(v * (base, -base)[i_xy := k % 2] + center[i_xy] for k, v in enumerate(coords))

def coords_circle_to_oval(coords) -> Coords:
    input_type = type(coords)

    # print(self.coords)
    match len(coords):
        case 3:                         # circulo definido pelo centro e raio coords = (x0, y0, r)
            x0, y0, r = coords

        case 4:                         # circulo definido pelo centro e ponto de intersecção coords = (x0, y0, x1, y1)
            x0, y0, x1, y1 = coords
            r = sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

        case _:
            raise ValueError(f'círculo são definidos por 3 ou 4 valores, foi recebido {len(coords)=}')

    return input_type((x0 - r, y0 - r, x0 + r, y0 + r))


def clip(v: Numeric, v_min: Numeric, v_max) -> Numeric:
    return max(min(v, v_max), v_min)


def rgb_to_hex(r, g, b) -> str:
    if isinstance(r, float) and isinstance(g, float) and isinstance(b, float):
        r *= 255
        g *= 255
        b *= 255

    r = clip(int(r), 0, 255)
    g = clip(int(g), 0, 255)
    b = clip(int(b), 0, 255)

    return f'#{r:02x}{g:02x}{b:02x}'