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

from carbon import CarbonSimulatorUI, P
from carbon.simulators.carbon_simulator import __version__ as uiversion, __date__ as uidate

print("[carbon_simulator] version", uiversion, uidate)

# # Carbon Simulation - Test 40 - PairInSim

# ## Pair without CarbonPair defaults

Sim = CarbonSimulatorUI(raiseonerror=True)
assert(Sim.slashpair is None)
Sim

ETHUSDC = P("ETH/USDC")

try:
    Sim.add_order("ETH", 10, 2000, 3000)
except ValueError as e:
    print(e)
    assert(str(e)=="Pair must be provided in function or simulation defaults")

try:
    Sim.add_order("ETH", 10, 2000, 3000, pair="ETHUSDC")["orders"]
except ValueError as e:
    print(e)
    assert(str(e)=="('Illegal slashpair', 'ETHUSDC')")

try:
    Sim.add_order("LINK", 10, 2000, 3000, pair=ETHUSDC)
except ValueError as e:
    print(e)
    resp = "('Token not part of pair', 'LINK', CarbonPair(slashpair='ETH/USDC'"
    assert(str(e)[:len(resp)]==resp)    

o = Sim.add_order("ETH", 10, 2000, 3000, pair=ETHUSDC)["orders"]
assert(o.iloc[0]["pair"]=="ETHUSDC")
assert(o.iloc[0]["tkn"]=="ETH")
assert(o.iloc[0]["p_unit"]=="USDC per ETH")
o

Sim.add_order("ETH", 10, 2000, 3000, pair="ETH/USDC")["orders"]

try:
    Sim.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750)["orders"]
except ValueError as e:
    print(e)
    assert(str(e)=="Pair must be provided in function or simulation defaults")

Sim.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750, pair="ETH/USDC")["orders"]

# ## Pair with CarbonPair defaults

SimP = CarbonSimulatorUI(pair="ETH/USDC", raiseonerror=True)
assert(SimP.slashpair=="ETH/USDC")
SimP

o = SimP.add_order("ETH", 10, 2000, 3000)["orders"]
assert(o.iloc[0]["pair"]=="ETHUSDC")
assert(o.iloc[0]["tkn"]=="ETH")
assert(o.iloc[0]["p_unit"]=="USDC per ETH")
o

o = SimP.add_order("ETH", 10, 2000, 3000, pair=ETHUSDC)["orders"]
assert(o.iloc[0]["pair"]=="ETHUSDC")
assert(o.iloc[0]["tkn"]=="ETH")
assert(o.iloc[0]["p_unit"]=="USDC per ETH")
o

SimP.add_order("ETH", 10, 2000, 3000, pair="ETH/USDC")["orders"]

o = SimP.add_order("ETH", 10, 2000, 3000, pair="ETH/DAI")["orders"]
assert(o.iloc[0]["pair"]=="ETHDAI")
assert(o.iloc[0]["tkn"]=="ETH")
assert(o.iloc[0]["p_unit"]=="DAI per ETH")
o

SimP.add_strategy("ETH", 10, 2000, 3000, 10000, 1000, 750)["orders"]











