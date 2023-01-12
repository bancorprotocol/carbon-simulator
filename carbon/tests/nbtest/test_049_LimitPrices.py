# ------------------------------------------------------------
# Auto generated test file `test_049_LimitPrices.py`
# ------------------------------------------------------------
# source file   = NBTest_049_LimitPrices.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 049
# test comment  = LimitPrices
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))





# ------------------------------------------------------------
# Test      049
# File      test_049_LimitPrices.py
# Segment   Limit prices
# ------------------------------------------------------------
def test_limit_prices():
# ------------------------------------------------------------
    
    SimR = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
    SimNR = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=False)
    SimR, SimNR
    
    SimR.add_order("ETH", 10, 2000, 3000)
    SimNR.add_order("ETH", 10, 2000, 3000)
    SimR.add_order("USDC", 10000, 1000, 500)
    SimNR.add_order("USDC", 10000, 1000, 500)
    assert len(SimR.state()["orders"]) == 4
    assert len(SimNR.state()["orders"]) == 4
    
    help(SimR._trade)
    
    assert SimR.trader_buys == SimR.amm_sells
    assert SimR.trader_sells == SimR.amm_buys
    assert SimR.trader_buys != SimR.amm_buys
    assert SimR.trader_sells != SimR.amm_sells
    help(SimR.trader_buys)
    help(SimR.trader_sells)
    
    r = SimR.amm_sells("ETH", 1, execute=False)
    assert r["success"] == True
    r["trades"]
    
    # ### Check that you can't give both price and amount, both by amount and by target
    
    try:
        SimR.amm_sells("ETH", 1, limit_price=1000, limit_amt=1000)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    
    try:
        SimR.amm_buys("ETH", 1, limit_price=1000, limit_amt=1000)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    
    try:
        SimR.amm_sells("USDC", 1, limit_price=1000, limit_amt=1000)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    
    try:
        SimR.amm_buys("USDC", 1, limit_price=1000, limit_amt=1000)
        raise RuntimeError("should raise")
    except ValueError as e:
        print(e)
    
    
    assert SimNR.amm_sells("ETH", 1, limit_price=1000, limit_amt=1000)["success"] == False
    assert SimNR.amm_buys("ETH", 1, limit_price=1000, limit_amt=1000)["success"] == False
    assert SimNR.amm_sells("USDC", 1, limit_price=1000, limit_amt=1000)["success"] == False
    assert SimNR.amm_buys("USDC", 1, limit_price=1000, limit_amt=1000)["success"] == False
    
    # ### Check price limits
    
    r = SimR.trader_buys("ETH", 1, execute=False)
    price_buy_eth = r["trades"]["price"].iloc[0]
    assert int(price_buy_eth) == 2037
    
    r = SimR.trader_buys("USDC", 1000, execute=False)
    price_buy_usdc = r["trades"]["price"].iloc[0]
    assert int(price_buy_usdc) == 970
    
    r = SimR.trader_sells("ETH", 1, execute=False)
    price_sell_eth = r["trades"]["price"].iloc[0]
    assert int(price_sell_eth) == 971
    
    r = SimR.trader_sells("USDC", 1000, execute=False)
    price_sell_usdc = r["trades"]["price"].iloc[0]
    assert int(price_sell_usdc) == 2018
    
    print(f"buy  ETH   @ {price_buy_eth:10.0f} USDC/ETH")
    print(f"buy  USDC  @ {price_buy_usdc:10.0f} USDC/ETH")
    print(f"sell ETH   @ {price_sell_eth:10.0f} USDC/ETH")
    print(f"sell USDC  @ {price_sell_usdc:10.0f} USDC/ETH")
    
    limitfail = lambda  r: "fail" if r["trades"].query("aggr==True")["limitfail"].iloc[0] else "nofail"
    
    # worse than limit transactions
    
    fail_r = (
        limitfail(SimR.trader_buys("ETH", 1, limit_price = int(price_buy_eth) - 1, execute=False)),
        limitfail(SimR.trader_buys("USDC", 1000, limit_price = int(price_buy_usdc) + 1, execute=False)),
        limitfail(SimR.trader_sells("ETH", 1, limit_price = int(price_sell_eth) + 1, execute=False)),
        limitfail(SimR.trader_sells("USDC", 1000, limit_price = int(price_sell_usdc) - 1, execute=False)),
    )
    assert fail_r == ("fail",)*4
    fail_r
    
    # better than limit transactions
    
    fail_r = (
        limitfail(SimR.trader_buys("ETH", 1, limit_price = int(price_buy_eth) + 1, execute=False)),
        limitfail(SimR.trader_buys("USDC", 1000, limit_price = int(price_buy_usdc) - 1, execute=False)),
        limitfail(SimR.trader_sells("ETH", 1, limit_price = int(price_sell_eth) - 1, execute=False)),
        limitfail(SimR.trader_sells("USDC", 1000, limit_price = int(price_sell_usdc) + 1, execute=False)),
    )
    assert fail_r == ("nofail",)*4
    fail_r
    
    # ### Check amount limits
    
    # worse than limit transactions
    
    fail_r = (
        limitfail(SimR.trader_buys("ETH", 1, limit_amt = (int(price_buy_eth) - 1)*1, execute=False)),
        limitfail(SimR.trader_buys("USDC", 1000, limit_amt = 1000/(int(price_buy_usdc) + 1), execute=False)),
        limitfail(SimR.trader_sells("ETH", 1, limit_amt = (int(price_sell_eth) + 5)*1, execute=False)),
        limitfail(SimR.trader_sells("USDC", 1000, limit_amt = 1000/(int(price_sell_usdc) - 1), execute=False)),
    )
    assert fail_r == ("fail",)*4
    fail_r
    
    price_sell_usdc
    
    price_sell_usdc
    
    # better than limit transactions
    
    fail_r = (
        limitfail(SimR.trader_buys("ETH", 1, limit_amt = (int(price_buy_eth) + 1)*1, execute=False)),
        limitfail(SimR.trader_buys("USDC", 1000, limit_amt = 1000/(int(price_buy_usdc) - 1), execute=False)),
        limitfail(SimR.trader_sells("ETH", 1, limit_amt = (int(price_sell_eth) - 1)*1, execute=False)),
        limitfail(SimR.trader_sells("USDC", 1000, limit_amt = 1000/(int(price_sell_usdc) + 1), execute=False)),
    )
    assert fail_r == ("nofail",)*4
    fail_r
    
    
    # ### Check amount limits (ranges)
    
    # +
    def goalseek(f, target, xlo, xhi):
        if not f(xhi)>target and f(xlo)<target:
            raise ValueError("must have f(xhi) > target, f(xlo)<target ", f(xhi), f(xlo))
        return _goalseek(f, target, xlo, xhi)
        
    def _goalseek(f, target, xlo, xhi):
        xmid = 0.5*(xhi+xlo)
        #print(xlo, xhi, xmid)
        if abs(xhi-xlo)<1: return xmid
        if f(xmid) > target:
            return _goalseek(f, target, xlo, xmid)
        else:
            return _goalseek(f, target, xmid, xhi)
    limitfail_ind = lambda  r: 0 if r["trades"].query("aggr==True")["limitfail"].iloc[0] else 1
    # -
    
    x = goalseek(lambda x: limitfail_ind(SimR.trader_buys("ETH", 1, limit_amt=x, execute=False)), 0.5, 500, 3000)
    assert int(x) == int(price_buy_eth)
    
    x = goalseek(lambda x: limitfail_ind(SimR.trader_sells("ETH", 1, limit_amt=x, execute=False)), 0.5, 3000, 500)
    assert int(x) == int(price_sell_eth)
    
    