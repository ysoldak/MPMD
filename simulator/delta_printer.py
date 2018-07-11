#!/usr/bin/env python3

import sys
import argparse

from numpy import sqrt, dot, cross, array, zeros, radians, cos, sin, tan, pi
from numpy.linalg import norm

# FIXME tower lean does not work correctly
# TODO Support different L/R per tower
# TODO Support different lean and step_size per tower
class DeltaPrinter:
    
    def __init__(self, length, radius, lean = 90.0, step_size = 0.01, angles = [210., 330., 90.]):
        
        # geometry
        self.l = length
        self.r = radius
        # self.h = sqrt(self.l*self.l - self.r*self.r)
        self.tower_lean = lean # tower lean, t<90 means towers lean outwards
        self.step_size = step_size
        self.tower_angles = angles

        # pre-calc
        self.tower_coords = [(cos(radians(angle)) * self.r, sin(radians(angle)) * self.r) for angle in self.tower_angles]

        # home
        #steps = round(self.h/self.step_size)
        self.tower_steps = [None, None, None]
        self.move(0,0,0)
        self.tower_home_steps = [s for s in self.tower_steps]


    def move(self, x, y, z = 0):
        for tower in [0, 1, 2]:
            if self.tower_lean == 90.0:
                tx = self.tower_coords[tower][0]
                ty = self.tower_coords[tower][1]
                tz = sqrt(self.l*self.l - (tx-x)*(tx-x) - (ty-y)*(ty-y)) + z
                self.tower_steps[tower] = round(tz/self.step_size)
            else:
                print("ERROR! FIXME")
                tx = self.tower_coords[tower][0]
                ty = self.tower_coords[tower][1]
                tr = sqrt((tx-x)*(tx-x) + (ty-y)*(ty-y)) # distance from tower base to (x,y)

                # r_error_z                     <-- tower projection for z
                # tga                           <-- tan of tower lean
                # r_z = tr + r_error_z          <-- distance from (x,y) to carriage projection for z
                # c_z = tga * r_error_z         <-- carriage height for z

                # (X-X0)^2 + (Y-Y0)^2 = R^2     <-- generic circle equation
                # (r_z-0)^2 + (c_z-z)^2 = L^2   <-- circle with center in (x,y,z) in plane of tower arm
                # (c_z/tga + tr)^2 + c_z^2 - 2*z*c_z + z^2 - L^2 = 0
                # (1+1/tga^2)*c_z^2 + (2*tr/tga - 2*z)*c_z + tr^2 + z^2 - L^2 = 0
                
                # solve for c_z and convert to actual carriage position on rail

                tga = tan(radians(self.tower_lean))
                a = 1 + 1/(tga*tga)
                b_2 = tr/tga - z
                c = tr*tr + z*z - self.l*self.l
                d_2 = b_2*b_2 - a*c
                if d_2 < 0:
                    raise Exception('spam', 'eggs')
                c_z = (sqrt(d_2) - b_2)/a 
                c_position = c_z / sin(radians(self.tower_lean))
                self.tower_steps[tower] = round(c_position/self.step_size)

    def carriage_position(self, tower):
        if self.tower_lean == 90.0:
            _x = self.tower_coords[tower][0]
            _y = self.tower_coords[tower][1]
            _z = self.tower_steps[tower]*self.step_size
            return array([_x, _y, _z])
        else:
            print("ERROR! FIXME")
            _re = self.tower_steps[tower] * self.step_size * cos(radians(self.tower_lean))
            _r = self.r + _re
            _x = cos(radians(self.tower_angles[tower])) * _r
            _y = sin(radians(self.tower_angles[tower])) * _r
            _z = self.tower_steps[tower] * self.step_size * sin(radians(self.tower_lean))
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
        x = (d*d) / (2*d)
        y = (i*i + j*j - 2*i*x) / (2*j)
        temp4 = self.l*self.l - x*x - y*y
        if temp4<0:
            raise Exception("The three spheres do not intersect!")
        z = sqrt(temp4)
        return sphere_centers[0] + x*e_x + y*e_y - z*e_z
    
    def tower_step_deltas(self):
        return [s-h for h, s in zip(self.tower_home_steps, self.tower_steps)]

    def tower_mm_deltas(self):
        return [s*self.step_size for s in self.tower_step_deltas()]

def error(correct, wrong, x, y, z = 0):
    # we move wrongly configured printer and copy carriage steps to correct model and see where the nozzle ends up
    wrong.move(x, y, z)
    correct.tower_steps = wrong.tower_steps
    return correct.nozzle_position()

# Example usage:
#   ./delta_printer.py -l 120 -r 62 -s 0.01 -n '0,10,0;0,-10,5'
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-l','--l-value',type=float,default=120.8,help='Correct l-value, in mm')
    parser.add_argument('-r','--r-value',type=float,default=61.7,help='Correct r-value, in mm')
    parser.add_argument('-tl','--tl-value',type=float,default=90.0,help='Tower lean, in deg, tl<90 means towers lean outwards')
    parser.add_argument('-s','--s-value',type=float,default=0.01,help='Step size, in mm')
    parser.add_argument('-a','--a-value',type=str,default='210,330,90',help='Tower angles comma separated, in deg')
    parser.add_argument('-n','--n-value',type=str,default='0,0',help='Nozzle moves, semicolon separated, in mm')
    parser.add_argument('-t','--t-value',type=str,default=None,help='Tower moves, semicolon separated, in mm')
    args = parser.parse_args()

    printer = DeltaPrinter(args.l_value, args.r_value, args.tl_value, args.s_value, [float(a) for a in args.a_value.split(',')])

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
