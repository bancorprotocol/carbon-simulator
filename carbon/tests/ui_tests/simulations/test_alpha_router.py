from carbon import CarbonSimulatorUI


def test_alpha_routing_trade_by_src():
    """
    Derived from notebook 4-1
    """
    AlphaSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method=CarbonSimulatorUI.MATCH_ALPHA)
    strat = ['ETH', 10, 2000, 2500, 1000, 2800, 2700]
    for _ in range(5):
        AlphaSim.add_strategy(*strat)

    usdc_trade_amount = 1000
    eth_trade_amount = 0.5

    AlphaSim.amm_buys('USDC', usdc_trade_amount, execute=False, threshold_orders=3)  # route_trade_by_source
    assert AlphaSim.state()["trades"].iloc[3]["amt1"] == 0.499121771875

    AlphaSim.amm_buys('ETH', eth_trade_amount, execute=False, threshold_orders=3)  # route_trade_by_source
    assert AlphaSim.state()["trades"].query("uid=='1'").iloc[0]["amt1"] == 1388.325436499391


def test_alpha_routing_trade_by_target():
    """
    Derived from notebook 4-1
    """
    AlphaSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method=CarbonSimulatorUI.MATCH_ALPHA)
    strat = ['ETH', 10, 2000, 2500, 1000, 2800, 2700]
    for _ in range(5):
        AlphaSim.add_strategy(*strat)

    usdc_trade_amount = 1000
    eth_trade_amount = 0.5

    AlphaSim.amm_sells('USDC', usdc_trade_amount, execute=False, threshold_orders=3)  # route_trade_by_target
    assert AlphaSim.state()["trades"].query("uid=='0'").iloc[0]["amt2"] == 0.35930099786

    AlphaSim.amm_sells('ETH', eth_trade_amount, execute=False, threshold_orders=2)  # route_trade_by_target
    assert AlphaSim.state()["trades"].query("uid=='1'").iloc[0]["amt2"] == 1002.64630467044

    AlphaSim.amm_sells('ETH', eth_trade_amount, execute=False, threshold_orders=4)  # route_trade_by_target
    assert AlphaSim.state()["trades"].query("uid=='2'").iloc[0]["amt2"] == 1001.321403916542
