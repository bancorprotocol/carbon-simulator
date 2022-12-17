# ------------------------------------------------------------
# Auto generated test file `test_035_UsePositions.py`
# ------------------------------------------------------------
# source file   = NBTest_035_UsePositions.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 035
# test comment  = UsePositions
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))





# ------------------------------------------------------------
# Test      035
# File      test_035_UsePositions.py
# Segment   use_position
# ------------------------------------------------------------
def test_use_position():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
    Sim
    
    for i in range(10):
        Sim.add_order("ETH", 10, 2000+i, 2200)
    
    r = Sim.state()["orders"].query("disabled==False")
    assert len(r) == 10
    assert sum(r.query("tkn=='ETH'")["y"]) == 100
    r
    
    help(Sim.amm_sells)
    
    r = Sim.amm_sells("ETH", 10, execute=False, pair="ETH/USDC")["trades"]
    p = r.iloc[-1]["price"]
    print(p)
    r
    
    r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[2])["trades"]
    p1 = r.iloc[-1]["price"]
    print(p1, p)
    assert p1>p
    assert r.iloc[-1]["routeix"] == "[2]"
    r
    
    r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[4])["trades"]
    p2 = r.iloc[-1]["price"]
    print(p2, p1, p)
    assert p2>p1
    assert r.iloc[-1]["routeix"] == "[4]"
    r
    
    r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[6,8])["trades"]
    p3 = r.iloc[-1]["price"]
    print(p3, p2, p1, p)
    assert p3>p
    assert r.iloc[-1]["routeix"] == "[6, 8]"
    r
    
    r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[12,14])["trades"]
    p4 = r.iloc[-1]["price"]
    print(p4, p3, p2, p1, p)
    assert p4>p3
    assert r.iloc[-1]["routeix"] == "[12, 14]"
    r
    
    r.iloc[-1]["routeix"]
    
    