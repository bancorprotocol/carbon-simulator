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

# # Carbon Simulation - Test 42 - Exclusions

Sim = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
Sim

for i in range(3):
    Sim.add_strategy("ETH", 10+0.1*i, 2000+10*i, 3000, 1000+10*i, 1001-10*i, 750)
    Sim.add_strategy("ETH", 11+0.1*i, 2000+10*i, 3000, None, None, None)
    Sim.add_strategy("ETH", None, None, None, 1001+10*i, 1001-10*i, 750)

o = Sim.state()["orders"]
assert len(o) == 18
o

o = Sim.state()["orders"].query("disabled==False")
assert len(o) == 12
print(list(o.query("tkn=='ETH'")["id"]))
assert list(o.query("tkn=='ETH'")["id"]) == [0, 2, 6, 8, 12, 14]
print(list(o.query("tkn=='USDC'")["id"]))
assert list(o.query("tkn=='USDC'")["id"]) == [1, 5, 7, 11, 13, 17]
o

t = Sim.amm_sells("ETH", 10, execute=False)["trades"]
print(list(t.query("aggr==False")["routeix"]))
assert(list(t.query("aggr==False")["routeix"])==[0, 2, 6, 8, 12, 14])
t

# ## Whitelist (`use_positions`)

t = Sim.amm_sells("ETH", 10, use_positions=[0,2], execute=False)["trades"]
print(list(t.query("aggr==False")["routeix"]))
assert(list(t.query("aggr==False")["routeix"])==[0, 2])
t

t = Sim.amm_sells("ETH", 10, use_positions=[6,12], execute=False)["trades"]
print(list(t.query("aggr==False")["routeix"]))
assert(list(t.query("aggr==False")["routeix"])==[6,12])
t

# ## Blacklist (`exclude_positions`)

t = Sim.amm_sells("ETH", 10, excl_positions=[8,12,14], execute=False)["trades"]
print(list(t.query("aggr==False")["routeix"]))
assert(list(t.query("aggr==False")["routeix"])==[0, 2, 6])
t

t


