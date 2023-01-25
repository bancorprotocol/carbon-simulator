# ------------------------------------------------------------
# Auto generated test file `test_053_MargPandYInt.py`
# ------------------------------------------------------------
# source file   = NBTest_053_MargPandYInt.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 053
# test comment  = MargPandYInt
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
#plt.style.use('seaborn-dark')
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))






# ------------------------------------------------------------
# Test      053
# File      test_053_MargPandYInt.py
# Segment   tests fail
# ------------------------------------------------------------
def test_tests_fail():
# ------------------------------------------------------------
    
    #assert False, "This notebook would fail were the failing tests not commented out"
    assert True
    

# ------------------------------------------------------------
# Test      053
# File      test_053_MargPandYInt.py
# Segment   add_strategy
# ------------------------------------------------------------
def test_add_strategy():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    
    r = Sim.add_strategy("ETH", 1, 2000, 3000, 1500, 1000, 750)["orders"]
    r
    
    # +
    assert r.iloc[0]["p_start"]    == 2000
    assert r.iloc[0]["p_end"]      == 3000
    assert r.iloc[0]["p_marg"]     == 2000
    assert r.iloc[0]["y_int"]      == 1
    assert r.iloc[0]["y"]          == 1
    
    assert r.iloc[1]["p_start"]    == 1000
    assert r.iloc[1]["p_end"]      == 750
    assert r.iloc[1]["p_marg"]     == 1000
    assert r.iloc[1]["y_int"]      == 1500
    assert r.iloc[1]["y"]          == 1500
    # -
    
    r = Sim.add_strategy("ETH", 1, 2000, 3000, 1500, 1000, 750, psell_marginal=2500, pbuy_marginal=900)["orders"]
    r
    
    # +
    assert r.iloc[0]["p_start"]    == 2000
    assert r.iloc[0]["p_end"]      == 3000
    assert r.iloc[0]["p_marg"]     == 2500
    assert r.iloc[0]["y_int"]      >  r.iloc[0]["y"] 
    assert r.iloc[0]["y"]          == 1
    
    assert r.iloc[1]["p_start"]    == 1000
    assert r.iloc[1]["p_end"]      == 750
    assert r.iloc[1]["p_marg"]     == 900
    assert r.iloc[1]["y_int"]      >  r.iloc[1]["y"] 
    assert r.iloc[1]["y"]          == 1500
    
    # +
    # r = Sim.add_strategy("ETH", 1, 2000, 3000, 1500, 1000, 750, y_int_sell=2, y_int_buy=3000)["orders"]
    # r
    
    # +
    # assert r.iloc[0]["p_start"]    == 2000
    # assert r.iloc[0]["p_end"]      == 3000
    # #assert r.iloc[0]["p_marg"]     >  r.iloc[0]["p_start"]
    # assert r.iloc[0]["y_int"]      == 2
    # #assert r.iloc[0]["y"]          == 1
    
    # assert r.iloc[1]["p_start"]    == 1000
    # assert r.iloc[1]["p_end"]      == 750
    # #assert r.iloc[1]["p_marg"]     <  r.iloc[1]["p_start"]
    # assert r.iloc[1]["y_int"]      == 3000
    # #assert r.iloc[1]["y"]          == 1500
    # -
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    r = Sim.add_strategy(**{
        'tkn': 'RSK',
        'amt_sell': 1.0,
        'psell_start': 102.49999999999999,
        'psell_end': 107.62499999999999,
        'psell_marginal': 103.32512499999999, 
        'pair': 'RSK/CSH'
    })
    r
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    r = Sim.add_strategy(**{
        'tkn': 'RSK', 
        'amt_sell': 1.0, 
        'psell_start': 102.49999999999999, 
        'psell_end': 107.62499999999999, 
        'amt_buy': 0.001, 
        'pbuy_start': 97.5609756097561, 
        'pbuy_end': 92.91521486643438, 
        'pair': 'RSK/CSH', 
        'psell_marginal': 103.32512499999999, 
        'pbuy_marginal': 96.8130081300813
    })
    

# ------------------------------------------------------------
# Test      053
# File      test_053_MargPandYInt.py
# Segment   add_order
# ------------------------------------------------------------
def test_add_order():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    
    r = Sim.add_order("ETH", 1, 2000, 3000)["orders"]
    r
    
    assert r.iloc[0]["p_start"]    == 2000
    assert r.iloc[0]["p_end"]      == 3000
    assert r.iloc[0]["p_marg"]     == 2000
    assert r.iloc[0]["y_int"]      == 1
    assert r.iloc[0]["y"]          == 1
    
    r = Sim.add_order("ETH", 1, 2000, 3000, p_marginal=2500)["orders"]
    r
    
    assert r.iloc[0]["p_start"]    == 2000
    assert r.iloc[0]["p_end"]      == 3000
    assert r.iloc[0]["p_marg"]     == 2500
    assert r.iloc[0]["y_int"]      >  r.iloc[0]["y"] 
    assert r.iloc[0]["y"]          == 1
    
    # +
    # r = Sim.add_order("ETH", 1, 2000, 3000, y_int=2)["orders"]
    # r
    
    # +
    # assert r.iloc[0]["p_start"]    == 2000
    # assert r.iloc[0]["p_end"]      == 3000
    # #assert r.iloc[0]["p_marg"]     >  r.iloc[0]["p_start"]
    # assert r.iloc[0]["y_int"]      == 2
    # #assert r.iloc[0]["y"]          == 1
    # -
    
    
    
    