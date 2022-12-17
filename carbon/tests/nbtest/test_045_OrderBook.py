# ------------------------------------------------------------
# Auto generated test file `test_045_OrderBook.py`
# ------------------------------------------------------------
# source file   = NBTest_045_OrderBook.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 045
# test comment  = OrderBook
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, P, analytics as al, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))




NUM_POINTS = 100   # number of points on the precise chart

ETHUSDC = P(tknq="USDC", tknb="ETH")
Sim = CarbonSimulatorUI(pair=ETHUSDC, verbose=False, raiseonerror=True)
orders = tuple([
    al.orders_nt("ETH", 100, 2000, 3000),
    al.orders_nt("ETH", 100, 2100, 2550),
    al.orders_nt("ETH", 50, 2300, 2450),
    al.orders_nt("ETH", 75, 2400, 2500),
    al.orders_nt("ETH", 80, 2500, 2700),
    al.orders_nt("USDC", 1000*150, 1500, 500),
    al.orders_nt("USDC", 1000*50, 1500, 1300),
    al.orders_nt("USDC", 1000*20, 1450, 1350),
    al.orders_nt("USDC", 1100*150, 1200, 1000),
])
for o in orders:
    Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)
Sim.add_order("WBTC", 1, 10000, 15000, pair="WBTC/USDC")
Sim.add_order("USDC", 1, 9000, 7500, pair="WBTC/USDC")
Sim.add_order("USDC", 10000, 0.99, 1.01, pair="USDC/USDT")
Sim.add_order("USDT", 10000, 1.01, 0.99, pair="USDC/USDT")
Sim.state()["orders"]

prices = al.linspace(500,3000, NUM_POINTS)
prices

curves_by_pair_bidask = CarbonOrderUI.curves_by_pair_bidask(Sim.state()["orderuis"])
print(list(curves_by_pair_bidask.keys()))


# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   curves_by_pair_bidask
# ------------------------------------------------------------
def test_curves_by_pair_bidask():
# ------------------------------------------------------------
    
    cbpba = curves_by_pair_bidask
    #cbpba["ETH/USDC"]
    
    print(list(cbpba.keys()))
    assert set(cbpba.keys()) == {'ETH/USDC', 'WBTC/USDC', 'USDC/USDT'}
    assert "ALL" in cbpba["WBTC/USDC"].keys()
    assert "BID" in cbpba["WBTC/USDC"].keys()
    assert "ASK" in cbpba["WBTC/USDC"].keys()
    assert len(cbpba["WBTC/USDC"]["ALL"])==len(cbpba["WBTC/USDC"]["BID"])+len(cbpba["WBTC/USDC"]["ASK"])
    assert len(cbpba["ETH/USDC"]["ALL"])==len(cbpba["ETH/USDC"]["BID"])+len(cbpba["ETH/USDC"]["ASK"])
    
    assert set(c.tkn for c in cbpba["ETH/USDC"]["ALL"]) == {'ETH', 'USDC'}
    assert set(c.tkn for c in cbpba["ETH/USDC"]["BID"]) == {'USDC'}
    assert set(c.tkn for c in cbpba["ETH/USDC"]["ASK"]) == {'ETH'}
    
    assert [int(c.p_marg) for c in cbpba["ETH/USDC"]["BID"] if not c.p_marg is None] == [1500, 1500, 1450, 1200]
    assert [int(c.p_marg) for c in cbpba["ETH/USDC"]["ASK"] if not c.p_marg is None] == [2000, 2100, 2300, 2399, 2500]
    

# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   CarbonOrderUI id and linked
# ------------------------------------------------------------
def test_carbonorderui_id_and_linked():
# ------------------------------------------------------------
    
    p1 = CarbonOrderUI.from_prices(ETHUSDC, "ETH", 2000, 3000, 10, 10)
    p2 = CarbonOrderUI.from_prices(ETHUSDC, "USDC", 1000, 750, 10, 10)
    p1,p2
    
    assert p1.id is None
    assert p1.linked is None
    
    p1.set_id(1)
    p2.set_id(2)
    assert p1.id == 1
    assert p2.id == 2
    
    p1.set_linked(p2)
    p2.set_linked(p1)
    assert p1.linked.id == 2
    assert p2.linked.id == 1
    
    p1.linked
    
    try:
        p1.set_id(1)
        raise RuntimeError("Should raise")
    except ValueError as e:
        print(e)
    
    try:
        p1.set_linked(p2)
        raise RuntimeError("Should raise")
    except ValueError as e:
        print(e)
    
    curves = curves_by_pair_bidask["ETH/USDC"]
    assert [c.id for c in curves["ALL"]] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    assert [c.id for c in curves["BID"]] == [1, 3, 5, 7, 9, 10, 12, 14, 16]
    assert [c.id for c in curves["ASK"]] == [0, 2, 4, 6, 8, 11, 13, 15, 17]
    
    assert [c.linked.id for c in curves["ALL"]] == [1, 0, 3, 2, 5, 4, 7, 6, 9, 8, 11, 10, 13, 12, 15, 14, 17, 16]
    assert [c.linked.id for c in curves["BID"]] == [c.id for c in curves["ASK"]]
    assert [c.linked.id for c in curves["ASK"]] == [c.id for c in curves["BID"]]
    

# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   Approximate liquidity [NOTEST]
# ------------------------------------------------------------
def notest_approximate_liquidity():
# ------------------------------------------------------------
    
    liq =  al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False)
    liqr = al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=True)
    
    al.plot_approx_orderbook_chart(liq)
    
    al.plot_approx_orderbook_chart(liqr)
    

# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   ASK _ AMM SELLS base token [NOTEST]
# ------------------------------------------------------------
def notest_ask___amm_sells_base_token():
# ------------------------------------------------------------
    
    curves = curves_by_pair_bidask["ETH/USDC"]["ASK"]
    c0 = curves[0]
    print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
    dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
    dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)
    dy_amounts = [dy_p(p) for p in prices]
    dx_amounts = [dx_p(p) for p in prices]
    
    plt.plot(prices, dy_amounts)
    plt.xlabel(f"market price [{c0.pair.price_convention}]")
    plt.ylabel(f"Cumulative amount of y sold [{c0.tkny}]")
    
    plt.plot(prices, dx_amounts)
    plt.xlabel(f"market price [{c0.pair.price_convention}]")
    plt.ylabel(f"Cumulative amount of x bought [{c0.tknx}]")
    
    OB = al.OrderBook(dy_amounts, dx_amounts, "ETH", "USDC")
    print(OB.explain())
    
    OB.plot_token_amount_chart()
    
    # When SELLING ETH, the AMM sells more and more expensively the more ETH it sells
    
    OB.plot_price_chart()
    
    # When SELLING ETH, the AMM pays more (in ETH terms) for the first units of USD received than for the later ones
    
    OB.plot_orderbook_chart()
    

# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   BID _ AMM BUYS base token [NOTEST]
# ------------------------------------------------------------
def notest_bid___amm_buys_base_token():
# ------------------------------------------------------------
    
    curves = curves_by_pair_bidask["ETH/USDC"]["BID"]
    c0 = curves[0]
    print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
    dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
    dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)
    dy_amounts = [dy_p(p) for p in prices]
    dx_amounts = [dx_p(p) for p in prices]
    
    OB2 = al.OrderBook(dx_amounts, dy_amounts, "ETH", "USDC", bidask=al.OrderBook.BID)
    print(OB2.explain())
    
    OB2.plot_token_amount_chart()
    
    OB2.plot_price_chart()
    
    OB2.plot_orderbook_chart()
    

# ------------------------------------------------------------
# Test      045
# File      test_045_OrderBook.py
# Segment   Combined [NOTEST]
# ------------------------------------------------------------
def notest_combined():
# ------------------------------------------------------------
    
    # Note: the liquidity is USDC liquidity, not ETH liquidity. This makes the numbers somewhat harder to verify. However -- this means that liquidity can be compared across different pairs that are using the same quote token.
    
    OB.plot_orderbook_chart(otherob=OB2)
    
    al.plot_approx_orderbook_chart(liqr)
    
    al.plot_approx_orderbook_chart(liq)
    
    