#!/usr/bin/env python3

import sys
import argparse

from delta_printer import DeltaPrinter, error

def try_for(l, r, observations, error_treshold = 0.5):
    # finds all L/R pairs that give correct dimensions, consumes observations
    max_error = 0
    for o in observations:
        trial_l = l
        trial_r = r
        observed_l = float(o[0])
        observed_r = float(o[1])
        trial = DeltaPrinter(trial_l, trial_r)
        observed  = DeltaPrinter(observed_l, observed_r)

        max_y = error(trial, observed, 0, 50)[1]
        min_y = error(trial, observed, 0, -50)[1]
        xy_error = (max_y - min_y) - float(o[2])
        if abs(xy_error) > error_treshold:
            return 100
        if abs(xy_error) > abs(max_error):
            max_error = xy_error

        points = [[0,0,0],[0,-50,0.3],[0,50,0]]
        center_error = error(trial, observed, 0, 0)[2]
        for point in points:
            ep = error(trial, observed, point[0], point[1])[2] - center_error
            if abs(ep - point[2]) > 0.07: #error_treshold:
                print("{0:.3f}, {1:.3f}, {2:.3f}, {3:.3f}, {4:.3f}".format(l, r, point[0], point[1], ep - point[2]))
                # exit(1)
                return 100
    return max_error

def f_range(start, end, step):
    while start <= end:
        yield start
        start += step

# Example: ./find_lr.py -l 120.8 -r 61.7 -o '122.49,63.16,99;121.36,62.7,99.5' -f 1

def main():

    s_value = 0.05

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-s','--s-value',type=float,default=s_value,help='Step value')
    parser.add_argument('-o','--observations',type=str,dest='observations',default=None,help='Semicolon separated observation triplets, each in form or: l,r,dimension observed')
    args = parser.parse_args()

    if not args.observations:
        print("Observations shall be provided")
        exit(1)

    observations = [x.split(",") for x in args.observations.split(";")]
    for l in f_range(110.0, 150.0, args.s_value):
        print(l)
        for r in f_range(55.0, 90.0, args.s_value):
            e = try_for(l, r, observations, 0.2)
            if abs(e) < 100:
                print("L{0}, R{1} - {2:.2f}".format(l, r, e))

if __name__ == '__main__':
    main()
