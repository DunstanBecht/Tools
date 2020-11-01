#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORT ====================================================#

import sys
sys.path.append('../../../')
from tools.supervision import *

    #========= FUNCTIONS =================================================#

# Merge
def merge(l1, l2):
    return [(l1[i], l2[i]) for i in range(len(l1))]

# Split
def split(p):
    n = len(p)
    return [[p[i][0] for i in range(n)], [p[i][1] for i in range(n)]]

# Deleting duplicates
def delDup(rf, rI):
    old = merge(rf, rI)
    new = []
    for i in range(len(old)):
        if not old[i] in new:
            new.append(old[i])
    return split(new)

# Fusion
def fusion(rf1, rI1, rf2, rI2):
    p1 = merge(rf1, rI1)
    p2 = merge(rf2, rI2)
    for i in range(len(p1)):
        p2.append(p1[i])
    return split(p2)

    #========= LAUNCHER ==================================================#

# Fusion
if False:
    rf1, rI1 = eval(load("Save1.txt"))
    rf2, rI2 = eval(load("Save2.txt"))
    save("SaveWithDuplicates.txt", fusion(rf1, rI1, rf2, rI2))

# Deleting duplicates
if False:
    rf, rI = eval(load("SaveWithDuplicates.txt"))
    save("SaveWithoutDuplicates.txt", delDup(rf, rI))

# Sort
if False:
    rf, rI= eval(load("SaveWithoutDuplicates.txt"))
    L = merge(rf, rI)
    def order(a, b):
        return a[1] < b[1] or a[1] == b[1] and a[0] < b[0]
    L = mergeSort(order)(L)
    save("SaveSorted.txt", split(L))
