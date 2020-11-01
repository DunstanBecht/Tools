#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORT MODULES ============================================#

from Settings import *
from tools.supervision import *

    #========= TRAJECTORY AND FIELD ======================================#

def processTrajectories(T, dt, s1, s2):
   
    # Field
    field = Field(Volume(0, mul(3, au), mul(2, au)), div(au, 10))

    # Trajectories
    trajectory1 = Trajectory(star1)
    trajectory2 = Trajectory(star2)
    trajectory1.F = netForce
    trajectory2.F = netForce
    trajectory1.iniSpe = s1
    trajectory2.iniSpe = s2
    trajectory1.iniAngVel = vec(0, 0, Quantity(math.pi/(24*60*60), "s-1"))
    trajectory2.iniAngVel = vec(0, 0, Quantity(math.pi/(12*60*60), "s-1"))

    # Sequence
    def sequence():
        trajectory1.calculate(dt)
        trajectory2.calculate(dt)
        trajectory1.save()
        trajectory2.save()
        field.sample(g)
        
    # Calculation
    print("\n[TRAJECTORIES CALCULATION]")
    n = int(div(T, dt).magnitude)
    timer = Timer(n)
    for i in range(n):
        timer.before()
        sequence()
        timer.after()
    print("(i) Done!")

    # Rendering
    print("\n[TRAJECTORIES RENDERING]")
    rendering = Rendering([trajectory1, trajectory2, field])
    rendering.settings["nameFig"] = "Binary system"
    rendering.settings["dispAxe"] = False
    rendering.settings["coloTra"] = ["blue", "green"]
    rendering.settings["coloFie"] = "white"
    rendering.settings["normFie"] = True
    rendering.settings["dispCon"] = False
    rendering.comment.extend(["Mass star 1: "+str(star1.m),
                              "Mass star 2: "+str(star2.m)])
    print("(i) Done!")

    # Saving
    print("\n[TRAJECTORIES SAVING]")
    save("Saves/Trajectories.txt", rendering)
    print("(i) Done!")

    #========= LAUNCHER ==================================================#

if True:
    T = Quantity(24*60*60*250, "s") # modeling time
    dt = Quantity(24*60*60, "s") # cutting time
    s1 = Quantity(Vector(0, 0, 10000), "m.s-1") # star1 speed 
    s2 = Quantity(Vector(0, 0, -13000), "m.s-1") # star2 speed
    processTrajectories(T, dt, s1, s2)

input("")
