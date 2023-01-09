import subprocess
import sys

import pytest

from carbon import CarbonPair, CarbonSimulatorUI, analytics as al


def test_orderbook_explain():
    """
    Derived from `passed_tests` notebook demo-3-2
    """
    Sim = CarbonSimulatorUI(
        pair=CarbonPair("ETH/USDC"), verbose=False, raiseonerror=True
    )
    CA = al.Analytics(Sim, verbose=True)
    maxx = 3000
    orders = tuple(
        [
            al.orders_nt("ETH", 100, 2000, maxx),
            al.orders_nt("ETH", 100, 2500, 2700),
            al.orders_nt("USDC", 1000 * 100, 1500, 500),
            al.orders_nt("USDC", 1100 * 100, 1200, 1000),
        ]
    )

    for o in orders:
        Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)

    max_liquidity = Sim.liquidity()["ETHUSDC"]["ETH"]
    src_amounts = al.linspace(max_liquidity, 20)
    CA.simulate_trades(60, CA.ASK)
    CA.simulate_trades(70, CA.ASK)
    trg_amounts = al.vec([CA.simulate_trades(size, CA.ASK) for size in src_amounts])

    OB = al.OrderBook(src_amounts, trg_amounts, "ETH", "USDC")
    assert (
            OB.explain()
            == "This is the ASK book.\nSource token = ETH, target token = USDC.\nAMM sells ETH for USDC.\nBase token = ETH, quote token = USDC.\nPrices are quoted in USDC per ETH.\nOrder book amounts are quoted in USDC."
    )


def test_orderbook_plot_token_amount_chart_text():
    """
    Derived from `passed_tests` notebook demo-3-2
    """
    Sim = CarbonSimulatorUI(
        pair=CarbonPair("ETH/USDC"), verbose=False, raiseonerror=True
    )
    CA = al.Analytics(Sim, verbose=True)
    maxx = 3000
    orders = tuple(
        [
            al.orders_nt("ETH", 100, 2000, maxx),
            al.orders_nt("ETH", 100, 2500, 2700),
            al.orders_nt("USDC", 1000 * 100, 1500, 500),
            al.orders_nt("USDC", 1100 * 100, 1200, 1000),
        ]
    )

    for o in orders:
        Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)

    max_liquidity = Sim.liquidity()["ETHUSDC"]["ETH"]
    src_amounts = al.linspace0(max_liquidity, 20)
    CA.simulate_trades(60, CA.ASK)
    CA.simulate_trades(70, CA.ASK)
    trg_amounts = al.vec([CA.simulate_trades(size, CA.ASK) for size in src_amounts])

    OB = al.OrderBook(src_amounts, trg_amounts, "ETH", "USDC")
    result = OB.plot_tokenamount_chart()
    assert result == "plotted tokens received against trade size (504,750)"


# The following tests the matplotlib functionality using the `mpl` fixture
# https://github.com/matplotlib/pytest-mpl/blob/main/tests/test_pytest_mpl.py
#
# @pytest.mark.mpl_image_compare(baseline_dir='/carbon/tests/ui_tests/analytics/baseline',
#                                filename='orderbook_plot_token_amount_chart_1.png',
#                                tolerance=100)
# def test_orderbook_plot_token_amount_chart():
#     """
#     Derived from `passed_tests` notebook demo-3-2
#     """
#     Sim = CarbonSimulatorUI(pair=CarbonPair("ETH/USDC"), verbose=False, raiseonerror=True)
#     CA = al.Analytics(Sim, verbose=True)
#     maxx = 3000
#     orders = tuple([
#         al.orders_nt("ETH", 100, 2000, maxx),
#         al.orders_nt("ETH", 100, 2500, 2700),
#         al.orders_nt("USDC", 1000 * 100, 1500, 500),
#         al.orders_nt("USDC", 1100 * 100, 1200, 1000),
#     ])
#
#     for o in orders:
#         Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)
#
#     max_liquidity = Sim.liquidity()["ETHUSDC"]["ETH"]
#     src_amounts = al.linspace(max_liquidity, 20)
#     CA.simulate_trades(60, CA.ASK)
#     CA.simulate_trades(70, CA.ASK)
#     trg_amounts = al.vec([
#         CA.simulate_trades(size, CA.ASK) for size in src_amounts
#     ])
#
#     OB = al.OrderBook(src_amounts, trg_amounts, "ETH", "USDC")
#
#     return OB.plot_token_amount_chart(return_fig=True)
