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

from carbon import CarbonSimulatorUI, P, analytics as cal, __version__, __date__
from math import sqrt
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

# # Carbon Simulation - Test 36 - Liquidity Approximation 2

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

# ## Order 0 (ETH, range)

oui = Sim.state()["orderuis"][0]
oui.pmin, oui.pmax, oui.total_liquidity

oui.liquidity_approx(500, 600, "ETH", asperc=True)

oui.liquidity_approx(3000, 3020, "ETH", asperc=True)

oui.liquidity_approx(2000, 3000, "ETH", asperc=True)

oui.liquidity_approx(3000, 2000, "ETH", asperc=True)

oui.liquidity_approx(2000, 2500, "ETH", asperc=True)

oui.liquidity_approx(2500, 3000, "ETH", asperc=True)

oui.liquidity_approx(2250, 2750, "ETH", asperc=True)


oui.liquidity_approx(2000, 3000, "ETH", asperc=False)

oui.liquidity_approx(2000, 2500, "ETH", asperc=False)

oui.liquidity_approx(2000, 2500, asperc=False)

oui.liquidity_approx(2000, 3000, "USDC", asperc=False), sqrt(2000*3000)

oui.liquidity_approx(2250, 2750, "USDC", asperc=False), sqrt(2250*2750)*0.5



# ## Order 1 (ETH, point)

oui = Sim.state()["orderuis"][1]
oui.pmin, oui.pmax, oui.total_liquidity

oui.liquidity_approx(2000, 2499, "ETH", asperc=True)

oui.liquidity_approx(2501, 3020, "ETH", asperc=True)

oui.liquidity_approx(2499, 2501, "ETH", asperc=True)

oui.liquidity_approx(2500, 2501, "ETH", asperc=True)

oui.liquidity_approx(2499, 2500, "ETH", asperc=True)

oui.liquidity_approx(2500, 2500, "ETH", asperc=True)


oui.liquidity_approx(2499, 2501, "ETH", asperc=False)

oui.liquidity_approx(2499, 2501, "USDC", asperc=False)

oui.liquidity_approx(2500, 2501, "USDC", asperc=False)

oui.liquidity_approx(2500, 2500, "USDC", asperc=False)

oui.liquidity_approx(2000, 3000, "USDC", asperc=False)

# ## Order 2 (USDC, range)

oui = Sim.state()["orderuis"][2]
oui.pmin, oui.pmax, oui.total_liquidity

oui.liquidity_approx(500, 600, "USDC", asperc=False)

oui.liquidity_approx(1600, 2000, "USDC", asperc=False)

oui.liquidity_approx(1000, 1500, "USDC", asperc=False)

oui.liquidity_approx(1000, 1100, "USDC", asperc=False)

oui.liquidity_approx(1400, 1500, "USDC", asperc=False)

oui.liquidity_approx(1000, 1100, "ETH", asperc=False), 2500/sqrt(1000*1100)

oui.liquidity_approx(1400, 1500, "ETH", asperc=False), 2500/sqrt(1400*1500)

# ## Order 3 (USDC, point)

oui = Sim.state()["orderuis"][3]
oui.pmin, oui.pmax, oui.total_liquidity

oui.liquidity_approx(1249, 1251, "USDC", asperc=False)

oui.liquidity_approx(1000, 2000, "USDC", asperc=False)

oui.liquidity_approx(1249, 1250, "USDC", asperc=False)

oui.liquidity_approx(1250, 1251, "USDC", asperc=False)

oui.liquidity_approx(1249, 1251, "ETH", asperc=False)

oui.liquidity_approx(1000, 2000, "ETH", asperc=False)

oui.liquidity_approx(1249, 1250, "ETH", asperc=False)

oui.liquidity_approx(1250, 1251, "ETH", asperc=False)

# ## Not ignoring state
# ### ETH

Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
Sim.add_order("ETH", 10, 2000, 3000)
Sim.add_order("USDC", 10*1000, 1000, 500)
oui = Sim.state()["orderuis"][0]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(2000, 3000, "ETH", ignore_state=False),
    oui.liquidity_approx(2000, 2500, "ETH", ignore_state=False),
    oui.liquidity_approx(2500, 3000, "ETH", ignore_state=False),
)

Sim.amm_sells("ETH", 5)
Sim.state()["orders"].query("id==0")

oui = Sim.state()["orderuis"][0]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(2000, 3000, "ETH", ignore_state=False),
    oui.liquidity_approx(2000, 2500, "ETH", ignore_state=False),
    oui.liquidity_approx(2500, 3000, "ETH", ignore_state=False),
)

Sim.amm_sells("ETH", 2.5)
Sim.state()["orders"].query("id==0")

oui = Sim.state()["orderuis"][0]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(2000, 3000, "ETH", ignore_state=False),
    oui.liquidity_approx(2000, 2500, "ETH", ignore_state=False),
    oui.liquidity_approx(2500, 3000, "ETH", ignore_state=False),
)

# ### USDC

oui = Sim.state()["orderuis"][1]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(1000, 500, "USDC", ignore_state=False),
    oui.liquidity_approx(1000, 750, "USDC", ignore_state=False),
    oui.liquidity_approx(750, 500, "USDC", ignore_state=False),
)

Sim.amm_sells("USDC", 5000)
Sim.state()["orders"].query("id==1")

oui = Sim.state()["orderuis"][1]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(1000, 500, "USDC", ignore_state=False),
    oui.liquidity_approx(1000, 750, "USDC", ignore_state=False),
    oui.liquidity_approx(750, 500, "USDC", ignore_state=False),
)

Sim.amm_sells("USDC", 2500)
Sim.state()["orders"].query("id==1")

oui = Sim.state()["orderuis"][1]
oui.pmin, oui.pmax, oui.total_liquidity, oui.max_liquidity

(
    oui.liquidity_approx(1000, 500, "USDC", ignore_state=False),
    oui.liquidity_approx(1000, 750, "USDC", ignore_state=False),
    oui.liquidity_approx(750, 500, "USDC", ignore_state=False),
)

# ## Order book charts

prices = cal.linspace(400,3000, 500)
ETHUSDC = P(tknq="USDC", tknb="ETH")
Sim = CarbonSimulatorUI(pair=ETHUSDC, verbose=False, raiseonerror=True)
CA = cal.Analytics(Sim, verbose=True)
orders = [
    ["ETH", 100, 2000, 3000],
    ["ETH", 100, 2400, 2500],
    ["ETH", 100, 2500, 2700],
    ["USDC", 1000*150, 1500, 500],
    ["USDC", 1100*150, 1200, 1000],
]
for o in orders:
    Sim.add_order(*o)
Sim.state()["orders"]

liq = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False, ignore_state=True)
cal.plot_approx_orderbook_chart(liq)

# +
#liqr = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=True)
#cal.plot_approx_orderbook_chart(liqr)
# -

Sim.amm_sells("ETH", 50)
Sim.amm_sells("USDC", 900*150)
Sim.state()["orders"]

liq = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False, ignore_state=True)
cal.plot_approx_orderbook_chart(liq)

liq = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False, ignore_state=False)
cal.plot_approx_orderbook_chart(liq)


