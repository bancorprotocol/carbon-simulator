from math import *
from dataclasses import dataclass, asdict


### FRONT END ###
def encode_user_inputs(pa, pb, y, z, decx, decy, xS):
    """returns (y,z,A,B,s) from prices, curve loading and capacity, decimals and scaling exponent"""
    decf = 10**(decy-decx)
    one = 2**xS
    a = sqrt(pa*decf)-sqrt(pb*decf) # p_ = dy/dx
    b = sqrt(pb*decf)               # pw_ = dyw/dxw = dy*decy / dx*decx
    return int(y*10**decy), int(z*10**decy), int(a*one), int(b*one), one, xS


### Variables we are familar with ###
y,z,A,B,S,xS = encode_user_inputs(0.00001555, 0.00001453, 100000, 100000, 18, 18, 32)
print('\nStandard variables')
print(y,z,A,B,S)
print("\n")


### Encode for contract storage ###

@dataclass
class CarbonFloatInt():
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
    
    BITS_SIGNIFICANT =  40
    BITS_EXPONENT    =   8
    ONE_EXPONENT     =  xS  # the exponent of "number 1", ie the global scale parameter
        
    def __post_init__(self):
        assert isinstance(self.significant, int), f"significant must be an int [{self.significant}]"
        assert isinstance(self.exponent, int), f"exponent must be an int [{self.exponent}]"
        assert self.exponent >= 0, f"exponent must be >= 0 [{self.exponent}]"
        
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
        
        lenval = ceil(log2(rawint+1))
        exponent = lenval - cls.BITS_SIGNIFICANT
        assert exponent <= 2**cls.BITS_EXPONENT, f"exponent must be <= {2**cls.BITS_EXPONENT}, is {exponent} [{rawint}]"
        if exponent <= 0:
            return cls(rawint, 0)
        return cls(rawint >> exponent, exponent)

storage = {}
storage['y'] = int(y)
storage['z'] = int(z)
storage['A'] = int(CarbonFloatInt.from_int(A).significant)
storage['B'] = int(CarbonFloatInt.from_int(B).significant)
storage['xA'] = int(CarbonFloatInt.from_int(A).exponent)
storage['xB'] = int(CarbonFloatInt.from_int(B).exponent)
storage['xS'] = int(xS)

print("A contract encoded", CarbonFloatInt.from_int(A))
print("B contract encoded", CarbonFloatInt.from_int(B))
print("\n")

### Read Storage from Contract ###

def readStorage(read):
    y   = read["y"]     # curve liqudity
    z   = read["z"]     # curve capacity 
    A   = read["A"]     # A coefficient, base number
    B   = read["B"]     # B coefficient, base number 
    
    xA  = read["xA"]    # ditto, exponent
    xB  = read["xB"]    # ditto, exponent
    xS  = read["xS"]    # scaling exponent
    
    S  = 2**xS
    A *= 2**xA
    B *= 2**xB
    
    return y,z,A,B,S

y,z,A,B,S = readStorage(storage)
print('\nStandard variables read from contract')
print(y,z,A,B,S)
print("\n")

