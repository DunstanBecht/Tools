#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .fields import *
from .mechanics import *

    #========= CONSTANTS =================================================#

G = Quantity(6.67408*10**-11, "N.m2.kg-2") # Newtonian constant of gravitation

    #========= POTENTIAL =================================================#

def gravitationalPotential(solid):
    """Return the gravitational potential generated by 'solid'."""
    checkType([solid], Solid)
    def aux(r):
        return -div(mul(G, solid.m), norm(sub(r, solid.cfg.position)))
    return aux

def gravitationalField(origin):
    """Return the gravitational field according to a potential or a solid."""
    if callable(origin):
        return mul(-1, gradient(origin))
    if isinstance(origin, Solid):
        def aux(r):
            r = sub(r, origin.cfg.position)
            n = norm(r)
            if n.magnitude == 0:
                return Quantity(Vector(0, 0, 0), "m.s-2")
            return div(mul(-1, G, origin.m, r), pwr(3)(n))
        return aux
    raise TypeError(name(origin)+" is not a valid origin")

def gravitationalForce(solid, g):
    """Return the gravitationnel force applied on 'solid'."""
    checkType([solid], Solid)
    return mul(solid.m, g(solid.cfg.position))
