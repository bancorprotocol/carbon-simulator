# ------------------------------------------------------------
# Auto generated test file `test_058_CurveTest.py`
# ------------------------------------------------------------
# source file   = NBTest_058_CurveTest.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 058
# test comment  = CurveTest
# ------------------------------------------------------------



from carbon.helpers.stdimports import *
from carbon.helpers.soltest import SolTestBase
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolTestBase))
from math import log2
print_version(require="2.3.2")




# ------------------------------------------------------------
# Test      058
# File      test_058_CurveTest.py
# Segment   Demo [NOTEST]
# ------------------------------------------------------------
def notest_demo():
# ------------------------------------------------------------
    
    from collections import namedtuple
    p_nt = namedtuple("p", "y,z,A,B,S")
    def yzABS(pb, w, y, z, decx, decy, sx):
        """returns (y,z,A,B,s) from prices, curve loading and capacity, decimals and scaling exponent"""
        decf = 10**(decy-decx)
        one = 2**sx
        pa = w*pb
        a = sqrt(pa*decf)-sqrt(pb*decf) # p_ = dy/dx
        b = sqrt(pb*decf)               # pw_ = dyw/dxw = dy*decy / dx*decx
        return p_nt(int(y*10**decy), int(z*10**decy), int(a*one), int(b*one), one)
    mulDivF = lambda x, y, z: x * y // z
    mulDiv = mulDivF
    mulDivC = lambda x, y, z: (x * y + z - 1) // z
    
    
    def trade_by_source(params, check_f):
        """
        examined function in standard format
        
        :params:         parameter tuple; the function then expands it into variables
        :check_f:  the check function, checking for over and underflow; must wrap all
                   integer operations that could over or underflow
        """
    
        dy,y,z,A,B,s = params
        C = check_f
        ONE = s
        temp1 = C(y * A + z * B, "temp1")               # 177 bits at most; cannot overflow
        temp2 = C(temp1 * dy / ONE, "temp2")            # 224 bits at most; can overflow; some precision loss
        temp3 = C(temp2 * A + z * z * ONE, "temp3")     # 256 bits at most; can overflow
        dx = mulDiv(temp1, temp2, temp3)
        return dx
    
    
    def trade_by_target(params, check_f):
    
        dx,y,z,A,B,s = params
        C = check_f
        ONE = s
        temp1 = C(z * ONE, "temp1")                                 # 144 bits at most; cannot overflow
        temp2 = C(y * A + z * B, "temp2")                           # 177 bits at most; cannot overflow
        temp3 = C(temp2 - dx * A, "temp3")                          # 177 bits at most
        dy = mulDiv(
            C(dx*temp1, "dx*temp1"), 
            temp1, 
            C(temp2*temp3, "temp2*temp3")
        )   # each multiplication can overflow
        return dy
    
    
    TB = SolTestBase()
    
    # y = SHIB, x = USDC
    curve = yzABS(
        y    = 1000*1e5,                  # number of tokens on curve (SHIB for $1000)
        z    = 1000*1e5,                  # curve capacity (ditto)
        pb   = 1e5,                       # curve END price dy/dx (SHIB per USDC)
        w    = 1.1,                       # width of the range (1=point)
        decx = 6,                         # decimals x (USDC)
        decy = 18,                        # decimals y (SHIB)
        sx   = 40,                        # scaling exponent
    )
    params_bytarg = (1*1e6,) + curve      # dx = token wei received (target, USDC)
    params_bysrc  = (1*1e5*1e18,) + curve # dy = token wei sent (source, SHIB, worth 1 USDC)
    print(curve)
    print("--- by target:")
    check_f = lambda n,l: TB.check_uint256(n,l, context=("by_target", params_bytarg[0], curve), log_f=TB.print_err_f)
    trade_by_target(params_bytarg, check_f)
    print("--- by source:")
    check_f = lambda n,l: TB.check_uint256(n,l, context=("by_source", params_bysrc[0], curve), log_f=TB.print_err_f)
    trade_by_source(params_bysrc, check_f)
    
    
    
    # +
    # def trade_by_target(dx,readStorage):
    
    #     y,z,A,B,s = readStorage()
    #     ONE = s
    #     temp1 = z * ONE                                 # 144 bits at most; cannot overflow
    #     temp2 = y * A + z * B                           # 177 bits at most; cannot overflow
    #     temp3 = temp2 - dx * A                          # 177 bits at most
    #     scale = ???
    #     dy = mulDiv(dx * (temp1//scale), temp1, (temp2//scale) * temp3)   # each multiplication can overflow
    #     return dy
    
    # +

    # mulDivF = lambda x, y, z: x * y // z
    # mulDivC = lambda x, y, z: (x * y + z - 1) // z
    
    # temp1 = z * ONE
    # temp2 = y * A + z * B
    # temp3 = temp2 - dx * A
    # scale = mulDivC(temp2, temp3, 2**256-1)
    # temp4 = mulDivC(temp1, temp1, scale)
    # temp5 = mulDivF(temp2, temp3, scale)
    # dy    = mulDivC(dx, temp4, temp5)
    
    # +

    # mulDivF = lambda x, y, z: x * y // z
    # mulDivC = lambda x, y, z: (x * y + z - 1) // z
    
    # temp1 = z * ONE
    # temp2 = y * A + z * B
    # temp3 = temp2 * dy
    # scale = mulDivC(temp3, A, 2**256-1)
    # temp4 = mulDivC(temp1, temp1, scale)
    # temp5 = mulDivC(temp3, A, scale)
    # dx    = mulDivF(temp2, temp3 // scale, temp4 + temp5)
    # -
    

