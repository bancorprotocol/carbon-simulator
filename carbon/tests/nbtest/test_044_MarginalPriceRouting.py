# ------------------------------------------------------------
# Auto generated test file `test_044_MarginalPriceRouting.py`
# ------------------------------------------------------------
# source file   = NBTest_044_MarginalPriceRouting.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 044
# test comment  = MarginalPriceRouting
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))






# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonPair related tests
# ------------------------------------------------------------
def test_carbonpair_related_tests():
# ------------------------------------------------------------
    
    pair = P("ETH/USDC")
    assert isinstance(pair, P)
    print(str(pair))
    assert str(pair) == "P('ETH/USDC')"
    pair2 = P.from_slashpair("  ETH / USDC")
    print(pair2)
    assert isinstance(pair2, P)
    assert pair2.slashpair == "ETH/USDC"
    pair3 = P(pair2)
    assert isinstance(pair3, P)
    assert pair3==pair2
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonOrderUI general tests
# ------------------------------------------------------------
def test_carbonorderui_general_tests():
# ------------------------------------------------------------
    
    order = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 10)
    assert isinstance(order, CarbonOrderUI)
    #print(round(order.B,10))
    assert round(order.B,10) == 0.0182574186
    #print(round(order.S,10))
    assert round(order.S,10) == 0.0041032612
    assert order.yint == 10
    assert order.y == 10
    assert order.pa == 2000
    assert order.pb == 3000
    assert order.p_marg == 2000
    assert order.pa == order.py
    assert order.pb == order.px
    assert order.total_liquidity == (10, 'ETH')
    assert round(order.p0, 10) == round(sqrt(2000*3000),10)
    assert round(order.widthpc, 10) == round((3000-2000)/sqrt(2000*3000),10)
    assert round(order.widthr, 10) == round(3000/2000,10)
    order
    
    try:
        CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 5, 10)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    
    try:
        CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, -10, -10)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    
    try:
        CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, -10)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    
    order = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 3000, 2000, 10, 10)
    assert order.pa == 2000
    assert order.pb == 3000
    order
    
    orderr = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1000, 750, 10000, 10000)
    assert orderr.pa == 1000
    assert round(orderr.pb,6) == 750
    orderr
    
    assert order.p_marg_f(0) == order.p_marg
    assert round(order.p_marg_f(5), 6) == 2424.492346
    assert order.p_marg_f(10) == 3000
    
    assert orderr.p_marg_f(0) == orderr.p_marg
    assert round(orderr.p_marg_f(10000),8) == 750
    
    assert order.p_marg_f(-1, raiseonerror=False) is None
    assert order.p_marg_f(10.0001, raiseonerror=False) is None
    assert order.p_marg_f(-1) is None
    assert order.p_marg_f(10.0001) is None
    
    assert orderr.p_marg_f(10001, raiseonerror=False) is None
    assert orderr.p_marg_f(10001) is None
    
    try:
        order.p_marg_f(-1, raiseonerror=True)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
        assert str(e) == "('Trade size dy must be a non-negative number', -1)"
    
    try:
        order.p_marg_f(10.001, raiseonerror=True)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    
    try:
        order.p_marg_f(10001, raiseonerror=True)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonOrderUI tests yfromp
