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

from carbon.helpers.stdimports import *
from carbon.routers import ExactBase, ExactRouterX0Y0N, AlphaRouter, FastRouter
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))
print_version(require="2.3.3")

# # Simulation Parameters (NBTest 060)

# ## New parameter handling
#
# In v2.3.3 we introduced a `parameters` dict into `BaseRouter` that is collecting all simulation parameters, instead of adding them individually as function parameters. The parameters removed are the following:
#
# - `debug`
# - `verbose`
# - `raiseonerror`
# - `assert_precision`
# - `use_floor_division`
#
#
# Note that for compatibility reasons all those paramters can still be accessed as properties, as well through the regular `p("...")` pathway.

ROUTERS = (ExactBase, ExactRouterX0Y0N, AlphaRouter, FastRouter)
#ROUTERS = (ExactBase, ExactRouterX0Y0N, AlphaRouter)

for Router in ROUTERS:
    print(Router)
    router = Router()
    assert router.parameters == {}
    assert router.debug == False
    assert router.verbose == False
    assert router.raiseonerror == False
    assert router.assert_precision == 4
    assert router.use_floor_division == False

    params = {
        "debug": True,
        "verbose": True,
        "raiseonerror": True,
        "assert_precision": 5,
        "use_floor_division": True,
    }
    router = Router(parameters=params)
    assert router.parameters == params
    assert router.debug == True
    assert router.verbose == True
    assert router.raiseonerror == True
    assert router.assert_precision == 5
    assert router.use_floor_division == True
# ## CarbonSimulatorUI
#
# Make sure the Simulation object is working correctly

Sim = CarbonSimulatorUI()
assert Sim.matcher.parameters == {
    'debug': False,
    'verbose': False,
    'raiseonerror': False,
    'assert_precision': 4,
    'use_floor_division': False
}

Sim = CarbonSimulatorUI(debug=True)
assert Sim.matcher.p("debug") == True

Sim = CarbonSimulatorUI(verbose=True)
assert Sim.matcher.p("verbose") == True

Sim = CarbonSimulatorUI(raiseonerror=True)
assert Sim.matcher.p("raiseonerror") == True

pass






