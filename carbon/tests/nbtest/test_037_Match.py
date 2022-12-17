# ------------------------------------------------------------
# Auto generated test file `test_037_Match.py`
# ------------------------------------------------------------
# source file   = NBTest_037_Match.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 037
# test comment  = Match
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))







Sim = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC")
assert(Sim._mm==CarbonSimulatorUI.MATCH_EXACT)
Sim

SimE = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_EXACT)
assert(SimE._mm==CarbonSimulatorUI.MATCH_EXACT)
SimE

SimA = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_ALPHA)
assert(SimA._mm==CarbonSimulatorUI.MATCH_ALPHA)
SimA

#SimF = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC", matching_method=CarbonSimulatorUI.MATCH_FAST)
SimF = CarbonSimulatorUI(raiseonerror=False, pair="ETH/USDC")
#assert(SimA._mm==CarbonSimulatorUI.MATCH_FAST)
SimF

SIMS = [Sim, SimE, SimA, SimF]



ORDERS = [
    ("ETH", 1, 2000+10*i, 3000)
    for i in range(20)   
]
ORDERS[:2]

for sim in SIMS:
    for o in ORDERS:
        sim.add_order(*o)
    print(sim, len(sim.state()["orders"]), len(ORDERS))
    assert(len(sim.state()["orders"])==2*len(ORDERS))



Sim.amm_sells("ETH", 1, execute=False)["trades"]

SimA.amm_sells("ETH", 1, execute=False)["trades"]

