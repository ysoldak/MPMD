#!/usr/bin/env python3

import sys

import matplotlib.pyplot as plt
import numpy as np

import math

from scipy import interpolate
from scipy.interpolate import griddata

def plot(titles, input_data, output_file = None, show_window = True, note = None, invert = False):

    plt.figure(1, figsize=(10,4.7))
    if note is not None:
        plt.figtext(0.1, 0.1, note, bbox=dict(facecolor='gray', alpha=0.5))

    for i in range(len(input_data)):
        plt.subplot(2, 3, i+1)
        plt.title(titles[i])
        X, Y, Z = np.loadtxt(input_data[i], delimiter=',', unpack=True)

        xi = np.linspace(X.min(),X.max(),1000)
        yi = np.linspace(Y.min(),Y.max(),1000)
        zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method='cubic')
        if invert:
            zi = -zi

        plt.contourf(xi, yi, zi,32)
        plt.colorbar()

    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

    if output_file:
        plt.savefig(output_file)
    if show_window:
        plt.show()

def sparse(titles, input_data, output_file = None, show_window = True, note = None, invert = False):

    plt.figure(1, figsize=(10,4.7))
    if note is not None:
        plt.figtext(0.1, 0.1, note, bbox=dict(facecolor='gray', alpha=0.5))

    for i in range(len(input_data)):
        plt.subplot(2, 3, i+1)
        plt.title(titles[i])
        X, Y, Z = np.loadtxt(input_data[i], delimiter=',', unpack=True)

        zi = np.empty((100, 100))
        for i in range(len(X)):
            zi[-int(Y[i]+49), int(X[i]+49)] = Z[i]
        if invert:
            zi = -zi

        plt.spy(zi,markersize=1, precision=0)

    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

    if output_file:
        plt.savefig(output_file)
    if show_window:
        plt.show()

def get_points_square(size):
    points = [(0, 0)]
    for x in range(size+1):
        for y in range(size+1):
            if x == 0 or x == int(size/2) or x == size or y == 0 or y == size or y == x or y == size - x:
                points.append((int(x-size/2),int(y-size/2)))
    return points


def get_points_wheel(max_dist = 50, scatter_step = 5, angle_step = 15.):
    points = [(0, 0)]
    scatter = [x/100 for x in range(100, 5, -scatter_step)]
    for i in range(len(scatter)):
        dist = max_dist * scatter[i]
        for j in range(int(360/angle_step)):
            r = math.radians(90. + angle_step * j)
            points.append((math.cos(r) * dist, math.sin(r) * dist))
    return points


def scatter(titles, input_data, output_file = None, show_window = True, note = None, invert = False):

    glue_centers = True

    plt.figure(1, figsize=(7,7))
    if note is not None:
        plt.figtext(0.1, 0.01, note, bbox=dict(facecolor='gray', alpha=0.5))

    for i in range(len(input_data)):
        plt.subplot(1, 1, i+1)
        plt.title(titles[i])
        X, Y, Z = np.loadtxt(input_data[i], delimiter=',', unpack=True)

        # zi = np.empty((100, 100))
        # for i in range(len(X)):
        #     zi[-int(Y[i]+49), int(X[i]+49)] = Z[i]
        # if invert:
        #     zi = -zi

        points = []
        points.extend(get_points_wheel(45, 50, 60.))
        # points.extend(get_points_wheel(47, 100, 60.))
        # points = get_points_square(50)
        Xs = [p[0]+X[0] if glue_centers else p[0] for p in points]
        Ys = [p[1]+Y[0] if glue_centers else p[1] for p in points]
        # size = 50
        # for x in range(size+1):
        #     for y in range(size+1):
        #         if x == 0 or x == int(size/2) or x == size or y == 0 or y == size or y == x or y == size - x:
        #             new_x = int(x-size/2)+X[0] if glue_centers else int(x-size/2)
        #             new_y = int(y-size/2)+Y[0] if glue_centers else int(y-size/2)
        #             Xs.append(new_x)
        #             Ys.append(new_y)

        plt.scatter(Xs, Ys, 15, 'gray')

        plt.scatter(X, Y, 15, 'blue')

        print("Distances to center: C, FarB, A, FarC, B, FarA") # TODO is this correct order? Klipper starts with A
        for i in range(len(X)-1):
            idx1 = i+1
            idx2 = 0
            dist = math.hypot(X[idx1]-X[idx2],Y[idx1]-Y[idx2]) + 3.8
            print("{2:.2f} - {0},{1}".format(X[idx1], Y[idx1], dist))

        print("Distances round: C-FarB, etc")
        for i in range(len(X)-1):
            idx1 = i+1
            idx2 = i+2 if i < len(X)-2 else 1
            dist = math.hypot(X[idx1]-X[idx2],Y[idx1]-Y[idx2]) + 3.8
            print("{2:.2f} - {0},{1}".format(X[idx1], Y[idx1], dist))


    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)

    if output_file:
        plt.savefig(output_file)
    if show_window:
        plt.show()


def main():
    input_file = sys.argv[1]
    # output_file = "{0}.png".format(sys.argv[1])
    plot(["Z"], [input_file], None, True, str(sys.argv).replace("', '", " ").replace("['", "").replace("']", ""), True)

if __name__ == '__main__':
    main()
