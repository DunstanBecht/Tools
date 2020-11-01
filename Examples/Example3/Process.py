#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORT MODULES ============================================#

from Settings import *
from tools.supervision import *

    #========= TRAJECTORY AND FIELD ======================================#

def processTrajectories(T, dt, n):

    # Trajectories
    trajectories = [Trajectory(stars[i]) for i in range(n)]
    for i in range(n):
        trajectories[i].F = netForce
        trajectories[i].iniSpe = randomSpeed(stars[i].cfg.position)

    # Sequence
    def sequence():
        for i in range(n):
            trajectories[i].calculate(dt)
        for i in range(n):
            trajectories[i].save()
        
    # Calculation
    print("\n[TRAJECTORIES CALCULATION]")
    N = int(div(T, dt).magnitude)
    timer = Timer(N)
    for i in range(N):
        timer.before()
        sequence()
        timer.after()
    print("(i) Done!")

    # Rendering
    print("\n[TRAJECTORIES RENDERING]")
    rendering = Rendering(trajectories+[blackHole])
    rendering.settings["nameFig"] = "Black hole"
    rendering.settings["dispAxe"] = False
    rendering.settings["dispFor"] = True
    rendering.settings["coloTra"] = ["blue", "green", "red"]*5
    rendering.settings["coloDef"] = "grey"
    rendering.settings["coloFor"] = "white"
    rendering.settings["normFie"] = True
    rendering.settings["dispCon"] = False
    rendering.settings["listGra"] = ["f", "s"]
    print("(i) Done!")

    # Saving
    print("\n[TRAJECTORIES SAVING]")
    save("Saves/Trajectories.txt", rendering)
    print("(i) Done!")

    #========= LAUNCHER ==================================================#

if True:
    T = Quantity(60*60*24*40, "s") # modeling time
    dt = Quantity(60*60, "s") # cutting time
    processTrajectories(T, dt, n)

input("")
