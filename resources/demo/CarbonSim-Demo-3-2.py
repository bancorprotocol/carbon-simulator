# -*- coding: utf-8 -*-
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

from carbon import CarbonPair, CarbonSimulatorUI, analytics as al
from carbon import __version__ as cversion, __date__ as cdate
import numpy as np
from matplotlib import pyplot as plt
from collections import namedtuple
print (f"Carbon Version v{cversion} ({cdate})")
print (f"Analytics Version v{al.__version__} ({al.__date__})")


# # Carbon Simulation - Demo 3-2
#
# In this demo we look at an **order book**

NUM_POINTS = 50   # number of points on the precise chart

# ## Setup

Sim = CarbonSimulatorUI(pair="ETH/USDC", verbose=False, raiseonerror=True)
CA = al.Analytics(Sim, verbose=True)
CA

maxx = 3000
orders = tuple([
    al.orders_nt("ETH", 100, 2000, maxx),
    al.orders_nt("ETH", 100, 2400, 2500),
    al.orders_nt("ETH", 100, 2500, 2700),
    #al.orders_nt("ETH", 100, 2200, 2600),
    al.orders_nt("USDC", 1000*150, 1500, 500),
    al.orders_nt("USDC", 1100*150, 1200, 1000),
])

for o in orders:
    Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)
Sim.state()["orders"]

Sim.liquidity(Sim.ASDF)

# ## Approximate liquidity

prices = al.linspace(400,3000, 500)
ETHUSDC = CarbonPair(tknq="USDC", tknb="ETH")

liq =  al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False)
liqr = al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=True)

al.plot_approx_orderbook_chart(liq)

al.plot_approx_orderbook_chart(liqr)

# ## AMM sells base token (ask side)

max_liquidity_eth = Sim.liquidity()["ETHUSDC"]["ETH"]
print(f'sim liquidity {Sim.liquidity()["ETHUSDC"]["ETH"]} ETH')
print("max liquidity", max_liquidity_eth)
src_amounts_eth = al.linspace0(max_liquidity_eth*1.1, NUM_POINTS)

CA.simulate_trades(60, CA.ASK)

CA.simulate_trades(70, CA.ASK)

trg_amounts = al.vec([
    CA.simulate_trades(size, CA.ASK) for size in src_amounts_eth
])

OB = al.OrderBook(src_amounts_eth, trg_amounts, "ETH", "USDC")
print(OB.explain())

OB

trg_amounts

OB.plot_token_amount_chart()

# When SELLING ETH, the AMM sells more and more expensively the more ETH it sells

OB.plot_price_chart()

# When SELLING ETH, the AMM pays more (in ETH terms) for the first units of USD received than for the later ones

OB.plot_orderbook_chart()

# ## AMM sells base token (bid side)

max_liquidity_usdc = Sim.liquidity()["ETHUSDC"]["USDC"]
print(f'sim liquidity {Sim.liquidity()["ETHUSDC"]["USDC"]} USDC')
print("max liquidity", max_liquidity_usdc)
src_amounts_eth2 = al.linspace0(max_liquidity_usdc/1000*1.1, NUM_POINTS)

trg_amounts = al.vec([
    CA.simulate_trades(size, CA.BID) for size in src_amounts_eth2
])

OB2 = al.OrderBook(src_amounts_eth2, trg_amounts, "ETH", "USDC", bidask=al.OrderBook.BID)
print(OB2.explain())

OB2.plot_token_amount_chart()

OB2.plot_price_chart()

OB2.plot_orderbook_chart()

# ## Combined

# Note: the liquidity is USDC liquidity, not ETH liquidity. This makes the numbers somewhat harder to verify. However -- this means that liquidity can be compared across different pairs that are using the same quote token.

OB.plot_orderbook_chart(otherob=OB2)

al.plot_approx_orderbook_chart(liqr)

al.plot_approx_orderbook_chart(liq)


