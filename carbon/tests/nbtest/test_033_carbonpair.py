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
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonPair))


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
    

# ------------------------------------------------------------
# Test      033
# File      test_033_carbonpair.py
# Segment   Decimals
# ------------------------------------------------------------
def test_decimals():
# ------------------------------------------------------------
    
    assert P("ETH/USDC").has_decimals == False
    assert P("ETH/USDC").sd().has_decimals == False
    assert P("ETH/USDC").sd(18).has_decimals == False
    assert P("ETH/USDC").sd(dec_tknq=18).has_decimals == False
    assert P("ETH/USDC").sd(18,6).has_decimals == True
    
    assert P("ETH/USDC").decimals == {'ETH': None, 'USDC': None, '_TKNB': None, '_TKNQ': None, '_DIFFQB': None}
    assert P("ETH/USDC").sd().decimals == {'ETH': None, 'USDC': None, '_TKNB': None, '_TKNQ': None, '_DIFFQB': None}
    assert P("ETH/USDC").sd(18,6).decimals == {'ETH': 18, 'USDC': 6, '_TKNB': 18, '_TKNQ': 6, '_DIFFQB': -12}
    
    DECDICT = {"ETH": 18, "USDC": 6, "WBTC": 8, "BNT": 18}
    
    assert P("ETH/USDC").sd(dct=DECDICT).decimals == {'ETH': 18, 'USDC': 6, '_TKNB': 18, '_TKNQ': 6, '_DIFFQB': -12}
    
    assert P("ETH/USDC").sd(dct=P.DECDICT).decimals["_DIFFQB"] == -12
    assert P("USDC/ETH").sd(dct=P.DECDICT).decimals["_DIFFQB"] == 12
    assert P("SHIB/ETH").sd(dct=P.DECDICT).decimals["_DIFFQB"] == 0
    assert P("WBTC/ETH").sd(dct=P.DECDICT).decimals["_DIFFQB"] == 10
    assert P("NEAR/ETH").sd(dct=P.DECDICT).decimals["_DIFFQB"] == 18
    
    assert P("ETH/USDC").sd(dct=P.DECDICT).decdiffqb == -12
    assert P("USDC/ETH").sd(dct=P.DECDICT).decdiffqb == 12
    assert P("SHIB/ETH").sd(dct=P.DECDICT).decdiffqb == 0
    assert P("WBTC/ETH").sd(dct=P.DECDICT).decdiffqb == 10
    assert P("NEAR/ETH").sd(dct=P.DECDICT).decdiffqb == 18
    
    ETHUSDC = P("ETH/USDC").sd(18,6)
    assert str(ETHUSDC) == "P('ETH/USDC').sd(18,6)"
    assert P(ETHUSDC).has_decimals
    assert str(P(ETHUSDC)) == "P('ETH/USDC').sd(18,6)"
    
    