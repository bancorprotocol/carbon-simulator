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
from carbon.helpers.floatint import *
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolTestBase))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonFloatInt32))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(P))
from math import log2, floor, ceil, sqrt
print_version(require="2.3.2")


#
#
#
#
#
#
#
#
#
#

FI32 = CarbonFloatInt32
FI40 = CarbonFloatInt40


# ------------------------------------------------------------
# Test      058
# File      test_058_CurveTest.py
# Segment   Demo and test of yzABS in CarbonOrderUI and pair decimals
# ------------------------------------------------------------
def test_demo_and_test_of_yzabs_in_carbonorderui_and_pair_decimals():
# ------------------------------------------------------------
    
    ETHUSDC = P("ETH/USDC").sd(18,6)
    assert ETHUSDC.decimals == {'ETH': 18, 'USDC': 6, '_TKNB': 18, '_TKNQ': 6, '_DIFFQB': -12}
    assert ETHUSDC.decdiffqb == -12
    assert P(ETHUSDC).has_decimals
    assert ETHUSDC.price_convention == 'USDC per ETH'
    ETHUSDC
    
    oui = CarbonOrderUI.from_prices(ETHUSDC, "ETH", 1500, 2000, 1, 0.5)
    r = oui.yzABS(sx=10, verbose=True)
    ddf, ddf2 = 10**12, 10**6
    assert r.y == 0.5 * 10**18
    assert r.z == 10**18
    assert r.A == int(oui.S * ddf2 * r.S)
    assert r.B == int(oui.B * ddf2 * r.S)
    assert r.S == 2**10
    assert oui.descr() == 'Sell ETH buy USDC from 1500.0000 to 2000.0000 USDC per ETH'
    
    oui = CarbonOrderUI.from_prices(ETHUSDC, "USDC", 1000, 500, 1100, 790)
    r = oui.yzABS(sx=40, verbose=True)
    ddf, ddf2 = 10**-12, 10**-6
    assert r.y == 790 * 10**6
    assert r.z == 1100 * 10**6
    assert r.A == int(oui.S * ddf2 * r.S)
    assert r.B == int(oui.B * ddf2 * r.S)
    assert r.S == 2**40
    

