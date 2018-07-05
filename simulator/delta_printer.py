#!/usr/bin/env python

import sys

import math
from numpy import sqrt, dot, cross, array, zeros
from numpy.linalg import norm


class DeltaPrinter:
    
    def __init__(self, l, r, t = 90.0):
        self.l = l
        self.r = r
        self.t = math.radians(t) # tower tilt, t<90 means towers tilt outwards
        # self.h = math.sqrt(self.l*self.l - self.r*self.r)
        self.tower_angles = [210., 330., 90.]
        self.tower_coords = [(
            math.cos(math.radians(angle)) * self.r,
            math.sin(math.radians(angle)) * self.r) for angle in self.tower_angles]
        self.tower_positions = [0,0,0] # these positions are wrong, home() initialises them
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
# 1 : L (diagonal rod length)
# 2 : R (delta radius)
# 3 : T (towers tilt, in degrees; tilt < 90deg means towers tilted outwards, i.e. R increases with height)
# 4 : X (x coordinate of nozzle to move to)
# 5 : Y (y coordinate of nozzle to move to)
if __name__ == '__main__':
    #print(sys.argv)
    printer = DeltaPrinter(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
    printer.move(float(sys.argv[4]), float(sys.argv[5]))
    pos = printer.position()
    print("{0:.3f}, {1:.3f}, {2:.3f}".format(pos[0], pos[1], pos[2]))
    deltas = printer.tower_deltas()
    print("{0:.3f}, {1:.3f}, {2:.3f}".format(deltas[0],deltas[1],deltas[2]))
