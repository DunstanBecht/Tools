#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import sys
sys.path.append('../../')
from tools.gravitation import *

    #========= CONSTANTS =================================================#

au = Quantity(149597870700, "m") # astronomical unit
M = Quantity(2*10**30, "kg") # solar mass
R = Quantity(600000000, "m") # radius

    #========= STARS =====================================================#

star1 = Solid(Configuration(vec(0, -au, 0), Basis(identity(3))), Volume(R))
star1.m = M

star2 = Solid(Configuration(vec(0, au, 0), Basis(identity(3))), Volume(R))
star2.m = M

    #========= GRAVITATIONAL FIELD =======================================#

g = add(gravitationalField(star2), gravitationalField(star1))

    #========= NET FORCE =================================================#

def netForce(t, solid, speed, angularVelocity):
    return gravitationalForce(solid, g)

    #========= INFORMATIONS ==============================================#

if __name__ == "__main__":
    print("\n[CONSTANTS]")
    print("(i) Astronomical unit: "+str(au))
    print("(i) Solar mass: "+str(M))
    print("(i) Solar radius: "+str(R))
    input("")
