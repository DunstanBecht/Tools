#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from Settings import *
from tools.supervision import *

    #========= FIELD =====================================================#

def processField(I, L, spg, n):

    # Field
    field = Field(Volume(0, L, L), spg)

    # Sequence
    def sequence(i):
        coil.i = mul(I, math.cos(2*math.pi*(i/n)))
        field.sample(B)

    # Calculation
    print("\n[FIELD CALCULATION]")
    timer = Timer(n)
    for i in range(n):
        timer.before()
        sequence(i)
        timer.after()
    print("(i) Done!")

    # Rendering
    print("\n[FIELD RENDERING]")
    rendering = Rendering([field, coil])
    rendering.settings["nameFig"] = "Magnetic field"
    rendering.settings["dispAxe"] = False
    rendering.settings["coloFie"] = "white"
    print("(i) Done!")

    # Saving
    print("\n[FIELD SAVING]")
    save("Saves/Field.txt", rendering)
    print("(i) Done!")

    #========= TRAJECTORY ================================================#

def processTrajectory(T, dt, f, I, s, w):

    # Trajectory
    trajectory = Trajectory(electron)
    trajectory.F = netForce
    trajectory.iniSpe, trajectory.iniAngVel = s, w 

    # Field
    field = Field(Volume(0, 0.1, 0.1), Quantity(0.02, "m"))

    # Sequence
    def sequence(t):
        coil.i = mul(I, cos(mul(2*math.pi, f, t)))
        trajectory.calculate(dt)
        trajectory.save()
        field.sample(B)

    # Calculation
    print("\n[TRAJECTORY CALCULATION]")
    n = int(div(T, dt).magnitude)
    timer = Timer(n)
    for i in range(n):
        timer.before()
        sequence(mul(i, dt))
        timer.after()
    print("(i) Done!")

    # Rendering
    print("\n[TRAJECTORY RENDERING]")
    rendering = Rendering([coil, trajectory, field])
    rendering.settings["nameFig"] = "Magnet trajectory"
    rendering.settings["dispAxe"] = False
    rendering.settings["dispCon"] = False
    rendering.settings["coloFie"] = "white"
    rendering.settings["coloTra"] = ["blue"]
    rendering.settings["sizeDef"] = R.magnitude
    rendering.settings["listGra"] = ["s", "f"]
    print("(i) Done!")

    # Saving
    print("\n[TRAJECTORY SAVING]")
    save("Saves/Trajectory.txt", rendering)
    print("(i) Done!")

    #========= LAUNCHER ==================================================#

# Field
if True:
    I = Quantity(1, "A")
    L = Quantity(0.6, "m") # field size (m)
    spg = Quantity(0.02, "m") # field spacing
    n = 36 # subdivisions of a time period
    processField(I, L, spg, n)

# Trajectory
if True:
    electron.cfg.position = Quantity(Vector(0, -0.2, 0.1), "m")
    T = Quantity(3, "s") # modeling duration
    dt = Quantity(0.005, "s") # cutting time
    f = Quantity(4, "s-1") # frequency
    I = Quantity(0.00003, "A") # current amplitude (A)*winding
    s = Quantity(Vector(0, 0.1, -0.01), "m.s-1") # initial speed
    w = Quantity(Vector(0, 0, 0), "s-1") # initial angular velocity
    processTrajectory(T, dt, f, I, s, w)

input('')
