from carbon import CarbonSimulatorUI


def test_inverted_range_positions_1():
    """
    Derived from `passed_tests` notebook test-13
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_order("ETH", 10, 2000, 3000, pair="ETH/USDC")
    result = Sim.add_order("ETH", 10, 3000, 2000, pair="ETH/USDC")
    assert result["success"] is True
    assert list(Sim.state()["orders"]["p_end"].values) == [3000.0, None, 3000.0, None]


def test_inverted_range_positions_2():
    """
    Derived from `passed_tests` notebook test-13
    """
    Sim = CarbonSimulatorUI(verbose=True)
    result = Sim.add_strategy("BAT", 10, 12.0, 10, 0, 5, 7.5, pair="BAT/MAN")
    assert result["success"] is True
    assert list(Sim.state()["orders"]["p_end"].values) == [12.0, 5.0]