# ------------------------------------------------------------
# Test      058
# File      test_058_CurveTest.py
# Segment   Demo [NOTEST]
# ------------------------------------------------------------
def notest_demo():
# ------------------------------------------------------------
    
    # ### Trade functions
    
    mulDivF = lambda x, y, z: (x * y) // z
    mulDiv = mulDivF
    mulDivC = lambda x, y, z: (x * y + z - 1) // z
    
    
    # **this is actually by target**
    
    def trade_by_target_act(params, C):
    
        dx = params[0]
        y,z,A,B,s = params[1]
        print(params)
        ONE = s
        temp1 = C(y * A + z * B, "temp1")               # 177 bits at most; cannot overflow
        temp2 = C(temp1 * dx / ONE, "temp2")            # 224 bits at most; can overflow; some precision loss
        temp3 = C(temp2 * A + z * z * ONE, "temp3")     # 256 bits at most; can overflow
        dy = mulDiv(temp1, temp2, temp3)
        print(dx, temp1, temp2, temp3, dy)
        return dy
    
    
    # +

    
    # temp1 = z * ONE
    # temp2 = y * A + z * B
    # temp3 = temp2 * dy
    # scale = mulDivC(temp3, A, 2**256-1)
    # temp4 = mulDivC(temp1, temp1, scale)
    # temp5 = mulDivC(temp3, A, scale)
    # dx    = mulDivF(temp2, temp3 // scale, temp4 + temp5)
    # -
    
    # **those are actually by source**
    #
    # this one is SKL version of the fixed code
    
    def trade_by_source_act(params, C):
    
        dy = params[0]
        y,z,A,B,s = params[1]
        print(params)
        ONE = s
        temp1 = C(z * ONE, "temp1")                  
        temp2 = C(y * A + z * B, "temp2")         
        temp3 = C(temp2 - dy * A, "temp3")        
        scale = mulDiv(temp2, temp3, 2**255)+1
        temp1s = C(temp1//scale, "temp1s")
        temp2s = C(temp2//scale, "temp2s")
        dx = mulDiv(
            C(dy*temp1s, "dx*temp1s"), 
            temp1, 
            C(temp2s*temp3, "temp2s*temp3")
        )
        print(dy, dx*temp1s, temp1, temp2s*temp3, dx)
        return dx
    
    
    # this is BM version of the fixed code
    
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
    # -
    
    # that's the previous, failing, version of the code
    
    def trade_by_source_old_act(params, C):
    
        dy = params[0]
        y,z,A,B,s = params[1]
        ONE = s
        temp1 = C(z * ONE, "temp1")                  
        temp2 = C(y * A + z * B, "temp2")         
        temp3 = C(temp2 - dy * A, "temp3")        
        dx = mulDiv(
            C(dy*temp1, "dy*temp1"), 
            temp1, 
            C(temp2*temp3, "temp2*temp3")
        ) 
        print(dy, dy*temp1, temp1, temp2*temp3, dx)
        return dx
    
    
    # ### Analysis
    
    class STB(SolTestBase):
        #PRINT_LVL_DEFAULT = SolTestBase.LVL_LOG
        PRINT_LVL_DEFAULT = SolTestBase.LVL_WARN
    VERBOSE = False
    
    # #### TKN/DAI -- same decimality, same reasonable price
    
    TKNDAI = P("TKN/DAI").sd(18,18)
    price = 5  # DAI per TKN
    oui = CarbonOrderUI.from_prices(TKNDAI, "TKN", price, price, 1000, 1000)
    c = curve = oui.yzABS(sx=40, verbose=VERBOSE)
    
    params_bysrc  = (1e18, curve) # dy = wei sent (by source, 1 TKN)
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)))
    dx/1e18 # 1 TKN -> 5 DAI ==> 5 DAI per TKN
    
    params_bytarg = (5e18, curve)       # dx = token wei received (target, DAI)
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy/1e18 # 1 TKN ->  5 DAI --> 5 DAI per TKN
    
    # #### ETH/USDC -- y=ETH, x=USDC
    
    ETHUSDC = P("ETH/USDC").sd(18,6)
    oui = CarbonOrderUI.from_prices(ETHUSDC, "ETH", 2000, 2000, 1, 0.5)
    curve = oui.yzABS(sx=40, verbose=VERBOSE)
    
    params_bysrc  = (1*1e18, curve) # dy = token wei sent (by source, 1 ETH)
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)))
    dx/1e6 # 1 ETH -> 2000 USDC
    
    params_bytarg = (2000*1e6, curve)       # dx = token wei received (target, USDC)
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy/1e18 # 1 ETH -> 2000 USDC
    
    # #### ETH/USDC -- y=USDC, x=ETH
    
    oui = CarbonOrderUI.from_prices(ETHUSDC, "USDC", 1000, 1000, 750, 750)
    curve = oui.yzABS(sx=40, verbose=VERBOSE)
    print(curve)
    
    params_bysrc  = (1000*1e6, curve)       # dy = USDC-wei
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)) )
    dx/1e18 # 1000 USDC -> 1 ETH
    
    params_bytarg = (1e18, curve)  # dx = ETH-wei
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy/1e6 # 1000 USDC -> 1 ETH
    
    # #### SHIB/USDC -- y=SHIB, x=USDC
    
    SHIBUSDC = P("SHIB/USDC").sd(18,6)
    price = 1e-5
    oui = CarbonOrderUI.from_prices(SHIBUSDC, "SHIB", price, price, 2e5, 2e5)
    curve = oui.yzABS(sx=40, verbose=VERBOSE)
    print(curve)
    
    params_bysrc  = (1*1e5*1e18, curve)      # dy = SHIB-wei (1 USD worth of SHIB)
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)) )
    dx / 1e6 # 1e5 SHIB -> 1 USDC
    
    params_bytarg = (1*1e6, curve) # dx = USDC-wei
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy/1e18 # 1e5 SHIB -> 1 USDC
    
    # #### Nick's example DAI/USDC -- Selling DAI
    
    DAIUSDC = P("DAI/USDC").sd(18,6)
    price = 1
    oui = CarbonOrderUI.from_prices(DAIUSDC, "DAI", price, price, 1e5, 1e5)
    curve = oui.yzABS(sx=40, verbose=VERBOSE)
    print(curve)
    
    params_bysrc  = (1*1e18, curve)        # dy = DAI-wei
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)) )
    dx/1e6 # 1 DAI -> 1 USDC
    
    
    params_bytarg = (1*1e6, curve)  # dx = USDC-wei
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy / 1e18 # 1 DAI -> 1 USDC
    
    
    # #### Nick's example DAI/USDC -- Selling USDC
    
    SHIBUSDC = P("DAI/USDC").sd(18,6)
    price = 1
    oui = CarbonOrderUI.from_prices(SHIBUSDC, "USDC", price, price, 1e5, 1e5)
    curve = oui.yzABS(sx=40, verbose=VERBOSE)
    
    params_bysrc  = (1*1e6, curve)       # dy = USDC-wei
    dx = trade_by_source_act( params_bysrc, STB(context=("by_source", curve)) )
    dx/1e18
    
    params_bytarg = (1e18, curve)      # dx = DAI-wei
    dy = trade_by_target_act( params_bytarg, STB(context=("by_target", curve)) )
    dy/1e6
    

