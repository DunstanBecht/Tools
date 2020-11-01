#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

__author__ = "Dunstan Becht"
__version__ = "1.0.0"

    #========= IMPORTS ===================================================#

import os

    #========= STORAGE ===================================================#

def save(path, data):
    """Save the data to a file."""
    file = open(path, "w")
    file.write(__version__+"\n"+repr(data))
    file.close()
    
def load(path):
    """Load the data from a file and return a string."""
    file = open(path, "r")
    version, content = file.read().splitlines()
    file.close()
    if version == __version__:
        return content
    raise ImportError("version conflict: requires version "+version)

    #========= UNIT ERRORS ===============================================#

class UnitError(ValueError):
    """Non homogenous operation or incorrect unit."""

    #========= ARGUMENTS =================================================#

def arguments(args):
    """Simplify the recognition of arguments for functions using *args."""
    if len(args) is 0:
        raise ValueError("no argument is given")
    if len(args) is 1 and isinstance(args[0], (list, tuple)):
        return args[0]
    return args

def checkType(args, t=None):
    """Check the type of the items in 'args'."""
    if t is None: # the arguments must have the same type
        for i in range(1, len(args)):
            if type(args[0]) is not type(args[i]):
                raise TypeError("the arguments have different types")
        return type(args[0])
    else: # the arguments must have the type 't'
        for a in args:
            if not isinstance(a, t):
                message = "type "+str(type(a))+" invalid, "+str(t)+" requested"
                raise TypeError(message)
            
def checkSize(args, s=None):
    """Check the size of the items in 'args'."""
    if s is None: # the arguments must be the same size
        for i in range(1, len(args)):
            if len(args[0]) is not len(args[i]):
                raise TypeError("the arguments have different sizes")
        return len(args[0])
    else: # the arguments must be of size 's'
        for a in args:
            if len(a) is not s:
                message = "size "+str(len(a))+" invalid, "+str(s)+" requested"
                raise ValueError(message)

def checkUnit(args, u=None):
    """Check the unit of the items in 'args'."""
    if u is None: # the arguments must have the same unit
        for i in range(1, len(args)):
            if args[0].unit != args[i].unit:
                raise UnitError("the arguments have different units")
        return args[0].unit
    else: # the arguments must have the unit 'u'
        for a in args:
            if a.unit != u:
                message = "unit "+str(a.unit)+" invalid, "+str(u)+" requested"
                raise UnitError(message)
