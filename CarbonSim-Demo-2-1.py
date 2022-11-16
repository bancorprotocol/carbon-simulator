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

from carbon import CarbonSimulatorUI

# # Carbon Simulation - Demo 2-1
#
# In this demo we look at **single-curve bidirectional liquidity ("strategies") with a zero width range**

# Set up the similation, with the pair USDCETH as default

Sim = CarbonSimulatorUI(pair="ETHUSDC", verbose=False, raiseonerror=False)
Sim

help(Sim.add_strategy)

# We assert that we can not add an unrelated position to this pair, either using an existing token like LINK, or a token like DNE (does not exist).

Sim.add_strategy("LINK", 10, 2000, 2000, 0, 1000, 1000)

Sim.add_strategy("DNE", 10, 2000, 2000, 0, 1000, 1000)

# We set up a single curve where the AMM sells ETH against USDC at 2000, and buys it back at 1000. Note the `linked_to_id` flag that links those two curves; more specifically, it implies that the tokens bought on one curve are available for sale on the other.

Sim.add_strategy("ETH", 100, 2000, 2000, 0, 1000, 1000)["orders"]

# We are trying to make the AMM buy ETH. That fails because it does not have any USD.

Sim.amm_buys("ETH", 10)

# Now we are trying to make the AMM sell more ETH than it has. That also fails.

Sim.amm_sells("ETH", 101)

# ## First cycle, part A: sell ETH

# Let's look at the order book first: we have 100 ETH for sale at 2000, and we buy ETH at 1000, but currently have no USDC to sell

Sim.state()["orders"]

# So as we've seen above, we can't buy ETH. Not even a tiny little bit.

Sim.amm_buys("ETH", 0.00001)

# However, the AMM can sell say 10 ETH, at a price of 2000.

Sim.amm_sells("ETH", 10)["trades"]

# Note that the 10 ETH that were sold against 20000 USDC now show up on the USDC curve where `y=20,000`. Also note that `y_int=20,000`, after we previously had `y_int=0`. This means the curve has been expanded to make space for the USDC received.

Sim.state()["orders"]

# We've sold 10 above, so can we sell 90+epsilon? Obviously not

Sim.amm_sells("ETH", 90.0000001)

# However, it can sell 90

Sim.amm_sells("ETH", 90)["trades"]

# Now the ETH curve is empty (`y=0`), but the USDC curve is loaded with `y=200,000` USDC (100*2000), so we went cycle down.

Sim.state()["orders"]

Sim.state()["trades"]

# Can it now sell epsilon? No, obviously not. And neither can it sell zero

Sim.amm_sells("ETH", 0.0000001)

Sim.amm_sells("ETH", 0)

# ## First cycle, part B: sell USDC

# Reminder, the current state of the system is 0 ETH and 200,000 USDC

Sim.state()["orders"]

# As we have just seen, there is no ETH left to sell

Sim.amm_sells("ETH", 0.0000001)

# But of course we can sell USDC. Let's sell the whole bunch. Note that we sell it at a price of 1,000 USDC per ETH (because this is where the curve is)

Sim.amm_sells("USDC", 200000)["trades"]

Sim.state()["orders"]


