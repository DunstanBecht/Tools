#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import sys
sys.path.append('../../')
from tools.electromagnetism import *

    #========= PHYSICAL CONSTANTS ========================================#

m_e = Quantity(9.10938356*10**-31, "kg")  # electron mass
m_p = Quantity(1.672621898*10**-27, "kg") # proton mass
a_0 = Quantity(5.2917721067*10**-11, "m") # Bohr radius
g = Quantity(9.81, "m.s-2")               # standard gravity
h = Quantity(6.626070040*10**-34, "J.s")  # Planck constant
e = Quantity(-1.602*10**-19, "C")         # electron electric charge
lambda_e = -div(e, mul(2, m_e))           # gyromagnetic ratio
mu_B = mul(lambda_e, div(h, 2*math.pi))   # Bohr magneton

    #========= TRAP GEOMETRY =============================================#

L = Quantity(0.6, "m")  # trap length
R = Quantity(0.1, "m")  # trap radius
D = Quantity(0.02, "m") # trap spacing
N = 8                   # number of poles

def multipoleGeometry(n, length, radius):
    """Return a path corresponding to a coil with 'n' poles."""
    points = Storage("m", Vector)
    for i in range(n):
        a = 2*math.pi*(i/n)+math.pi/n
        x, y, z = mul(radius, cos(a)), mul(radius, sin(a)), div(length, 2)
        v1, v2 = vec(x, y, z), vec(x, y, -z)
        if i%2 is 0:
            points.add(v1)
            points.add(v2)
        else:
            points.add(v2)
            points.add(v1)
    points.add(points[0])
    return Path(points)

    #========= MIRROR COILS ==============================================#

n_sub = 72 # number of subdivisions
shape1 = regularPolygon(n_sub, add(R, D))

basisA = basisCreator(Vector(0, 1, 0))
basisB = basisCreator(Vector(0, -1, 0))

positionA = vec(0, -div(L, 2), 0)
positionB = vec(0, div(L, 2), 0)

coilA = Solid(Configuration(positionA, basisA), shape1)
coilB = Solid(Configuration(positionB, basisB), shape1)

    #========= MULTIPOLE =================================================#

d_sub = Quantity(0.01, "m") # integration lenght
shape2 = subdivide(d_sub, multipoleGeometry(N, add(L, mul(4, D)), R))

basisC = basisCreator(Vector(0, 1, 0))
positionC = Quantity(Vector(0, 0, 0), "m")
coilC = Solid(Configuration(positionC, basisC), shape2)

    #========= ELECTRIC CURRENT ==========================================#

def setCurrent(i):
    i = Quantity(i, "A")
    coilA.i, coilB.i, coilC.i = i, i, i

setCurrent(Quantity(1, "A"))

    #========= ANTIHYDROGEN ==============================================#

n = 1 # principal quantum number
positionH = Quantity(Vector(0, 0, 0), "m")
basisH = Basis(identity(3))
antihydrogen = Solid(Configuration(positionH, basisH), Volume(a_0))
antihydrogen.m = add(m_p, m_e)
antihydrogen.M = vec(0, 0, mul(n, mu_B))

    #========= EXACT MAGNETIC FIELD ======================================#

B1 = add(magneticField(coilA), magneticField(coilB), magneticField(coilC))

    #========= APPROXIMATED MAGNETIC FIELD ===============================#

if False: # calculation of a new field
    
    from tools.supervision import *
    field = Field(Volume(mul(2, R), mul(2, R), L), 0.005, coilC.cfg)
    timer = Timer(field.n[0]*field.n[1]*field.n[2])
    
    def function(r):
        timer.before()
        result = B1(r)
        timer.after()
        return result
    
    print("\n[FIELD CALCULATION]")
    field.sample(function)
    print("(i) Done!")
    save("Saves/FieldForApproximation.txt", field)

field = eval(load("Saves/FieldForApproximation.txt"))
oneAmpereB = continuousApproximation(field)
def B2(r):
    try:
        return mul(oneAmpereB(r), coilC.i.magnitude)
    except:
        print("/i\ Approximation error.")
        return Quantity(Vector(0, 0, 0), "T")

    #========= INFORMATIONS ==============================================#

if __name__ == "__main__":
    print("\n[CONSTANTS]")
    print("(i) Electron mass: "+str(m_e))
    print("(i) Proton mass: "+str(m_p))
    print("(i) Bohr radius: "+str(a_0))
    print("(i) Standard gravity: "+str(g))
    print("(i) Planck constant: "+str(h))
    print("(i) Electron electric charge: "+str(e))
    print("(i) Gyromagnetic ratio: "+str(lambda_e))
    print("(i) Bohr magneton: "+str(mu_B))
    print("\n[MAGNETIC FIELD]")
    print("(i) Sample spacing: "+str(field.spg))
    print("(i) Number of samples: "+str(field.n[0]*field.n[1]*field.n[2]))
    print("\n[ANTI HYDROGEN]")
    print("(i) Mass: "+str(antihydrogen.m))
    print("(i) Principal quantum number: "+str(n))
    print("(i) Magnetic moment: "+str(norm(antihydrogen.M)))
    print("\n[TRAP]")
    print("(i) Radius: "+str(R))
    print("(i) Length: "+str(L))
    print("\n[MIRROR COILS]")
    print("(i) Subivisions: "+str(n_sub))
    print("(i) Integration length: "+str(mul(add(R, D), 2*math.pi/n_sub)))
    print("\n[MULTIPOLE]")
    print("(i) Number of poles: "+str(N))
    print("(i) Subivisions: "+str(len(coilC.shp)))
    print("(i) Integration length: "+str(d_sub))
    input("")
