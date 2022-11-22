# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from carbon import CarbonSimulatorUI, __version__, __date__
from collections import namedtuple
print("[carbon] version", __version__, __date__)

# # Prices and Slippage

# ## Introduction and definitions
#
# This workbook serves to define certain quantities, and explains how to exactly compute them. As context, we are operating within an AMM framework where $x,y$ are the respective token balances. Depending on the price convention of the pair, prices are either expressed in $x/y$ or in $y/x$. We here assume the latter. For the opposite convention, $x,y$ need to be reversed in _all_ formulas below.
#
# - **Effective Price**. The _effective price_ is the overall price obtained by a specific trade of a specific size. Specifically, $P_{eff}(\Delta y) = - \Delta x / \Delta y$. Note that prices are always positive but we assume that outflows (from the AMM point of view) have a negative sign, inflows a positive one.
#
# - **Marginal Price** or **Current Price**. The _marginal price_ aka _current price_ is the effective price for a very small trade; formally we define that the marginal / current price is given as $P_{marg}^\pm = P_{curr}^\pm = P_{eff}(\Delta x^\pm \rightarrow 0^\pm)$; the $\pm$ sign (that we will omit below) reminds us that the marginal price will be different on the bid and on the ask side.
#
# - **Price Impact**. We define* the _price impact_ as the difference (or percentace change) of the marginal prices before or after that trade; formally we define it as $P_{imp}^\pm = P_{marg;post}^\pm - P_{marg;pre}^\pm$ and $P_{imp;\%}^\pm = (P_{marg;post}^\pm - P_{marg;pre})^\pm/P_{marg;pre}^\pm$
#
# - **Slippage**. We define* _slippage_ as the difference between the marginal and the effective price of a trade of a specific size, again either as number or as percentage; specifically, $P_{slip}^\pm(\Delta x) = P_{eff}^\pm(\Delta x) - P_{marg}^\pm$ and $P_{slip\%}^\pm = (P_{eff}^\pm(\Delta x) - P_{marg})^\pm/P_{marg}^\pm$

# ## Calculations

# ### Setup

Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETHEURC")
Sim

# Add the **ask** positions (AMM sells ETH)

Sim.add_order("ETH", 10, 2000, 2200)
Sim.add_order("ETH", 10, 2005, 2010)
Sim.add_order("ETH", 20, 2000, 2050)
Sim.add_order("ETH", 30, 2020, 2080)
Sim.add_order("ETH", 40, 2030, 2130)
Sim

# Add the **bid** positions (AMM buys ETH)

Sim.add_order("EURC", 10000, 1000, 800)
Sim.add_order("EURC", 10000, 995, 990)
Sim.add_order("EURC", 20000, 995, 850)
Sim.add_order("EURC", 30000, 950, 920)
Sim.add_order("EURC", 40000, 970, 870)
Sim

# This gives us the following order book

Sim.state()["orders"]

dxdy_nt = namedtuple("dxdy_nt", "dx,dy")

# ## Ranges
#
# We now look at the ranges for which we calculate prices. For this, we need a rough estimate for where the current USD price of that asset is. Then we use a range of powers of 10 where the USD value corresponding to the smallest power is between USD 1-10.

current_eth_usd_price = 1500
raw_ranges = ((10**i, i) for i in range(-20,20))
usd_range = ((current_eth_usd_price*x, i) for x,i in raw_ranges)
usd_range = [(x,i) for x,i in usd_range if x>1][0:6]
tkn_range = [10**i for _, i in usd_range]
usd_range, tkn_range

# ## Calculate the amounts

ask = lambda dx: Sim.amm_sells("ETH", dx, execute=False)["trades"].iloc[-1]
bid = lambda dx: Sim.amm_buys("ETH", dx, execute=False)["trades"].iloc[-1]
ask(1)

amounts_ask = [dxdy_nt(dx=dx, dy=ask(dx)["amt2"]) for dx in tkn_range]
amounts_ask

amounts_bid = [dxdy_nt(dx=dx, dy=bid(dx)["amt1"]) for dx in tkn_range]
amounts_bid

# ## Calculate effective prices
#
# Reminder: we calculate the prices for the amounts $10^n, 10^{n+1}, \ldots ETH$ such that $1 USD \leq 10^n ETH < 10 USD$

p_eff_ask = [r.dy/r.dx for r in amounts_ask]
p_eff_ask

p_eff_bid = [r.dy/r.dx for r in amounts_bid]
p_eff_bid

# ## Calculate slippage
#
# Reminder: `slip[n] = price[n] - price[0]` and `slip_pc[n] = (price[n] - price[0])/price[0]`.
#
# Note: take care of the sign adjustment for the bid side! For $x/y$ this adjustment is on the ask side instead.

slip_ask = [f"{p-p_eff_ask[0]:8.4f} USDC/ETH" for p in p_eff_ask]
slip_ask

slip_pc_ask = [f"{(p/p_eff_ask[0]-1)*100:0.4f}%" for p in p_eff_ask]
slip_pc_ask

slip_bid = [f"{-p+p_eff_bid[0]:8.4f} USDC/ETH" for p in p_eff_bid]
slip_bid

slip_pc_bid = [f"{-(p/p_eff_bid[0]-1)*100:0.4f}%" for p in p_eff_bid]
slip_pc_bid


