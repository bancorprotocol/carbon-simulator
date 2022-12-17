# -*- coding: utf-8 -*-
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

from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

# # Carbon Simulation - Test 37 - Match

# NBTEST: NOTEST_DEFAULT = TEST

# ## Match

# ### Set up the routers and check that the matching method has been properly accepted

# First we set up a number of simulators that use the different matching methods

Sim = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC")
assert(Sim._mm==CarbonSimulatorUI.MATCH_EXACT)
Sim

SimE = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_EXACT)
assert(SimE._mm==CarbonSimulatorUI.MATCH_EXACT)
SimE

SimA = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_ALPHA)
assert(SimA._mm==CarbonSimulatorUI.MATCH_ALPHA)
SimA

#SimF = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_FAST)
SimF = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC")
#assert(SimA._mm==CarbonSimulatorUI.MATCH_FAST)
SimF

SIMS = [Sim, SimE, SimA, SimF]

# ### Set up the orders and make sure they have been accepted

# We now set up a number of orders that each of the sims will get

ORDERS = [
    ("ETH", 1, 2000+10*i, 3000)
    for i in range(20)   
]
ORDERS[:2]

for sim in SIMS:
    for o in ORDERS:
        sim.add_order(*o)
    print(sim, len(sim.state()["orders"]), len(ORDERS))
    assert(len(sim.state()["orders"])==2*len(ORDERS))

# ### Run the trades and look at the routing

# Now look at a trade of 1 ETH 

Sim.amm_sells("ETH", 1, execute=False)["trades"]

SimA.amm_sells("ETH", 1, execute=False)["trades"]


