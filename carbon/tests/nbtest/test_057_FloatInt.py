# ------------------------------------------------------------
# Auto generated test file `test_057_FloatInt.py`
# ------------------------------------------------------------
# source file   = NBTest_057_FloatInt.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 057
# test comment  = FloatInt
# ------------------------------------------------------------



from carbon.helpers.stdimports import *
from carbon.helpers.floatint import *
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonFloatInt32))
from math import sqrt, log2, ceil, floor
print_version(require="2.3.2")




# ------------------------------------------------------------
# Test      057
# File      test_057_FloatInt.py
# Segment   floatint params
# ------------------------------------------------------------
def test_floatint_params():
# ------------------------------------------------------------
    
    CFI_t = (CarbonFloatInt32, CarbonFloatInt40, CarbonFloatInt48, 
            CarbonFloatInt60, CarbonFloatInt64, CarbonFloatInt128)
    
    assert CarbonFloatInt32.ONE_EXPONENT  == 32
    assert CarbonFloatInt40.ONE_EXPONENT  == 40
    assert CarbonFloatInt48.ONE_EXPONENT  == 48
    assert CarbonFloatInt60.ONE_EXPONENT  == 60
    assert CarbonFloatInt64.ONE_EXPONENT  == 64
    assert CarbonFloatInt128.ONE_EXPONENT == 128
    
    for CFI in CFI_t:
        assert CFI.BITS_SIGNIFICANT == 40
        assert CFI.from_int(2**40-1).exponent == 0
        assert CFI.from_int(2**40).exponent == 1
    

# ------------------------------------------------------------
# Test      057
# File      test_057_FloatInt.py
# Segment   floatint
# ------------------------------------------------------------
def test_floatint():
# ------------------------------------------------------------
    
    I32 = CarbonFloatInt32
    I40 = CarbonFloatInt40
    I64 = CarbonFloatInt64
    
    r = I64.from_float(sqrt(2))
    assert r.significant == 777472127993
    assert r.exponent == 25
    assert r.one == 18446744073709551616
    assert r.asint == 26087635650636414976
    assert r.asint1 == (r.asint, r.one)
    assert r.astuple == (777472127993, 25)
    assert r.astuple1 == (777472127993, 25, 64)
    assert r.astuple1 == (r.significant, r.exponent, r.ONE_EXPONENT)
    assert r.asdict == {'significant': 777472127993, 'exponent': 25}
    assert r.asdict1 == {'significant': 777472127993, 'exponent': 25, 'one_exponent': 64}
    assert r.asdict1 == {'significant': r.significant, 'exponent': r.exponent, 'one_exponent': r.ONE_EXPONENT}
    assert r.asfloat == float(r)
    assert r.asint == int(r)
    
    r  = I64.from_int(2**234-1)
    r2 = I32.from_int(2**234-1)
    assert r.asint == 27606985387137146742797476726052758652111605223017136798872240757145600
    assert r.asint == r2.asint
    assert r.ashex == "0x3fffffffffc000000000000000000000000000000000000000000000000"
    assert r.ashex == r2.ashex
    
    assert r.max().asint == 63657374260394794151270269665081282040354043348133872840046568760304686825600315503411200
    assert r.max().ashex == '0x7fffffffff8000000000000000000000000000000000000000000000000000000000000000'
    assert abs(r.max().asfloat/3.45087e+69-1)<1e-6
    assert r.max().significant == 2**40-1
    assert r.max().exponent == 2**8-1
    
    assert r.min().asint == 1
    assert r.min().ashex == '0x1'
    assert abs(r.min().asfloat/5.421010e-20-1) < 1e-6
    assert r.min().significant == 1
    assert r.min().exponent == 0
    
    assert abs(I32.from_float(sqrt(2)).asfloat/sqrt(2)-1) < 1e-9
    assert abs(I40.from_float(sqrt(2)).asfloat/sqrt(2)-1) < 1e-11
    assert abs(I64.from_float(sqrt(2)).asfloat/sqrt(2)-1) < 1e-11
    
    
    class I96(I64):
        ONE_EXPONENT = 96
    r = I96.from_float(sqrt(2))
    assert r.asint == 112045541949447083908604624896
    assert r.astuple1 == (777472127993, 57, 96)
    
    
    
    