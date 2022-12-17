# ------------------------------------------------------------
# Auto generated test file `test_043_SglOrder.py`
# ------------------------------------------------------------
# source file   = NBTest_043_SglOrder.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 043
# test comment  = SglOrder
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))





# ------------------------------------------------------------
# Test      043
# File      test_043_SglOrder.py
# Segment   Single orders
# ------------------------------------------------------------
def test_single_orders():
# ------------------------------------------------------------
    
    # ### add_order as shortcut for add_strategy
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True, exclude_future=False)
    Sim
    
    # #### Base token (ETH)
    
    r = Sim.add_order("ETH", 10, 2000, 3000)["orders"]
    assert len(r) == 2
    r
    
    rr=r.query("tkn=='ETH'")
    assert rr.iloc[0]["y"] == 10
    assert rr.iloc[0]["disabled"] == False
    assert rr.iloc[0]["p_start"] == 2000
    ix = rr.iloc[0]["id"]
    lix = rr.iloc[0]["lid"]
    print(f"id={ix} lid={lix}")
    rr
    
    rr=r.query("tkn=='USDC'")
    assert rr.iloc[0]["y"] == 0
    assert not rr.iloc[0]["y"] is None
    assert rr.iloc[0]["disabled"] == True
    assert rr.iloc[0]["p_start"] is None
    ix2 = rr.iloc[0]["id"]
    lix2 = rr.iloc[0]["lid"]
    print(f"id={ix2} lid={lix2}")
    assert ix == lix2
    assert lix == ix2
    rr
    
    # #### Quote token (USDC)
    
    r = Sim.add_order("USDC", 1000, 1000, 750)["orders"]
    assert len(r) == 2
    r
    
    rr=r.query("tkn=='USDC'")
    assert rr.iloc[0]["y"] == 1000
    assert rr.iloc[0]["disabled"] == False
    assert rr.iloc[0]["p_start"] == 1000
    rr
    
    rr=r.query("tkn=='ETH'")
    assert rr.iloc[0]["y"] == 0
    assert not rr.iloc[0]["y"] is None
    assert rr.iloc[0]["disabled"] == True
    assert rr.iloc[0]["p_start"] is None
    rr
    
    # ### _add_replace_single_order
    #
    # this is a private function that allows to place single orders; this is an advanced feature and the API may change over time
    
    # #### Ensure it only works with future enabled
    
    try:
        SimNF = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
        SimNF._add_replace_single_order("ETH", 20, 2000, 3000)
    except CarbonSimulatorUI.ExcludedFutureFunctionality as e:
        print(e)
        assert str(e) == "Feature disabled (us `exclude_future = False` to enable)"
    
    # #### Generating new orders (use with care; money disappears)
    
    r = Sim._add_replace_single_order("ETH", 20, 2000, 3000)
    ro=r["orders"]
    print(f"id={r['id']}, lid={r['lid']}")
    assert ro.iloc[0]["id"] == r['id']
    assert ro.iloc[0]["lid"] == r['lid']
    ro
    
    r = Sim._add_replace_single_order("USDC", None, 1000, 750)
    ro=r["orders"]
    print(f"id={r['id']}, lid={r['lid']}")
    assert ro.iloc[0]["id"] == r['id']
    assert ro.iloc[0]["lid"] == r['lid']
    ro
    
    r = Sim._add_replace_single_order("ETH", 20, None, None)
    ro=r["orders"]
    print(f"id={r['id']}, lid={r['lid']}")
    assert ro.iloc[0]["id"] == r['id']
    assert ro.iloc[0]["lid"] == r['lid']
    ro
    
    r = Sim._add_replace_single_order("USDC")
    ro=r["orders"]
    print(f"id={r['id']}, lid={r['lid']}")
    assert ro.iloc[0]["id"] == r['id']
    assert ro.iloc[0]["lid"] == r['lid']
    ro
    
    r = Sim.state()["orders"]
    assert len(r) == 8
    r
    
    # #### Replacing existing orders
    # note: this completely replaces those orders; there are no checks whether the curve and token are the same
    
    
    r = Sim._add_replace_single_order("ETH", 21, 2010, 3010, oid=4, lid=5)
    ro=r["orders"]
    ro
    
    r = Sim._add_replace_single_order("USDC", 1100, 1001, 751, oid=5, lid=4)
    ro=r["orders"]
    ro
    
    r = Sim.state()["orders"]
    assert len(r) == 8
    r
    
    rr = r.query("id==5 or id==4")
    assert len(rr) == 2
    assert list(rr["id"]) == [4,5]
    assert list(rr["lid"]) == [5,4]
    rr
    
    # #### Generating a collection account
    # We here link multiple positions to a single USD account; **note that this is _not_ functionality that the MVP would allow**
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True, exclude_future=False)
    Sim
    
    # Setting up the collection account in USDC
    
    r = Sim._add_replace_single_order("USDC")
    coid = r["id"]
    print(f"Collection order id coid={coid}")
    r["orders"]
    
    # Setting up an account selling ETH for USDC
    
    r = Sim._add_replace_single_order("ETH", 10, 2000, 2000, lid=coid)
    r["orders"]
    
    # Setting up an account selling WBTC for USDC
    
    r = Sim._add_replace_single_order("WBTC", 1, 10000, 10000, pair="WBTC/USDC", lid=coid)
    r["orders"]
    
    # Setting up an account selling BNT for USDC
    
    r = Sim._add_replace_single_order("BNT", 100000, 2, 2, pair="BNT/USDC", lid=coid)
    r["orders"]
    
    r = Sim.state()["orders"]
    assert len(r) == 4
    assert list(r["lid"]) == [coid]*4
    assert len(set(r["id"])) == 4
    r
    
    Sim.amm_sells("ETH", 5)
    r=Sim.state()["trades"]
    r
    
    r=Sim.state()["orders"]
    r0=r.query(f"id=={coid}")
    assert int(r0["y"]) == 5*2000
    r
    
    Sim.amm_sells("WBTC", 0.5, pair="WBTC/USDC")
    Sim.amm_sells("BNT", 50000, pair="BNT/USDC")
    r=Sim.state()["trades"]
    r
    
    r=Sim.state()["orders"]
    r0=r.query(f"id=={coid}")
    print(int(r0["y"]), 5*2000 + 0.5 * 10000 + 50000*2)
    assert int(r0["y"]) == int(5*2000 + 0.5 * 10000 + 50000*2)
    r
    
    