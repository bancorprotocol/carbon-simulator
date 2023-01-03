# ------------------------------------------------------------
# Auto generated test file `test_046_ThresholdOrders.py`
# ------------------------------------------------------------
# source file   = NBTest_046_ThresholdOrders.py
# source path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# target path   = /Users/skl/REPOES/Bancor/CarbonSimulator/resources/NBTest/
# test id       = 046
# test comment  = ThresholdOrders
# ------------------------------------------------------------



from carbon import CarbonSimulatorUI, __version__, __date__
print(f"Carbon Version v{__version__} ({__date__})", )





# ------------------------------------------------------------
# Test      046
# File      test_046_ThresholdOrders.py
# Segment   ThresholdOrdersUsePos
# ------------------------------------------------------------
def test_thresholdordersusepos():
# ------------------------------------------------------------
    
    Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False)
    AlphaSim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, matching_method=CarbonSimulatorUI.MATCH_ALPHA)
    
    # +
    strat = ['ETH', 10, 2000, 2500, 1000, 2800, 2700]
    for _ in range(10):
        Sim.add_strategy(*strat)
        AlphaSim.add_strategy(*strat)
    
    for _ in range(3):
        Sim.add_strategy('ETH', 0.1, 1950, 1950, 1, 2750, 2750)
        AlphaSim.add_strategy('ETH', 0.1, 1950, 1950, 1, 2750, 2750)
    
    #Sim.state()['orders']
    AlphaSim.state()['orders']
    # -
    
    # set test amounts
    usdc_trade_amount = 1000
    eth_trade_amount = 0.5
    
    # ### Route by Source
    
    # #### AMM buys USDC
    
    threshold_orders=4
    use_positions=[0, 22, 24]
    
    Sim.amm_buys('USDC',usdc_trade_amount, execute=False)['trades']  # route_trade_by_source
    
    r = AlphaSim.amm_buys('USDC',usdc_trade_amount, execute=False, threshold_orders=threshold_orders)['trades']  # route_trade_by_source
    # threshold orders is only utilized on the alpha router
    # check that the maximum number of orders used is less than or equal to the number of threshold orders
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    r
    
    r = Sim.amm_buys('USDC',usdc_trade_amount, execute=False, use_positions=use_positions)['trades']  # route_trade_by_source
    # use_positions is used on any router
    # check that the maximum number of orders used is less than or equal to the number of use_positions
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    r = AlphaSim.amm_buys('USDC',usdc_trade_amount, execute=False, threshold_orders=threshold_orders, use_positions=use_positions)['trades']  # route_trade_by_source
    # thus both use_positions and threshold should apply for alpha router
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    # #### AMM buys ETH
    
    threshold_orders=4
    use_positions=[1, 13, 19]
    
    Sim.amm_buys('ETH',eth_trade_amount, execute=False)['trades']  # route_trade_by_source
    
    r = AlphaSim.amm_buys('ETH',eth_trade_amount, execute=False, threshold_orders=threshold_orders)['trades']  # route_trade_by_source
    # threshold orders is only utilized on the alpha router
    # check that the maximum number of orders used is less than or equal to the number of threshold orders
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    r
    
    r = Sim.amm_buys('ETH',eth_trade_amount, execute=False, use_positions=use_positions)['trades']  # route_trade_by_source
    # use_positions is used on any router
    # check that the maximum number of orders used is less than or equal to the number of use_positions
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    r = AlphaSim.amm_buys('ETH',eth_trade_amount, execute=False, threshold_orders=threshold_orders, use_positions=use_positions)['trades']  # route_trade_by_source
    # thus both use_positions and threshold should apply for alpha router
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    # ### Route by Target
    
    # #### AMM sells USDC
    
    # First we test the standard simulator which should route through all 5 positions
    
    Sim.amm_sells('USDC',usdc_trade_amount, execute=False)['trades']  # route_trade_by_target
    
    # Then we can set a threshold on the number of orders using the AlphaSim
    
    r = AlphaSim.amm_sells('USDC',usdc_trade_amount, execute=False, threshold_orders=threshold_orders)['trades']  # route_trade_by_source
    # threshold orders is only utilized on the alpha router
    # check that the maximum number of orders used is less than or equal to the number of threshold orders
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    r
    
    r = Sim.amm_sells('USDC',usdc_trade_amount, execute=False, use_positions=use_positions)['trades']  # route_trade_by_source
    # use_positions is used on any router
    # check that the maximum number of orders used is less than or equal to the number of use_positions
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    r = AlphaSim.amm_sells('USDC',usdc_trade_amount, execute=False, threshold_orders=threshold_orders, use_positions=use_positions)['trades']  # route_trade_by_source
    # thus both use_positions and threshold should apply for alpha router
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    # #### AMM sells ETH
    
    threshold_orders=4
    use_positions=[0, 22, 24]
    
    Sim.amm_sells('ETH',eth_trade_amount, execute=False)['trades']  # route_trade_by_target
    
    r = AlphaSim.amm_sells('ETH',eth_trade_amount, execute=False, threshold_orders = threshold_orders)['trades'] # route_trade_by_target
    # threshold orders is only utilized on the alpha router
    # check that the maximum number of orders used is less than or equal to the number of threshold orders
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    r
    
    r = Sim.amm_sells('ETH',eth_trade_amount, execute=False, use_positions=use_positions)['trades']  # route_trade_by_source
    # use_positions is used on any router
    # check that the maximum number of orders used is less than or equal to the number of use_positions
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r
    
    r = AlphaSim.amm_sells('ETH',eth_trade_amount, execute=False, threshold_orders=threshold_orders, use_positions=use_positions)['trades']  # route_trade_by_source
    # thus both use_positions and threshold should apply for alpha router
    assert(len(r.query('subid!="A"')) <= threshold_orders)
    assert(len(r.query('subid!="A"')) <= len(use_positions))
    r