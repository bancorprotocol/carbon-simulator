# ------------------------------------------------------------
# Auto generated test file `test_040_PairInSim.py`
# ------------------------------------------------------------
# source file   = NBTest_040_PairInSim.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 040
# test comment  = PairInSim
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))




ETHUSDC = P("ETH/USDC")


# ------------------------------------------------------------
# Test      040
# File      test_040_PairInSim.py
# Segment   Pair without CarbonPair defaults
# ------------------------------------------------------------
def test_pair_without_carbonpair_defaults():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(raiseonerror=True)
    assert(Sim.slashpair is None)
    Sim
    
    try:
        Sim.add_order("ETH", 10, 2000, 3000)
    except ValueError as e:
        print(e)
        assert(str(e)=="Pair must be provided in function or simulation defaults")
    
    try:
        Sim.add_order("ETH", 10, 2000, 3000, pair="ETHUSDC")["orders"]
    except ValueError as e:
        print(e)
        assert(str(e)=="('Illegal slashpair', 'ETHUSDC')")
    
    try:
        Sim.add_order("LINK", 10, 2000, 3000, pair=ETHUSDC)
    except ValueError as e:
        print(e)
        assert str(e) == "('Token not in pair', 'LINK', 'ETH/USDC', 'ETH/USDC')"
    
    o = Sim.add_order("ETH", 10, 2000, 3000, pair=ETHUSDC)["orders"]
    assert(o.iloc[0]["pair"]=="ETHUSDC")
    assert(o.iloc[0]["tkn"]=="ETH")
    assert(o.iloc[0]["p_unit"]=="USDC per ETH")
    o
    
    Sim.add_order("ETH", 10, 2000, 3000, pair="ETH/USDC")["orders"]
    
    try:
        Sim.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750)["orders"]
    except ValueError as e:
        print(e)
        assert(str(e)=="Pair must be provided in function or simulation defaults")
    
    Sim.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750, pair="ETH/USDC")["orders"]
    

# ------------------------------------------------------------
# Test      040
# File      test_040_PairInSim.py
# Segment   Pair with CarbonPair defaults
# ------------------------------------------------------------
def test_pair_with_carbonpair_defaults():
# ------------------------------------------------------------
    
    SimP = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    assert(SimP.slashpair=="ETH/USDC")
    SimP
    
    o = SimP.add_order("ETH", 10, 2000, 3000)["orders"]
    assert(o.iloc[0]["pair"]=="ETHUSDC")
    assert(o.iloc[0]["tkn"]=="ETH")
    assert(o.iloc[0]["p_unit"]=="USDC per ETH")
    o
    
    o = SimP.add_order("ETH", 10, 2000, 3000, pair=ETHUSDC)["orders"]
    assert(o.iloc[0]["pair"]=="ETHUSDC")
    assert(o.iloc[0]["tkn"]=="ETH")
    assert(o.iloc[0]["p_unit"]=="USDC per ETH")
    o
    
    SimP.add_order("ETH", 10, 2000, 3000, pair="ETH/USDC")["orders"]
    
    o = SimP.add_order("ETH", 10, 2000, 3000, pair="ETH/DAI")["orders"]
    assert(o.iloc[0]["pair"]=="ETHDAI")
    assert(o.iloc[0]["tkn"]=="ETH")
    assert(o.iloc[0]["p_unit"]=="DAI per ETH")
    o
    
    SimP.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750)["orders"]
    
    
    