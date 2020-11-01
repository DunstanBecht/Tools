#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import sys
sys.path.append('../../')
from tools.gravitation import *
import random

    #========= CONSTANTS =================================================#

au = Quantity(149597870700, "m") # astronomical unit
M = Quantity(2*10**30, "kg") # solar mass
R = Quantity(600000000, "m") # radius

    #========= BLACK HOLE ================================================#
    
blackHoleConfiguration = Configuration(Vector(0, 0, 0), Basis(identity(3)))
blackHoleShape = regularPolygon(36, R)
blackHole = Solid(blackHoleConfiguration, blackHoleShape)
blackHole.m = mul(10000, M)

    #========= STARS =====================================================#

n = 15 # number of stars

def randomOrientation():
    phi = Quantity(2*math.pi*random.randint(0, 1999)/2000)
    theta = Quantity(math.pi*random.randint(400, 600)/1000)
    return fromSpherical(Quantity(1), theta, phi)

def randomConfiguration():
    position = mul(10, au, randomOrientation())
    position = mul(position, random.randint(500, 1500)/1000)
    basis = Basis(identity(3))
    return Configuration(position, basis)

def randomSpeed(position):
    v = pwr(1/2)(div(mul(G, blackHole.m), norm(position)))
    v = mul(v, random.randint(40, 50)/100)
    d = vecPro(position.magnitude, Vector(0, 0, 1))
    d = div(d, norm(d))
    return mul(v, d)
 
stars = [Solid(randomConfiguration(), Volume(R)) for i in range(n)]

for i in range(n):
    stars[i].m = M

    #========= GRAVITATIONAL FIELD =======================================#

g = add([gravitationalField(stars[i]) for i in range(n)])
g = add(g, gravitationalField(blackHole))

    #========= NET FORCE =================================================#

def netForce(t, solid, speed, angularVelocity):
    Ep = mul(norm(solid.cfg.position), norm(gravitationalForce(solid, g)))
    Ec = mul(1/2, solid.m, pwr(2)(norm(speed)))
    # print(add(Ec, Ep))
    return gravitationalForce(solid, g)

    #========= INFORMATIONS ==============================================#

if __name__ == "__main__":
    print("\n[CONSTANTS]")
    print("(i) Astronomical unit: "+str(au))
    print("(i) Solar mass: "+str(M))
    print("(i) Solar radius: "+str(R))
    print("\n[STARS]")
    print("(i) Number: "+str(n))
    print("\n[BLACK HOLE]")
    print("(i) Mass: "+str(blackHole.m))
    input("")

