#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from Settings import *
from tools.supervision import *

    #========= FIELD =====================================================#

def processField(B, vol, spg, fileName="FieldCut"):

    field = Field(vol, spg, coilC.cfg)

    timer = Timer(field.n[0]*field.n[1]*field.n[2])
    
    def function(r):
        timer.before()
        result = B(r)
        timer.after()
        return result

    print("\n[FIELD CALCULATION]")
    field.sample(function)
    print("(i) Done!")

    print("\n[FIELD RENDERING]")
    rendering = Rendering([field, coilA, coilB, coilC])
    rendering.settings["nameFig"] = "Magnetic field"
    rendering.settings["dispAxe"] = True
    rendering.settings["normFie"] = True
    rendering.settings["coloFie"] = "white"
    rendering.settings["coloEnv"] = ["red", "red", "blue"]
    print("(i) Done!")

    print("\n[FIELD SAVING]")
    save("Saves/Simulations/"+fileName+".txt", rendering)
    print("(i) Done!")
    
    #========= TRAJECTORY ================================================#

def processTrajectory(B, T, f, I, fileName="Trajectory"):

    alpha2 = Quantity(-10**-12, "N.kg-1.m.s") # coefficient of friction?
    
    def netForce(t, solid, speed, angularVelocity):
        weight = vec(0, 0, -mul(g, solid.m))
        magnetic = magneticForce(solid, B)
        return add(magnetic, weight)

    def netTorque(t, solid, speed, angularVelocity):
        friction = mul(alpha2, solid.m, angularVelocity)
        magnetic = magneticTorque(solid, B)
        return add(friction, magnetic)

    dt = inv(f) # integration time

    trajectory = Trajectory(antihydrogen)
    trajectory.F, trajectory.T = netForce, netTorque
 
    print("\n[TRAJECTORY CALCULATION]")
    n = int(div(T, dt).magnitude)
    timer = Timer(n)
    for i in range(n):
        timer.before()
        trajectory.calculate(dt)
        trajectory.save()
        x, y, z = antihydrogen.cfg.position
        if pwr(1/2)(add(pwr(2)(z), pwr(2)(x))) > R or norm(y) > L:
            print("/!\ Ineffective trap!")
            break
        timer.after()
    print("(i) Done!")

    print("\n[TRAJECTORY RENDERING]")
    rendering = Rendering([trajectory, coilA, coilB, coilC])
    rendering.settings["nameFig"] = "Antihydrogen trajectory"
    rendering.settings["coloAxe"] = ["grey", "grey", "green"]
    rendering.settings["coloEnv"] = ["red", "red", "blue"]
    rendering.settings["dispAxe"] = False
    rendering.settings["dispPos"] = False
    print("(i) Done!")

    print("\n[TRAJECTORY SAVING]")
    save("Saves/Simulations/"+fileName+".txt", rendering)
    print("(i) Done!")

    #========= LAUNCHER ==================================================#

# Field
if True:
    spg = Quantity(0.01, "m")
    if True: # profil
        vol = Volume(0, mul(2, R), L)
        processField(B1, vol, spg, "FieldProfil")
    if True: # face
        vol = Volume(mul(2, R), mul(2, R), 0)
        processField(B1, vol, spg, "FieldFace")

# Trajetory
if True:
    T = Quantity(10**-6, "s") # modeling duration
    f = Quantity(10**10, "s-1") # frequency
    I = Quantity(100000, "A") # electric current (A)*winding
    processTrajectory(B2, T, f, I)

input('')
