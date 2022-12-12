"""
some useful sympy extensions
"""
__VERSION__ = "1.0"
__DATE__ = "12/Dec/2022"

from sympy import *
from sympy import Eq as sympyEq


class XEq(sympyEq):
    """
    extended SymPy equation

    USAGE

        eqn.invert                  # 1/eqn
        eqn.neg                     # -eqn
        eqn.swap                    # swaps lhs, rhs
        eqn.isolate(x)              # isolate x, returns eqn x=...
        eqn.subs_eq(eqn2)           # in eqn, substitute eqn2.lhs with rhs
        -eqn                        # -eqn
        eqn1 + eqn2                 # sum (equations)
        1 + eqn + 1                 # sum (scalars)
        eqn1 - eqn2                 # difference (equations)
        1 - eqn - 1                 # difference (scalars)
        eqn1 * eqn2                 # product (equations)
        2 * eqn * 3                 # product (scalars)
        eqn1 / eqn2                 # division (equations)
        2 / eqn / 3                 # division (scalars)

    """

    def _simplify(self):
        "dummy"
        return self

    def simplify0(self):
        "brings all to the lsh and then simplified"
        return self.__class__(self.lhs-self.rhs,0).simplify()
    
    def simplify1(self):
        "simplifies both sides independently"
        return self.__class__(self.lhs.simplify(), self.rhs.simplify())

    def invert(self):
        "returns 1/eqn"
        return 1/self
    
    def neg(self):
        "returns -eqn"
        return -self

    def swap(self):
        "swaps lhs, rsh"
        return self.__class__(self.rhs, self.lhs) 
    
    def isolate(self, var, ix=0):
        "isolates var in equation (ix is solution index)"
        return self.__class__(var, solve(self, var)[ix])
    
    def subs_eq(self, eqn):
        "substitutes self with the relation in eqn (eg `y=x**2`)"
        return self.subs(eqn.lhs, eqn.rhs)._simplify()

    s = subs_eq
    
    def sy(self):
        "alias for simplify"
        return self.simplify()
        
    def __add__(self, o):
        "adds two equations or scalar to equation"
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs+o.lhs, self.rhs+o.rhs)._simplify()
        return self.__class__(self.lhs+o, self.rhs+o)._simplify()
    
    __radd__ = __add__
    
    def __sub__(self, o):
        "substracts two equations or scalar from an equation"
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs-o.lhs, self.rhs-o.rhs)._simplify()
        return self.__class__(self.lhs-o, self.rhs-o)._simplify()
    
    def __rsub__(self, o):
        "substracts two equations or scalar from an equation"
        if isinstance(o, sympyEq):
            return self.__class__(-self.lhs+o.lhs, -self.rhs+o.rhs)._simplify()
        return self.__class__(-self.lhs+o, -self.rhs+o)._simplify()

    def __neg__(self):
        "negative equation"
        return self.__class__(-self.lhs, -self.rhs)
        
    def __mul__(self, o):
        "multiplies two equations or scalar with equation "
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs*o.lhs, self.rhs*o.rhs)._simplify()
        return self.__class__(self.lhs*o, self.rhs*o)._simplify()

    __rmul__ = __mul__
    
    def __truediv__(self, o):
        "divides two equations or equation by scalar"
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs/o.lhs, self.rhs/o.rhs)._simplify()
        return self.__class__(self.lhs/o, self.rhs/o)._simplify()
    
    def __rtruediv__(self, o):
        "divides two equations or equation by scalar"
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs/o.lhs, self.rhs/o.rhs)._simplify()
        return self.__class__(o/self.lhs, o/self.rhs)._simplify()  
    
    def __pow__(self, o):
        "raises one equation to the power of the other (or scalar)"
        if isinstance(o, sympyEq):
            return self.__class__(self.lhs**o.lhs, self.rhs**o.rhs)._simplify()
        return self.__class__(self.lhs**o, self.rhs**o)._simplify()
 
    def __rpow__(self, o):
        "raises one equation to the power of the other (or scalar)"
        if isinstance(o, sympyEq):
            return self.__class__(o.lhs**self.lhs, o.rhs**self.rhs)._simplify()
        return self.__class__(o**self.lhs, o**self.rhs)._simplify()

def subs(expr, eqn, simplify=True):
    "substitute eqn.lhs for eqn.rhs in expr"
    result = expr.subs(eqn.lhs, eqh.rhs)
    if simplify:
        result = result._simplify()
    return result

Eq = XEq