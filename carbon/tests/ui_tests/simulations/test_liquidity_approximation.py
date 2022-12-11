import math

from carbon import CarbonSimulatorUI


def test_liquidity_approx_order0():
    """
    Test Order 0 (ETH, range) - Derived from Test36-LiquidityApprox.ipynb
    """
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000)
    Sim.add_order("ETH", 10, 2500, 2500)
    Sim.add_order("USDC", 10*1250, 1500, 1000)
    Sim.add_order("USDC", 10*1250, 1250, 1250)

    oui = Sim.state()["orderuis"][0]
    assert (oui.pmin, oui.pmax, oui.total_liquidity) == (2000.0, 3000.0, (10.0, 'ETH'))
    assert oui.liquidity_approx(500, 600, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(3000, 3020, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2000, 3000, "ETH", asperc=True) == 1.0
    assert oui.liquidity_approx(3000, 2000, "ETH", asperc=True) == 1.0
    assert oui.liquidity_approx(2000, 2500, "ETH", asperc=True) == 0.5
    assert oui.liquidity_approx(2500, 3000, "ETH", asperc=True) == 0.5
    assert oui.liquidity_approx(2250, 2750, "ETH", asperc=True) == 0.5
    assert oui.liquidity_approx(2000, 3000, "ETH", asperc=False) == 10.0
    assert oui.liquidity_approx(2000, 2500, "ETH", asperc=False) == 5.0
    assert oui.liquidity_approx(2000, 2500, asperc=False) == 5.0
    assert oui.liquidity_approx(2000, 3000, "USDC", asperc=False) == math.sqrt(2000*3000)*10
    assert oui.liquidity_approx(2250, 2750, "USDC", asperc=False) == math.sqrt(2250*2750)*0.5*10


def test_liquidity_approx_order1():
    """
    Test Order 1 (ETH, point) - Derived from Test36-LiquidityApprox.ipynb
    """
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000)
    Sim.add_order("ETH", 10, 2500, 2500)
    Sim.add_order("USDC", 10*1250, 1500, 1000)
    Sim.add_order("USDC", 10*1250, 1250, 1250)

    oui = Sim.state()["orderuis"][1]
    assert oui.total_liquidity == (0.0, 'USDC')
    assert oui.liquidity_approx(2000, 2499, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2501, 3020, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2499, 2501, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2500, 2501, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2499, 2500, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2500, 2500, "ETH", asperc=True) == 0.0
    assert oui.liquidity_approx(2499, 2501, "ETH", asperc=False) == 0.0
    assert oui.liquidity_approx(2499, 2501, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(2500, 2501, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(2500, 2500, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(2000, 3000, "USDC", asperc=False) == 0.0


def test_liquidity_approx_order2():
    """
    Test Order 2 (USDC, range) - Derived from Test36-LiquidityApprox.ipynb
    """
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000)
    Sim.add_order("ETH", 10, 2500, 2500)
    Sim.add_order("USDC", 10*1250, 1500, 1000)
    Sim.add_order("USDC", 10*1250, 1250, 1250)


    oui = Sim.state()["orderuis"][2]
    assert (oui.pmin, oui.pmax, oui.total_liquidity) == (2500.0, 2500.0, (10.0, 'ETH'))
    assert oui.liquidity_approx(500, 600, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1600, 2000, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1000, 1500, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1000, 1100, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1400, 1500, "USDC", asperc=False) == 0.0
    assert round(oui.liquidity_approx(1000, 1100, "ETH", asperc=False),6) == 0
    assert round(oui.liquidity_approx(1400, 1500, "ETH", asperc=False),6) == 0


def test_liquidity_approx_order3():
    """
    Test Order 3 (USDC, point) - Derived from Test36-LiquidityApprox.ipynb
    """
    Sim = CarbonSimulatorUI(verbose=False, raiseonerror=False, pair="ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 3000)
    Sim.add_order("ETH", 10, 2500, 2500)
    Sim.add_order("USDC", 10*1250, 1500, 1000)
    Sim.add_order("USDC", 10*1250, 1250, 1250)

    oui = Sim.state()["orderuis"][3]
    assert oui.total_liquidity == (0.0, 'USDC')
    assert oui.liquidity_approx(1249, 1251, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1000, 2000, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1249, 1250, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1250, 1251, "USDC", asperc=False) == 0.0
    assert oui.liquidity_approx(1249, 1251, "ETH", asperc=False) == 0.0
    assert oui.liquidity_approx(1000, 2000, "ETH", asperc=False) == 0.0
    assert oui.liquidity_approx(1249, 1250, "ETH", asperc=False) == 0.0
    assert oui.liquidity_approx(1250, 1251, "ETH", asperc=False) == 0.0