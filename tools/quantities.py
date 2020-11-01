#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import string
from .vectorspace import *

    #========= UNITS =====================================================#
    
class Unit:
    """Represents the unit of a physical quantity."""

    base = [("kg",  [1, 0, 0, 0, 0, 0, 0], "mass"),
            ("m",   [0, 1, 0, 0, 0, 0, 0], "length"),
            ("s",   [0, 0, 1, 0, 0, 0, 0], "time"),
            ("A",   [0, 0, 0, 1, 0, 0, 0], "electric current"),
            ("K",   [0, 0, 0, 0, 1, 0, 0], "temperature"),
            ("mol", [0, 0, 0, 0, 0, 1, 0], "amount of substance"),
            ("cd",  [0, 0, 0, 0, 0, 0, 1], "luminous intensity")]

    derived = [("C",  [ 0,  0,  1,  1,  0,  0,  0], "electric charge"),
               ("F",  [-1, -2,  4,  2,  0,  0,  0], "electrical capacitance"),
               ("H",  [ 1,  2, -2, -2,  0,  0,  0], "electrical inductance"),
               ("J",  [ 1,  2, -2,  0,  0,  0,  0], "energy"),
               ("lx", [ 0, -2,  0,  0,  0,  0,  1], "illuminance"),
               ("N",  [ 1,  1, -2,  0,  0,  0,  0], "force"),
               ("Pa", [ 1, -1, -2,  0,  0,  0,  0], "pressure"),
               ("S",  [-1, -2,  3,  2,  0,  0,  0], "electrical conductance"),
               ("T",  [ 1,  0, -2, -1,  0,  0,  0], "magnetic field"),
               ("V",  [ 1,  2, -3, -1,  0,  0,  0], "voltage"),
               ("W",  [ 1,  2, -3,  0,  0,  0,  0], "power"),
               ("Wb", [ 1,  2, -2, -1,  0,  0,  0], "magnetic flux")]

    usual = [("",        [ 0,  0,  0,  0,  0,  0,  0], "dimensionless"),
             ("V.m-1",   [ 1,  1, -3, -1,  0,  0,  0], "electric field"),
             ("C.m-1",   [ 0, -1,  1,  1,  0,  0,  0], "linear charge"),
             ("C.m-2",   [ 0, -2,  1,  1,  0,  0,  0], "surface charge"),
             ("C.m-3",   [ 0, -3,  1,  1,  0,  0,  0], "volume charge"),
             ("F.m-1",   [-1, -3,  4,  2,  0,  0,  0], "permittivity"),
             ("H.m-1",   [ 1,  1, -2, -2,  0,  0,  0], "permeability"),
             ("A.m-1",   [ 0, -1,  0,  1,  0,  0,  0], "magnetization"),
             ("A.m-2",   [ 0, -2,  0,  1,  0,  0,  0], "current density"),
             ("m-1",     [ 0, -1,  0,  0,  0,  0,  0], "wavenumber"),
             ("m2",      [ 0,  2,  0,  0,  0,  0,  0], "area"),
             ("m3",      [ 0,  3,  0,  0,  0,  0,  0], "volume"),
             ("kg.m-1",  [ 1, -1,  0,  0,  0,  0,  0], "linear mass"),
             ("kg.m-2",  [ 1, -2,  0,  0,  0,  0,  0], "surface mass"),
             ("kg.m-3",  [ 1, -3,  0,  0,  0,  0,  0], "volume mass"),
             ("S.m-1",   [-1, -3,  3,  2,  0,  0,  0], "conductivity"),
             ("m.s-1",   [ 0,  1, -1,  0,  0,  0,  0], "speed"),
             ("m.s-2",   [ 0,  1, -2,  0,  0,  0,  0], "acceleration"),
             ("m.s-3",   [ 0,  1, -3,  0,  0,  0,  0], "jerk"),
             ("m.s-4",   [ 0,  1, -4,  0,  0,  0,  0], "jounce"),
             ("N.s",     [ 1,  1, -1,  0,  0,  0,  0], "momentum"),
             ("N.m.s",   [ 1,  2, -1,  0,  0,  0,  0], "angular momentum"),
             ("kg.m2",   [ 1,  2,  0,  0,  0,  0,  0], "moment of inertia"),
             ("J.K-1",   [ 1,  2, -2,  0, -1,  0,  0], "heat capacity"),
             ("K.W-1",   [-1, -2,  3,  0,  1,  0,  0], "thermal resistance")]

    def __init__(self, u=None):
        """Convert 'u' to its associated dimensional list."""

        if u is None:
            self.dimension = [0, 0, 0, 0, 0, 0, 0]
            
        elif isinstance(u, Unit):
            self.dimension = list(u.dimension)

        elif isinstance(u, list):
            checkSize([u], 7)
            checkType(u, int)
            self.dimension = list(u)

        elif isinstance(u, str):
            
            def convert1(s):
                for table in [Unit.base, Unit.derived, Unit.usual]:
                    for u in table:
                        if s == u[0]:
                            return u[1]
                raise ValueError(s+" is not a valid unit")
            
            def convert2(s):
                if s == "":
                    return 1
                try:
                    return int(s)
                except:
                    raise ValueError(s+" is not a valid power")
                
            dimension = [0, 0, 0, 0, 0, 0, 0]
            for g in u.split("."):
                d = convert1(g.strip("+-0123456789"))
                p = convert2(g.strip(string.ascii_letters))
                dimension = [dimension[i] + d[i]*p for i in range(7)]
                
            self.dimension =  dimension

        else:
            raise TypeError(str(u)+" is not a valid unit")

    def __repr__(self):
        return "Unit("+str(self.dimension)+")"
            
    def __floordiv__(self, d):
        checkType([d], (Unit, list))
        if isinstance(d, Unit):
            d = d.dimension
        q1, q2 = float('inf'), float('inf')
        for i in range(7):
            if d[i] is not 0:
                q1 = min(max(0, self.dimension[i]//d[i]), q1)
                q2 = min(max(0, -self.dimension[i]//d[i]), q2)
        return q1-q2

    def __str__(self):
        """Convert the dimensional list into a string."""

        # search in usual units
        for u in self.usual:
            if self.dimension == u[1]:
                return u[0]

        # decomposition into derived units
        q, w = 0, 0
        for i in range(len(Unit.derived)):
            s_i = Unit.derived[i][0]         # symbol
            d_i = Unit.derived[i][1]         # dimension
            q_i = self//d_i                  # quotient
            w_i = sum([abs(c) for c in d_i]) # weight
            if q_i is not 0 and w_i > w:
                s, d, q, w = s_i, d_i, q_i, w_i
        if q is not 0:
            if q is 1:
                p = ""
            else:
                p = str(q)
            r = str(Unit([self.dimension[i] - q*d[i] for i in range(7)]))
            if r is "":
                 return s+p
            return s+p+"."+r

        # decomposition into base units
        s = []
        for i in range(7):
            if self.dimension[i] is not 0:
                if self.dimension[i] is 1:
                    s.append(Unit.base[i][0])
                else:
                    s.append(Unit.base[i][0]+str(self.dimension[i]))
        return ".".join(s)

    def __eq__(self, u):
        checkType([u], (Unit, list))
        if isinstance(u, list):
            return self.dimension == u
        return self.dimension == u.dimension

    def name(self):
        for table in [Unit.base, Unit.derived, Unit.usual]:
            for u in table:
                if self.dimension == u[1]:
                    return u[2]
        return "unknown"

    def dimensionString(self):
        p, d = ["M", "L", "T", "I", "\u03F4", "N", "J"], self.dimension
        return ".".join([p[i]+str(d[i]) for i in range(7) if d[i] is not 0])

    def copy(self):
        return eval(repr(self))

def uniAdd(*args):
    """Verify that the units are the same and return the unit."""
    if not all([args[0] == args[i] for i in range(1, len(args))]):
        raise UnitError("the arguments have different units")
    return args[0]

def uniMul(*args):
    """Return the product unit."""
    return Unit([sum([u.dimension[i] for u in args]) for i in range(7)])

def uniDiv(a, b):
    """Return the divided unit."""
    return Unit([a.dimension[i] - b.dimension[i] for i in range(7)])

def uniPwr(p):
    """Return the 'p'-th power function."""
    def aux(u):
        d = [u.dimension[i]*p for i in range(7)]
        if isinstance(p, int):
            return Unit(d)
        if isinstance(p, float):
            q = [int(c) for c in d]
            if d == q:
                return Unit(q)
        raise ValueError("invalid power "+str(p)+" for unit "+str(u))
    return aux

    #========= QUANTITIES ================================================#
        
class Quantity:
    """A physical quantity is defined by a magnitude and a unit."""

    magnitudes = tuple(list(Vector.scalars)+[Vector, Matrix])

    def __init__(self, magnitude, unit=None, rewriteUnit=False):
        if isinstance(magnitude, Quantity): 
            if not rewriteUnit:
                unit = magnitude.unit
            magnitude = magnitude.magnitude
        checkType([magnitude], Quantity.magnitudes)
        self.magnitude, self.unit = magnitude, Unit(unit)

    def __repr__(self):
        return "Quantity("+repr(self.magnitude)+", "+repr(self.unit)+")"

    def __str__(self):
        return str(self.magnitude)+" "+str(self.unit)

    def __eq__(self, q):
        return self.magnitude == q.magnitude and self.unit == q.unit

    def __lt__(self, q):
        checkUnit([self, q])
        return self.magnitude < q.magnitude

    def __gt__(self, q):
        checkUnit([self, q])
        return self.magnitude > q.magnitude

    def __le__(self, q):
        checkUnit([self, q])
        return self.magnitude <= q.magnitude

    def __ge__(self, q):
        checkUnit([self, q])
        return self.magnitude >= q.magnitude

    def __neg__(self):
        return Quantity(magMul(-1, self.magnitude), self.unit)

    def __getitem__(self, index):
        return Quantity(self.magnitude[index], self.unit)
    
    def __len__(self):
        return len(self.magnitude)

    def copy(self):
        return eval(repr(self))

    #========= STORAGE ===================================================#

class Storage:
    """Stores a sequence of comparable physical quantities."""

    def __init__(self, unit=None, magType=None, data=None):
        if unit is not None:
            unit = Unit(unit)
        if data is None:
            data = []
        self.unit, self.magType, self.data = unit, magType, data

    def __repr__(self): 
        if self.magType is None:
            magType = "None"
        elif isinstance(self.magType, type):
            magType = self.magType.__name__
        else:
            magType = "("+", ".join([t.__name__ for t in self.magType])+")"
        return "Storage("+repr(self.unit)+", "+magType+", "+repr(self.data)+")"

    def serialize(self, value):
        if self.magType is Vector:
            return value.coordinates
        if self.magType is Matrix:
            return [v.coordinates for v in value.vectors]
        return value

    def deserialize(self, value):
        if self.magType is Vector:
            return Vector(value)
        if self.magType is Matrix:
            return Matrix([Vector(v) for v in value])
        return value

    def add(self, value):
        value = Quantity(value)
        if self.unit is None:
            self.unit = Unit(value.unit)
        if self.magType is None:
            self.magType = type(value.magnitude)
        checkUnit([value], self.unit)
        checkType([value.magnitude], self.magType)
        self.data.append(self.serialize(value.magnitude))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return Quantity(self.deserialize(self.data[index]), self.unit)
    
    def copy(self):
        return eval(repr(self))
