from carbon import CarbonSimulatorUI


def test_inverted_range_positions_1():
    """
    Derrived from `passed_tests` notebook test-13
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_sgl_pos("ETH", 10, 2000, 3000, pair="ETHUSDC")
    result = Sim.add_sgl_pos("ETH", 10, 3000, 2000, pair="ETHUSDC")
    assert result["success"] is True
    assert list(Sim.state()["orders"]["p_end"].values) == [3000.0, 3000.0]


def test_inverted_range_positions_2():
    """
    Derrived from `passed_tests` notebook test-13
    """
    Sim = CarbonSimulatorUI(verbose=True)
    result = Sim.add_linked_pos("BAT", 10, 12.0, 10, 0, 5, 7.5, pair="BATMAN")
    assert result["success"] is True
    assert list(Sim.state()["orders"]["p_end"].values) == [12.0, 7.5]
