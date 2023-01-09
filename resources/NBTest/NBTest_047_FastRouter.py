# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3.10.8 64-bit
#     language: python
#     name: python3
# ---

# +
import pandas as pd
from decimal import Decimal

from carbon import CarbonSimulatorUI, __version__, __date__
print(f"Carbon Version v{__version__} ({__date__})", )
# -

# # FastRouter (NBTest 47)

# NBTEST: NOTEST_DEFAULT = TEST

# ## FastRouterTests

# Initialize a fast simulator

Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=True)
FastSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method='fast', raiseonerror=True)

# Here we restrain the orders to just the top ones such that we can test the exact algo alongside

test_orders = pd.read_csv('orders.csv', dtype=str)
test_orders = test_orders[test_orders.id.isin(['0','1','2','3','251','250','6','248','247','246','10'])].copy()
test_orders

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
