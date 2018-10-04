#!/usr/bin/env python3

import sys
import argparse

from numpy import sqrt, dot, cross, array, zeros, radians, cos, sin, tan, pi
from numpy.linalg import norm

from delta_printer import DeltaPrinter

# FIXME tower lean does not work correctly
# TODO Support different L/R per tower
# TODO Support different lean and step_size per tower

class DeltaPrinterLean(DeltaPrinter):
    def __init__(self, length, radius, step_size = 0.01, angles = [210., 330., 90.], endstops = [0., 0., 0.], lean = 90.0):
        super().__init__(length, radius, step_size, angles, endstops)
        self.tower_lean = lean # tower lean, t<90 means towers lean outwards

    def move(self, x, y, z = 0, force = False):
        if self.tower_steps[0] is None and not force:
            raise Exception("Must home first")
        if self.tower_lean == 90.0:
            super().move(x, y, z, force)
        for tower in [0, 1, 2]:
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
            return super().carriage_position(tower)
        else:
            print("ERROR! FIXME")
            _re = self.tower_steps[tower] * self.step_size * cos(radians(self.tower_lean))
            _r = self.r + _re
            _x = cos(radians(self.tower_angles[tower])) * _r
            _y = sin(radians(self.tower_angles[tower])) * _r
            _z = self.tower_steps[tower] * self.step_size * sin(radians(self.tower_lean))
            return array([_x, _y, _z])

    @staticmethod
    def argument_parser():
        parser = DeltaPrinter.argument_parser()
        parser.add_argument('-tl','--tl-value',type=float,default=90.0,help='Tower lean, in deg, tl<90 means towers lean outwards')
        return parser
