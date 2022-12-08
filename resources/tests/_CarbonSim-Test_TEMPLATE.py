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

# # Carbon Simulation - Test TEMPLATE - TOPIC

Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
Sim















r = Sim.add_strategy("ETH", 10, 2000, 3000, 1000, 1000, 750)
r = Sim.add_strategy("ETH", 11, 2010, 3010, 1010, 1010, 760)
r["orders"]

r = Sim.state()["orders"]
assert len(r) == 4
r

r = Sim.state()["orders"].query("tkn=='ETH'")
assert len(r) == 2
r

r = Sim.amm_sells("ETH", 10, execute=False)["trades"]
assert len(r) == 3
r

r = Sim.amm_buys("ETH", 1, execute=False)["trades"].query("aggr==True")
assert len(r) == 1
r


