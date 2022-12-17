# ------------------------------------------------------------
# Auto generated test file `test_033_carbonpair.py`
# ------------------------------------------------------------
# source file   = NBTest_033_carbonpair.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 033
# test comment  = carbonpair
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonPair, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))


#


#

# ------------------------------------------------------------
# Test      033
# File      test_033_carbonpair.py
# Segment   CarbonPair
# ------------------------------------------------------------
def test_carbonpair():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair=CarbonPair("ETH/USDC"))
    Sim
    
    assert (Sim.default_basetoken, Sim.default_quotetoken) == ('ETH', 'USDC')
    
    assert (Sim.tknb, Sim.tknq) == ('ETH', 'USDC')
    
    Sim.add_order("ETH", 10, 2000, 3000)["orders"]
    Sim.add_order("ETH", 10, 2000, 2500)["orders"]
    r = Sim.state()["orders"]
    assert list(r["pair"]) == ["ETHUSDC"]*4
    r
    
    r = Sim.amm_sells("ETH", 1)["trades"]
    assert list(r["p_unit"]) == ["USDC per ETH"]*3
    r
    
    Sim.state()["orders"]
    
    