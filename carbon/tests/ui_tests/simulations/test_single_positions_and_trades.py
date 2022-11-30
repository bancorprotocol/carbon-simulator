"""Derived from `passed_tests` notebook test-1"""
from carbon import CarbonSimulatorUI


def test_add_sgl_pos_concentrated_on_one_point():
    """
    Derived from `passed_tests` notebook test-1
    """
    Sim = CarbonSimulatorUI(pair="USDCETH", verbose=True)
    assert Sim.add_sgl_pos("ETH", 100, 2000, 2000)["orders"].to_dict() == {
        "id": {0: 0},
        "pair": {0: "USDCETH"},
        "tkn": {0: "ETH"},
        "y_int": {0: 100.0},
        "y": {0: 100.0},
        "y_unit": {0: "ETH"},
        "p_start": {0: 2000.0},
        "p_end": {0: 2000.0},
        "p_marg": {0: 2000.0000000000002},
        "p_unit": {0: "ETH per USDC"},
        "lid": {0: 0},
    }


def test_amm_cannot_buy_eth_with_no_usdc():
    """
    Derived from `passed_tests` notebook test-1
    """
    Sim = CarbonSimulatorUI(pair="USDCETH", verbose=True)
    Sim.add_sgl_pos("ETH", 100, 2000, 2000)
    result = Sim.amm_buys("ETH", 2)
    assert result["success"] is False
    assert result["error"] == "token USDC has no non-empty liquidity positions"


def test_amm_can_sell_eth_at_curve_price():
    """
    Derived from `passed_tests` notebook test-1
    """
    Sim = CarbonSimulatorUI(pair="USDCETH", verbose=True)
    Sim.add_sgl_pos("ETH", 100, 2000, 2000)
    result = Sim.amm_sells("ETH", 2)
    assert result["success"] is True
    assert result["trades"].to_dict() == {
        "uid": {0: "0"},
        "id": {0: 0},
        "subid": {0: "A"},
        "note": {0: "AMM sells 2ETH buys 0USDC"},
        "aggr": {0: True},
        "exec": {0: True},
        "limitfail": {0: None},
        "amt1": {0: 2.0},
        "tkn1": {0: "ETH"},
        "amt2": {0: 0.001},
        "tkn2": {0: "USDC"},
        "pair": {0: "USDCETH"},
        "routeix": {0: "[0]"},
        "nroutes": {0: 1},
        "price": {0: "2000.0"},
        "p_unit": {0: "ETH per USDC"},
        'threshold_orders': {0: None},
    }


def test_can_add_multiple_single_positions():
    """
    Derived from `passed_tests` notebook test-4
    """
    Sim = CarbonSimulatorUI(pair="USDCETH", verbose=True)
    test_cases = [
        ("ETH", 0.0005, 2700, 2800),
        ("ETH", 0.0005, 2000, 2700),
        ("USDC", 1000, 2700, 2800),
        ("USDC", 1000, 2000, 2700),
    ]
    for case in test_cases:
        assert Sim.add_sgl_pos(*case)["success"] is True


def test_no_pair_provided():
    """
    Derived from `passed_tests` notebook test-6
    """
    Sim = CarbonSimulatorUI(verbose=True)
    result = Sim.add_sgl_pos("ETH", 100, 2000, 2000)
    assert result["success"] is False
    assert (
        result["error"]
        == "Trading pair must be provided either in function call or in simulation defaults"
    )


def test_geometric_mean_in_one_step():
    """
    Derived from `passed_tests` notebook test-10
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_sgl_pos("ETH", 100, 2000, 3000, "ETHUSDC")
    result = Sim.amm_sells("ETH", 100, "ETHUSDC")
    assert result["success"] is True
    assert round(Sim.state()["trades"]["price"].astype(float).mean(), 4) == 2449.4897


def test_geometric_mean_in_two_steps():
    """
    Derived from `passed_tests` notebook test-10
    """
    Sim = CarbonSimulatorUI(verbose=True)
    Sim.add_sgl_pos("ETH", 100, 2000, 3000, "ETHUSDC")
    Sim.amm_sells("ETH", 50, "ETHUSDC")
    result = Sim.amm_sells("ETH", 50, "ETHUSDC")
    assert result["success"] is True
    assert round(Sim.state()["trades"]["price"].astype(float).mean(), 4) == 2449.4897