# ------------------------------------------------------------
# Test      058
# File      test_058_CurveTest.py
# Segment   SolTestBase tests
# ------------------------------------------------------------
def test_soltestbase_tests():
# ------------------------------------------------------------
    
    TB0 = SolTestBase()
    TBrw = SolTestBase(raise_lvl=TB0.LVL_WARN)
    TBre = SolTestBase(raise_lvl=TB0.LVL_ERR)
    
    try:
        TBrw.check_uint256(1, "testlabel")
        raise RuntimeError("should raise")
    except TB0.UnderflowError as e:
        print(e)
    try:
        TBrw.check_uint256(2000, "testlabel")
        raise RuntimeError("should raise")
    except TB0.UnderflowWarning as e:
        print(e)
    try:
        TBrw.check_uint256(2**254, "testlabel")
        raise RuntimeError("should raise")
    except TB0.OverflowWarning as e:
        print(e)
    try:
        TBrw.check_uint256(2**256-1, "testlabel")
        raise RuntimeError("should raise")
    except TB0.OverflowWarning as e:
        print(e)
    try:
        TBrw.check_uint256(2**256, "testlabel")
        raise RuntimeError("should raise")
    except TB0.OverflowError as e:
        print(e)
    
    
    try:
        TBre.check_uint256(1, label="testlabel")
        raise RuntimeError("should raise")
    except TBre.UnderflowError as e:
        print(e)
    assert TBre.check_uint256(2000, label="testlabel") == 2000
    assert TBre.check_uint256(2**254, label="testlabel") == 2**254
    assert TBre.check_uint256(2**256-1, label="testlabel") == 2**256-1
    try:
        TBre.check_uint256(2**256, label="testlabel")
        raise RuntimeError("should raise")
    except TBre.OverflowError as e:
        print(e)
    
    
    assert TB0.check_uint256(1, log_f=TB0.print_f) == 1
    assert TB0.check_uint256(2000, log_f=TB0.print_f) == 2000
    assert TB0.check_uint256(2**254, log_f=TB0.print_f) == 2**254
    assert TB0.check_uint256(2**256-1, log_f=TB0.print_f) == 2**256-1
    assert TB0.check_uint256(2**256, log_f=TB0.print_f) == 2**256
    
    assert TB0._logmsg(level=TB0.LVL_WARN, isoverflow=True, label="1", msg="") == '[WARNING:OVERFLOW:1] '
    assert TB0._logmsg(TB0.LVL_ERR, False, "mylabel", "mymessage") == '[ERROR:UNDERFLOW:MYLABEL] mymessage'
    TB0.print_f(False, False, "mylabel", "mymessage")
    
    assert TB0.bindig(0) == 0
    assert TB0.bindig(1) == 1
    assert TB0.bindig(2) == 2
    assert TB0.bindig(3) == 2
    assert TB0.bindig(2**10) == 11
    assert TB0.bindig(2**10+1) == 11
    assert TB0.bindig(2**10-1) == 10
    
    