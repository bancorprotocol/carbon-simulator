# ------------------------------------------------------------
# Auto generated test file `test_048_PartialFullfilment.py`
# ------------------------------------------------------------
# source file   = NBTest_048_PartialFullfilment.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 048
# test comment  = PartialFullfilment
# ------------------------------------------------------------



import pandas as pd
from decimal import Decimal

from carbon import CarbonSimulatorUI, __version__, __date__
print(f"Carbon Version v{__version__} ({__date__})", )


#


# ------------------------------------------------------------
# Test      048
# File      test_048_PartialFullfilment.py
# Segment   Init
# ------------------------------------------------------------
def test_init():
# ------------------------------------------------------------
    
    # Initialize a fast simulator
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=True)
    
    Sim.add_strategy("ETH", 10, 2000, 2000, 10000, 1000, 1000)
    Sim.add_strategy("ETH", 10, 2010, 2010, 10000, 1010, 1010)
    Sim.add_strategy("ETH", 10, 2020, 2020, 10000, 1020, 1020)
    Sim.add_strategy("ETH", 10, 2030, 2030, 10000, 1030, 1030)
    Sim.add_strategy("ETH", 10, 2040, 2040, 10000, 1040, 1040)
    Sim.state()["orders"]
    
    # ### Route by Source
    
    # #### AMM buys ETH
    
    # Start with an acceptable amount and support_partial set to False
    
    results = Sim.amm_buys('ETH',10, execute=False, support_partial=False)['trades']  # route_trade_by_source
    results
    
    # Then try an unacceptable amount with support_partial still set to False
    #
    # Should FAIL
    
    try:
        results = Sim.amm_buys('ETH',1000000, execute=False, support_partial=False)['trades']  # route_trade_by_source
    except AssertionError as e:
        print('Should FAIL with insufficient liquidity...')
        assert(True)
        print(e)
    
    # Then set support_partial = True and pass an acceptable amount
    
    results = Sim.amm_buys('ETH',10, execute=False, support_partial=True)['trades']  # route_trade_by_source
    results
    
    # Then set support_partial = True and pass an unacceptable amount
    #
    # Should NOT FAIL
    
    results = Sim.amm_buys('ETH',10000000, execute=False, support_partial=True)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='2']['amt1'].values[0]:.0f}" == "50000")
    results
    
    # Now test the other combinations
    
    # #### AMM buys USDC
    
    try:
        results = Sim.amm_buys('USDC',1000000, execute=False, support_partial=False)['trades']  # route_trade_by_source
    except AssertionError as e:
        print('Should FAIL with insufficient liquidity...')
        assert(True)
        print(e)
    
    results = Sim.amm_buys('USDC',10000000, execute=False, support_partial=True)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='3']['amt1'].values[0]:.0f}" == "50")
    results
    
    # ### Route by Target
    
    # #### AMM sells ETH
    
    try:
        results = Sim.amm_sells('ETH',1000000, execute=False, support_partial=False)['trades']  # route_trade_by_source
    except AssertionError as e:
        print('Should FAIL with insufficient liquidity...')
        assert(True)
        print(e)
    
    results = Sim.amm_sells('ETH',10000000, execute=False, support_partial=True)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='4']['amt1'].values[0]:.0f}" == "50")
    results
    
    # #### AMM sells USDC
    
    try:
        results = Sim.amm_sells('USDC',1000000, execute=False, support_partial=False)['trades']  # route_trade_by_source
    except AssertionError as e:
        print('Should FAIL with insufficient liquidity...')
        assert(True)
        print(e)
    
    results = Sim.amm_sells('USDC',10000000, execute=False, support_partial=True)['trades']  # route_trade_by_source
    assert(f"{results[results.uid=='5']['amt1'].values[0]:.0f}" == "50000")
    results