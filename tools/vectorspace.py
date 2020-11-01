#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

import math
from . import *

    #========= VECTORS ===================================================#
        
class Vector:
    """A vector is defined by a sequence of scalars."""

    scalars = (int, float, complex)

    def __init__(self, *args):
        args = arguments(args)
        checkType(args, Vector.scalars)
        self.coordinates = list(args)

    def __len__(self):
        return len(self.coordinates)

    def __getitem__(self, index):
        return self.coordinates[index]

    def __setitem__(self, index, value):
        checkType([value], Vector.scalars)
        self.coordinates[index] = value

    def __repr__(self):
        return "Vector("+", ".join([repr(c) for c in self])+")"

    def __str__(self):
        n = max([len(str(c)) for c in self])
        return "\n".join(["|"+" "*(n-len(str(c)))+str(c)+"|" for c in self])

    def __eq__(self, vector):
        checkType([vector], Vector)
        return self.coordinates == vector.coordinates

    def copy(self):
        return eval(repr(self))

    #========= MATRICES ==================================================#

class Matrix:
    """A matrix is defined by a sequence of column vectors."""

    def __init__(self, *args):
        args = arguments(args)
        checkType(args, Vector)
        checkSize(args, len(args))
        self.vectors = [v for v in args]

    def __len__(self):
        return len(self.vectors)

    def __getitem__(self, index):
        return self.vectors[index]

    def __setitem__(self, index, value):
        checkType(value, Vector)
        checkSize(value, len(self))
        self.vectors[index] = value

    def __repr__(self):
        return "Matrix("+", ".join([repr(v) for v in self])+")"
    
    def __str__(self):
        n = [max([len(str(c)) for c in v]) for v in self]
        p = [[" "*(n[j]-len(str(self[j][i])))+str(self[j][i])
              for j in range(len(self))]
              for i in range(len(self))]
        return "\n".join(["|"+" ".join(line)+"|" for line in p])

    def __eq__(self, matrix):
        checkType(matrix, Matrix)
        return self.vectors == matrix.vectors

    def copy(self):
        return eval(repr(self))

    #========= MAGNITUDE FUNCTIONS =======================================#

def magAdd(*args):
    """Return the sum of the elements in 'args'."""
    args = arguments(args)
    if isinstance(args[0], Vector.scalars):
        checkType(args, Vector.scalars)
        return sum(args)
    argType = checkType(args)
    if argType is Vector:
        argSize = checkSize(args)
        return Vector([sum([c[i] for c in args]) for i in range(argSize)])
    if argType is Matrix:
        argSize = checkSize(args)
        return Matrix([magAdd([c[i] for c in args]) for i in range(argSize)])
    raise TypeError("addition not defined for "+str(argType))

def magSub(a, b):
    """Return the difference of 'a' and 'b'."""
    if isinstance(a, Vector.scalars):
        checkType([b], Vector.scalars)
        return a-b
    argType = checkType([a, b])
    if argType is Vector:
        argSize = checkSize([a, b])
        return Vector([a[j]-b[j] for j in range(argSize)])
    if argType is Matrix:
        argSize = checkSize([a, b])
        return Matrix([magSub(a[j], b[j]) for j in range(argSize)])
    raise TypeError("substraction not defined for "+str(argType))

def auxMul(a, b):
    """Return the product of 'a' and 'b'."""
    if isinstance(a, Vector.scalars):
        if isinstance(b, Vector.scalars):
            return a*b
        if isinstance(b, Vector):
            return Vector([a*c for c in b])
        if isinstance(b, Matrix):
            return Matrix([auxMul(a, v) for v in b])
    if isinstance(a, Vector) and isinstance(b, Vector.scalars):
        return Vector([b*c for c in a])
    if isinstance(a, Matrix):
        if isinstance(b, Vector.scalars):
            return Matrix([auxMul(b, v) for v in a])
        if isinstance(b, Vector):
            if len(a) is not len(b):
                raise ValueError(str(len(a))+"-dimensional matrix * "+
                                 str(len(b))+"-dimensional vector invalid")
            coordinates = [sum([a[j][i]*b[j] for j in range(len(a))])
                                             for i in range(len(a))]
            return Vector(coordinates)
        if isinstance(b, Matrix):
            if len(a) is not len(b):
                raise ValueError(str(len(a))+"-dimensional matrix * "+
                                 str(len(b))+"-dimensional matrix invalid")
            vectors = [auxMul(a, v) for v in b]
            return Matrix(vectors)
    raise TypeError(str(type(a))+" * "+str(type(b))+" multiplication invalid")

def magMul(*args):
    """Return the product of the elements in 'args'."""
    i = len(args)-1
    a = args[i]
    while i is not 0:
        i -= 1
        a = auxMul(args[i], a)
    return a

def magDiv(a, b):
    """Return the division of 'a' by 'b'."""
    checkType([b], Vector.scalars)
    return auxMul(a, 1/b)

def magPwr(p):
    """Return the 'p'-th power function."""
    def aux(a):
        if isinstance(a, Vector.scalars):
            return a**p
        if isinstance(a, Matrix) and isinstance(p, int) and p >= 0:
            if p is 0:
                return identity(len(a))
            return magMul([a for i in range(p)])
        raise TypeError("power "+str(p)+" not defined for "+str(type(a)))
    return aux

