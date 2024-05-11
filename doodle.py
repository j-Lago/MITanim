
from transforms import clip, rgb_to_hex, hex_to_rgb
from colorsys import hls_to_rgb, rgb_to_hls
from math import pi
# from collections import OrderedDict

def main():
    class CircularDict(dict):
        def __init__(self, *args):
            dict()
            super().__init__(*args)
            keys = list(self.keys())
            self._current_key = keys[0]

        @property
        def name(self):
            return self._current_key

        @property
        def ratio(self):
            return self[self._current_key]

        def __next__(self):
            keys = list(self.keys())
            self._current_key = keys[(keys.index(self._current_key) + 1) % len(keys)]
            return self._current_key


    um = CircularDict({'Hz': 1.0, 'rad/s': 2*pi, 'rpm': 60})
    print(um)
    print('..', um.name, um.ratio)
    next(um)
    print('>>', um.name, um.ratio)
    next(um)
    print('>>', um.name, um.ratio)
    next(um)
    print('>>', um.name, um.ratio)

    print('-----------')
    for u in um:
        print(u, um[u])



if __name__ == '__main__':
    main()