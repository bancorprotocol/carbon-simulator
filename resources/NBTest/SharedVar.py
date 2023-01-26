# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from math import floor, ceil, trunc

# # SharedVar class

# +
import math as _math

# __VERSION__ = "0.1"
# __DATE_== "26/Jan/2023"

class SharedVar:
    """
    encapsulates numbers into objects so that state can be shared

    :value:      the value with which to initialise the object
    :oid:        disregarded; just for the benefit of __repr__
    """
#     __VERSION__ = __VERSION__
#     __DATE_ = __DATE_
    
    def __init__(self, value, oid=None):
        self._value = value
    
    @property
    def id(self):
        """the unique object id"""
        return id(self)
     
    @property
    def value(self):
        """the object value"""
        return self._value

    # comparison

    def __eq__(self, other):
        return self._value == other

    def __eq__(self, other):
        return self._value == other

    def __nq__(self, other):
        return self._value != other

    def __ge__(self, other):
        return self._value >= other

    def __le__(self, other):
        return self._value <= other

    def __lt__(self, other):
        return self._value < other

    def __gt__(self, other):
        return self._value > other

    # unitary operations (return values, not the object)
    def _wrap(self, val):
        """result wrapper"""
        return self.__class__(val)

    def __pos__(self):
        return self._wrap(self._value)

    def __neg__(self):
        return self._wrap(-self._value)

    def __abs__(self):
        return self._wrap(abs(self._value))

    def __round__(self, n):
        return self._wrap(round(self._value,n))

    def __floor__(self):
        return self._wrap(_math.floor(self._value))

    def __ceil__(self):
        return self._wrap(_math.ceil(self._value))

    def __trunc__(self):
        return self._wrap(_math.trunc(self._value))
    
    
    # binary operations

    def __add__(self, other):
        return self._wrap(self._value+other)
    __radd__ = __add__

    def __sub__(self, other):
        return self._wrap(self._value-other)    
    def __rsub__(self, other):
        return self._wrap(other-self._value)

    def __mul__(self, other):
        return self._wrap(self._value*other)
    __rmul__ = __mul__
    
    def __floordiv__(self, other):
        return self._wrap(self._value//other)
    def __rfloordiv__(self, other):
        return self._wrap(other//self._value)

    def __div__(self, other):
        return self._wrap(self._value/other)
    def __rdiv__(self, other):
        return self._wrap(other/self._value)

    def __truediv__(self, other):
        return self._wrap(self._value/other)
    def __rtruediv__(self, other):
        return self._wrap(other/self._value)

    def __mod__(self, other):
        return self._wrap(self._value%other)
    def __rmod__(self, other):
        return self._wrap(other%self._value)

    def __divmod__(self, other):
        d,m = divmod(self._value,other)
        return (self._wrap(d), self._wrap(m))
    def __rdivmod__(self, other):
        d,m = divmod(other, self._value)
        return (self._wrap(d), self._wrap(m))

    def __pow__(self, other):
        return self._wrap(self._value**other)
    def __rpow__(self, other):
        return self._wrap(other**self._value)

    def __lshift__(self, other):
        return self._wrap(self._value<<other)
    def __rlshift__(self, other):
        return self._wrap(other<<self._value)

    def __rshift__(self, other):
        return self._wrap(self._value>>other)
    def __rrshift__(self, other):
            return self._wrap(other>>self._value)
  
    def __and__(self, other):
        return self._wrap(self._value&other)    
    __rand__ = __and__
    
    def __or__(self, other):
        return self._wrap(self._value|other)    
    __ror__ = __or__
    
    def __xor__(self, other):
        return self._wrap(self._value^other)    
    __rxor__ = __xor__

    
    # Assignment operations
    def __iadd__(self, other):
        self._value+=other
        return self
    
    def __isub__(self, other):
        self._value-=other
        return self
        
    def __imul__(self, other):
        self._value*=other
        return self
        
    def __ifloordiv__(self, other):
        self._value//=other
        return self
        
    def __idiv__(self, other):
        self._value//=other
        return self
        
    def __itruediv__(self, other):
        self._value/=other   
        return self
        
    def __imod__(self, other):
        self._value%=other   
        return self
        
    def __ipow__(self, other):
        self._value**=other   
        return self
        
    def __ilshift__(self, other):
        self._value<<=other   
        return self
        
    def __irshift__(self, other):
        self._value>>=other   
        return self
        
    def __iand__(self, other):
        self._value&=other   
        return self
        
    def __ior__(self, other):
        self._value|=other   
        return self
        
    def __ixor__(self, other):
        self._value^=other   
        return self
 

    # Type conversions
    def __int__(self):
        return self.value.__int__()
    
    def __str__(self):
        return self.value.__str__()

    def __long__(self):
        return self.value.__long__()

    def __float__(self):
        return self.value.__float__()

    def __complex__(self):
        return complex(self.value)
    
    def __oct__(self):
        return self.value.__oct__()

    def __hex__(self):
        return self.value.__hex__()

    def __index__(self):
        return self.value.__int__()

    def __coerce__(self):
        return None

    # repr
    def __repr__(self):
        return f"{self.__class__.__name__}({self._value}, oid={self.id})"
# -

1+x

# #### Definitions

x, x2 = SharedVar(5), SharedVar(5.1234)
x

assert repr(x)[:20] == "SharedVar(5, oid="

# #### Comparisons

assert (x==x, x==5, x<5, x>5, x<=5, x>=5, 5<x, 5>x) == (True, True, False, False, True, True, False, False)
assert (x==x, 5<=x, 5>=x) == (True, True, True)

# #### Unitary operations

assert x==+x
assert x.id != (+x).id
assert (-x).value == -5
assert x.id != (-x).id
assert (abs(-x)).value == 5
assert x.id != (abs(-x)).id
assert round(x2,2)==5.12
assert x2.id != round(x2,2).id
assert trunc(x2)==5
assert x2.id != trunc(x2).id
assert floor(x2)==5
assert x2.id != floor(x2).id
assert ceil(x2)==6
assert x2.id != ceil(x2).id

# #### Binary operations

assert x+1 == 6
assert x.id != (x+1).id
assert x-1 == 4
assert x.id != (x-1).id
assert x*2 == 10
assert x.id != (x*2).id
assert x/2 == 2.5
assert x.id != (x/2).id
assert x//2 == 2
assert x.id != (x//2).id
assert x**2 == 25
assert x.id != (x//2).id
assert x<<1 == 10
assert x.id != (x<<1).id
assert x>>1 == 2
assert x.id != (x>>1).id
assert x&3 == 1
assert x.id != (x&3).id
assert x|2 == 7
assert x.id != (x|2).id
assert x^1 == 4
assert x.id != (x^1).id

assert divmod(x,2)[0] == 2
assert divmod(x,2)[1] == 1
assert x.id != divmod(x,2)[0].id
assert x.id != divmod(x,2)[1].id

# #### Reverse binary operations

assert 1+x == 6
assert x.id != (1+x).id
assert 1-x == -4
assert x.id != (1-x).id
assert 2*x == 10
assert x.id != (2*x).id
assert 2/x == 0.4
assert x.id != (2/x).id
assert 2//x == 0
assert x.id != (2//x).id
assert 2**x == 32
assert x.id != (2**x).id
assert 1<<x == 32
assert x.id != (1<<x).id
assert 1024>>x == 32
assert x.id != (1024>>x).id
assert 3&x == 1
assert x.id != (3&x).id
assert 2|x == 7
assert x.id != (2|x).id
assert 1^x == 4
assert x.id != (1^x).id

assert divmod(16,x)[0] == 3
assert divmod(16,x)[1] == 1
assert x.id != divmod(16,x)[0].id
assert x.id != divmod(16,x)[1].id

# #### Assignment operations

y = SharedVar(100)
id0 = y.id
y+=1
y-=1
y*=10
y//=10
assert y == 100
y<<=2
y>>=1
assert y == 200
y&=199
y|=1
y^=17
assert y == 208
y /= 32
assert y == 6.5
assert y.id == id0

# #### Conversions

x = SharedVar(5.5)
assert int(x) == 5
assert str(x) == "5.5"
assert float(x) == 5.5
assert complex(x) == complex(float(x))

1+x

__radd__(self, other)
Implements reflected addition.
__rsub__(self, other)
Implements reflected subtraction.
__rmul__(self, other)
Implements reflected multiplication.
__rfloordiv__(self, other)
Implements reflected integer division using the // operator.
__rdiv__(self, other)
Implements reflected division using the / operator.
__rtruediv__(self, other)
Implements reflected true division. Note that this only works when from __future__ import division is in effect.
__rmod__(self, other)
Implements reflected modulo using the % operator.
__rdivmod__(self, other)
Implements behavior for long division using the divmod() built in function, when divmod(other, self) is called.
__rpow__
Implements behavior for reflected exponents using the ** operator.
__rlshift__(self, other)
Implements reflected left bitwise shift using the << operator.
__rrshift__(self, other)
Implements reflected right bitwise shift using the >> operator.
__rand__(self, other)
Implements reflected bitwise and using the & operator.
__ror__(self, other)
Implements reflected bitwise or using the | operator.
__rxor__(self, other)
Implements reflected bitwise xor using the ^ operator.





