#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .calculation import *

    #========= VOLUMES ===================================================#

class Volume:
    """Represents a volume."""

    def __init__(self, *args):
        args = [Quantity(a, Unit("m")) for a in arguments(args)]
        checkUnit(args, Unit("m"))
        checkType([a.magnitude for a in args], Vector.scalars)
        if len(args) is 1:
            self.geometry = "sphere"
        elif len(args) is 2:
            self.geometry = "cylinder"
        elif len(args) is 3:
            self.geometry = "cuboid"   
        else:
            raise ValueError("invalid dimensions")
        self.size = list(args)
        
    def __repr__(self):
        return "Volume("+", ".join([str(d.magnitude) for d in self.size])+")"
    
    def volume(self):
        if len(self.size) is 1:
            return mul(pwr(3)(self.size[0]), (4/3)*math.pi)
        if len(self.size) is 2:
            return mul(pwr(2)(self.size[0]), self.size[1], math.pi)
        return mul(self.size[0], self.size[1], self.size[2])

    def copy(self):
        return eval(repr(self))

    #========= PATHS =====================================================#

class Path:
    """Represents a path connecting the points defined by the vectors."""

    def __init__(self, *args):
        args = arguments(args)
        if isinstance(args[0], Storage):
            if args[0].magType is not Vector:
                raise ValueError("Storage unit invalid :"+str(args[0].unit))
            if args[0].unit != Unit("m"):
                raise ValueError("Storage type invalid :"+str(args[0].magType))
            self.points = args[0]
            self.dimension = checkSize(self.points.data)
        else:
            self.points = Storage("m", Vector)
            for a in [Quantity(a, Unit("m")) for a in args]:
                self.points.add(a)
            self.dimension = checkSize(self.points)

    def __repr__(self):
        return "Path("+repr(self.points)+")"

    def __getitem__(self, index):
        return self.points[index]

    def __setitem__(self, index, value):
        value = Quantity(value, "m")
        checkType([value.magnitude], Vector)
        checkSize([value], self.dimension)
        self.points[index] = value

    def __len__(self):
        return len(self.points)

    def length(self):
        if len(self) is 1:
            return Quantity(0, "m")
        return add([norm(sub(self[i+1], self[i])) for i in range(len(self)-1)])

    def copy(self):
        return eval(repr(self))

    #========= FUNCTIONS =================================================#

def regularPolygon(n, r=1):
    """Return the path of a regular polygon on the plane (O, x, y)."""
    points, r = Storage("m", Vector), Quantity(r, "m")
    for i in range(n):
        a = 2*math.pi*(i/n)
        points.add(vec(mul(r, cos(a)), mul(r, sin(a)), 0))
    points.add(points[0].copy())
    return Path(points)

def subdivide(d, path):
    """Return a path whose distance between two points is less than 'd'."""
    checkType([path], Path)
    points, d = Storage("m", Vector), Quantity(d, "m")
    for i in range(len(path)-1):
        r = norm(sub(path[i], path[i+1]))
        if r <= d:
            points.add(path[i].copy())
        else:
            n = int(div(r, d).magnitude)
            for k in range(n):
                t = k/n
                points.add(add(mul(1-t, path[i]), mul(t, path[i+1])))
    points.add(path[-1].copy())
    return Path(points)
