#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .calculation import *

    #========= BASES =====================================================#

class Basis:
    """A basis is defined by a change-of-basis matrix."""

    def __init__(self, matrixBtoE, matrixEtoB=None):
        matrixBtoE = Quantity(matrixBtoE).magnitude
        checkType([matrixBtoE], Matrix)
        if matrixEtoB is not None:
            matrixEtoB = Quantity(matrixEtoB).magnitude
            checkType([matrixEtoB], Matrix)
        self.matrixBtoE = matrixBtoE
        self.matrixEtoB = matrixEtoB

    def __repr__(self):
        return "Basis("+repr(self.matrixBtoE)+", "+repr(self.matrixEtoB)+")"

    def matrixInverse(self):
        if self.matrixEtoB is None:
            self.matrixEtoB = inv(self.matrixBtoE).magnitude
        return self.matrixEtoB

    def inside(self, a):
        def aux(*args):
            q = Quantity(makeCallable(a)(*args), "m")
            if isinstance(q.magnitude, Vector):
                return mul(self.matrixInverse(), q)
            if isinstance(q.magnitude, Matrix):
                return mul(self.matrixInverse(), q, self.matrixBtoE)
            raise TypeError("no change of basis for "+str(type(q.magnitude)))
        return appropriateType(aux, [a])

    def outside(self, a):
        def aux(*args):
            q = Quantity(makeCallable(a)(*args), "m")
            if isinstance(q.magnitude, Vector):
                return mul(self.matrixBtoE, q)
            if isinstance(q.magnitude, Matrix):
                return mul(self.matrixBtoE, q, self.matrixInverse())
            raise TypeError("no change of basis for "+str(type(q.magnitude)))
        return appropriateType(aux, [a])

    def copy(self):
        return eval(repr(self))

    #========= CONFIGURATIONS ============================================#

class Configuration:
    """A configuration is defined by a position vector and a basis."""

    def __init__(self, position, basis):
        position = Quantity(position, "m")
        checkType([position.magnitude], Vector)
        checkUnit([position], Unit("m"))
        checkType([basis], Basis)
        self.position = position
        self.basis = basis

    def __repr__(self):
        position = self.position.magnitude
        return "Configuration("+repr(position)+", "+repr(self.basis)+")"

    def inside(self, v):
        """Return 'v' with respect to the configuration."""
        return self.basis.inside(sub(v, self.position))
        
    def outside(self, v):
        """Return 'v' with respect to the parent basis."""
        return add(self.basis.outside(v), self.position)

    def copy(self):
        return eval(repr(self))

    #========= COORDINATE TRANSFORMATIONS ================================#

def toSpherical(v):
    """(r: radial distance, theta: polar angle, phi: azimuthal angle)"""
    v = Quantity(v, "m")
    checkType([v.magnitude], Vector)
    r = norm(v)
    if r.magnitude == 0:
        return [r, Quantity(0), Quantity(0)]
    theta = arcCos(div(v[2], r))
    if v.magnitude[0] == 0:
        if v.magnitude[1] > 0:
            return [r, theta, Quantity(math.pi/2)]
        if v.magnitude[1] < 0:
            return [r, theta, Quantity(-math.pi/2)]
        return [r, theta, Quantity(0)]
    return [r, theta, arcTan(div(v[1], v[0]))]

def fromSpherical(r, theta, phi):
    """(r: radial distance, theta: polar angle, phi: azimuthal angle)"""
    r, theta, phi = Quantity(r, "m"), Quantity(theta), Quantity(phi)
    checkType([a.magnitude for a in [r, theta, phi]], Vector.scalars)
    if r.magnitude < 0:
        raise ValueError("'r' < 0")
    if theta.magnitude < 0 or theta.magnitude > math.pi:
        raise ValueError("'theta' < 0 or 'theta' > pi")
    if phi.magnitude < 0 or phi.magnitude > 2*math.pi:
        raise ValueError("'phi' < 0 or 'phi' > 2*pi")
    x, y = mul(r, sin(theta), cos(phi)), mul(r, sin(theta), sin(phi))
    return vec(x, y, mul(r, cos(theta)))

def toCylindrical(v):
    """(r : radial distance, phi: angular coordinate, z: height)"""
    v = Quantity(v, "m")
    checkType([v.magnitude], Vector)
    r = pwr(1/2)(add(pwr(2)(v[0]), pwr(2)(v[1])))
    z = v[2]
    if v.magnitude[0] == 0:
        if v.magnitude[1] > 0:
            return [r, Quantity(math.pi/2), z]  
        if v.magnitude[1] < 0:
            return [r, Quantity(-math.pi/2), z]
        return [r, Quantity(0), z]
    return [r, arcTan(div(v[1], v[0])), z]

def fromCylindrical(r, phi, z):
    """(r : radial distance, phi: angular coordinate, z: height)"""
    r, phi, z = Quantity(r, "m"), Quantity(phi), Quantity(z, "m")
    checkType([a.magnitude for a in [r, phi, z]], Vector.scalars)
    if r.magnitude < 0:
        raise ValueError("r < 0")
    if phi.magnitude < 0 or phi.magnitude > 2*math.pi:
        raise ValueError("phi < 0 or phi > 2*pi")
    return vec(mul(r, cos(phi)), mul(r, sin(phi)), z)
