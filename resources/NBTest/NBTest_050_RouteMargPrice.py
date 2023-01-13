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

from carbon import CarbonSimulatorUI, CarbonOrderUI, P, __version__, __date__
from math import sqrt
import numpy as np
from matplotlib import pyplot as plt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

# # Carbon Simulation - Test 50 - Route marginal prices

# NBTEST: NOTEST_DEFAULT = TEST

# ## Route marginal prices

Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
for i in range(3):
    Sim.add_strategy("ETH", 1, 2000+i, 2100, 1000, 1000-i, 900)
Sim.state()["orders"]

r = Sim.amm_sells("ETH", 0.05, execute=False)
prc_r = r["trades"]["amt2"]/r["trades"]["amt1"]
assert prc_r.iloc[-1] == r["trades"].iloc[-1]["price"]
for i in range(len(prc_r)):
    print(prc_r.iloc[i], r["trades"].iloc[i]["price"])


r = Sim.amm_sells("USDC", 50, execute=False)
prc_r = r["trades"]["amt1"]/r["trades"]["amt2"]
assert prc_r.iloc[-1] == r["trades"].iloc[-1]["price"]
for i in range(len(prc_r)):
    print(prc_r.iloc[i], r["trades"].iloc[i]["price"])

# The below fails with assertion error; the goal of this branch is to make this work...

r = Sim.amm_sells("ETH", 0.05, execute=False)
prc_r = r["trades"]["amt2"]/r["trades"]["amt1"]
for i in range(len(prc_r)):
    assert prc_r.iloc[i] == r["trades"].iloc[i]["price"]

r = Sim.amm_sells("USDC", 50, execute=False)
prc_r = r["trades"]["amt1"]/r["trades"]["amt2"]
for i in range(len(prc_r)):
    assert prc_r.iloc[i] == r["trades"].iloc[i]["price"]


