# %%
import pandas as pd
from decimal import Decimal
from carbon import CarbonSimulatorUI, __version__, __date__

threshold_orders = 10

match_by_src = True
amount = 5              # full_fill
# amount = 8            # partial_fill

# match_by_src = False
# amount = 2700         # full_fill
# amount = 2800         # partial_fill

numOfOrders = 32 

input_orders = []

for id in range(numOfOrders):
    y = 10 * (id + 1)
    p_low = 10 * (id + 1)
    p_high = 25 * (id + 1)
    p_marginal = p_high
    input_orders += [(y, p_high, p_low, p_marginal)]

test_orders = pd.DataFrame(input_orders, columns= ['y', 'p_high', 'p_low', 'p_marginal'])

Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method='alpha', raiseonerror=True)
FastSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method='fast', raiseonerror=True)

for i in test_orders.index:
    Sim.add_strategy('USDC', Decimal(str(test_orders.y[i])), Decimal(str(test_orders.p_high[i])), Decimal(str(test_orders.p_low[i])), pbuy_marginal=Decimal(str(test_orders.p_marginal[i])))
    FastSim.add_strategy('USDC', Decimal(str(test_orders.y[i])), Decimal(str(test_orders.p_high[i])), Decimal(str(test_orders.p_low[i])), pbuy_marginal=Decimal(str(test_orders.p_marginal[i])))

if match_by_src:
    # match_by_src
    Exact_results = Sim.amm_buys('ETH', amount, execute=False, threshold_orders=threshold_orders, support_partial=True)['trades']  # route_trade_by_source
    Fast_results = FastSim.amm_buys('ETH', amount, execute=False, threshold_orders=threshold_orders, support_partial=True)['trades']  # route_trade_by_source

    Exact_total_output = Exact_results.query("subid=='A'")['amt1'][0]
    Exact_total_actions = len(Exact_results.query("subid!='A'"))

    Fast_total_output = Fast_results.query("subid=='A'")['amt1'][0]
    Fast_total_actions = len(Fast_results.query("subid!='A'"))

    Fast_results_Truncated = Fast_results.query("subid!='A'")[:Exact_total_actions].copy()
    FastT_total_output = Fast_results_Truncated['amt1'].sum()
    FastT_total_actions = len(Fast_results_Truncated.query("subid!='A'"))

else: 
    # match_by_target
    Exact_results = Sim.amm_sells('USDC', amount, execute=False, threshold_orders=threshold_orders, support_partial=True)['trades']  # route_trade_by_target
    Fast_results = FastSim.amm_sells('USDC', amount, execute=False, threshold_orders=threshold_orders, support_partial=True)['trades']  # route_trade_by_target

    Exact_total_output = Exact_results.query("subid=='A'")['amt2'][0]
    Exact_total_actions = len(Exact_results.query("subid!='A'"))

    Fast_total_output = Fast_results.query("subid=='A'")['amt2'][0]
    Fast_total_actions = len(Fast_results.query("subid!='A'"))

    Fast_results_Truncated = Fast_results.query("subid!='A'")[:Exact_total_actions].copy()
    FastT_total_output = Fast_results_Truncated['amt2'].sum()
    FastT_total_actions = len(Fast_results_Truncated.query("subid!='A'"))

print("Exact:", Exact_total_output, f"({Exact_total_actions} actions)")
print("Fast :", Fast_total_output, f"({Fast_total_actions} actions)")
print("FastT:", FastT_total_output, f"({FastT_total_actions} actions)")  # T for truncated



