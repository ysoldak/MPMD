#!/usr/bin/env python3

import sys
import argparse

import math
from scipy.spatial import distance

from io import StringIO

from delta_printer import DeltaPrinter, error

from plot import plot, sparse, scatter

# Examples:
# ./sim_warp.py -l 123.5 -r 63.7 -wl 120 -wr 62.7

# horizontal, vertical and diagonal lines
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
            #points.append((int(math.cos(r) * dist), int(math.sin(r) * dist)))
            points.append((math.cos(r) * dist, math.sin(r) * dist))
    return points

def main():

    l_value = "120.8"
    r_value = "61.7"

    parser = argparse.ArgumentParser(description='Delta errors simulation')

    parser.add_argument('-l','--l-value',type=str,default=l_value,help='Correct l-value')
    parser.add_argument('-r','--r-value',type=str,default=r_value,help='Correct r-value')
    parser.add_argument('-s','--s-value',type=float,default=0.01,help='Correct step size, in mm')
    parser.add_argument('-a','--a-value',type=str,default="210,330,90",help='Correct tower angles, in deg')

    parser.add_argument('-wl','--wl-value',type=str,default=l_value,help='Wrong l-value')
    parser.add_argument('-wr','--wr-value',type=str,default=r_value,help='Wrong r-value')
    parser.add_argument('-ws','--ws-value',type=float,default=None,help='Wrong step size, in mm')
    parser.add_argument('-wa','--wa-value',type=str,default=None,help='Wrong tower angles, in deg')

    parser.add_argument('-we','--we-value',type=str,default="0",help='Wrong endstops')

    parser.add_argument('-v','--v-value',type=str,default="wheel",help='Visualization type')
    # parser.add_argument('-save','--save-value',type=str,default="sim_warp.png",help='Save plot to file with name')
    args = parser.parse_args()

    if args.ws_value is None:
        args.ws_value = args.s_value
    if args.wa_value is None:
        args.wa_value = args.a_value

    correct_l = [float(l) for l in args.l_value.split(',')] if "," in args.l_value else [float(args.l_value) for x in range(3)]
    correct_r = [float(r) for r in args.r_value.split(',')] if "," in args.r_value else [float(args.r_value) for x in range(3)]
    correct_a = [float(a) for a in args.a_value.split(',')]
    correct_e = [0.,0.,0.]

    wrong_l = [float(l) for l in args.wl_value.split(',')] if "," in args.wl_value else [float(args.wl_value) for x in range(3)]
    wrong_r = [float(r) for r in args.wr_value.split(',')] if "," in args.wr_value else [float(args.wr_value) for x in range(3)]
    wrong_a = [float(a) for a in args.wa_value.split(',')]
    wrong_e = [float(e) for e in args.we_value.replace("#","-").split(',')] if "," in args.we_value else [float(args.we_value.replace("#","-")) for x in range(3)]


    # print(correct_l)
    # print(wrong_l)
    # print(args.s_value)

    correct = DeltaPrinter(correct_l, correct_r, args.s_value, correct_a, correct_e)
    wrong  = DeltaPrinter(wrong_l, wrong_r, args.ws_value, wrong_a, wrong_e)
    # lean on wrong printer is always 90, i.e. it thinks it's correct. NB! lean does not work now anyway

    # correct.home()
    wrong.home()

    center_error = error(correct, wrong, 0, 0)[2] # glue good and bad centers together

    viz = args.v_value

    csv = ["","",""] if viz == "heatmaps" else [""]

    points = []
    if viz == "heatmaps":
        points.extend(get_points_wheel(45, 5, 15.))
    else:
        points.extend(get_points_wheel(45, 100, 60.))

    for point in points:
        x = point[0]
        y = point[1]
        wrong.move(x, y)
        correct.tower_steps = [s for s in wrong.tower_steps]
        nozzle_position = correct.nozzle_position()

        if viz == "heatmaps":
            err = [0,0,0]
            err[0] =  nozzle_position[0] - point[0]              # sign matches direction of shift
            err[1] =  nozzle_position[1] - point[1]              # sign matches direction of shift
            err[2] =  nozzle_position[2] - center_error          # sign matches direction of shift
            for i in range(3):
                csv[i] += "{0:.3f},{1:.3f},{2:.3f}\n".format(x,y,err[i])
        else:
            csv[0] += "{0:.3f},{1:.3f},{2:.3f}\n".format(nozzle_position[0],nozzle_position[1],nozzle_position[2])

    # max_y = error(correct, wrong, 0, 50)[1]
    # min_y = error(correct, wrong, 0, -50)[1]
    # xy_error = (max_y - min_y)
    # print("Dimensional accuracy:")
    # print("{0:.3f}mm for 100.000mm".format(xy_error))

    # print("")

    # FIXME different args for different filenames
    # csv = StringIO(z_csv)
    # png = "{0}-{1}-with-{2}_{3}_z.png".format(correct_l, correct_r, wrong_l, wrong_r) if args.save_value == "generate" else args.save_value
    # print("Plot saved to file:\n" + png)
    # plot(csv, png, True)

    data = [StringIO(csv[i]) for i in range(len(csv))]
    # png = "{0}-{1}-with-{2}_{3}_xy.png".format(correct_l, correct_r, wrong_l, wrong_r) if args.save_value == "generate" else args.save_value
    # print("Plot saved to file:\n" + png)
    if viz == "heatmaps":
        plot(["X","Y","Z"], data, None, True, str(sys.argv).replace("', '", " ").replace("['", "").replace("']", ""))
    else:
        scatter(["COORDS"], data, None, True, str(sys.argv).replace("', '", " ").replace("['", "").replace("']", ""))

if __name__ == '__main__':
    main()
