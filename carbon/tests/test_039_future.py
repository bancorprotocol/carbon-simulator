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
from carbon.simulators.carbon_simulator import __version__ as uiversion, __date__ as uidate
#from carbon.pair import __version__ as pversion, __date__ as pdate

print("[carbon_simulator] version", uiversion, uidate)
#print("[pair] version", pversion, pdate)

# # Carbon Simulation - Test 39 - Future

# +
#help(CarbonSimulatorUI)
# -

def test_039():
    
    Sim = CarbonSimulatorUI()
    SimXF = CarbonSimulatorUI(exclude_future=True)
    SimIF = CarbonSimulatorUI(exclude_future=False)

    assert(Sim.exclude_future==True)
    assert(SimXF.exclude_future==True)
    assert(SimIF.exclude_future==False)

    try:
        Sim._raise_if_future_restricted()
    except Sim.ExcludedFutureFunctionality as e:
        print(e)
        assert(str(e)=="Feature disabled (us `exclude_future = False` to enable)")

    try:
        SimXF._raise_if_future_restricted()
    except Sim.ExcludedFutureFunctionality as e:
        print(e)
        assert(str(e)=="Feature disabled (us `exclude_future = False` to enable)")

    assert(SimIF._raise_if_future_restricted()==None)


