# ------------------------------------------------------------
# Auto generated test file `test_905_ReconciliationsSlow.py`
# ------------------------------------------------------------
# source file   = NBTest_905_ReconciliationsSlow.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 905
# test comment  = ReconciliationsSlow
# ------------------------------------------------------------



from carbon.helpers.stdimports import *
from carbon.helpers.soltest import SolTestBase
from carbon.helpers.floatint import *
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolTestBase))
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonFloatInt32))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(P))
from math import log2, floor, ceil, sqrt
print_version(require="2.3.3")




# ------------------------------------------------------------
# Test      905
# File      test_905_ReconciliationsSlow.py
# Segment   Reconcile CarbonOrderUI vs Core Sim
# ------------------------------------------------------------
def test_reconcile_carbonorderui_vs_core_sim():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair=P("ETH/USDC"), raiseonerror=True)
    r = Sim.add_strategy("ETH", 10, 1500, 2000, 1000, 750, 500)
    r["orders"]
    
    ouis=r["orderuis"]
    ouis
    
    # ### amm_sells ETH (dx from dy)
    
    size = 0.1
    r = Sim.amm_sells("ETH", size, execute=False)
    tr = r["trades"].query("aggr==True").iloc[0]
    r = Sim.amm_sells("ETH", size, execute=False)
    tr2 = r["trades"].query("aggr==True").iloc[0]
    assert tr["price"] == tr2["price"] # check trades are NOT being executed
    dx = ouis[0].dxfromdy_f(size)
    assert abs(dx/tr["amt2"] - 1) < 1e-10
    tr2["amt2"], dx
    
    for size in np.linspace(0.1,1,10):
        r = Sim.amm_sells("ETH", size, execute=False)
        tr = r["trades"].query("aggr==True").iloc[0]
        amts = tr["amt2"]
        dx = ouis[0].dxfromdy_f(size)
        print(size, amts, dx, amts/dx-1)
        assert abs(amts/dx - 1) < 1e-10
    
    # ### amm_sells USDC (dx from dy)
    
    for size in np.linspace(0.1,1000,10):
        r = Sim.amm_sells("USDC", size, execute=False)
        tr = r["trades"].query("aggr==True").iloc[0]
        amts = tr["amt2"]
        dx = ouis[1].dxfromdy_f(size)
        print(size, amts, dx, amts/dx-1)
        assert abs(amts/dx - 1) < 1e-8
    
    # ### amm_buys USDC (dy from dx)
    
    for size in np.linspace(0.1,1000,10):
        r = Sim.amm_buys("USDC", size, execute=False)
        tr = r["trades"].query("aggr==True").iloc[0]
        amts = tr["amt1"]
        dx = ouis[0].dyfromdx_f(size)
        print(size, amts, dx, amts/dx-1)
        assert abs(amts/dx - 1) < 1e-8
    
    # ### amm_buys ETH (dy from dx)
    
    for size in np.linspace(0.1,1,10):
        r = Sim.amm_buys("ETH", size, execute=False)
        tr = r["trades"].query("aggr==True").iloc[0]
        amts = tr["amt1"]
        dx = ouis[1].dyfromdx_f(size)
        print(size, amts, dx, amts/dx-1)
        assert abs(amts/dx - 1) < 1e-8
    

# ------------------------------------------------------------
# Test      905
# File      test_905_ReconciliationsSlow.py
# Segment   Verifying equivalence of both order sets
# ------------------------------------------------------------
def test_verifying_equivalence_of_both_order_sets():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair=P("ETH/USDC"), raiseonerror=True)
    Sim.add_strategy("ETH", 1, 1500, 2000, 1000, 750, 500)
    Sim.add_strategy("ETH", 1.1, 1501, 2001, 1001, 751, 501)
    r = Sim.state()
    os = r["orders"]
    os
    
    ouis = r["orderuis"]
    ouis
    
    assert len(ouis)==len(os)
    for oui, oo in zip(ouis.values(),os.iterrows()):
        o = oo[1]
        #print (oui, o)
        assert o["id"] == oui.id
        assert o["lid"] == oui.lid
        assert o["pair"] == oui.pair.pair_iso
        assert o["tkn"] == oui.tkn
        assert o["tkn"] == oui.tkn
        assert o["y_int"] == oui.yint
        assert abs(o["p_start"]/oui.pa-1) < 1e-10
        assert abs(o["p_end"]/oui.pb-1) < 1e-10
        assert abs(o["y_int"]/oui.yint-1) < 1e-10
        assert abs(o["y"]/oui.y-1) < 1e-10
        assert o["p_unit"] == oui.price_convention
        assert oui.linked.linked is oui
    
    