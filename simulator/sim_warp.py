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
    # tl_value = 90.0
    dl_value = 0.0
    dr_value = 0.0

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-l','--l-value',type=float,default=l_value,help='Correct l-value')
    parser.add_argument('-r','--r-value',type=float,default=r_value,help='Correct r-value')
    parser.add_argument('-dl','--dl-value',type=float,default=dl_value,help='Deviation from correct l-value')
    parser.add_argument('-dr','--dr-value',type=float,default=dr_value,help='Deviation from correct r-value')
    parser.add_argument('-wl','--wl-value',type=float,default=None,help='Wrong l-value')
    parser.add_argument('-wr','--wr-value',type=float,default=None,help='Wrong r-value')
    # parser.add_argument('-tl','--tl-value',type=float,default=tl_value,help='Tower lean, t<90 means towers tilt outwards')
    parser.add_argument('-s','--s-value',type=float,default=0.01,help='Correct step size, in mm')
    parser.add_argument('-ws','--ws-value',type=float,default=None,help='Wrong step size, in mm')
    parser.add_argument('-a','--a-value',type=str,default="210,330,90",help='Correct tower angles, in deg')
    parser.add_argument('-wa','--wa-value',type=str,default=None,help='Wrong tower angles, in deg')
    parser.add_argument('-save','--save-value',type=str,default="sim_warp.png",help='Save plot to file with name')
    args = parser.parse_args()

    correct_l = args.l_value
    correct_r = args.r_value
    wrong_l = correct_l + args.dl_value if args.wl_value is None else args.wl_value
    wrong_r = correct_r + args.dr_value if args.wr_value is None else args.wr_value

    if args.ws_value is None:
        args.ws_value = args.s_value
    if args.wa_value is None:
        args.wa_value = args.a_value

    correct = DeltaPrinter(correct_l, correct_r, 90.0, args.s_value, [float(a) for a in args.a_value.split(',')])
    wrong  = DeltaPrinter(wrong_l, wrong_r, 90.0, args.ws_value, [float(a) for a in args.wa_value.split(',')])
    # lean on wrong printer is always 90, i.e. it thinks it's correct. NB! lean does not work now anyway

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

    print("")

    csv = StringIO(warp_csv)
    png = "{0}-{1}-with-{2}_{3}.png".format(correct_l, correct_r, wrong_l, wrong_r) if args.save_value == "generate" else args.save_value
    print("Plot saved to file:\n" + png)
    plot(csv, png, True)

if __name__ == '__main__':
    main()
