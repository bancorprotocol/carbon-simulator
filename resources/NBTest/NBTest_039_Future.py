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

# # Carbon Simulation - Test 39 - Future
# ## Future

# +
#help(CarbonSimulatorUI)
# -

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


