#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .frames import *
from .geometry import *
    
    #========= OPERATORS =================================================#

def gradient(f, d=0.001):
    """Return the gradient of 'f'."""
    def aux(r):
        return vec([parDer(i, d)(f)(r) for i in range(len(r))])
    return aux

def divergence(v, d=0.001):
    """Return the divergence of 'v'."""
    def aux(r):
        return add([parDer(i, d)(com(i)(v))(r) for i in range(len(r))])
    return aux

def scaLap(f, d=0.001):
    """Return the scalar Laplacian of 'f'."""
    return divergence(gradient(f, d), d)

def vecLap(v, d=0.001):
    """Return the vector Laplacian of 'v'."""
    def aux(r):
        return vec([scaLap(com(i)(v), d)(r) for i in range(len(r))])
    return aux

def curl(v, d=0.001):
    """Return the curl of 'v'."""
    v_x = com(0)(v)
    v_y = com(1)(v)
    v_z = com(2)(v)
    def aux(r):
        x = sub(parDer(1,d)(v_z)(r), parDer(2,d)(v_y)(r))
        y = sub(parDer(2,d)(v_x)(r), parDer(0,d)(v_z)(r))
        z = sub(parDer(0,d)(v_y)(r), parDer(1,d)(v_x)(r))
        return vec(x, y, z)
    return aux

    #========= FIELD =====================================================#

class Field:
    """Simplifies the sampling of a field."""

    def __init__(self, vol, spg, cfg=None, stg=None, n=None):
        checkType([vol], Volume) # shape of the sampling area
        spg = Quantity(spg, "m") # spacing of measurements
        if cfg is None:
            cfg = Configuration(Vector(0, 0, 0), Basis(identity(3)))
        else:
            checkType([cfg], Configuration)
        if stg is None:
            stg = Storage()
            if vol.geometry is "cuboid":
                n = [int(div(vol.size[0], spg).magnitude)+1,
                     int(div(vol.size[1], spg).magnitude)+1,
                     int(div(vol.size[2], spg).magnitude)+1, 0]
            elif vol.geometry is "cylinder":
                n = [int(div(vol.size[0], spg).magnitude/2),
                     int(div(vol.size[0], spg).magnitude*math.pi/2),
                     int(div(vol.size[1], spg).magnitude)+1, 0]
            elif vol.geometry is "sphere":
                n = [int(div(vol.size[0], spg).magnitude/2),
                     int(div(vol.size[0], spg).magnitude*math.pi/4),
                     int(div(vol.size[0], spg).magnitude*math.pi/2), 0]
        else:
            checkType([stg], Storage), checkType([n], list), checkType(n, int)
        self.vol, self.spg, self.cfg, self.stg, self.n = vol, spg, cfg, stg, n

    def __repr__(self):
        args = [self.vol, self.spg, self.cfg, self.stg, self.n]
        return "Field("+", ".join([repr(a) for a in args])+")"

    def position(self, i, j, k):
        if self.vol.geometry is "cuboid":
            v = Vector(i-(self.n[0]-1)/2, j-(self.n[1]-1)/2, k-(self.n[2]-1)/2)
            return self.cfg.outside(mul(self.spg, v))
        if self.vol.geometry is "cylinder":
            phi, z = 2*math.pi*(j/self.n[1]), mul(self.spg, k-self.n[2]/2)
            return self.cfg.outside(fromCylindrical(mul(self.spg,i+1), phi, z))
        theta, phi = math.pi*(j/self.n[1]), 2*math.pi*(k/self.n[2])
        return self.cfg.outside(fromSpherical(mul(self.spg,i+1), theta, phi))

    def sample(self, f):
        self.n[3] +=1
        for i in range(self.n[0]):
            for j in range(self.n[1]):
                for k in range(self.n[2]):
                    self.stg.add(f(self.position(i, j, k)))
        
    def value(self, i, j, k, t=0):
        return self.stg[k + self.n[2]*(j + self.n[1]*(i + self.n[0]*t))]

    #========= APPROXIMATION =============================================#

def continuousApproximation(field, t=0):
    """Return a continuous function of the field according to the samples."""
    checkType([field], Field)
    checkType([t], int)
    if field.vol.geometry is not "cuboid":
        raise ValueError("invalid field shape: "+field.vol.geometry)
    
    def aux(r):
        r = field.cfg.inside(Quantity(r, "m")).magnitude
        for axe in range(3):
            if abs(r[axe]) > field.spg.magnitude*(field.n[axe]-1)/2:
                raise ValueError("'r' is outside the sampled zone")
        i = (field.n[0]-1)//2 + int(r[0]/field.spg.magnitude)
        j = (field.n[1]-1)//2 + int(r[1]/field.spg.magnitude)
        k = (field.n[2]-1)//2 + int(r[2]/field.spg.magnitude)
        if i is field.n[0]-1:
            i -=1
        if j is field.n[1]-1:
            j -=1
        if k is field.n[2]-1:
            k -=1
        d = [[r[0] - field.spg.magnitude*(i-(field.n[0]-1)/2)],
             [r[1] - field.spg.magnitude*(j-(field.n[1]-1)/2)],
             [r[2] - field.spg.magnitude*(k-(field.n[2]-1)/2)]]
        for axe in range(3):
            d[axe].append(field.spg.magnitude - d[axe][0])
        values, weight, totVol = [], [], field.spg.magnitude**3
        for c in range(2):
            for b in range(2):
                for a in range(2):
                    values.append(field.value(i+a, j+b, k+c, t))
                    weight.append(d[0][1-a]*d[1][1-b]*d[2][1-c]/totVol)
        return add([mul(weight[i], values[i]) for i in range(8)])
    return aux
