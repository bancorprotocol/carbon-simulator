# ------------------------------------------------------------
# Auto generated test file `test_041_DisabledStrategies.py`
# ------------------------------------------------------------
# source file   = NBTest_041_DisabledStrategies.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 041
# test comment  = DisabledStrategies
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))




Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
Sim


# ------------------------------------------------------------
# Test      041
# File      test_041_DisabledStrategies.py
# Segment   Disabled Orders
# ------------------------------------------------------------
def test_disabled_orders():
# ------------------------------------------------------------
    # ### Base token
    
    o = Sim.add_order("ETH", 100, 2000, 3000)["orders"]
    assert(o.iloc[0]["y"] == 100)
    assert(o.iloc[0]["y_int"] == 100)
    assert(o.iloc[0]["p_start"] == 2000)
    assert(o.iloc[0]["p_end"] == 3000)
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[0]["p_unit"] == "USDC per ETH")
    o
    
    o = Sim.add_order("ETH", None, 2000, 3000)["orders"]
    assert(o.iloc[0]["y"] == 0)
    assert(o.iloc[0]["y_int"] == 0)
    assert(o.iloc[0]["p_start"] == 2000)
    assert(o.iloc[0]["p_end"] == 3000)
    assert(o.iloc[0]["disabled"] == False)
    o
    
    o = Sim.add_order("ETH", None, 3000, 2000)["orders"]
    assert(o.iloc[0]["p_start"] == 2000)
    assert(o.iloc[0]["p_end"] == 3000)
    o
    
    o = Sim.add_order("ETH", 1, None, None)["orders"]
    assert(o.iloc[0]["y"] == 1)
    assert(o.iloc[0]["y_int"] == 1)
    assert(o.iloc[0]["disabled"] == True)
    assert(o.iloc[0]["p_start"] is None)
    assert(o.iloc[0]["p_end"] is None)
    assert(o.iloc[0]["p_marg"] is None)
    o
    
    o = Sim.add_order("ETH", None, None, None)["orders"]
    assert(o.iloc[0]["y"] == 0)
    assert(o.iloc[0]["y_int"] == 0)
    o
    
    # ### Quote token
    
    o = Sim.add_order("USDC", 1000, 1000, 750)["orders"]
    assert(o.iloc[0]["y"] == 1000)
    assert(o.iloc[0]["y_int"] == 1000)
    assert(o.iloc[0]["p_start"] == 1000)
    assert(o.iloc[0]["p_end"] == 750)
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[0]["p_unit"] == "USDC per ETH")
    o
    
    o = Sim.add_order("USDC", None, 1000, 750)["orders"]
    assert(o.iloc[0]["y"] == 0)
    assert(o.iloc[0]["y_int"] == 0)
    assert(o.iloc[0]["p_start"] == 1000)
    assert(o.iloc[0]["p_end"] == 750)
    assert(o.iloc[0]["disabled"] == False)
    o
    
    o = Sim.add_order("USDC", None, 750, 1000)["orders"]
    assert(o.iloc[0]["p_start"] == 1000)
    assert(o.iloc[0]["p_end"] == 750)
    o
    
    o = Sim.add_order("USDC", 1000, None, None)["orders"]
    assert(o.iloc[0]["y"] == 1000)
    assert(o.iloc[0]["y_int"] == 1000)
    assert(o.iloc[0]["disabled"] == True)
    assert(o.iloc[0]["p_start"] is None)
    assert(o.iloc[0]["p_end"] is None)
    assert(o.iloc[0]["p_marg"] is None)
    o
    
    o = Sim.add_order("USDC", None, None, None)["orders"]
    assert(o.iloc[0]["y"] == 0)
    assert(o.iloc[0]["y_int"] == 0)
    o
    
    
    # ### Fails
    
    try:
        Sim.add_order("USDC", 10, None, 1000)
    except ValueError as e:
        print(e)
        assert(str(e)=="('p_lo, p_hi must either be both None or both numbers', 1000, None)")
    
    try:
        Sim.add_order("ETH", 10, 2000, None)
    except ValueError as e:
        print(e)
        assert(str(e)=="('p_lo, p_hi must either be both None or both numbers', None, 0.0005)")
    

