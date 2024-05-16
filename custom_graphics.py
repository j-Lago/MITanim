from primitive import Primitive, PrimitivesGroup
from assets import assets, cl
from transformations import translate, rotate, scale, reverse, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip, \
    CircularDict
from math import pi
from typing import Literal
from collections.abc import Iterator, Iterable


def synchronous_generator_draw(canvas, prims, coils_per_phase, phases=3):

    prims['stator'] = []

    prims['stator']['core'] = []
    prims['stator']['core']['mount'] = [
        Primitive(canvas, **assets[name := 'mount'], name=name),
        Primitive(canvas, **assets[name := 'mount'], name=name + '.mirrored', transforms=(scale, (-1.0, 1.0))),
    ]
    prims['stator']['core']['outer'] = Primitive(canvas, **assets[name := 'stator_outer'], name=name)
    prims['stator']['core']['inner'] = Primitive(canvas, **assets[name := 'stator_inner'], name=name)

    prims['stator']['core']['slots'] = create_circular_pattern(canvas,
                                                               ['stator_cutout', 'stator_cutout_outline'],
                                                               pattern=phases * coils_per_phase)

    prims['stator']['coil'] = []
    prims['stator']['coil']['a'] = create_circular_pattern(canvas, ['stator_esp'], pattern=ThreePhaseIndexIterator(phases * coils_per_phase, 0))
    prims['stator']['coil']['a'].stroke = cl['a']
    prims['stator']['coil']['a'].fill = cl['a']
    prims['stator']['coil']['b'] = create_circular_pattern(canvas, ['stator_esp'], pattern=ThreePhaseIndexIterator(phases * coils_per_phase, 1))
    prims['stator']['coil']['b'].stroke = cl['b']
    prims['stator']['coil']['b'].fill = cl['b']
    prims['stator']['coil']['c'] = create_circular_pattern(canvas, ['stator_esp'], pattern=ThreePhaseIndexIterator(phases * coils_per_phase, 2))
    prims['stator']['coil']['c'].stroke = cl['c']
    prims['stator']['coil']['c'].fill = cl['c']

    # prims['stator']['coil_front'] = create_circular_pattern(canvas, ['stator_esp_front'], pattern=ThreePhaseSkipIndexIterator(phases*coils_per_phase))
    # prims['stator']['coil_front'].stipple = 'gray50'
    # prims['stator']['coil_front'].fill = '#00ffaa'

    prims['rotor'] = []
    prims['rotor']['shaft'] = Primitive(canvas, **assets[name := 'shaft'], name=name)


def create_circular_pattern(canvas,
                            assets_keys: str | list,
                            pattern: Iterator | int  # iterator para filtrar elementos de cada fase ou int. caso seja int, iterator será range(int)
                            ):

    if isinstance(assets_keys, str):
        assets_keys = [assets_keys]

    if isinstance(pattern, int):
        pattern = range(pattern)

    n = len(pattern)
    pitch = 2 * pi / n
    start = 0 if (n//6) % 2 != 0 else pitch/2
    return [*(Primitive(canvas, **assets[name := key],
                        name=name + f'.rotated({start + pitch * i * 180 / pi:3.0f}°)',
                        transforms=(rotate, start + pitch * i)) for i in pattern for key in assets_keys)]


class ThreePhaseIndexIterator:
    def __init__(self, limit, phase=0):
        self.phase = limit-1 + (limit//3)*phase
        if limit == 6:
            self.phase += 1
        if limit == 24:
            self.phase += 11
        self.phase %= limit
        self.limit = limit
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ', self.limit, self.phase)

    def __len__(self):
        return self.limit

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        ret = (self.i + self.phase) % self.limit
        if self.i >= self.limit:
            raise StopIteration
        inc = 1 if self.i % (self.limit//2) < (self.limit//6-1) else 1+self.limit//3
        self.i += inc
        return ret

