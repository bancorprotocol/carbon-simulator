# ------------------------------------------------------------
# Auto generated test file `test_038_CarbonPair.py`
# ------------------------------------------------------------
# source file   = NBTest_038_CarbonPair.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 038
# test comment  = CarbonPair
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonPair, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))




#

# ------------------------------------------------------------
# Test      038
# File      test_038_CarbonPair.py
# Segment   CarbonPair
# ------------------------------------------------------------
def test_carbonpair():
# ------------------------------------------------------------
    #
    # Testing the new CarbonPair interface -- **BREAKING CHANGE**
    
    # +
    #help(CarbonPair)
    # -
    
    assert(P==CarbonPair)
    assert(str(P("ETH/USDC"))=="P('ETH/USDC')")
    
    str(P("ETH/USDC"))
    
    try:
        p = CarbonPair()
    except ValueError as e:
        print(e)
        assert(str(e)=="('If pair is None must provide tknb, tknq', None, None, None)")
    
    try:
        p = CarbonPair("ETH", "USDC")
    except ValueError as e:
        print(e)
        assert(str(e)=="""("Parameters are pair, tknb, tknq; did you mean `tknb='ETH', tknq='USDC'` ?", 'ETH', 'USDC', None)""")
    
    p = CarbonPair("", "ETH", "USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    p = CarbonPair(tknb="ETH", tknq="USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    p = CarbonPair(tknq="USDC", tknb="ETH")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    try:
        p = CarbonPair("ETHUSDC")
    except ValueError as e:
        print(e)
        assert(str(e)=="""('Illegal slashpair', 'ETHUSDC')""")
    
    p = CarbonPair("ETH/USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "ETH")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    try:
        p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "WBTC")
    except ValueError as e:
        print(e)
        assert(str(e) == "('Invalid token specification (tkn not part of isopair)', 'ETHUSDC', 'WBTC')")
    
    p = CarbonPair.create("ETH/USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    p = CarbonPair.create("ETH", "USDC")
    print(p)
    assert(str(p) == "P('ETH/USDC')")
    
    pp = CarbonPair.create(p)
    print(pp)
    assert(str(pp) == "P('ETH/USDC')")
    assert(pp is p)
    
    try:
        pp = CarbonPair.create(p, "ETH")
    except ValueError as e:
        print(e)
        assert(str(e) == "('Second argument must be None if arg1 is pair', P('ETH/USDC'), 'ETH')")
    
    assert(p.tknb=="ETH")
    assert(p.tknq=="USDC")
    assert(p.basetoken=="ETH")
    assert(p.quotetoken=="USDC")
    assert(p.slashpair=="ETH/USDC")
    assert(p.pair_slash=="ETH/USDC")
    assert(p.pair_iso=="ETHUSDC")
    assert(p.price_convention=="USDC per ETH")
    assert(str(p.reverse)=="P('USDC/ETH')")
    
    assert(p.has_token("ETH"))
    assert(p.has_token("USDC"))
    assert(not p.has_token("WBTC"))
    
    assert(not p.has_quotetoken("ETH"))
    assert(p.has_quotetoken("USDC"))
    assert(not p.has_quotetoken("WBTC"))
    
    assert(p.has_basetoken("ETH"))
    assert(not p.has_basetoken("USDC"))
    assert(not p.has_basetoken("WBTC"))
    
    assert(p.other("ETH")=="USDC")
    assert(p.other("USDC")=="ETH")
    assert(p.other("WBTC") is None)
    
    # Convert an ETH amount into a USDC amount with the price in the price convention of the pair
    
    p.convert(1, "ETH", "USDC", 2000)
    
    # ditto ETH -> ETH (trivial)
    
    p.convert(1, "ETH", "ETH", 2000)
    
    # ditto USDC -> ETH (inverse rate!)
    
    p.convert(2000, "USDC", "ETH", 2000)
    
    assert(p.convert(1, "ETH", "USDC", 2000) == 2000)
    assert(p.convert(1, "ETH", "ETH", 2000) == 1)
    assert(p.convert(2000, "USDC", "ETH", 2000) == 1)
    assert(p.convert(1, "USDC", "USDC", 2000) == 1)
    
    assert(p.convert_price(2000, "USDC")==2000)
    assert(p.convert_price(1/2000, "ETH")==2000)
    
    # +
    #help(p.limit_is_met)
    # -
    
    p.limit_is_met("ETH", 2000, p.BUY, 1000, asphrase=True)
    
    p.limit_is_met("ETH", 2000, p.SELL, 1000, asphrase=True)
    
    p.limit_is_met("USDC", 2000, p.BUY, 1000, asphrase=True)
    
    p.limit_is_met("USDC", 2000, p.SELL, 1000, asphrase=True)
    
    assert(p.limit_is_met("ETH", 2000, p.BUY, 1000))
    assert(not p.limit_is_met("ETH", 2000, p.SELL, 1000))
    assert(not p.limit_is_met("USDC", 2000, p.BUY, 1000))
    assert(p.limit_is_met("USDC", 2000, p.SELL, 1000))
    
    
    