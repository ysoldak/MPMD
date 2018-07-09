#!/usr/bin/env python

import sys
import argparse

import math
from numpy import sqrt, dot, cross, array, zeros
from numpy.linalg import norm


class DeltaPrinter:
    
    def __init__(self, l, r, t = 90.0, e = 0):
        self.l = l
        self.r = r
        self.t = math.radians(t) # tower tilt, t<90 means towers tilt outwards
        self.e = e/100
        # self.h = math.sqrt(self.l*self.l - self.r*self.r)
        self.tower_angles = [210., 330., 90.]
        self.tower_coords = [(
            math.cos(math.radians(angle)) * self.r,
            math.sin(math.radians(angle)) * self.r) for angle in self.tower_angles]
        self.tower_positions = [None,None,None]
        self.home()
        self.tower_home_positions = [p for p in self.tower_positions]

    def home(self):
        self.move(0, 0, 0)

    def move(self, x, y, z = 0):
        for i in [0, 1, 2]:

            tx = self.tower_coords[i][0]
            ty = self.tower_coords[i][1]
            tr = math.sqrt((tx-x)*(tx-x) + (ty-y)*(ty-y))

            tga = math.tan(self.t)

            a = 1 + 1/(tga*tga)
            b = 2*tr/tga - 2*z
            c = tr*tr + z*z - self.l*self.l

            d = b*b - 4*a*c
            if d < 0:
                raise Exception('spam', 'eggs')
            h1 = (-b - math.sqrt(d))/(2*a)
            h2 = (-b + math.sqrt(d))/(2*a)
            h = max(h1,h2)

            new_pos = h / math.sin(self.t)

            # following is code with no tower tilt support
            # tx = self.tower_coords[i][0]
            # ty = self.tower_coords[i][1]
            # new_pos = math.sqrt(self.l*self.l - (tx-x)*(tx-x) - (ty-y)*(ty-y)) + z
            if self.tower_positions[i] is not None:
                pos_delta = new_pos - self.tower_positions[i]
                self.tower_positions[i] += pos_delta*(1 + self.e)
            else:
                self.tower_positions[i] = new_pos
    # Trilateration, https://stackoverflow.com/a/18654302
    # Basically calculate intersection of 3 spheres, simplified version of code above
    def position(self):
        sphere_centers = [zeros(3),zeros(3),zeros(3)]
        for i in [0, 1, 2]:

            _re = self.tower_positions[i] * math.cos(self.t)
            _r = self.r + _re
            _x = math.cos(math.radians(self.tower_angles[i])) * _r
            _y = math.sin(math.radians(self.tower_angles[i])) * _r
            _z = self.tower_positions[i] * math.sin(self.t)

            # following is code with no tower tilt support
            # _x = self.tower_coords[i][0]
            # _y = self.tower_coords[i][1]
            # _z = self.tower_positions[i]

            sphere_centers[i] = array([_x, _y, _z])
        #print(sphere_centers)
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
        #print(temp4)
        if temp4<0:                                          
            raise Exception("The three spheres do not intersect!")
        z = sqrt(temp4)                                      
        return sphere_centers[0] + x*e_x + y*e_y - z*e_z
    
    def tower_deltas(self):
        return [p-h for h, p in zip(self.tower_home_positions, self.tower_positions)]

def error(correct, wrong, x, y, z = 0):
    # we move wrongly configured printer and copy carriage positions to correct model and see where the nozzle ends up
    wrong.move(x, y, z)
    correct.tower_positions = wrong.tower_positions
    return correct.position()

# args
# 1 : L (Diagonal rod length)
# 2 : R (Delta radius)
# 3 : T (Towers lean, in degrees; lean < 90deg means towers tilted outwards, i.e. R increases with height)
# 4 : E (Carriage movement error in %, to simpulate effect of wrong steps/mm configuration)
# 5 : C (Coordinates to move the nozzle to, semicolon separated triplets of 3d coords)

# Example usage:
#   ./delta_printer.py -l 120 -r 62 -t 89 -e -1 -c '0,10,0;0,-10,5'
if __name__ == '__main__':

    l_value = 120.8
    r_value = 61.7
    t_value = 90.0
    e_value = 0.0

    parser = argparse.ArgumentParser(description='Delta errors simulation')
    parser.add_argument('-l','--l-value',type=float,default=l_value,help='Correct l-value, in mm')
    parser.add_argument('-r','--r-value',type=float,default=r_value,help='Correct r-value, in mm')
    parser.add_argument('-t','--t-value',type=float,default=t_value,help='Tower lean, in deg, t<90 means towers leans outwards')
    parser.add_argument('-e','--e-value',type=float,default=e_value,help='Carriages error, in %')
    parser.add_argument('-c','--c-value',type=str,default='0,0',help='Coords to move, can specify several, semicolon separated, in mm')
    args = parser.parse_args()

    printer = DeltaPrinter(args.l_value, args.r_value, args.t_value, args.e_value)

    coords = [x.split(",") for x in args.c_value.split(";")]
    for coord in coords:
        coord = [float(coord[0]), float(coord[1]), float(coord[2]) if len(coord) == 3 else 0.0]
        printer.move(coord[0], coord[1], coord[2])
        pos = printer.position()
        print("Nozzle: {0:.3f}, {1:.3f}, {2:.3f}".format(pos[0], pos[1], pos[2]))
        towers = printer.tower_positions
        print("Towers: {0:.3f}, {1:.3f}, {2:.3f}".format(towers[0],towers[1],towers[2]))
        deltas = printer.tower_deltas()
        print("Deltas: {0:.3f}, {1:.3f}, {2:.3f}".format(deltas[0],deltas[1],deltas[2]))
        print("")