# ------------------------------------------------------------
# Test      058
# File      test_058_CurveTest.py
# Segment   SolTestBase
# ------------------------------------------------------------
def test_soltestbase():
# ------------------------------------------------------------
    
    TB = SolTestBase()
    
    try:
        TB.check_uint256(1, log_f=TB.raise_warn_f)
        raise RuntimeError("should raise")
    except TB.UnderflowError as e:
        print(e)
    try:
        TB.check_uint256(2000, log_f=TB.raise_warn_f)
        raise RuntimeError("should raise")
    except TB.UnderflowWarning as e:
        print(e)
    try:
        TB.check_uint256(2**254, log_f=TB.raise_warn_f)
        raise RuntimeError("should raise")
    except TB.OverflowWarning as e:
        print(e)
    try:
        TB.check_uint256(2**256-1, log_f=TB.raise_warn_f)
        raise RuntimeError("should raise")
    except TB.OverflowWarning as e:
        print(e)
    try:
        TB.check_uint256(2**256, log_f=TB.raise_warn_f)
        raise RuntimeError("should raise")
    except TB.OverflowError as e:
        print(e)
    
    
    try:
        TB.check_uint256(1, log_f=TB.raise_err_f)
        raise RuntimeError("should raise")
    except TB.UnderflowError as e:
        print(e)
    assert TB.check_uint256(2000, log_f=TB.raise_err_f) == 2000
    assert TB.check_uint256(2**254, log_f=TB.raise_err_f) == 2**254
    assert TB.check_uint256(2**256-1, log_f=TB.raise_err_f) == 2**256-1
    try:
        TB.check_uint256(2**256, log_f=TB.raise_err_f)
        raise RuntimeError("should raise")
    except TB.OverflowError as e:
        print(e)
    
    
    assert TB.check_uint256(1, log_f=TB.print_f) == 1
    assert TB.check_uint256(2000, log_f=TB.print_f) == 2000
    assert TB.check_uint256(2**254, log_f=TB.print_f) == 2**254
    assert TB.check_uint256(2**256-1, log_f=TB.print_f) == 2**256-1
    assert TB.check_uint256(2**256, log_f=TB.print_f) == 2**256
    
    assert TB.check_uint256(1, log_f=TB.null_f) == 1
    assert TB.check_uint256(2000, log_f=TB.null_f) == 2000
    assert TB.check_uint256(2**254, log_f=TB.null_f) == 2**254
    assert TB.check_uint256(2**256-1, log_f=TB.null_f) == 2**256-1
    assert TB.check_uint256(2**256, log_f=TB.null_f) == 2**256
    
    
    assert TB._logmsg(level=TB.LVL_WARN, isoverflow=True, label="1", msg="") == '[WARNING:OVERFLOW:1] '
    assert TB._logmsg(TB.LVL_ERR, False, "mylabel", "mymessage") == '[ERROR:UNDERFLOW:MYLABEL] mymessage'
    TB.print_f(False, False, "mylabel", "mymessage")
    
    try:
        TB.raise_warn_f(TB.LVL_ERR, False, "mylabel", "mymessage")
        raise RuntimeError("should raise")
    except TB.UnderflowError as e:
        print(e)
    try:
        TB.raise_warn_f(TB.LVL_WARN, False, "mylabel", "mymessage")
        raise RuntimeError("should raise")
    except TB.UnderflowWarning as e:
        print(e)
    try:
        TB.raise_warn_f(TB.LVL_ERR, True, "mylabel", "mymessage")
        raise RuntimeError("should raise")
    except TB.OverflowError as e:
        print(e)
    try:
        TB.raise_warn_f(TB.LVL_WARN, True, "mylabel", "mymessage")
        raise RuntimeError("should raise")
    except TB.OverflowWarning as e:
        print(e)
    
    assert TB.bindig(0) == 0
    assert TB.bindig(1) == 1
    assert TB.bindig(2) == 2
    assert TB.bindig(3) == 2
    assert TB.bindig(2**10) == 11
    assert TB.bindig(2**10+1) == 11
    assert TB.bindig(2**10-1) == 10
    
    