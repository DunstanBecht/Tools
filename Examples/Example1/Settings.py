#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import sys
sys.path.append('../../')
from tools.electromagnetism import *

    #========= CONSTANTS =================================================#

m_e = Quantity(9.10938356*10**-31, "kg")  # electron mass
e = Quantity(-1.602*10**-19, "C")         # electron electric charge
a_0 = Quantity(5.2917721067*10**-11, "m") # Bohr radius

    #========= COIL ======================================================#

R = Quantity(0.1, "m") # radius of the coil
n = 36 # subdivisions of the coil
coilPosition = Quantity(Vector(0, 0, 0), "m")
coilBasis = Basis(identity(3))
coilConfigurarion = Configuration(coilPosition, coilBasis)
coilShape = regularPolygon(n, R)
coil = Solid(coilConfigurarion, coilShape)

    #========= ELECTRON ==================================================#

electronPosition = Quantity(Vector(0, -0.1, 0), "m")
electronBasis = Basis(identity(3))
electronConfiguration = Configuration(electronPosition, electronBasis)
electronShape = Volume(a_0)
electron = Solid(electronConfiguration, electronShape)
electron.m = m_e
electron.q = -e

    #========= MAGNETIC FIELD ============================================#

B = magneticField(coil)

    #========= ELECTRIC FIELD ============================================#

def E(*args):
    return Quantity(Vector(0, 0, 0), "V.m-1")

    #========= NET FORCE =================================================#

def netForce(t, solid, speed, angularVelocity):
    return lorentzForce(solid, E, speed, B)

    #========= INFORMATIONS ==============================================#

if __name__ == "__main__":
    print("\n[COIL]")
    print("(i) Radius: "+str(R))
    print("(i) Subdivisions: "+str(n))
    print("(i) Integration length: "+str(mul(R, 2*math.pi/n)))
    print("\n[ELECTRON]")
    print("(i) Shape: "+electron.shp.geometry)
    print("(i) Radius: "+str(electron.shp.size[0]))
    print("(i) Mass: "+str(electron.m))
    print("(i) Charge: "+str(electron.q))
    input("")
