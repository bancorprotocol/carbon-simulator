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

from carbon import CarbonSimulatorUI, CarbonPair, P, __version__, __date__
print(f"Carbon v{__version__} ({__date__})")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSimulatorUI))

def test_033():
        
    # # Carbon Simulation - Test 33 - CarbonPair
    #

    # just checking we can add a CarbonPair

    Sim = CarbonSimulatorUI(pair=CarbonPair("ETH/USDC"))
    Sim

    assert (Sim.default_basetoken, Sim.default_quotetoken) == ('ETH', 'USDC')

    assert (Sim.tknb, Sim.tknq) == ('ETH', 'USDC')

    Sim.add_order("ETH", 10, 2000, 3000)["orders"]
    Sim.add_order("ETH", 10, 2000, 2500)["orders"]
    r = Sim.state()["orders"]
    assert list(r["pair"]) == ["ETHUSDC"]*4
    r

    r = Sim.amm_sells("ETH", 1)["trades"]
    assert list(r["p_unit"]) == ["USDC per ETH"]*3
    r

    Sim.state()["orders"]


