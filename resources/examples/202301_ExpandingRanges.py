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

# +
from carbon.helpers.stdimports import *

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
require_version("2.1")
# -


# # Expanding Ranges

# Set up a simulation with the following strategy
#
# - 10,000 USD to buy ETH at 1,500
# - Sell range set to 2,000-3,000 (initially empty and zero capacity)

Sim = CarbonSimulatorUI(pair="ETH/USDC")
r = Sim.add_strategy("USDC", 15000, 1500, 1500, 0, 2000, 3000)
r["orders"]

# Looking at the above we see that the SELL ETH curve has zero capacity. It will therefore be filled _across the range_ as we see in the trade below.
#
# We now sell 1500 USDC, netting us 1 ETH

r = Sim.amm_sells("USDC", 1500*5)
r["trades"].query("aggr == True")

Sim.state()["orders"]

# We see above that we now have 1 ETH on the curve; this 1 ETH. This ETH is evenly distruted over the curve (look at `price` in subsequent sells)

Sim.amm_sells("ETH", 1)["trades"].query("aggr == True")

Sim.amm_sells("ETH", 1)["trades"].query("aggr == True")

Sim.amm_sells("ETH", 1)["trades"].query("aggr == True")

Sim.amm_sells("ETH", 1)["trades"].query("aggr == True")

Sim.amm_sells("ETH", 1)["trades"].query("aggr == True")

# Note the ETH curve is now empty (marginal price = 3000 is at top end)

Sim.state()["orders"]

# Now we buy some more ETH (ie we sell USDC). Note the curve is now already expanded to 5ETH

Sim.amm_buys("ETH", 1)["trades"].query("aggr == True")

# We see that the marginal price moved down (to 2747)

Sim.state()["orders"]

# And the marginal price moves down again

Sim.amm_buys("ETH", 1)["trades"].query("aggr == True")
Sim.state()["orders"]
