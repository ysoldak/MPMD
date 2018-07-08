#!/usr/bin/env python3

import sys

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

from scipy import interpolate

class Estimation():
        def __init__(self,datax,datay,dataz):
            self.x = datax
            self.y = datay
            self.v = dataz

        def estimate(self,x,y,using='ISD'):
            """
            Estimate point at coordinate x,y based on the input data for this
            class.
            """
            if using == 'ISD':
                return self._isd(x,y)

        def _isd(self,x,y):
            d = np.sqrt((x-self.x)**2+(y-self.y)**2)
            if d.min() > 0:
                v = np.sum(self.v*(1/d**2)/np.sum(1/d**2))
                return v
            else:
                return self.v[d.argmin()]

def plot(input_data, output_file = None, show_window = True):

    x, y, z = np.loadtxt(input_data, delimiter=',', unpack=True)
    e = Estimation(x,y,z)
    surf = np.zeros((100,100))
    for i in range(100):
        for j in range(100):
            surf[i,j] = e.estimate(i-50,j-50)

    fig = plt.figure()

    plt.imshow(surf.T,origin='lower',interpolation='nearest')

    if output_file:
        plt.savefig(output_file)
    if show_window:
        plt.show()

def main():
    input_file = sys.argv[1]
    output_file = "{0}.png".format(sys.argv[1])
    plot(input_file, output_file)

if __name__ == '__main__':
    main()
