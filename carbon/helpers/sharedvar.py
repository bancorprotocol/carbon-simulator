"""
Carbon helper module - variables with shared state
"""
import math as _math

__VERSION__ = "1.0"
__DATE__= "26/Jan/2023"

class SharedVar:
    """
    encapsulates numbers into objects so that state can be shared

    :value:      the value with which to initialise the object
    :oid:        disregarded; just for the benefit of __repr__
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
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