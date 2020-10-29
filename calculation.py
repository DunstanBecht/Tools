#!/usr/bin/env python
# coding: utf-8

"""Source: highhopes.fr"""

    #========= IMPORTS ===================================================#

from .quantities import *

    #========= TYPE MANAGEMENT ===========================================#

def makeCallable(w):
    """Return:
    - 'w' if 'w' is a function
    - the constant function of value 'w' if 'w' is a constant"""
    if callable(w):
        return w
    def aux(r):
        return w
    return aux

def appropriateType(f, p):
    """Return:
    - the function 'f' if an item from the list 'p' is a function
    - the value of the constant function 'f' else"""
    for w in p:
        if callable(w):
            return f
    return f(None)

    #========= FUNCTION MAKER ============================================#

def functionMaker(magFun, uniFun=None):
    """Return the generalized version of the function."""
    if uniFun is None:
        def uniFun(u):
            if u.dimension != [0, 0, 0, 0, 0, 0, 0]:
                raise DimensionError("the quantity is not dimensionless")
            return [0, 0, 0, 0, 0, 0, 0]
    def aux1(*args1):
        args1 = arguments(args1)
        def aux2(*args2):
            q = [Quantity(makeCallable(a)(*args2)) for a in args1]
            m, u = [a.magnitude for a in q], [a.unit for a in q]
            return Quantity(magFun(*m), uniFun(*u))
        return appropriateType(aux2, args1)
    return aux1

    #========= GENERALIZED FUNCTIONS =====================================#

add = functionMaker(magAdd, uniAdd)

sub = functionMaker(magSub, uniAdd)

mul = functionMaker(magMul, uniMul)

div = functionMaker(magDiv, uniDiv)

exp = functionMaker(magExp)

scaPro = functionMaker(magScaPro, uniMul)

vecPro = functionMaker(magVecPro, uniMul)

norm = functionMaker(magNorm(2), uniAdd)

inv = functionMaker(magInv, uniPwr(-1))

rotMat = functionMaker(magRotMat)

sin = functionMaker(math.sin)

cos = functionMaker(math.cos)

tan = functionMaker(math.tan)

arcSin = functionMaker(math.asin)

arcCos = functionMaker(math.acos)

arcTan = functionMaker(math.atan)

def pwr(p):
    return functionMaker(magPwr(p), uniPwr(p))

def log(b):
    return functionMaker(magLog(b))

def det(m):
    def aux(r):
        q = Quantity(makeCallable(m)(r))
        return Quantity(magDet(q.magnitude), uniPwr(len(q.magnitude))(q.unit))
    return appropriateType(aux, [m])

def com(i):
    return functionMaker(magCom(i), uniAdd)

def der(f, d=0.001):
    """Return the derivative of the function 'f'."""
    def aux(x):
        delta = sub(f(add(x, Quantity(d, x.unit))),
                    f(sub(x, Quantity(d, x.unit))))
        if not isinstance(delta.magnitude, Vector.scalars):
            raise ValueError("'f' is not a scalar function")
        return Quantity((delta).magnitude/(2*d), uniDiv(delta.unit, x.unit))
    return aux

def parDer(i, d=0.001):
    """Return the partial derivative function with respect to axis 'i'."""
    def aux1(f):
        def aux2(r):
            def g(x):
                # g: scalar -> scalar
                v = r.copy()
                v.magnitude[i] += x.magnitude
                return f(v)
            return der(g, d)(Quantity(0, r.unit))
        return aux2
    return aux1

def simpson(a, b):
    """Return the operator integral over ['a','b'] using Simpson rule's."""
    def aux(f):
        return mul(sub(b,a), add(f(a), mul(f(div(add(a,b), 2)), 4), f(b)), 1/6)
    return aux

def defInt(a, b, d=0.001):
    """Return the operator integral over ['a','b']."""
    def aux(f):
        if b == a:
            return Quantity(0, uniMul(f(a).unit, a.unit))
        delta = sub(b, a)
        n = int(div(delta, d).magnitude)+1
        e = div(delta, n)
        p = [simpson(add(a, mul(e, i)), add(a, mul(e, 1+i)))(f)
             for i in range(n)]
        return add(p)
    return aux

def indInt(a=0, d=0.001):
    """Return the operator integral."""
    def aux1(f):
        def aux2(x):
            return defInt(a, x, d)(f)
        return aux2
    return aux1

def vec(*c):
    """Assemble scalar quantities into a vector."""
    def v(*r):
        c_r = [Quantity(makeCallable(a)(*r)) for a in arguments(c)]
        unit = checkUnit([a for a in c_r if a.magnitude is not 0])
        return Quantity(Vector([a.magnitude for a in c_r]), unit)
    return appropriateType(v, c)

def mat(*v):
    """Assemble vector quantities into a matrix."""
    def m(*r):
        v_r = [Quantity(makeCallable(a)(*r)) for a in arguments(v)]
        unit = checkUnit([a for a in v_r if a.magnitude is not 0])
        for i in range(len(v_r)):
            if v_r[i].magnitude is 0:
                v_r[i].magnitude = Vector([0 for j in range(len(v_r))])
        return Quantity(Matrix([a.magnitude for a in v_r]), unit)
    return appropriateType(m, v)
