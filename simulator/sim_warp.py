#!/usr/bin/env python3

import sys
import argparse

from io import StringIO

from delta_printer import DeltaPrinter, error

from plot import plot

# points = [
#     [[0, 0]],
# ]

# center, radius 50
# points = [
#     [None,          [0, 50],   None],
#     [[-43.3, 25],   None,      [43.3, 25]],
#     [None,          [0, 0],    None],
#     [[-43.3, -25],  None,      [43.3, -25]],
#     [None,          [0, -50],  None]
# ]

# center, radius 30, radius 50
points = [
    [[-43.3, 25],   [0, 50],   [43.3, 25]],
    [[-26, 15],     [0, 30],   [26, 15]],
    [[-30, 0],      [0, 0],    [30, 0]],
    [[-26, -15],    [0, -30],  [26, -15]],
    [[-43.3, -25],  [0, -50],  [43.3, -25]],
]

# center, square 25, radius 50
# points = [
#     [None,         [-25, 43.3],  [0, 50],  [25, 43.3],  None],
#     [[-43.3, 25],  [-25, 25],    [0, 25],  [25, 25],    [43.3, 25]],
#     [[-50, 0],     [-25, 0],     [0, 0],   [25, 0],     [50, 0]],
#     [[-43.3, -25], [-25, -25],   [0, -25], [25, -25],   [43.3, -25]],
#     [None,         [-25, -43.3], [0, -50], [25, -43.3], None],
# ]

# Examples:
# ./sim_warp.py -l 123.5 -r 63.7 -wl 120 -wr 62.7

def main():

    l_value = 120.8
    r_value = 61.7
    t_value = 90.0
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
    parser.add_argument('-t','--t-value',type=float,default=t_value,help='Tower tilt, t<90 means towers tilt outwards')
    args = parser.parse_args()

    correct_l = args.l_value
    correct_r = args.r_value
    correct_t = args.t_value
    wrong_l = correct_l + float(args.dl_value) if args.wl_value is None else args.wl_value
    wrong_r = correct_r + float(args.dr_value) if args.wr_value is None else args.wr_value

    correct = DeltaPrinter(correct_l, correct_r, correct_t)
    wrong  = DeltaPrinter(wrong_l, wrong_r, 90.0) # tilt on wrong printer is always 90, i.e. it thinks it's correct

    center_error = error(correct, wrong, 0, 0)[2] # glue good and bad centers together

    print("Warping:")
    warp_csv = ""
    for row in points:
        for point in row:
            error_value = error(correct, wrong, point[0], point[1])[2] - center_error if point is not None else -100
            v = "{0:.3f}".format(error_value) if error_value > -100 else " -/- "
            sys.stdout.write(v + "  ")
            sys.stdout.flush()
            if point is not None:
                warp_csv += "{0:.3f},{1:.3f},{2:.3f}\n".format(point[0],point[1],error_value)
        print("")

    print("")

    max_y = error(correct, wrong, 0, 50)[1]
    min_y = error(correct, wrong, 0, -50)[1]
    xy_error = (max_y - min_y)
    print("Dimensional accuracy:")
    print("{0:.3f}mm for 100.000mm".format(xy_error))

    print(warp_csv)
    csv = StringIO(warp_csv)
    plot(csv, "{0}-{1}-with-{2}_{3}.png".format(correct_l, correct_r, wrong_l, wrong_r), True)

if __name__ == '__main__':
    main()