# ------------------------------------------------------------
def test_carbonorderui_tests_yfromp():
# ------------------------------------------------------------
    
    order = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 10)
    order1 = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 5)
    orderr = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1000, 750, 10000, 10000)
    
    assert order.yfromp_f(2000) == 10
    assert order.yfromp_f(3000) == 0
    assert order.dyfromp_f(2000) == 0
    assert order.dyfromp_f(3000) == 10
    
    try:
        order1.yfromp_f(2000, raiseonerror=True)
        raise RuntimeError("Should have raised exception")
    except ValueError as e:
        print(e)
    
    assert orderr.yfromp_f(1000) == 10000
    assert orderr.yfromp_f(750.00000001) < 1e-6
    assert orderr.dyfromp_f(1000) == 0
    assert round(orderr.dyfromp_f(750.0000001),5)==10000
    
    for dy in np.linspace(0,10):
        yy = order.yfromp_f(order.p_marg_f(dy))
        assert round(yy - (10-dy),10) == 0
        #print (f"dy={dy}, y={yy}, 10-dy={10-dy}")
    
    for dy in np.linspace(0,10):
        dy1 = order.dyfromp_f(order.p_marg_f(dy))
        assert round(dy - dy1,10) == 0
        #print (f"dy={dy}, dy1={dy1}")
    
    for dy in np.linspace(0,10000):
        dy1 = orderr.dyfromp_f(orderr.p_marg_f(dy))
        assert round(dy - dy1,4) == 0
        #print (f"dy={dy}, dy1={dy1}")
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonOrderUI tests dyfromdx_f and dxfromdy_f
# ------------------------------------------------------------
def test_carbonorderui_tests_dyfromdx_f_and_dxfromdy_f():
# ------------------------------------------------------------
    
    help(CarbonOrderUI.dyfromdx_f)
    
    # +
    # in order, order1 dx is a USDC number and dy is an ETH number
    order = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 10)
    order1 = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 5)
    
    # in orderr dx is an ETH number and dy is a USDC number
    orderr = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1000, 750, 10000, 10000)
    dxeps = dyeps = 0.000001
    p0 = sqrt(2000*3000)
    p0r = sqrt(1000*750)
    dxmax = 10*p0-dxeps
    dxmaxr = 10000/p0r-dxeps
    p0, p0r, dxmax, dxmaxr
    # -
    
    # ### dyfromdx_f
    
    dy = order.dyfromdx_f(dxeps)
    assert round(dxeps/dy,6) == 2000
    dy/dxeps, dxeps/dy
    
    dy = order.dyfromdx_f(dxmax)
    assert round(dxmax/dy - p0,6) == 0
    dy/dxmax, dxmax/dy, p0
    
    dy = order1.dyfromdx_f(dxeps)
    assert dxeps/dy > 2000
    assert dxeps/dy < 3000
    dy/dxeps, dxeps/dy
    
    dy = orderr.dyfromdx_f(dxeps)
    assert round(dy/dxeps,4) == 1000
    dy/dxeps, dxeps/dy
    
    dy = orderr.dyfromdx_f(dxmaxr)
    assert round(dy/dxmaxr - p0r,4) == 0
    dy/dxmaxr, dxmaxr/dy, p0r
    
    # ### dxfromdy_f
    
    dx = order.dxfromdy_f(dyeps)
    assert round(dx/dyeps,4) == 2000
    dx/dyeps, dyeps/dx
    
    dx = order.dxfromdy_f(10)
    assert round(dx/10 - p0,6) == 0
    dx/10, 10/dx, p0
    
    dx = order1.dxfromdy_f(dyeps)
    assert dx/dyeps > 2000
    assert dx/dyeps < 3000
    dx/dyeps, dyeps/dx
    
    dx = orderr.dxfromdy_f(dyeps)
    assert round(dyeps/dx,4) == 1000
    dx/dyeps, dyeps/dx
    
    dx = orderr.dxfromdy_f(10000)
    assert round(10000/dx - p0r,4) == 0
    dx/10000, 10000/dx, p0r
    
    # ### xfromy_f
    
    assert order.xfromy_f(order.yint) == 0
    assert round(order.xfromy_f(0)- order.p0*order.yint, 10) == 0
    assert order.x == 0
    assert order.xfromy_f(order.y) == order.x
    for i in range(10):
        #print (i)
        assert round(order.dxfromdy_f(i) - order.xfromy_f(order.y-i), 10) == 0
    
    assert orderr.xfromy_f(orderr.yint) == 0
    assert round(orderr.xfromy_f(0)- orderr.yint/orderr.p0, 10) == 0
    assert orderr.xfromy_f(orderr.y) == orderr.x
    for i in range(10):
        #print (i)
        assert round(orderr.dxfromdy_f(i*1000) - orderr.xfromy_f(orderr.y-i*1000), 10) == 0
    
    assert order1.xfromy_f(order1.yint) == 0
    assert round(order1.xfromy_f(0)- order.p0*order.yint, 10) == 0
    assert order1.xfromy_f(order1.y) == order1.x
    for i in range(5):
        #print (i)
        assert round(order1.xfromy_f(order1.y) + order1.dxfromdy_f(i) - order1.xfromy_f(order1.y-i), 10) == 0
    
    # ### yfromx_f
    
    assert order.yfromx_f(0) == order.yint
    assert round(order.yfromx_f(order.xint),5) == 0
    for i in range(10):
        #print(i)
        assert round(order.yfromx_f(order.xfromy_f(i)) - i, 10)  == 0
    
    order.yfromx_f(order.xint)
    
    
    
    assert orderr.yfromx_f(0) == orderr.yint
    assert round(orderr.yfromx_f(orderr.xint-0.00000001),4)==0
    for i in range(1,10):
        #print(i)
        assert round(orderr.yfromx_f(orderr.xfromy_f(i*1000)) - i*1000, 10)  == 0
    
    # ### p_eff_f
    
    assert order.p_eff_f(0) == 2000
    assert round(order.p_eff_f(0.000000001)-2000,3) == 0
    assert round(order.p_eff_f(10) - order.p0, 6) == 0
    
    p1 = order1.p_eff_f(0)
    assert p1 == order1.p_marg_f(0)
    p2 = order1.p_marg_f(5)
    assert round(order1.p_eff_f(5) - sqrt(p1*p2),5) == 0
    p1,p2, sqrt(p1*p2)
    
    assert orderr.p_eff_f(0) == 1000
    assert round(orderr.p_eff_f(0.1)-1000,2) == 0
    assert round(orderr.p_eff_f(10000) - orderr.p0, 6) == 0
    
    # ### from_Qxy 
    
    assert order.Q == sqrt(order.pb_raw/order.pa_raw)
    assert order.Gamma == 1 - sqrt(order.Q)
    print(f"Q={order.Q}, Gamma={order.Gamma}")
    
    assert order1.Q == sqrt(order1.pb_raw/order1.pa_raw)
    assert order1.Gamma == 1 - sqrt(order1.Q)
    print(f"Q={order1.Q}, Gamma={order1.Gamma}")
    
    assert orderr.Q == sqrt(orderr.pb_raw/orderr.pa_raw)
    assert orderr.Gamma == 1 - sqrt(orderr.Q)
    print(f"Q={orderr.Q}, Gamma={orderr.Gamma}")
    
    order_ = CarbonOrderUI.from_Qxy(order.pair, order.tkn, order.Q, order.xint, order.yint, order.y)
    assert round(order_.B - order.B, 10) == 0
    assert round(order_.S - order.S, 10) == 0
    assert round(order_.xint - order.xint, 10) == 0
    assert round(order_.yint - order.yint, 10) == 0
    assert round(order_.y - order.y, 10) == 0
    order_
    
    orderr_ = CarbonOrderUI.from_Qxy(orderr.pair, orderr.tkn, orderr.Q, orderr.xint, orderr.yint, orderr.y)
    assert round(orderr_.B - orderr.B, 10) == 0
    assert round(orderr_.S - orderr.S, 10) == 0
    assert round(orderr_.xint - orderr.xint, 10) == 0
    assert round(orderr_.yint - orderr.yint, 10) == 0
    assert round(orderr_.y - orderr.y, 10) == 0
    orderr_
    
    # ### buyx
    
    order_ = CarbonOrderUI.from_order(order)
    r = order_.buyx(1000, raiseonerror=True)
    r
    
    assert round(r["x"],10) == 1000
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert round(r["dx/dy"] * r["dy/dx"],10) == 1
    assert r["tx"] == 'Sell 0.4954541237152398 ETH buy USDC'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)==0
    
    r  = order_.buyx(1000, raiseonerror=True)
    r
    
    assert round(r["x"],10) == 2000
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Sell 0.4865262015696128 ETH buy USDC'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)!=0
    
    order_ = CarbonOrderUI.from_order(orderr)
    r  = order_.buyx(1, raiseonerror=True)
    r
    
    assert round(r["x"],10) == 1
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Sell 986.7796593583731 USDC buy ETH'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)==0
    
    r  = order_.buyx(-0.5, raiseonerror=True)
    r
    
    assert round(r["x"],10) == 0.5
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Buy 490.10673706911854 USDC sell ETH'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)!=0
    
    # ### selly
    
    order_ = CarbonOrderUI.from_order(order)
    r  = order_.selly(1, raiseonerror=True)
    r
    
    assert r["y"] == 9
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Sell 1 ETH buy USDC'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)==0
    
    r  = order_.selly(1, raiseonerror=True)
    r
    
    assert r["y"] == 8
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Sell 1 ETH buy USDC'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)!=0
    
    order_ = CarbonOrderUI.from_order(order)
    r1 = order.selly(1, execute = False)
    r2 = order.selly(1, execute = False)
    assert r1 == r2
    
    order_ = CarbonOrderUI.from_order(orderr)
    r  = order_.selly(1000, raiseonerror=True)
    r
    
    assert r["y"] == 9000
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Sell 1000 USDC buy ETH'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)==0
    
    r  = order_.selly(-500, raiseonerror=True)
    r
    
    assert r["y"] == 9500
    assert round(r["p"] - sqrt(r["pmarg_old"]*r["pmarg"]),10) == 0
    assert r["dx/dy"] == 1 / r["dy/dx"]
    assert r["tx"] == 'Buy 500 USDC sell ETH'
    assert r["expanded"] == False
    assert r["y_old"] - r["dy"] == r["y"]
    assert round(r["x"] - r["dx"],10)!=0
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonOrderUI charts [NOTEST]
# ------------------------------------------------------------
def notest_carbonorderui_charts():
# ------------------------------------------------------------
    
    order1 = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 10)
    order2 = CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000, 3000, 10, 5)
    orderr = CarbonOrderUI.from_prices("ETH/USDC", "USDC", 1000, 750, 25000, 25000)
    
    ETHr = np.linspace(0,order1.yint)
    USDCr = np.linspace(0,orderr.yint)
    
    plt.plot([order1.xfromy_f(y) for y in ETHr], ETHr, label="order1 (y=10)")
    plt.plot([order2.xfromy_f(y) for y in ETHr], ETHr, label="order2 (y=5)")
    plt.ylabel("y [ETH]")
    plt.xlabel("x [USDC]")
    plt.legend()
    
    plt.plot([order1.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order1 (y=10)")
    plt.plot([order2.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order2 (y=5)")
    plt.ylabel("dy [ETH]")
    plt.xlabel("dx [USDC]")
    plt.legend()
    
    plt.plot([order1.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order1 (y=10)")
    plt.plot([order2.dxfromdy_f(y, raiseonerror=False) for y in ETHr], -ETHr, label="order2 (y=5)")
    plt.ylabel("dy [ETH]")
    plt.xlabel("dx [USDC]")
    plt.legend()
    
    plt.plot(
        [order1.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
        [order1.p_marg_f(dy, raiseonerror=False) for dy in ETHr], 
        label="marg (1; y=10 ETH)")
    plt.plot(
        [order2.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
        [order2.p_marg_f(dy, raiseonerror=False) for dy in ETHr], 
        label="marg (2; y=5 ETH)")
    plt.plot(
        USDCr, 
        [orderr.p_marg_f(dy, raiseonerror=False) for dy in USDCr], 
        label="marg(r; y=10k USDC)")
    plt.plot(
        [order1.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
        [order1.p_eff_f(dy, raiseonerror=False) for dy in ETHr], 
        label="eff (1; y=10 ETH)")
    plt.plot(
        [order2.dxfromdy_f(dy, raiseonerror=False) for dy in ETHr], 
        [order2.p_eff_f(dy, raiseonerror=False) for dy in ETHr], 
        label="eff (2; y=5 ETH)")
    plt.plot(
        USDCr, 
        [orderr.p_eff_f(dy, raiseonerror=False) for dy in USDCr], 
        label="eff (r; y=10k USDC)")
    plt.ylabel("Price [USDC per ETH]")
    plt.xlabel("dx [USDC]")
    plt.legend(loc="center right")
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   CarbonOrderUI tests goalseek
# ------------------------------------------------------------
def test_carbonorderui_tests_goalseek():
# ------------------------------------------------------------
    
    f = lambda x: sqrt(x)-3
    print (round(CarbonOrderUI.goalseek(f,1,10), 6))
    assert round(CarbonOrderUI.goalseek(f,1,10), 6) == 9
    
    try:
        CarbonOrderUI.goalseek(f,10,1)
        raise RuntimeError("Should raise exception")
    except ValueError as e:
        print(str(e))
    
    try:
        CarbonOrderUI.goalseek(f,10,20)
        raise RuntimeError("Should raise exception")
    except ValueError as e:
        print(str(e))
    

# ------------------------------------------------------------
# Test      044
# File      test_044_MarginalPriceRouting.py
# Segment   Example usage [NOTEST]
# ------------------------------------------------------------
def notest_example_usage():
# ------------------------------------------------------------
    #
    # This section shows how to use yfromp-related functions for routing. This section does not create test code.
    
    # First we create a staggered list of 10 orders. Note that all those orders are only half-filled. The corresponding marginal prices are shown in the printout.
    
    orders = [
        CarbonOrderUI.from_prices("ETH/USDC", "ETH", 2000+50*i, 2500+50*i, 10, 5)
        for i in range(10)
    ]
    for o in orders:
        print(f"y={o.y} pa={round(o.px,0)} pb={round(o.py,0)} pmarg={round(o.p_marg,1)}")
    margp = [o.p_marg for o in orders]
    min(margp), max(margp)
    
    # We are now looking at the dy released if we move to 2100. Spoiler: 0, because all positions are already beyond 2100.
    
    [o.dyfromp_f(2100) for o in orders]
    
    # If we go all the way to 3000 we see that all positions release their 5 ETH.
    
    [o.dyfromp_f(3000) for o in orders]
    
    # For 2300 we see that the first two positions can still get us to 2300. They release 1.39 and 0.40 ETH respectively on the way to 2300
    
    [o.dyfromp_f(2300) for o in orders]
    
    # For 2500, the first 6 positions release ETH
    
    [o.dyfromp_f(2500) for o in orders]
    
    # We define `dy_f` as the aggregate ETH released from all positions here
    
    dy_f = lambda p: sum(o.dyfromp_f(p) for o in orders)
    
    # The corresponding USDC inflow can be computed thus
    
    dx_f = lambda p: sum(o.dxfromdy_f(o.dyfromp_f(p)) for o in orders)
    
    # We can then plot the ETH release as a function of price
    
    pvals = np.linspace(2000, 3000)
    dyvals = [dy_f(p) for p in pvals]
    dxvals = [dx_f(p) for p in pvals]
    
    plt.plot(pvals, dyvals)
    plt.xlabel("Marginal price (USDC per ETH)")
    plt.ylabel("Aggregate ETH release")
    
    plt.plot(pvals, dxvals)
    plt.xlabel("Marginal price (USDC per ETH)")
    plt.ylabel("Aggregate USDC inflow")
    
    plt.plot(dxvals, dyvals)
    plt.xlabel("Aggregate USDC inflow")
    plt.ylabel("Aggregate ETH release")
    
    plt.plot(pvals, [dx/dy if dy>0 else None for dx,dy in zip(dxvals, dyvals)])
    plt.xlabel("Marginal price (USDC per ETH)")
    plt.ylabel("Effective price (USDC per ETH)")
    
    # Note for **Asaf**: this almost solves your "what is the price" problem if you plot it the other way round. The only issue is that here this is the marginal price after a move, so you'd have to integrate over it. We can also get the dx values the way we got the dy values (via the swap equation) but I do not have this implemented yet.
    
    plt.plot(dyvals, pvals)
    plt.ylabel("Marginal price (USDC per ETH)")
    plt.xlabel("Aggregate ETH release")
    
    # Now this does solve your price question
    
    plt.plot(dyvals, [dx/dy if dy>0 else None for dx,dy in zip(dxvals, dyvals)])
    plt.xlabel("Aggregate ETH release")
    plt.ylabel("Effective price (USDC per ETH)")
    
    # Going back to the routing problem we want to solve is that we have an aggregate release, say `15`, and we want the price; this we can do with goalseek
    
    p_goal = CarbonOrderUI.goalseek(lambda p: dy_f(p)-15, 2000, 3000)
    p_goal
    
    # The contribution of the positions at this price -- aka the **routing** -- is as follows
    
    rl1 = [o.dyfromp_f(p_goal) for o in orders]
    rl1
    
    # We can check that we routed indeed 15 ETH (the slight discrepancy is probably mostly related to goalseek precision)
    
    sum([o.dyfromp_f(p_goal) for o in orders])
    
    # And finally we can verify this against the exact algo match
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=True)
    Sim
    
    for i in range(10):
        Sim.add_strategy('ETH', 10, 2000+50*i, 2500+50*i, None, None, None, None)
        # sell 5 ETH off each order to get the appropriate p_marg
        Sim.amm_sells('ETH', 5, use_positions=[i*2])
    Sim.state()['orders'].query("disabled==False")
    
    Sim.state()
    
    r = Sim.amm_sells('ETH', 15)['trades']
    r
    
    # Below `rl2` is the route list obtained through routing, and `rl1` the original one. We see they are extremely close.
    
    rl2 = list(r.query("aggr==False")["amt1"])
    rl2
    
    
    rl1[:len(rl2)]
    
    [x2-x1 for x1,x2 in zip(rl1, rl2)]
    
    