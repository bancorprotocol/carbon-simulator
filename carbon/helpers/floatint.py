"""
Carbon helper module - efficiently store Carbon coefficients in ints
"""
__VERSION__ = "1.0"
__DATE__ = "10/Feb/2023"

from dataclasses import dataclass as _dataclass, asdict as _asdict
from math import log2 as _log2, ceil as _ceil

@_dataclass
class CarbonFloatInt64():
    """
    represents an integer as significant * 2**exponent with scale one_exponent
    
    :significant:     the significant digits of the number
    :exponent:        the (positive) base-2 exponent of the number
    
    purpose of this class is to compress an integer that has a natural precision
    compoment and a natural scale component; with the default values of 40, 8
    the resulting in can be any integer number with up to 40 significant bits 
    that can be shifted right up to 256 bit, for a total number of bits of
    296 bits.
    
    The global scale (for representing floats) is provided in the class level
    constant ONE_EXPONENT which, as indicated in the class name, is 64; 
    in order to change it use class inheritance
    
        class CarbonFloatInt32(CarbonFloatInt64):
            ONE_EXPONENT = 32
            
    """
    significant: int
    exponent: int

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    BITS_SIGNIFICANT =  40
    BITS_EXPONENT    =   8
    ONE_EXPONENT     =  64  # the exponent of "number 1", ie the global scale parameter
        
    def __post_init__(self):
        assert isinstance(self.significant, int), f"significant must be an int [{self.significant}]"
        assert isinstance(self.exponent, int), f"exponent must be an int [{self.exponent}]"
        assert self.exponent >= 0, f"exponent must be >= 0 [{self.exponent}]"
    
    @staticmethod
    def bindig(num):
        """binary digits for num >0 [_ceil(_log2(rawint+1))]"""
        return _ceil(_log2(num+1))

    @classmethod
    def from_int(cls, rawint):
        """
        alternative constructor: from raw int
        
        :rawint:    the _actual_ intval to be represented in the class
        """
        assert isinstance(rawint, int), f"value must be int [{rawint}]"
        assert rawint >= 0, f"value must be positive [{rawint}]"
        if rawint == 0:
            return cls(0,0)
        
        bindig = cls.bindig(rawint)
        exponent = bindig - cls.BITS_SIGNIFICANT
        assert exponent <= 2**cls.BITS_EXPONENT, f"exponent must be <= {2**cls.BITS_EXPONENT}, is {exponent} [{intval}]"
        if exponent <= 0:
            return cls(rawint, 0)
        return cls(rawint >> exponent, exponent)
    
    @classmethod
    def from_float(cls, floatval):
        """
        alternative constructor: from float
        
        :floatval:       the number to be represented
        :returns:        cls.from_int(floatval * cls._one())
        """
        return cls.from_int( int(floatval * cls._one()) )
    
    @classmethod
    def max(cls, minus=0):
        """returns maximum possible number (possibly 1,2,3 etc before)"""
        return cls(2**cls.BITS_SIGNIFICANT-1-minus, 2**cls.BITS_EXPONENT-1)
    
    @classmethod
    def min(cls, plus=0):
        """returns minimum possible number > 0 (possibly 1,2,3 etc after)"""
        return cls(1+plus, 0)   
    
    @property
    def astuple(self):
        """alias for tuple(asdict(self).values())"""
        return tuple(self.asdict.values())
    
    @property
    def astuple1(self):
        """alias for tuple(asdict1(self).values())"""
        return tuple(self.asdict1.values())
    
    @property
    def asdict(self):
        """alias for asdict(self)"""
        return _asdict(self)

    @property
    def asdict1(self):
        """adds ONE_EXPONENT to the dict"""
        return {**self.asdict, "one_exponent": self.ONE_EXPONENT}
    
    @property
    def ashex(self):
        """returns the rawint as hex"""
        return hex(self.asint)
    
    @property
    def asint(self):
        """returns the rawint"""
        return self.significant << self.exponent
    
    @property
    def asint1(self):
        """returns the tuple(rawint, 2**one_exponent)"""
        return (self.significant << self.exponent, self.one)
    
    @classmethod
    def _one(cls):
        """returns the global (class level) scaling factor 2**cls.ONE_EXPONENT """
        return 1 << cls.ONE_EXPONENT
    
    @property
    def one(self):
        """wraps classmethod cls._one() as property"""
        return self._one()
    
    @property
    def asfloat(self):
        """returns the float number TAKING INTO ACCOUNT the global exponent `self.one`"""
        return float(self.asint / self.one)
    
    def __int__(self):
        return self.asint
    
    def __float__(self):
        return self.asfloat

class CarbonFloatInt32(CarbonFloatInt64):
    ONE_EXPONENT = 32
    
class CarbonFloatInt40(CarbonFloatInt64):
    ONE_EXPONENT = 40

class CarbonFloatInt48(CarbonFloatInt64):
    ONE_EXPONENT = 48

class CarbonFloatInt60(CarbonFloatInt64):
    ONE_EXPONENT = 60

class CarbonFloatInt64(CarbonFloatInt64):
    ONE_EXPONENT = 64

class CarbonFloatInt128(CarbonFloatInt64):
    ONE_EXPONENT = 128