from primitive import Primitive, PrimitivesGroup
from assets import assets, cl
from transformations import translate, rotate, scale, reverse, rgb_to_hex, hex_to_rgb, scale_hsl, set_hsl, clip, \
    CircularDict
from math import pi


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
                                                               n=phases*coils_per_phase)

    prims['stator']['core']['coil'] = create_circular_pattern(canvas, ['stator_esp'], n=phases*coils_per_phase)
    prims['stator']['core']['coil'].stroke = '#ff0000'
    prims['stator']['core']['coil'].fill = '#00ffaa'
    prims['stator']['core']['coil'].width = 4

    prims['stator']['core']['coil_front'] = create_circular_pattern(canvas, ['stator_esp_front'], n=phases*coils_per_phase)
    prims['stator']['core']['coil_front'].stipple = 'gray50'
    prims['stator']['core']['coil_front'].fill = '#00ffaa'

    prims['rotor'] = []
    prims['rotor']['shaft'] = Primitive(canvas, **assets[name := 'shaft'], name=name)


def create_circular_pattern(canvas, assets_keys: str | list, n=6, picth_pattern='regular'):
    if isinstance(assets_keys, str):
        assets_keys = [assets_keys]

    pitch = 2 * pi / n
    return [*(Primitive(canvas, **assets[name := key],
                        name=name + f'.rotated({pitch * i * 180 / pi:3.0f}°)',
                        transforms=(rotate, pitch * i)) for i in range(n) for key in assets_keys)]
