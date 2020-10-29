#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .frames import *
from .geometry import *

    #========= SOLIDS ====================================================#

class Solid:
    """Represents a solid."""

    def __init__(self, cfg, shp, m=1, q=0, i=0, M=Vector(0, 0, 0)):
        checkType([cfg], Configuration)
        checkType([shp], (Volume, Path))
        self.cfg = cfg               # configuration
        self.shp = shp               # shape
        self.m = Quantity(m, "kg")   # mass
        self.q = Quantity(q, "C")    # electric charge
        self.i = Quantity(i, "A")    # intensity
        self.M = Quantity(M, "A.m2") # magnetic moment
        self.tensor = None           # inertia tensor

    def calculateTensor(self):
        if self.shp.geometry is "sphere":
            k = mul((2/5), self.m, pwr(2)(self.shp.size[0]))
            self.tensor = mul(k, identity(3))
        if self.shp.geometry is "cylinder":
            k = div(add(mul(3, pwr(2)(self.shp.size[0])),
                        mul(4, pwr(2)(self.shp.size[1]))), 12)
            z = vec(0, 0, mul(pwr(2)(self.shp.size[0]), 1/2))
            x, y = vec(k, 0, 0), vec(0, k, 0)
            self.tensor = mul(self.m, mat(x, y, z))
        if self.shp.geometry is "cuboid":
            x = vec(add(pwr(2)(self.shp.size[1]),pwr(2)(self.shp.size[2])),0,0)
            y = vec(0,add(pwr(2)(self.shp.size[0]),pwr(2)(self.shp.size[2])),0)
            z = vec(0,0,add(pwr(2)(self.shp.size[0]),pwr(2)(self.shp.size[1])))
            self.tensor = mul(self.m, 1/12, mat(x, y, z))

    def __repr__(self):
        args = [self.cfg, self.shp, self.m, self.q, self.i, self.M] 
        return "Solid("+", ".join([repr(a) for a in args])+")"

    def copy(self):
        return eval(repr(self))

    #========= TRAJECTORIES ==============================================#

class Trajectory:
    """Generates and saves the trajectory of a solid."""

    def __init__(self, solid, data=None):
        checkType([solid], Solid)
        self.solid = solid
        if data is None:
            self.data = {"times": Storage("s", Vector.scalars),
                         "mEtoB": Storage("", Matrix),  # orientation
                         "mBtoE": Storage("", Matrix),  # orientation
                         "p": Storage("m", Vector),     # position
                         "f": Storage("N", Vector),     # force
                         "t": Storage("N.m", Vector),   # torque
                         "s": Storage("m.s-1", Vector), # speed
                         "a": Storage("m.s-2", Vector), # acceleration
                         "av": Storage("s-1", Vector),  # angular velocity
                         "aa": Storage("s-2", Vector)}  # angular acceleration
        else:
            checkType([data], dict)
            self.data = data
            
        # initial conditions
        self.iniSpe = Quantity(Vector(0, 0, 0), "m.s-1")
        self.iniAngVel = Quantity(Vector(0, 0, 0), "s-1")
        
        # force and torque
        def zeroForce(time, solid, speed, angularVelocity):
            return Quantity(Vector(0, 0, 0), "N")
        def zeroTorque(time, solid, speed, angularVelocity):
            return Quantity(Vector(0, 0, 0), "N.m")
        self.F = zeroForce
        self.T = zeroTorque
        
        # decomposition of the process for n-body simulations
        self.waitingData = False

    def __repr__(self):
        return "Trajectory("+repr(self.solid)+", "+repr(self.data)+")"

    def generate(self, timeInterval, dt):
        for i in range(int(div(timeInterval, dt).magnitude)):
            self.calculate(dt)
            self.save()

    def path(self):
        return Path(self.data["p"])

    def __len__(self):
        return len(self.data["times"])
        
    def calculate(self, dt):
        """Calculate the new data."""
        dt = Quantity(dt, "s")
        if self.waitingData:
            raise Exception("data not saved")
        self.waitingData = True
        if len(self) is 0:
            self.solid.calculateTensor()
            self.time = -dt
            self.s = self.iniSpe
            self.av = self.iniAngVel
        self.time = add(dt, self.time)
        #1 (force and torque)
        self.f = self.F(self.time, self.solid, self.s, self.av)
        self.t = self.T(self.time, self.solid, self.s, self.av)
        #2 (speed)
        self.a = div(self.f, self.solid.m)
        self.s = add(self.s, mul(dt, self.a))
        #3 (angular velocity)
        M = self.solid.cfg.basis.inside(self.t)
        self.aa = euler(self.solid.tensor, M, self.av)
        self.aa = self.solid.cfg.basis.outside(self.aa)
        self.av = add(self.av, mul(dt, self.aa)) 
        #4 (position)
        self.p = add(self.solid.cfg.position, mul(dt, self.s))
        #5 (orientation)
        rot = rotMat(mul(dt, self.av))
        self.mBtoE = mul(rot, self.solid.cfg.basis.matrixBtoE)
        self.mEtoB = inv(self.mBtoE)
        
    def save(self):
        """Save the new data."""
        if not self.waitingData:
            raise Exception('no waiting data')
        self.waitingData = False
        self.data["times"].add(self.time)
        self.data["f"].add(self.f)
        self.data["t"].add(self.t)
        self.data["a"].add(self.a)
        self.data["aa"].add(self.aa)
        self.data["s"].add(self.s)
        self.data["av"].add(self.av)             
        self.data["p"].add(self.solid.cfg.position)
        self.data["mBtoE"].add(self.solid.cfg.basis.matrixBtoE)
        self.data["mEtoB"].add(self.solid.cfg.basis.matrixInverse())
        self.solid.cfg = Configuration(self.p, Basis(self.mBtoE, self.mEtoB))

    def copy(self):
        return eval(repr(self))

    #========= FUNCTIONS =================================================#

def basisCreator(z):
    """Return a direct basis in which 'z' is the ordinate axis."""
    z = Quantity(z).magnitude
    checkType([z], Vector)
    if z[0] == 0 and z[1] == 0 and z[2] >= 0:
        return Basis(identity(3))
    if z[0] == 0 and z[1] == 0 and z[2] < 0:
        x, y, z = Vector(0, 1, 0), Vector(1, 0, 0), Vector(0, 0, -1)
        return Basis(Matrix(x, y, z))
    z = magDiv(z, magNorm(2)(z))
    x = magVecPro(z, Vector(0, 0, 1))
    x = magDiv(x, magNorm(2)(x))
    return Basis(Matrix(x, magVecPro(z, x), z))
    
def euler(I, M, w):
    """Return the angular acceleration using Euler's rotation equations.
    - I: Inertia tensor (solid basis) /!\ must be a diagonal matrix
    - M: torque (solid basis)
    - w: angular velocity (solid basis)"""
    I = Quantity(I, "kg.m2")
    M = Quantity(M, "N.m")
    w = Quantity(w, "s-1")
    
    checkType([I.magnitude], Matrix)
    checkType([M.magnitude], Vector)
    checkType([w.magnitude], Vector)
    
    w1, w2, w3 = w
    M1, M2, M3 = M
    I1, I2, I3 = I[0][0], I[1][1], I[2][2]
    
    a1 = div(add(mul(w2, w3, sub(I2, I3)), M1), I1)
    a2 = div(add(mul(w3, w1, sub(I3, I1)), M2), I2)
    a3 = div(add(mul(w1, w2, sub(I1, I2)), M3), I3)
    return vec(a1, a2, a3)
