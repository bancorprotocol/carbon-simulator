# ------------------------------------------------------------
# Auto generated test file `test_034_Liquidity.py`
# ------------------------------------------------------------
# source file   = NBTest_034_Liquidity.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 034
# test comment  = Liquidity
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))





# ------------------------------------------------------------
# Test      034
# File      test_034_Liquidity.py
# Segment   Liquidity
# ------------------------------------------------------------
def test_liquidity():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=True)
    Sim
    
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/USDC")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/USDC")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/USDC")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/USDC")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/USDC")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/USDC")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/USDC")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000, "ETH/DAI")
    Sim.add_order("ETH", 20, 2010, 3010, "ETH/DAI")
    Sim.add_order("ETH", 30, 2020, 3020, "ETH/DAI")
    Sim.add_order("ETH", 40, 2030, 2030, "ETH/DAI")
    Sim.add_strategy("ETH", 10, 2000, 3000, 5000, 1000, 900, "ETH/DAI")
    Sim.add_strategy("ETH", 20, 2010, 3010, 5100, 1010, 910, "ETH/DAI")
    Sim.add_strategy("ETH", 30, 2020, 3020, 5200, 1020, 920, "ETH/DAI")
    Sim.add_strategy("ETH", 40, 2030, 3030, 5300, 1030, 930, "ETH/DAI")
    Sim
    
    r = Sim.state()["orders"]
    assert len(r) == 32
    assert sum(r.query("tkn == 'ETH'")["y"]) == 400
    assert sum(r.query("tkn == 'USDC'")["y"]) == 20600
    assert sum(r.query("tkn == 'DAI'")["y"]) == 20600
    r
    
    df = Sim.liquidity(Sim.ASDF)
    assert float(df.query("pair=='ETHDAI'").query("tkn=='DAI'")["y"]) == 20600
    assert float(df.query("pair=='ETHUSDC'").query("tkn=='ETH'")["y"]) == 200
    df
    
    dct = df.to_dict(orient='dict')["y"]
    assert dct[('ETHUSDC', 'USDC')] == 20600
    dct
    
    pairs = set(k[0] for k in dct)
    assert pairs == {'ETHDAI', 'ETHUSDC'}
    pairs
    
    {p:{k[1]:1 for k in dct if k[0]==p} for p in pairs}
    
    Sim.liquidity(Sim.ASDICT)
    
    Sim.liquidity()
    
    assert Sim.liquidity(Sim.ASDICT) == Sim.liquidity()
    
    