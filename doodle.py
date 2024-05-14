from MITsim import MITsim
from colorsys import hls_to_rgb, rgb_to_hls
from math import pi
# from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt

def main():
    base = 1 #11.26 * 4  / 1e3
    mit = MITsim(R1=14.7000 * base,
                 X1=14.9862 * base,
                 R2=10.5445 * base,
                 X2=22.4793 * base,
                 Rc=1.6261e+03 * base,
                 Xm=419.2075 * base,
                 V1=380.0,
                 f0=60.0,
                 p=2
                 )



    wrs = np.linspace(0, 377, 200)
    y0s = np.empty_like(wrs)
    y1s = np.empty_like(wrs)
    y2s = np.empty_like(wrs)
    for k, wr in enumerate(wrs):
        mit.wr = wr
        mit.solve()
        y0s[k] = abs(mit.Im)
        y1s[k] = abs(mit.I1)
        y2s[k] = mit.Tind

    print(mit.__dict__['Rc'])
    print(mit['I1'])

    plt.plot(wrs, y0s)
    plt.plot(wrs, y1s)
    plt.plot(wrs, y2s)
    plt.show()



if __name__ == '__main__':
    main()