def magLog(b=math.e):
    """Return the logarithm to base 'b' function."""
    def aux(a):
        checkType([a], Vector.scalars)
        return math.log(a, b)
    return aux

def magExp(a, n=1000):
    """Return the exponential of 'a'."""
    if isinstance(a, Vector.scalars):
        return math.exp(a)
    if isinstance(a, Matrix):
        p = [magDiv(magPwr(k)(a), math.factorial(k)) for k in range(n)]
        return magAdd(p)
    raise TypeError("exponential not defined for "+str(type(a)))

def magScaPro(a, b):
    """Return the scalar product of 'a' and 'b'."""
    checkType([a, b], Vector)
    argSize = checkSize([a, b])
    return sum([a[i]*b[i] for i in range(argSize)])

def magVecPro(a, b):
    """Return the vector product of 'a' and 'b' in dimension 3."""
    checkType([a, b], Vector)
    checkSize([a, b], 3)
    x = a[1]*b[2] - a[2]*b[1]
    y = a[2]*b[0] - a[0]*b[2]
    z = a[0]*b[1] - a[1]*b[0]
    return Vector(x, y, z)

def magNorm(p=2):
    """Return the 'p'-norm function."""
    def aux(a):
        if isinstance(a, Vector.scalars):
            return abs(a)
        if isinstance(a, Vector):
            return sum([abs(c)**p for c in a])**(1/p)
        raise TypeError("norm "+str(p)+" not defined for "+str(type(a)))
    return aux

def submatrix(iCut, jCut, m):
    """Return 'm' without the line 'iCut' and the column 'jCut'."""
    p = [[m[j][i] for i in range(len(m)) if i is not iCut]
                  for j in range(len(m)) if j is not jCut]
    return Matrix([Vector(coordinates) for coordinates in p])

def magDet(m):
    """Return the determinant of 'm' using recursion."""
    checkType([m], Matrix)
    if len(m) is 1:
        return m[0][0]
    p = [((-1)**j)*m[j][0]*magDet(submatrix(0, j, m)) for j in range(len(m))]
    return sum(p)

def identity(n):
    """Return the identity matrix of size 'n'."""
    p = [[1 if i is j else 0 for i in range(n)] for j in range(n)]
    return Matrix([Vector(coordinates) for coordinates in p])

def rowSwi(i, j, m):
    """Apply the elementary operation R'i' <-> R'j' to 'm'."""
    for k in range(len(m)):
        m[k][i], m[k][j] = m[k][j], m[k][i]

def rowMul(i, k, m):
    """Apply the elementary operation 'k' * R'i' -> R'i' to 'm'."""
    if k == 0:
        raise ValueError("'k' is zero")
    for j in range(len(m)):
        m[j][i] = k*m[j][i]

def rowAdd(i, k, j, m):
    """Apply the elementary operation R'i' + 'k' * R'j' -> R'i' to 'm'."""
    if i is j:
        raise ValueError("'i' = 'j'")
    for p in range(len(m)):
        m[p][i] += k*m[p][j]
        
def pivot(j, m):
    """Return a pivot for the 'j'th column of 'm'."""
    row, absMax = j, abs(m[j][j])
    for i in range(j+1, len(m)):
        if abs(m[j][i]) > absMax:
            row, absMax = i, abs(m[j][i])
    return row

def magInv(m, checkDet=True):
    """Return the inverse of 'm' using Gaussian elimination."""
    if isinstance(m, Vector.scalars):
        return 1/m
    if not isinstance(m, Matrix):
        raise TypeError("inverse not defined for "+str(type(m)))
    if checkDet and magDet(m) == 0:
        raise ValueError("the determinant of the matrix is zero")

    auxMatrix = m.copy()
    invMatrix = identity(len(m))
    for j in range(len(m)):

        # Switching
        i = pivot(j, auxMatrix)
        rowSwi(i, j, auxMatrix)
        rowSwi(i, j, invMatrix)

        # Multiplication
        k = 1/auxMatrix[j][j]
        rowMul(j, k, auxMatrix)
        rowMul(j, k, invMatrix)

        # Addition
        for i in range(len(m)):
            if i is not j:
                k = -auxMatrix[j][i]
                rowAdd(i, k, j, auxMatrix)
                rowAdd(i, k, j, invMatrix)
                
    return invMatrix

def magRotMat(v):
    """Return the rotation matrix associated with the rotation vector 'v'."""
    checkType([v], Vector)
    checkSize([v], 3)
    
    theta = magNorm(2)(v)
    if theta == 0:
        return identity(3)
    
    u = auxMul(v, 1/theta)
    x, y, z = u[0], u[1], u[2]
    c, s = math.cos(theta), math.sin(theta)
    
    r1 = Vector(x*x*(1-c)+c, x*y*(1-c)+z*s, x*z*(1-c)-y*s)
    r2 = Vector(x*y*(1-c)-z*s, y*y*(1-c)+c, y*z*(1-c)+x*s)
    r3 = Vector(x*z*(1-c)+y*s, y*z*(1-c)-x*s, z*z*(1-c)+c)
    
    return Matrix(r1, r2, r3)

def magCom(i):
    """Return the 'i'th component of 'v'."""
    def aux(v):
        checkType([v], Vector)
        return v[i]
    return aux
