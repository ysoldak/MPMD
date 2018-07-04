#!/usr/bin/env python

import sys

import math
from numpy import sqrt, dot, cross, array, zeros
from numpy.linalg import norm


class DeltaPrinter:
    
    def __init__(self, l, r, t = 1.0):
        self.l = l
        self.r = r
        self.t = t # tower tilt, t<1 means towers tilt outwards
        self.h = math.sqrt(self.l*self.l - self.r*self.r)
        tx = math.sin(math.radians(60))*r
        ty = math.cos(math.radians(60))*r
        self.tower_coords = [
            [-tx, -ty], [tx, -ty], [0, r]
        ]
        self.tower_positions = [self.h, self.h, self.h]

    def home(self):
        self.move(0, 0, 0)

    def move(self, x, y, z = 0):
        for i in [0, 1, 2]:
            tx = self.tower_coords[i][0]
            ty = self.tower_coords[i][1]
            new_pos = self.t * (math.sqrt(self.l*self.l - (tx-x)*(tx-x) - (ty-y)*(ty-y)) + z)
            self.tower_positions[i] = new_pos

    # Trilateration, https://stackoverflow.com/a/18654302
    # Basically calculate intersection of 3 spheres, simplified version of code above
    def position(self):
        sphere_centers = [zeros(3),zeros(3),zeros(3)]
        for i in [0, 1, 2]:
            _x = self.tower_coords[i][0]
            _y = self.tower_coords[i][1]
            _z = self.tower_positions[i]
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
        return [x-self.h for x in self.tower_positions]

if __name__ == '__main__':
    #print(sys.argv)
    printer = DeltaPrinter(float(sys.argv[1]), float(sys.argv[2]))
    printer.move(float(sys.argv[3]), float(sys.argv[4]))
    pos = printer.position()
    print("{0:.3f}, {1:.3f}, {2:.3f}".format(pos[0], pos[1], pos[2]))
    deltas = printer.tower_deltas()
    print("{0:.3f}, {1:.3f}, {2:.3f}".format(deltas[0],deltas[1],deltas[2]))
