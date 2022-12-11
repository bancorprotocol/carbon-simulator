from carbon import CarbonSimulatorUI


def test_use_positions():
    """
    Test feature that allows the user to be able to provide a set of position numbers that the trade will be ONLY
    filled from those positions.
    """
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    result = Sim.trader_buys("ETH", 1, use_positions=[0, 2, 4])
    assert list(result['trades']['routeix'].values) == [0, 2, 4, '[0, 2, 4]']


def test_use_positions_with_missing():
    """
    Test that `use_positions` feature does not crash even if not both positions in a strategy are given.
    """
    Sim = CarbonSimulatorUI(pair="ETH/USDC")
    Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)
    Sim.add_strategy("TEST", 10, 2000, 2500, 10000, 1000, 750, pair='TEST/USDC')
    result = Sim.trader_buys("ETH", 1, use_positions=[0, 3])
    assert list(result['trades']['routeix'].values) == [0, '[0]']


def test_use_positions_display():
    """
    Test that `use_positions` feature displays the proper routeidx.
    """
    Sim = CarbonSimulatorUI(verbose=True, raiseonerror=False, pair="ETH/USDC")
    Sim.add_order("ETH", 10, 2000, 2000)
    Sim.add_order("ETH", 10, 2010, 2010)
    Sim.add_order("ETH", 20, 2020, 2020)
    Sim.add_order("ETH", 30, 2030, 2030)
    Sim.add_order("ETH", 40, 2040, 2040)
    Sim.add_strategy("ETH", 10, 2050, 2050, 5000, 1060, 1060)
    Sim.add_strategy("ETH", 10, 2070, 2070, 5000, 1080, 1080)
    Sim.add_strategy("ETH", 10, 2090, 2090, 5000, 1100, 1100)
    result = Sim.amm_sells("ETH", 50, execute=False, use_positions=[3, 4])
    assert result['success'] == False