#!/usr/bin/env python3

import sys
import argparse
import math

from delta_printer import DeltaPrinter, error

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

def points_to_nozzle_positions(points, wrong, correct):
    nozzle_positions = []
    for point in points:
        wrong.move(point[0], point[1])
        correct.tower_steps = [s for s in wrong.tower_steps]
        try:
            nozzle_position = correct.nozzle_position()
        except:
            return None
        nozzle_positions.append(nozzle_position)
    return nozzle_positions

def get_center_distances(nozzle_positions, adjustment = 2):
    X = [pos[0] for pos in nozzle_positions]
    Y = [pos[1] for pos in nozzle_positions]
    distances = []
    for i in range(len(nozzle_positions)-1):
        idx1 = i+1
        idx2 = 0
        dist = math.hypot(X[idx1]-X[idx2],Y[idx1]-Y[idx2]) + adjustment
        distances.append(dist)
    return distances

def get_round_distances(nozzle_positions, adjustment = 2):
    X = [pos[0] for pos in nozzle_positions]
    Y = [pos[1] for pos in nozzle_positions]
    distances = []
    for i in range(len(nozzle_positions)-1):
        idx1 = i+1
        idx2 = i+2 if i < len(X)-2 else 1
        dist = math.hypot(X[idx1]-X[idx2],Y[idx1]-Y[idx2]) + adjustment
        distances.append(dist)
    return distances

def main():

    # search space parameters
    step = 0.1
    area = 10

    distances = 45 # expected distances between the centers
    adjustment = 3.8 # pin/bolt head diameter
    da = distances + adjustment

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-l','--l-value',type=str,default="120.8",help='Diagonal rod lengths')
    parser.add_argument('-r','--r-value',type=str,default="61.7",help='Delta radii')
    parser.add_argument('-a','--a-value',type=str,default="210,330,90",help='Tower angles, in deg')
    parser.add_argument('-cd','--cd-value',type=str,default="{0},{0},{0},{0},{0},{0}".format(da),help='Center distances')
    parser.add_argument('-rd','--rd-value',type=str,default="{0},{0},{0},{0},{0},{0}".format(da),help='Round distances')
    args = parser.parse_args()

    l = [float(l) for l in args.l_value.split(',')] if "," in args.l_value else [float(args.l_value) for x in range(3)]
    r = [float(r) for r in args.r_value.split(',')] if "," in args.r_value else [float(args.r_value) for x in range(3)]
    a = [float(a) for a in args.a_value.split(',')]

    observe_c = [float(cd) for cd in args.cd_value.split(',')]
    observe_r = [float(rd) for rd in args.cd_value.split(',')]

    points = get_points_wheel(distances, distances*10, 60.)

    lengths_orig = [l1-area/2*step for l1 in l]
    angles_orig = [a1-area/2*step for a1 in a]

    # r_orig = r-area/2*step
    r_orig = r
    ir = 0

    solution_l = list(lengths_orig)
    solution_a = list(angles_orig)
    solution_r = r_orig
    min_error = 9999999999

    c = (area+1)*(area+1)*(area+1)
    for ila in range(area+1):
        for ilb in range(area+1):
            for ilc in range(area+1):
                lengths = [lengths_orig[0]+step*ila, lengths_orig[1]+step*ilb, lengths_orig[2]+step*ilc]
                print(c)
                # print(lengths)
                c-=1
                for iaa in range(area+1):
                    # for iab_tmp in range(1):
                            # iab = 3#area/2
                    for iab in range(area+1):
                        # for ir in range(area+1):
                        # for iac in range(area):
                            # angles = [angles_orig[0]+step*iaa,angles_orig[1]+step*iab,angles_orig[2]+step*iac]
                            angles = [angles_orig[0]+step*iaa,angles_orig[1]+step*iab,90.0]
                            logical  = DeltaPrinter(l, r, 0.01, a)
                            physical = DeltaPrinter(lengths, r_orig+step*ir, 0.01, angles)
                            nps = points_to_nozzle_positions(points, logical, physical)
                            if nps is None:
                                continue
                            # print(nps)
                            cds = get_center_distances(nps, adjustment)
                            rds = get_round_distances(nps, adjustment)
                            # print(cds)
                            cur_error = 0.0
                            for i in range(6):
                                # cur_error += abs(observe_c[i]-cds[i])
                                cur_error += (observe_c[i]-cds[i])*(observe_c[i]-cds[i])
                                cur_error += (observe_r[i]-rds[i])*(observe_r[i]-rds[i])
                            if cur_error < min_error:
                                solution_l = list(lengths)
                                solution_a = list(angles)
                                solution_r = r_orig+step*ir
                                min_error = cur_error
                                print(solution_l)
                                print(solution_a)
                                print(solution_r)
                                print(min_error)
                            # else:
                            #     print(cur_error)

    print(solution_l)
    print(solution_a)
    print(solution_r)
    print(min_error)

if __name__ == '__main__':
    main()
