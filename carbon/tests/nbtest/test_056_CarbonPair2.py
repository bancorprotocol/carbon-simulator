# ------------------------------------------------------------
# Auto generated test file `test_056_CarbonPair2.py`
# ------------------------------------------------------------
# source file   = NBTest_056_CarbonPair2.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 056
# test comment  = CarbonPair2
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, CarbonPair, __version__, __date__
from carbon.helpers import SharedVar, print_version
from math import floor, ceil, trunc
print("{0.__name__} {0.__VERSION__} ({0.__DATE__})".format(CarbonPair))
print_version(require="2.3.2")




# ------------------------------------------------------------
# Test      056
# File      test_056_CarbonPair2.py
# Segment   Ensure capitalisation
# ------------------------------------------------------------
def test_ensure_capitalisation():
# ------------------------------------------------------------
    
    assert CarbonPair("usd/eth").tknb == "USD"
    assert CarbonPair("usd/eth").tknq == "ETH"
    assert CarbonPair("usd/eth").slashpair == "USD/ETH"
    assert CarbonPair("bnBNT/eth").tknb == "BNBNT"
    
    assert CarbonPair(tknb="usd", tknq="eth").tknb == "USD"
    assert CarbonPair(tknb="usd", tknq="eth").tknq == "ETH"
    assert CarbonPair(tknb="usd", tknq="eth").slashpair == "USD/ETH"
    assert CarbonPair(tknb="bnBNT", tknq="eth").tknb == "BNBNT"
    

# ------------------------------------------------------------
# Test      056
# File      test_056_CarbonPair2.py
# Segment   Ensure originals are preserved
# ------------------------------------------------------------
def test_ensure_originals_are_preserved():
# ------------------------------------------------------------
    
    assert CarbonPair("usd/eth").tknb_o == "usd"
    assert CarbonPair("usd/eth").tknq_o == "eth"
    assert CarbonPair("usd/eth").slashpair_o == "usd/eth"
    assert CarbonPair("bnBNT/eth").tknb_o == "bnBNT"
    assert CarbonPair("bnBNT/eth").slashpair_o == "bnBNT/eth"
    
    assert CarbonPair(tknb="usd", tknq="eth").tknb_o == "usd"
    assert CarbonPair(tknb="usd", tknq="eth").tknq_o == "eth"
    assert CarbonPair(tknb="usd", tknq="eth").slashpair_o == "usd/eth"
    assert CarbonPair(tknb="bnBNT", tknq="eth").tknb_o == "bnBNT"
    assert CarbonPair(tknb="bnBNT", tknq="eth").slashpair_o == "bnBNT/eth"
    

# ------------------------------------------------------------
# Test      056
# File      test_056_CarbonPair2.py
# Segment   Ensure display values are correct
# ------------------------------------------------------------
def test_ensure_display_values_are_correct():
# ------------------------------------------------------------
    
    # ### display_orig = Default
    
    assert CarbonPair("usd/eth").tknb_d == "USD"
    assert CarbonPair("usd/eth").tknq_d == "ETH"
    assert CarbonPair("usd/eth").slashpair_d == "USD/ETH"
    assert CarbonPair("bnBNT/eth").tknb_d == "BNBNT"
    
    assert CarbonPair(tknb="usd", tknq="eth").tknb_d == "USD"
    assert CarbonPair(tknb="usd", tknq="eth").tknq_d == "ETH"
    assert CarbonPair(tknb="usd", tknq="eth").slashpair_d == "USD/ETH"
    assert CarbonPair(tknb="bnBNT", tknq="eth").tknb_d == "BNBNT"
    
    
    # ### display_orig = False
    
    assert CarbonPair("usd/eth", display_orig=False).tknb_d == "USD"
    assert CarbonPair("usd/eth", display_orig=False).tknq_d == "ETH"
    assert CarbonPair("usd/eth", display_orig=False).slashpair_d == "USD/ETH"
    assert CarbonPair("bnBNT/eth", display_orig=False).tknb_d == "BNBNT"
    
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).tknb_d == "USD"
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).tknq_d == "ETH"
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).slashpair_d == "USD/ETH"
    assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=False).tknb_d == "BNBNT"
    
    
    # ### display_orig = True
    
    assert CarbonPair("usd/eth", display_orig=True).tknb_d == "usd"
    assert CarbonPair("usd/eth", display_orig=True).tknq_d == "eth"
    assert CarbonPair("usd/eth", display_orig=True).slashpair_d == "usd/eth"
    assert CarbonPair("bnBNT/eth", display_orig=True).tknb_d == "bnBNT"
    assert CarbonPair("bnBNT/eth", display_orig=True).slashpair_d == "bnBNT/eth"
    
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).tknb_d == "usd"
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).tknq_d == "eth"
    assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).slashpair_d == "usd/eth"
    assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=True).tknb_d == "bnBNT"
    assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=True).slashpair_d == "bnBNT/eth"
    
    