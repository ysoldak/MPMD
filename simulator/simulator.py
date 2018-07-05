#!/usr/bin/env python

import sys
import argparse

from delta_printer import DeltaPrinter

def error(good, bad, x, y, z = 0):
    bad.move(x, y, z)
    good.tower_positions = bad.tower_positions
    return good.position()

def solve_for(l, r, conditions, error_treshold = 0.5):
    max_error = 0
    for c in conditions:
        good_l = l
        good_r = r
        bad_l = float(c[0])
        bad_r = float(c[1])
        good = DeltaPrinter(good_l, good_r)
        bad  = DeltaPrinter(bad_l, bad_r)

        center_error = error(good, bad, 0, 0)[2]
        
        max_y = error(good, bad, 0, 50)[1]
        min_y = error(good, bad, 0, -50)[1]
        xy_error = (max_y - min_y) - float(c[2])
        if abs(xy_error) > error_treshold:
            return 100
        if abs(xy_error) > abs(max_error):
            max_error = xy_error
        
        for row in points:
            for point in row:
                if point is not None:
                    ep = error(good, bad, point[0], point[1])[2] - center_error
                    if abs(ep) > error_treshold:
                        return 100
    return max_error

def frange(start, end, step):
    while start <= end:
        yield start
        start += step

points = [
    [None,         [-25, 43.3],  [0, 50],  [25, 43.3],  None],
    [[-43.3, 25],  [-25, 25],    [0, 25],  [25, 25],    [43.3, 25]],
    [[-50, 0],     [-25, 0],     [0, 0],   [25, 0],     [50, 0]],
    [[-43.3, -25], [-25, -25],   [0, -25], [25, -25],   [43.3, -25]],
    [None,         [-25, -43.3], [0, -50], [25, -43.3], None],
]

# points = [
#     [[0, 0]],
# ]

def main():

    l_value = 120.8
    r_value = 61.7
    t_value = 1.0
    dl_value = 0.0
    dr_value = 0.0
    wl_value = l_value + dl_value
    wr_value = r_value + dr_value

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-l','--l-value',type=float,default=l_value,help='Correct l-value')
    parser.add_argument('-r','--r-value',type=float,default=r_value,help='Correct r-value')
    parser.add_argument('-dl','--dl-value',type=float,default=dl_value,help='Deviation from correct l-value')
    parser.add_argument('-dr','--dr-value',type=float,default=dr_value,help='Deviation from correct r-value')
    parser.add_argument('-wl','--wl-value',type=float,default=None,help='Wrong l-value')
    parser.add_argument('-wr','--wr-value',type=float,default=None,help='Wrong r-value')
    parser.add_argument('-t','--t-value',type=float,default=t_value,help='Tower tilt, t<1 means towers tilt outwards')
    parser.add_argument('-s','--solve',type=str,dest='solve',default=None,help='')
    args = parser.parse_args()

    if args.solve:
        conditions = [x.split(",") for x in args.solve.split(";")]
        for l in frange(118.0, 124.0, 0.05):
            for r in frange(61.0, 65.0, 0.05):
                e = solve_for(l, r, conditions, 0.1)
                if abs(e) < 0.2:
                    print("L{0}, R{1} - {2:.2f}".format(l, r, e))
        exit(0)

    good_l = args.l_value
    good_r = args.r_value
    good_t = args.t_value
    bad_l = good_l + float(args.dl_value) if args.wl_value is None else args.wl_value
    bad_r = good_r + float(args.dr_value) if args.wr_value is None else args.wr_value

    good = DeltaPrinter(good_l, good_r, good_t)
    bad  = DeltaPrinter(bad_l, bad_r, 90.0)

    center_error = 0 #error(good, bad, 0, 0)[2] # glue good and bad centers together

    print("Warping at 0:")
    for row in points:
        for point in row:
            v = "{0:.3f}".format(error(good, bad, point[0], point[1])[2] - center_error) if point is not None else " -/- "
            sys.stdout.write(v + "  ")
            sys.stdout.flush()
        print("")

    print("")

    print("Warping at 50:")
    for row in points:
        for point in row:
            v = "{0:.3f}".format(error(good, bad, point[0], point[1], 50)[2] - center_error) if point is not None else " -/- "
            sys.stdout.write(v + "  ")
            sys.stdout.flush()
        print("")

    print("")

#    max_y = error(good, bad, 0, 42.2)[1]
#    min_y = error(good, bad, 0, -42.2)[1]
    max_y = error(good, bad, 0, 50)[1]
    min_y = error(good, bad, 0, -50)[1]
    xy_error = (max_y - min_y)
    print("Dimensional accuracy:")
    print("{0:.3f}mm for 100.000mm".format(xy_error))
    print("{0:.3f},{0:.3f}".format(max_y, min_y))

    #(122.49-121.36)/3*2+62.7=63.45

if __name__ == '__main__':
    main()
