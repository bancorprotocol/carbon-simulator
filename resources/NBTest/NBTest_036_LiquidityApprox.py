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
from math import sqrt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

# # Carbon Simulation - Test 36 - Liquidity Approximation

# NBTEST: NOTEST_DEFAULT = TEST

Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
Sim

Sim.add_order("ETH", 10, 2000, 3000)
Sim.add_order("ETH", 10, 2500, 2500)
Sim.add_order("USDC", 10*1250, 1500, 1000)
Sim.add_order("USDC", 10*1250, 1250, 1250)
Sim

Sim.state()["orders"]

Sim.state().keys()

Sim.state()["orderuis"]

help(Sim.state()["orderuis"][0].liquidity_approx)

# ## Order 0 ETH range

oui = Sim.state()["orderuis"][0]
assert (oui.pmin, oui.pmax, oui.total_liquidity) == (2000.0, 3000.0, (10.0, 'ETH'))
oui.pmin, oui.pmax, oui.total_liquidity

r = oui.liquidity_approx(500, 600, "ETH", asperc=True)
assert r == 0
r

r = oui.liquidity_approx(3000, 3020, "ETH", asperc=True)
assert r == 0
r

r = oui.liquidity_approx(2000, 3000, "ETH", asperc=True)
assert r == 1.
r

r = oui.liquidity_approx(3000, 2000, "ETH", asperc=True)
assert r == 1
r

r = oui.liquidity_approx(2000, 2500, "ETH", asperc=True)
assert r == 0.5
r

r = oui.liquidity_approx(2500, 3000, "ETH", asperc=True)
assert r == 0.5
r

r = oui.liquidity_approx(2250, 2750, "ETH", asperc=True)
assert r == 0.5
r


r = oui.liquidity_approx(2000, 3000, "ETH", asperc=False)
assert r == 10.
r

r = oui.liquidity_approx(2000, 2500, "ETH", asperc=False)
assert r == 5.
r

r = oui.liquidity_approx(2000, 2500, asperc=False)
assert r == 5.
r

r = oui.liquidity_approx(2000, 3000, "USDC", asperc=False)
assert int(r) == int(10*sqrt(2000*3000))
r, sqrt(2000*3000)

r = oui.liquidity_approx(2250, 2750, "USDC", asperc=False)
assert int(r) == int(10*sqrt(2250*2750)*0.5)
r, sqrt(2250*2750)*0.5

# ## Order 1 ETH point

oui = Sim.state()["orderuis"][2]
oui.pmin, oui.pmax, oui.total_liquidity

r = oui.liquidity_approx(2000, 2499, "ETH", asperc=True)
assert r == 0
r

r = oui.liquidity_approx(2501, 3020, "ETH", asperc=True)
assert r == 0
r

r = oui.liquidity_approx(2499, 2501, "ETH", asperc=True)
assert r == 1
r

r = oui.liquidity_approx(2500, 2501, "ETH", asperc=True)
assert r == 1
r

r = oui.liquidity_approx(2499, 2500, "ETH", asperc=True)
assert r == 0
r

r = oui.liquidity_approx(2500, 2500, "ETH", asperc=True)
assert r == 1
r


r = oui.liquidity_approx(2499, 2501, "ETH", asperc=False)
assert r == 10
r

r = oui.liquidity_approx(2499, 2501, "USDC", asperc=False)
assert r == 25000
r

r = oui.liquidity_approx(2500, 2501, "USDC", asperc=False)
assert r == 25000
r

r = oui.liquidity_approx(2500, 2500, "USDC", asperc=False)
assert r == 25000
r

r = oui.liquidity_approx(2000, 3000, "USDC", asperc=False)
assert r == 25000
r

# ## Order 2 USDC range

oui = Sim.state()["orderuis"][4]
oui.pmin, oui.pmax, oui.total_liquidity

r = oui.liquidity_approx(500, 600, "USDC", asperc=False)
assert r == 0
r

r = oui.liquidity_approx(1600, 2000, "USDC", asperc=False)
assert r == 0
r

r = oui.liquidity_approx(1000, 1500, "USDC", asperc=False)
assert r == 12500
r

r = oui.liquidity_approx(1000, 1100, "USDC", asperc=False)
assert r == 2500
r

r = oui.liquidity_approx(1400, 1500, "USDC", asperc=False)
assert r == 2500
r

r = oui.liquidity_approx(1000, 1100, "ETH", asperc=False)
assert r == 2500/sqrt(1000*1100)
r, 2500/sqrt(1000*1100)

r = oui.liquidity_approx(1400, 1500, "ETH", asperc=False)
assert int(r) == int(2500/sqrt(1400*1500))
r, 2500/sqrt(1400*1500)

# ## Order 3 USDC point

oui = Sim.state()["orderuis"][6]
oui.pmin, oui.pmax, oui.total_liquidity

r = oui.liquidity_approx(1249, 1251, "USDC", asperc=False)
assert r == 12500
r

r = oui.liquidity_approx(1000, 2000, "USDC", asperc=False)
assert r == 12500
r

r = oui.liquidity_approx(1249, 1250, "USDC", asperc=False)
assert r == 0
r

r = oui.liquidity_approx(1250, 1251, "USDC", asperc=False)
assert r == 12500
r

r = oui.liquidity_approx(1249, 1251, "ETH", asperc=False)
assert r == 10
r

r = oui.liquidity_approx(1000, 2000, "ETH", asperc=False)
assert r == 10
r

r = oui.liquidity_approx(1249, 1250, "ETH", asperc=False)
assert r == 0
r

r = oui.liquidity_approx(1250, 1251, "ETH", asperc=False)
assert r == 10
r


