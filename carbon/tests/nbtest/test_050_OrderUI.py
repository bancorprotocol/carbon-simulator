# ------------------------------------------------------------
# Auto generated test file `test_050_OrderUI.py`
# ------------------------------------------------------------
# source file   = NBTest_050_OrderUI.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 050
# test comment  = OrderUI
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))





# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   carbonorderui ids and data
# ------------------------------------------------------------
def test_carbonorderui_ids_and_data():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 750, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    
    # +
    # check that the id corresponds to the own dict key
    assert ouis[0].id == 0
    assert ouis[1].id == 1
    
    # check that the lid corresponds to the other dict key
    assert ouis[0].lid == 1
    assert ouis[1].lid == 0
    
    # check that the linked objects are correct
    assert ouis[0].linked is ouis[1]
    assert ouis[1].linked is ouis[0]
    
    # +
    # check curve data
    assert ouis[0].pair.slashpair == "ETH/USDC"
    assert ouis[1].pair.slashpair == "ETH/USDC"
    assert ouis[0].tkn == "ETH"
    assert ouis[1].tkn == "USDC"
    
    # prices
    assert ouis[0].pa == 2000
    assert ouis[0].pb == 2500
    assert ouis[1].pa == 1250
    assert ouis[1].pb == 1000
    
    # raw prices
    assert ouis[0].pa_raw == 1/2000
    assert ouis[0].pb_raw == 1/2500
    assert ouis[1].pa_raw == 1250
    assert ouis[1].pb_raw == 1000
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 750
    assert ouis[1].yint == 750
    assert ouis[1].p_marg == ouis[1].pa
    # -
    

# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   carbonorderui addliqy
# ------------------------------------------------------------
def test_carbonorderui_addliqy():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 750, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 750
    assert ouis[1].yint == 750
    assert ouis[1].p_marg == ouis[1].pa
    
    try:
        ouis[0].addliqy(0.5, expandcurve=False)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    
    r = ouis[0].addliqy(0.5)
    assert r["y_old"] == 1
    assert r["y"] == 1.5
    assert r["dy"] == 0.5
    assert r["yint_old"] == 1
    assert r["yint"] == 1.5
    assert r["pmarg_old"] == 2000
    assert r["pmarg"] == 2000
    assert r["tkny"] == "ETH"
    assert r["expanded"] == True
    r
    

# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   carbonorderui trading
# ------------------------------------------------------------
def test_carbonorderui_trading():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 750, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 750
    assert ouis[1].yint == 750
    assert ouis[1].p_marg == ouis[1].pa
    
    # check that the linked objects are correct
    assert ouis[0].linked is ouis[1]
    assert ouis[1].linked is ouis[0]
    
    # ### trade 1: bysource[selly]
    
    r = ouis[0].selly(0.5)
    l = r["linked"]
    assert r["action"] == "bysource[selly]"
    assert r["executed"] == True
    assert r["y_old"] == 1
    assert r["y"] == 0.5
    assert r["dy"] == 0.5
    assert r["expanded"] == False
    assert round(r["x"],4) == 1055.7281
    assert round(r["dx"],4) == 1055.7281
    assert r["x"] == r["dx"]
    assert r["pmarg_old"] == 2000
    assert round(r["pmarg"],4) == 2229.1236
    assert round(r["dx/dy"],4) == 2111.4562
    assert l["y_old"] == 750
    assert l["y"] == l["y_old"] + l["dy"]
    assert l["dy"] == r["dx"]
    assert l["pmarg_old"] == 1250
    assert l["pmarg"] == 1250
    assert round(l["yint_old"],4) == 750
    assert round(l["yint"],4) == 1805.7281
    assert l["expanded"] == True
    assert l["tkny"] == "USDC"
    l0 = l
    #r
    
    # ### trade 2: bysource[selly]
    
    r = ouis[0].selly(0.1)
    l = r["linked"]
    assert r["action"] == "bysource[selly]"
    assert r["executed"] == True
    assert r["y_old"] == 0.5
    assert r["y"] == 0.4
    assert r["dy"] == 0.1
    assert r["expanded"] == False
    assert round(r["x"],4) == 1281.1529
    assert round(r["dx"],4) == 225.4249
    assert round(r["pmarg_old"],4) == 2229.1236
    assert round(r["pmarg"],4) == 2279.6568
    assert round(r["dx/dy"],4) == 2254.2486
    assert l["y_old"] == l0["y"]
    assert l["y"] == l["y_old"] + l["dy"]
    assert l["dy"] == r["dx"]
    assert l["pmarg_old"] == 1250
    assert l["pmarg"] == 1250
    assert round(l["yint_old"],4) == 1805.7281
    assert round(l["yint"],4) == 2031.1529
    assert l["expanded"] == True
    assert l["tkny"] == "USDC"
    l0 = l
    #r
    
    # ### trade 3: bytarget[buyx]
    
    r = ouis[0].buyx(100)
    l = r["linked"]
    assert r["action"] == "bytarget[buyx]"
    assert r["executed"] == True
    assert r["y_old"] == 0.4
    assert round(r["y"],4) == 0.3563
    assert round(r["dy"],4) == 0.0437
    assert r["expanded"] == False
    assert round(r["x"],4) == 1381.1529
    assert round(r["dx"],4) == 100
    assert round(r["pmarg_old"],4) == 2279.6568
    assert round(r["pmarg"],4) == 2302.2550
    assert round(r["dx/dy"],4) == 2290.9280
    assert l["y_old"] == l0["y"]
    assert l["y"] == l["y_old"] + l["dy"]
    assert l["dy"] == r["dx"]
    assert l["pmarg_old"] == 1250
    assert l["pmarg"] == 1250
    assert round(l["yint_old"],4) == 2031.1529
    assert round(l["yint"],4) == 2131.1529
    assert l["expanded"] == True
    assert l["tkny"] == "USDC"
    l0 = l
    #r
    
    # ### trade 4: byprice[tradeto]
    
    r = ouis[0].tradeto(2330)
    l = r["linked"]
    assert r["action"] == "byprice[tradeto]"
    assert r["executed"] == True
    assert round(r["y_old"],4) == 0.3563
    assert round(r["y"],4) == 0.3036
    assert round(r["dy"],4) == 0.0527
    assert r["expanded"] == False
    assert round(r["x"],4) == 1503.2594
    assert round(r["dx"],4) == 122.1064
    assert round(r["pmarg_old"],4) == 2302.2550
    assert round(r["pmarg"],4) == 2330.0
    assert round(r["dx/dy"],4) == 2316.0860
    assert l["y_old"] == l0["y"]
    assert l["y"] == l["y_old"] + l["dy"]
    assert l["dy"] == r["dx"]
    assert l["pmarg_old"] == 1250
    assert l["pmarg"] == 1250
    assert round(l["yint_old"],4) == 2131.1529
    assert round(l["yint"],4) == 2253.2594
    assert l["expanded"] == True
    assert l["tkny"] == "USDC"
    l0 = l
    #r
    

# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   tradeto basics
# ------------------------------------------------------------
def test_tradeto_basics():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 750, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 750
    assert ouis[1].yint == 750
    assert ouis[1].p_marg == ouis[1].pa
    
    # check that the linked objects are correct
    assert ouis[0].linked is ouis[1]
    assert ouis[1].linked is ouis[0]
    
    # +
    # ensure the correct PriceOutOfBoundsError is raised
    try:
        ouis[0].yfromp_f(1000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ouis[0].PriceOutOfBoundsErrorBeyondStart as e:
        print(e)
    
    try:
        ouis[0].yfromp_f(3000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ouis[0].PriceOutOfBoundsErrorBeyondEnd as e:
        print(e)
    
    # +
    # ensure PriceOutOfBoundsError is raised
    try:
        ouis[0].yfromp_f(1000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ouis[0].PriceOutOfBoundsError as e:
        print(e)
        
    try:
        ouis[0].yfromp_f(3000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ouis[0].PriceOutOfBoundsError as e:
        print(e)
    
    # +
    # ensure ValueError is still captured
    try:
        ouis[0].yfromp_f(1000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
        
    try:
        ouis[0].yfromp_f(3000, raiseonerror=True)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    # -
    
    # ensure that going the wrong way beyond boundaries leads to dy=0, executed=False
    r = ouis[0].tradeto(1000)
    assert r["action"] == "byprice[tradeto]"
    assert r["dy"] == 0
    assert r["executed"] == False
    #r
    
    # ensure that going the right way yet beyond boundaries leads to full execution
    r = ouis[0].tradeto(3000)
    l = r["linked"]
    assert r["action"] == "byprice[tradeto]"
    assert r["executed"] == True
    assert r["y_old"] == 1
    assert r["y"] == 0
    assert r["dy"] == 1
    assert r["expanded"] == False
    assert round(r["x"],4) == 2236.0680
    assert round(r["dx"],4) == 2236.0680
    assert r["x"] == r["dx"]
    assert r["pmarg_old"] == 2000
    assert r["pmarg"] == 2500
    assert round(r["dx/dy"],4) == 2236.0680
    assert l["y_old"] == 750
    assert l["y"] == l["y_old"] + l["dy"]
    assert l["dy"] == r["dx"]
    assert l["pmarg_old"] == 1250
    assert l["pmarg"] == 1250
    assert round(l["yint_old"],4) == 750
    assert round(l["yint"],4) == 2986.0680
    assert l["expanded"] == True
    assert l["tkny"] == "USDC"
    #r
    
    # ensure you can't trade back
    r = ouis[0].tradeto(2250)
    assert r["action"] == "byprice[tradeto]"
    assert r["dy"] == 0
    assert r["executed"] == False
    #r
    

# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   tradeto over linked orders
# ------------------------------------------------------------
def test_tradeto_over_linked_orders():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 0, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 0
    assert ouis[1].yint == 0
    assert ouis[1].p_marg == ouis[1].pa
    
    # check that the linked objects are correct
    assert ouis[0].linked is ouis[1]
    assert ouis[1].linked is ouis[0]
    
    r0 = ouis[0].tradeto(3000)
    r1 = ouis[1].tradeto(3000)
    assert r0["dy"] == 1 
    assert r1["dy"] == 0 
    assert r0["pmarg"] == 2500 
    assert r1["pmarg"] == 1250 
    #r0
    
    r0 = ouis[0].tradeto(500)
    r1 = ouis[1].tradeto(500)
    assert round(r0["dy"],4) == 0
    assert round(r1["dy"],4) == 2236.0680
    assert r0["pmarg"] == 2500 
    assert r1["pmarg"] == 1000 
    #r1
    
    r0 = ouis[0].tradeto(3000)
    r1 = ouis[1].tradeto(3000)
    assert round(r0["dy"],4) == 2
    assert round(r1["dy"],4) == 0
    assert r0["pmarg"] == 2500 
    assert r1["pmarg"] == 1250 
    #r0
    

# ------------------------------------------------------------
# Test      050
# File      test_050_OrderUI.py
# Segment   more tradeto over linked orders
# ------------------------------------------------------------
def test_more_tradeto_over_linked_orders():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 1, 2000, 2500, 0, 1250, 1000)
    ouis = Sim.state()["orderuis"]
    ouis
    
    # y, yint, pmarg
    assert ouis[0].y == 1
    assert ouis[0].yint == 1
    assert ouis[0].p_marg == ouis[0].pa
    assert ouis[1].y == 0
    assert ouis[1].yint == 0
    assert ouis[1].p_marg == ouis[1].pa
    
    # check that the linked objects are correct
    assert ouis[0].linked is ouis[1]
    assert ouis[1].linked is ouis[0]
    
    assert ouis[0].tkn == "ETH"
    assert ouis[1].tkn == "USDC"
    ethamt_r  = [ouis[0].y]
    usdcamt_r = [ouis[1].y]
    for ix in range(5):
        
        # trade up to 3000
        r0 = ouis[0].tradeto(3000)
        r1 = ouis[1].tradeto(3000)
        ethamt_r  += [ouis[0].y]
        usdcamt_r += [ouis[1].y]
        
        # trade back down to 500
        r0 = ouis[0].tradeto(500)
        r1 = ouis[1].tradeto(500)
        ethamt_r  += [ouis[0].y]
        usdcamt_r += [ouis[1].y]
    
    #plt.scatter(x=ethamt_r, y=usdcamt_r)
    plt.plot(ethamt_r, usdcamt_r, "-o")
    plt.xlabel("ETH")
    plt.ylabel("USDC")
    plt.grid()
    
    assert [round(x,0) for x in ethamt_r]  == [1, 0, 2, 0, 4, 0, 8, 0, 16, 0, 32]
    assert [round(x,0) for x in usdcamt_r] == [0, 2236, 0, 4472, 0, 8944, 0, 17889, 0, 35777, 0]
    
    