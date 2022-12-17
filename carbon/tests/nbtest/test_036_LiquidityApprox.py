# ------------------------------------------------------------
# Auto generated test file `test_036_LiquidityApprox.py`
# ------------------------------------------------------------
# source file   = NBTest_036_LiquidityApprox.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 036
# test comment  = LiquidityApprox
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
from math import sqrt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))




Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
Sim

Sim.add_order("ETH", 10, 2000, 3000)
Sim.add_order("ETH", 10, 2500, 2500)
Sim.add_order("USDC", 10*1250, 1500, 1000)
Sim.add_order("USDC", 10*1250, 1250, 1250)
Sim

Sim.state()["orders"]

Sim.state().keys()

Sim.state()["orderuis"]

help(Sim.state()["orderuis"][0].liquidity_approx)


# ------------------------------------------------------------
# Test      036
# File      test_036_LiquidityApprox.py
# Segment   Order 0 ETH range
# ------------------------------------------------------------
def test_order_0_eth_range():
# ------------------------------------------------------------
    
    oui = Sim.state()["orderuis"][0]
    assert (oui.pmin, oui.pmax, oui.total_liquidity) == (2000.0, 3000.0, (10.0, 'ETH'))
    oui.pmin, oui.pmax, oui.total_liquidity
    
    r = oui.liquidity_approx(500, 600, "ETH", asperc=True)
    assert r == 0
    r
    
    r = oui.liquidity_approx(3000, 3020, "ETH", asperc=True)
    assert r == 0
    r
    
    r = oui.liquidity_approx(2000, 3000, "ETH", asperc=True)
    assert r == 1.
    r
    
    r = oui.liquidity_approx(3000, 2000, "ETH", asperc=True)
    assert r == 1
    r
    
    r = oui.liquidity_approx(2000, 2500, "ETH", asperc=True)
    assert r == 0.5
    r
    
    r = oui.liquidity_approx(2500, 3000, "ETH", asperc=True)
    assert r == 0.5
    r
    
    r = oui.liquidity_approx(2250, 2750, "ETH", asperc=True)
    assert r == 0.5
    r
    
    
    r = oui.liquidity_approx(2000, 3000, "ETH", asperc=False)
    assert r == 10.
    r
    
    r = oui.liquidity_approx(2000, 2500, "ETH", asperc=False)
    assert r == 5.
    r
    
    r = oui.liquidity_approx(2000, 2500, asperc=False)
    assert r == 5.
    r
    
    r = oui.liquidity_approx(2000, 3000, "USDC", asperc=False)
    assert int(r) == int(10*sqrt(2000*3000))
    r, sqrt(2000*3000)
    
    r = oui.liquidity_approx(2250, 2750, "USDC", asperc=False)
    assert int(r) == int(10*sqrt(2250*2750)*0.5)
    r, sqrt(2250*2750)*0.5
    

# ------------------------------------------------------------
# Test      036
# File      test_036_LiquidityApprox.py
# Segment   Order 1 ETH point
# ------------------------------------------------------------
def test_order_1_eth_point():
# ------------------------------------------------------------
    
    oui = Sim.state()["orderuis"][2]
    oui.pmin, oui.pmax, oui.total_liquidity
    
    r = oui.liquidity_approx(2000, 2499, "ETH", asperc=True)
    assert r == 0
    r
    
    r = oui.liquidity_approx(2501, 3020, "ETH", asperc=True)
    assert r == 0
    r
    
    r = oui.liquidity_approx(2499, 2501, "ETH", asperc=True)
    assert r == 1
    r
    
    r = oui.liquidity_approx(2500, 2501, "ETH", asperc=True)
    assert r == 1
    r
    
    r = oui.liquidity_approx(2499, 2500, "ETH", asperc=True)
    assert r == 0
    r
    
    r = oui.liquidity_approx(2500, 2500, "ETH", asperc=True)
    assert r == 1
    r
    
    
    r = oui.liquidity_approx(2499, 2501, "ETH", asperc=False)
    assert r == 10
    r
    
    r = oui.liquidity_approx(2499, 2501, "USDC", asperc=False)
    assert r == 25000
    r
    
    r = oui.liquidity_approx(2500, 2501, "USDC", asperc=False)
    assert r == 25000
    r
    
    r = oui.liquidity_approx(2500, 2500, "USDC", asperc=False)
    assert r == 25000
    r
    
    r = oui.liquidity_approx(2000, 3000, "USDC", asperc=False)
    assert r == 25000
    r
    

# ------------------------------------------------------------
# Test      036
# File      test_036_LiquidityApprox.py
# Segment   Order 2 USDC range
# ------------------------------------------------------------
def test_order_2_usdc_range():
# ------------------------------------------------------------
    
    oui = Sim.state()["orderuis"][4]
    oui.pmin, oui.pmax, oui.total_liquidity
    
    r = oui.liquidity_approx(500, 600, "USDC", asperc=False)
    assert r == 0
    r
    
    r = oui.liquidity_approx(1600, 2000, "USDC", asperc=False)
    assert r == 0
    r
    
    r = oui.liquidity_approx(1000, 1500, "USDC", asperc=False)
    assert r == 12500
    r
    
    r = oui.liquidity_approx(1000, 1100, "USDC", asperc=False)
    assert r == 2500
    r
    
    r = oui.liquidity_approx(1400, 1500, "USDC", asperc=False)
    assert r == 2500
    r
    
    r = oui.liquidity_approx(1000, 1100, "ETH", asperc=False)
    assert r == 2500/sqrt(1000*1100)
    r, 2500/sqrt(1000*1100)
    
    r = oui.liquidity_approx(1400, 1500, "ETH", asperc=False)
    assert int(r) == int(2500/sqrt(1400*1500))
    r, 2500/sqrt(1400*1500)
    

# ------------------------------------------------------------
# Test      036
# File      test_036_LiquidityApprox.py
# Segment   Order 3 USDC point
# ------------------------------------------------------------
def test_order_3_usdc_point():
# ------------------------------------------------------------
    
    oui = Sim.state()["orderuis"][6]
    oui.pmin, oui.pmax, oui.total_liquidity
    
    r = oui.liquidity_approx(1249, 1251, "USDC", asperc=False)
    assert r == 12500
    r
    
    r = oui.liquidity_approx(1000, 2000, "USDC", asperc=False)
    assert r == 12500
    r
    
    r = oui.liquidity_approx(1249, 1250, "USDC", asperc=False)
    assert r == 0
    r
    
    r = oui.liquidity_approx(1250, 1251, "USDC", asperc=False)
    assert r == 12500
    r
    
    r = oui.liquidity_approx(1249, 1251, "ETH", asperc=False)
    assert r == 10
    r
    
    r = oui.liquidity_approx(1000, 2000, "ETH", asperc=False)
    assert r == 10
    r
    
    r = oui.liquidity_approx(1249, 1250, "ETH", asperc=False)
    assert r == 0
    r
    
    r = oui.liquidity_approx(1250, 1251, "ETH", asperc=False)
    assert r == 10
    r
    
    