#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORT ====================================================#

import sys
sys.path.append('../')
sys.path.append('../../../')
from Settings import *
from tools.manager import *

    #========= TEST ======================================================#

def test(T, f, Ic, Im):
    
    # Antihydrogen reset
    antihydrogen.configuration = Configuration()

    # Settings
    if f == 0:
        dt = 0.01
    else:
        dt = 1/(f*16) # cutting time (s)
    w = 2*math.pi*f # pulse (rad/s)
    effectiveTrap = True

    # Trajectory
    trajectory = Trajectory(antihydrogen)
    trajectory.F, trajectory.T = netForce, netTorque
    trajectory.initialSpeed = Vector([0, 0, 0])

    # Sequence
    def sequence(t):
        phi = w*t
        multipole.intensity = Im*math.cos(phi)
        coilA.intensity = Ic*math.cos(phi)
        coilB.intensity = Ic*math.cos(phi)
        trajectory.calculate(dt)
        trajectory.save()  

    # Calculation
    n = int(T/dt)
    for i in range(n):
        sequence(i*dt)
        x, y, z = antihydrogen.configuration.position
        if (z**2+x**2)**(1/2) > trapRadius or abs(y) > trapLength:
            effectiveTrap = False
            print("-> Ineffective trap!")
            break

    if effectiveTrap:
        print("->   Effective trap!")

    return effectiveTrap

    #========= LAUNCHER ==================================================#

T = 5 # modeling duration (s)

# Results
rf, rI= load("Save.txt")

# Ranges
fList = [i for i in range(101)]
IList = [i*1000 for i in range(301)]

# Counter
n = len(fList)*len(IList)
c = 0

print("\n[TRAJECTORIES CALCULATION]")
for I in IList:
    for f in fList:
        c+=1
        strc = ' '*(len(str(n))-len(str(c)))+str(c)
        strI = ' '*(6-len(str(I)))+str(I)+" A"
        strf = ' '*(3-len(str(f)))+str(f)+" Hz"
        print("(i) f = "+strf+"  |  I = "+strI+"  | "+strc+"/"+str(n),
              end=" ")
        if test(T, f, I, I):
            rI.append(I)
            rf.append(f)
    save("Save.txt", [rf, rI])
    
print("(i) Done!")

input('')
