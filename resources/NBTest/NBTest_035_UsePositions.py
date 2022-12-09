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

# # Carbon Simulation - Test 34 - UsePositions
# ## use_position

Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
Sim

for i in range(10):
    Sim.add_order("ETH", 10, 2000+i, 2200)

r = Sim.state()["orders"].query("disabled==False")
assert len(r) == 10
assert sum(r.query("tkn=='ETH'")["y"]) == 100
r

help(Sim.amm_sells)

r = Sim.amm_sells("ETH", 10, execute=False, pair="ETH/USDC")["trades"]
p = r.iloc[-1]["price"]
print(p)
r

r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[2])["trades"]
p1 = r.iloc[-1]["price"]
print(p1, p)
assert p1>p
assert r.iloc[-1]["routeix"] == "[2]"
r

r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[4])["trades"]
p2 = r.iloc[-1]["price"]
print(p2, p1, p)
assert p2>p1
assert r.iloc[-1]["routeix"] == "[4]"
r

r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[6,8])["trades"]
p3 = r.iloc[-1]["price"]
print(p3, p2, p1, p)
assert p3>p
assert r.iloc[-1]["routeix"] == "[6, 8]"
r

r = Sim.amm_sells("ETH", 10, execute=False, use_positions=[12,14])["trades"]
p4 = r.iloc[-1]["price"]
print(p4, p3, p2, p1, p)
assert p4>p3
assert r.iloc[-1]["routeix"] == "[12, 14]"
r

r.iloc[-1]["routeix"]