# ------------------------------------------------------------
# Test      041
# File      test_041_DisabledStrategies.py
# Segment   Disabled Strategies
# ------------------------------------------------------------
def test_disabled_strategies():
# ------------------------------------------------------------
    # ### Base token
    
    o = Sim.add_strategy("ETH", 10, 2000, 3000, 1000, 1000, 750)["orders"]
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[1]["disabled"] == False)
    assert(o.iloc[0]["p_start"] == 2000)
    assert(o.iloc[1]["p_start"] == 1000)
    assert(o.iloc[0]["p_end"] == 3000)
    assert(o.iloc[1]["p_end"] == 750)
    o
    
    o = Sim.add_strategy("ETH", 10, 3000, 2000, 1000, 750, 1000)["orders"]
    assert(o.iloc[0]["p_start"] == 2000)
    assert(o.iloc[1]["p_start"] == 1000)
    assert(o.iloc[0]["p_end"] == 3000)
    assert(o.iloc[1]["p_end"] == 750)
    o
    
    o = Sim.add_strategy("ETH", None, 2000, 3000, None, 1000, 750)["orders"]
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[1]["disabled"] == False)
    o
    
    o = Sim.add_strategy("ETH", 10, None, None, 1100, 1000, 750)["orders"]
    assert(o.iloc[0]["y"] == 10)
    assert(o.iloc[1]["y"] == 1100)
    assert(o.iloc[0]["disabled"] == True)
    assert(o.iloc[1]["disabled"] == False)
    o
    
    
    o = Sim.add_strategy("ETH", 10, 2000, 3000, 1100, None, None)["orders"]
    assert(o.iloc[0]["y"] == 10)
    assert(o.iloc[1]["y"] == 1100)
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[1]["disabled"] == True)
    o
    
    # ### Quote token
    
    o = Sim.add_strategy("USDC", 1000, 1000, 750, 10, 2000, 3000)["orders"]
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[1]["disabled"] == False)
    assert(o.iloc[1]["p_start"] == 2000)
    assert(o.iloc[0]["p_start"] == 1000)
    assert(o.iloc[1]["p_end"] == 3000)
    assert(o.iloc[0]["p_end"] == 750)
    o
    
    o = Sim.add_strategy("USDC", 1000, 750, 1000, 10, 3000, 2000)["orders"]
    assert(o.iloc[0]["disabled"] == False)
    assert(o.iloc[1]["disabled"] == False)
    assert(o.iloc[1]["p_start"] == 2000)
    assert(o.iloc[0]["p_start"] == 1000)
    assert(o.iloc[1]["p_end"] == 3000)
    assert(o.iloc[0]["p_end"] == 750)
    o
    
    o = Sim.add_strategy("USDC", 1100, None, None, 10, 2000, 3000)["orders"]
    assert(o.iloc[0]["disabled"] == True)
    assert(o.iloc[1]["disabled"] == False)
    assert(o.iloc[0]["y"] == 1100)
    assert(o.iloc[1]["y"] == 10)
    o
    
    o = Sim.add_strategy("USDC", 1100, None, None, 10, None, None)["orders"]
    assert(o.iloc[0]["disabled"] == True)
    assert(o.iloc[1]["disabled"] == True)
    assert(o.iloc[0]["y"] == 1100)
    assert(o.iloc[1]["y"] == 10)
    o
    

# ------------------------------------------------------------
# Test      041
# File      test_041_DisabledStrategies.py
# Segment   Trading
# ------------------------------------------------------------
def test_trading():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    Sim.add_strategy("ETH", 10, 2000, 3000, 1000, 1000, 750)
    Sim.add_strategy("ETH", 10, None, None, 1000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 3000, 1000, None, None)
    Sim.add_strategy("ETH", None, 2000, 3000, None, 1000, 750)
    assert len(Sim.state()["orders"]) == 8
    Sim.state()["orders"]
    
    s = Sim.state()["orders"].query("disabled==False").query("y>0")
    assert list(s["id"]) == [0,1,3,4]
    s
    
    t = Sim.amm_sells("ETH", 10)["trades"]
    assert list(t["routeix"])[:-1] == [0,4]
    t
    
    s = Sim.state()["orders"].query("disabled==False").query("y>0")
    s
    
    t = Sim.amm_sells("USDC", 1000)["trades"]
    assert list(t["routeix"])[:-1] == [1,3]
    t
    
    