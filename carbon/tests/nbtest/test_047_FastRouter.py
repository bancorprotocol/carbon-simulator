# ------------------------------------------------------------
# Auto generated test file `test_047_FastRouter.py`
# ------------------------------------------------------------
# source file   = NBTest_047_FastRouter.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 047
# test comment  = FastRouter
# ------------------------------------------------------------



import pandas as pd
from decimal import Decimal
from io import StringIO

from carbon import CarbonSimulatorUI, __version__, __date__
print(f"Carbon Version v{__version__} ({__date__})", )





# ------------------------------------------------------------
# Test      047
# File      test_047_FastRouter.py
# Segment   FastRouterTests
# ------------------------------------------------------------
def test_fastroutertests():
# ------------------------------------------------------------
    
    # Initialize a fast simulator
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=True)
    FastSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method='fast', raiseonerror=True)
    
    # Here we restrain the orders to just the top ones such that we can test the exact algo alongside
    
    test_orders = pd.DataFrame.from_dict(
        {'id': {0: '0',
      1: '1',
      2: '2',
      3: '3',
      6: '6',
      10: '10',
      246: '246',
      247: '247',
      248: '248',
      250: '250',
      251: '251'},
     'liquidity': {0: '254814732',
      1: '253827078',
      2: '252839424',
      3: '251851770',
      6: '248888808',
      10: '244938192',
      246: '245925846',
      247: '246913500',
      248: '247901154',
      250: '249876462',
      251: '250864116'},
     'lowest_rate': {0: '256',
      1: '255',
      2: '254',
      3: '253',
      6: '250',
      10: '246',
      246: '247',
      247: '248',
      248: '249',
      250: '251',
      251: '252'},
     'highest_rate': {0: '257',
      1: '256',
      2: '255',
      3: '254',
      6: '251',
      10: '247',
      246: '248',
      247: '249',
      248: '250',
      250: '252',
      251: '253'},
     'current_rate': {0: '257',
      1: '256',
      2: '255',
      3: '254',
      6: '251',
      10: '247',
      246: '248',
      247: '249',
      248: '250',
      250: '252',
      251: '253'}}
    )
    
    # +
    for i in test_orders.index:
        Sim.add_strategy('USDC', Decimal(test_orders.liquidity[i]), Decimal(test_orders.highest_rate[i]), Decimal(test_orders.lowest_rate[i]),  None, None, None)
        FastSim.add_strategy('USDC', Decimal(test_orders.liquidity[i]), Decimal(test_orders.highest_rate[i]), Decimal(test_orders.lowest_rate[i]),  None, None, None)
    
    FastSim.state()['orders']
    # -
    
    FastSim.state()['orders']
    
    # ### Route by Source
    
    # #### AMM buys ETH
    
    # Lets do some simple checks against the exact algo and then verify against the fast router results
    #
    # 1. Trade an amount against exact
    
    results = Sim.amm_buys('ETH',10000000, execute=False)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='0']['amt1'].values[0]:.0f}" == "2519667817")
    results
    
    # We can observe the price is 251.996 USDC per ETH.
    #
    # For trade_by_source, when we increase the trade amount we push further down the curve which means that effective price should get worse.
    
    results = Sim.amm_buys('ETH',10500000, execute=False)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='1']['amt1'].values[0]:.0f}" == "2643009195")
    results
    
    # And indeed for the exact algo, the price gets lower (251.996 vs 251.715), i.e. for every unit of ETH spent I get less units of USDC in return
    
    # We can then do a similar thing for the fast router
    
    results = FastSim.amm_buys('ETH',10000000, execute=False)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='0']['amt1'].values[0]:.0f}" == "2519667817")
    results
    
    # We see that the orders are filled the same and the corresponding price is as we saw before.
    #
    # We can then trade the higher amount and again, expect to see the effectice rate decrease.
    
    results = FastSim.amm_buys('ETH',10500000, execute=False)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='1']['amt1'].values[0]:.0f}" == "2643009195")
    results
    
    # Again, we see that the price has, as before, decreased appropriately.
    
    # ### Route by Target
    
    # #### AMM sells USDC
    
    # We can now test the route by target.
    #
    # First we do the counter trade - selling the output amount of USDC from the initial ETH trade
    
    results = Sim.amm_sells('USDC',2519667817, execute=False)['trades']  # route_trade_by_target
    assert(f"{results[results.uid=='2']['amt2'].values[0]:.0f}" == "10000000")
    results
    
    # And we see that the return amount is 10000000 we saw before - but importantly so is the price
    #
    # Now we expect that if we take less off the curve then the rate gets better
    
    results = Sim.amm_sells('USDC',1500000000, execute=False)['trades']  # route_trade_by_target
    assert(f"{results[results.uid=='3']['amt2'].values[0]:.0f}" == "5904869")
    results
    
    # Indeed we see that the price is better for a smaller amount is less (254.027 vs 251.996)
    
    # Now we do the same for the Fast router. Trade in the previous output amount
    
    results = FastSim.amm_sells('USDC',2519667817, execute=False)['trades']  # route_trade_by_target
    assert(f"{results[results.uid=='2']['amt2'].values[0]:.0f}" == "10000000")
    results
    
    # And importantly we see the same price to the exact algo
    
    # The test now is to see the price get better as the request amount is lowered
    
    results = FastSim.amm_sells('USDC',1500000000, execute=False)['trades']  # route_trade_by_target
    assert(f"{results[results.uid=='3']['amt2'].values[0]:.0f}" == "5904869")
    results
    
    # And indeed the rate gets better