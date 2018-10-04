#!/usr/bin/env python3

import sys
import argparse

from numpy import sqrt, dot, cross, array, zeros, radians, cos, sin, tan, pi
from numpy.linalg import norm
#from numpy import cos, sin, radians

# FIXME tower lean does not work correctly
# TODO Support different L/R per tower
# TODO Support different lean and step_size per tower
class DeltaPrinter:
    
    @classmethod
    def from_args(cls, args):
        lengths = [float(l) for l in args.l_value.split(',')] if "," in args.l_value else [float(args.l_value) for x in range(3)]
        radii = [float(r) for r in args.r_value.split(',')] if "," in args.r_value else [float(args.r_value) for x in range(3)]
        angles = [float(a) for a in args.a_value.split(',')]
        endstops = [float(e) for e in args.e_value.split(',')] if "," in args.e_value else [float(args.e_value) for x in range(3)]
        return cls(lengths, radii, args.s_value, angles, endstops)

    def __init__(self, length, radius, step_size = 0.01, angles = [210., 330., 90.], endstops = 0.):
        
        # geometry
        self.l = length if type(length) is list else [length, length, length]
        self.r = radius if type(radius) is list else [radius, radius, radius]
        self.endstops = endstops if type(endstops) is list else [endstops, endstops, endstops]
        self.step_size = step_size
        self.tower_angles = angles

        # must home first
        self.tower_steps = [None, None, None]

        # pre-calc
        self.tower_coords = [(cos(radians(angle)) * self.r[idx], sin(radians(angle)) * self.r[idx]) for idx, angle in enumerate(self.tower_angles)]

    def home(self):
        self.move(0,0,0,True)
        # print(self.tower_steps)
        self.tower_steps = [self.endstops[idx]/self.step_size + s for idx, s in enumerate(self.tower_steps)]
        # print(self.tower_steps)
        self.tower_home_steps = [s for s in self.tower_steps]

    def move(self, x, y, z = 0, force = False):
        if self.tower_steps[0] is None and not force:
            raise Exception("Must home first")
        for tower in [0, 1, 2]:
            tx = self.tower_coords[tower][0]
            ty = self.tower_coords[tower][1]
            tz = sqrt(self.l[tower]**2 - (tx-x)**2 - (ty-y)**2) + z
            self.tower_steps[tower] = round(tz/self.step_size) + self.endstops[tower]/self.step_size

    def carriage_position(self, tower):
        _x = self.tower_coords[tower][0]
        _y = self.tower_coords[tower][1]
        _z = self.tower_steps[tower]*self.step_size
        return array([_x, _y, _z])

    # Trilateration
    # Calculate intersection of 3 spheres, simplified version of code at https://stackoverflow.com/a/18654302
    def nozzle_position(self):
        sphere_centers = [self.carriage_position(tower) for tower in [0,1,2]]
        temp1 = sphere_centers[1]-sphere_centers[0]
        d = norm(temp1)
        e_x = temp1/d
        temp2 = sphere_centers[2]-sphere_centers[0]
        i = dot(e_x,temp2)
        temp3 = temp2 - i*e_x
        e_y = temp3/norm(temp3)
        e_z = cross(e_x,e_y)
        j = dot(e_y,temp2)
        x = (self.l[0]**2 - self.l[1]**2 + d*d) / (2*d)
        y = (self.l[0]**2 - self.l[2]**2 -2*i*x + i*i + j*j) / (2*j)
        temp4 = self.l[0]**2 - x*x - y*y
        if temp4<0:
            raise Exception("The three spheres do not intersect!")
        z = sqrt(temp4)
        return sphere_centers[0] + x*e_x + y*e_y - z*e_z
    
    def tower_step_deltas(self):
        return [s-h for h, s in zip(self.tower_home_steps, self.tower_steps)]

    def tower_mm_deltas(self):
        return [s*self.step_size for s in self.tower_step_deltas()]

    @staticmethod
    def argument_parser():
        parser = argparse.ArgumentParser(description='Delta errors simulation')
        parser.add_argument('-l','--l-value',type=str,default="120.8",help='Diagonal rod length, in mm')
        parser.add_argument('-r','--r-value',type=str,default="61.7",help='Delta radius, in mm')
        parser.add_argument('-e','--e-value',type=str,default="0",help='End stops diff, in mm')
        parser.add_argument('-s','--s-value',type=float,default=0.01,help='Step size, in mm')
        parser.add_argument('-a','--a-value',type=str,default='210,330,90',help='Tower angles comma separated, in deg')
        parser.add_argument('-n','--n-value',type=str,default='0,0',help='Nozzle moves, semicolon separated, in mm')
        parser.add_argument('-t','--t-value',type=str,default=None,help='Tower moves, semicolon separated, in mm')
        return parser

def error(physical, logical, x, y, z = 0):
    # we move logical model of the printer, copy carriage positions to physical model and see where the nozzle tip ends up
    logical.move(x, y, z)
    physical.tower_steps = logical.tower_steps
    return physical.nozzle_position()

# Example usage:
#   ./delta_printer.py -l 120 -r 62 -s 0.01 -n '0,10,0;0,-10,5'
if __name__ == '__main__':

    parser = DeltaPrinter.argument_parser
    args = parser.parse_args()
    printer = DeltaPrinter.from_args(args)

    def report():
        pos = printer.nozzle_position()
        print("Nozzle: {0:.3f}, {1:.3f}, {2:.3f}".format(pos[0], pos[1], pos[2]))
        towers = printer.tower_steps
        print("Towers mm: {0:.3f}, {1:.3f}, {2:.3f}".format(towers[0]*printer.step_size,towers[1]*printer.step_size,towers[2]*printer.step_size))
        print("Towers step: {0:.3f}, {1:.3f}, {2:.3f}".format(towers[0],towers[1],towers[2]))
        deltas = printer.tower_step_deltas()
        print("Deltas step: {0:.3f}, {1:.3f}, {2:.3f}".format(deltas[0],deltas[1],deltas[2]))
        print("")

    if args.t_value is not None:
        steps_sequence = [x.split(",") for x in args.t_value.split(";")]
        for steps in steps_sequence:
            printer.tower_steps = [float(steps[i]) for i in range(3)]
            print(printer.tower_steps)
            report()
    else:
        coords = [x.split(",") for x in args.n_value.split(";")]
        for coord in coords:
            coord = [float(coord[0]), float(coord[1]), float(coord[2]) if len(coord) == 3 else 0.0]
            printer.move(coord[0], coord[1], coord[2])
            report()
