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

from carbon import CarbonPair, CarbonOrderUI, CarbonSimulatorUI, analytics as al
from carbon import __version__ as cversion, __date__ as cdate
import numpy as np
from matplotlib import pyplot as plt
from collections import namedtuple
print (f"Carbon Version v{cversion} ({cdate})")
print (f"Analytics Version v{al.__version__} ({al.__date__})")


# # Carbon Simulation - Demo 3-2
#
# In this demo we look at an **order book**

NUM_POINTS = 1000   # number of points on the precise chart

# ## Setup

ETHUSDC = CarbonPair(tknq="USDC", tknb="ETH")
Sim = CarbonSimulatorUI(pair=ETHUSDC, verbose=False, raiseonerror=True)
CA = al.Analytics(Sim, verbose=True)
CA

orders = tuple([
    al.orders_nt("ETH", 100, 2000, 3000),
    al.orders_nt("ETH", 100, 2100, 2550),
    al.orders_nt("ETH", 50, 2300, 2450),
    al.orders_nt("ETH", 75, 2400, 2500),
    al.orders_nt("ETH", 80, 2500, 2700),
    #al.orders_nt("ETH", 100, 2200, 2600),
    al.orders_nt("USDC", 1000*150, 1500, 500),
    al.orders_nt("USDC", 1000*50, 1500, 1300),
    al.orders_nt("USDC", 1000*20, 1450, 1350),
    al.orders_nt("USDC", 1100*150, 1200, 1000),
])

for o in orders:
    Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)
Sim.state()["orders"]

Sim.liquidity(Sim.ASDF)

prices = al.linspace(400,3000, NUM_POINTS)
prices

curves_by_pair_bidask = CarbonOrderUI.curves_by_pair_bidask(Sim.state()["orderuis"])
print(list(curves_by_pair_bidask.keys()))

# ## Approximate liquidity

liq =  al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=False)
liqr = al.calc_liquidity_approx(Sim.state()["orderuis"], prices, ETHUSDC, reverse=True)

al.plot_approx_orderbook_chart(liq)

al.plot_approx_orderbook_chart(liqr)

# ## AMM SELLS base token (ASK side)

# +
# This code calculates the orderbook using the old method, with similates trades, ie 
# using the standard routing algo; this is highly inefficient

# max_liquidity_eth = Sim.liquidity()["ETHUSDC"]["ETH"]
# print(f'sim liquidity {Sim.liquidity()["ETHUSDC"]["ETH"]} ETH')
# print("max liquidity", max_liquidity_eth)
# src_amounts_eth = al.linspace0(max_liquidity_eth*1.1, NUM_POINTS)

# CA.simulate_trades(60, CA.ASK)
# CA.simulate_trades(70, CA.ASK)
# trg_amounts = al.vec([
#     CA.simulate_trades(size, CA.ASK) for size in src_amounts_eth
# ])
# -

curves = curves_by_pair_bidask["ETH/USDC"]["ASK"]
c0 = curves[0]
print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)
dy_amounts = [dy_p(p) for p in prices]
dx_amounts = [dx_p(p) for p in prices]

plt.plot(prices, dy_amounts)
plt.xlabel(f"market price [{c0.pair.price_convention}]")
plt.ylabel(f"Cumulative amount of y sold [{c0.tkny}]")

plt.plot(prices, dx_amounts)
plt.xlabel(f"market price [{c0.pair.price_convention}]")
plt.ylabel(f"Cumulative amount of x bought [{c0.tknx}]")

OB = al.OrderBook(dy_amounts, dx_amounts, "ETH", "USDC")
print(OB.explain())

OB.plot_token_amount_chart()

# When SELLING ETH, the AMM sells more and more expensively the more ETH it sells

OB.plot_price_chart()

# When SELLING ETH, the AMM pays more (in ETH terms) for the first units of USD received than for the later ones

OB.plot_orderbook_chart()

# ## AMM BUYS base token (BID side)

# +
# max_liquidity_usdc = Sim.liquidity()["ETHUSDC"]["USDC"]
# print(f'sim liquidity {Sim.liquidity()["ETHUSDC"]["USDC"]} USDC')
# print("max liquidity", max_liquidity_usdc)
# src_amounts_eth2 = al.linspace0(max_liquidity_usdc/1000*1.1, NUM_POINTS)
# trg_amounts = al.vec([
#     CA.simulate_trades(size, CA.BID) for size in src_amounts_eth2
# ])
# -

curves = curves_by_pair_bidask["ETH/USDC"]["BID"]
c0 = curves[0]
print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)
dy_amounts = [dy_p(p) for p in prices]
dx_amounts = [dx_p(p) for p in prices]

OB2 = al.OrderBook(dx_amounts, dy_amounts, "ETH", "USDC", bidask=al.OrderBook.BID)
print(OB2.explain())

OB2.plot_token_amount_chart()

OB2.plot_price_chart()

OB2.plot_orderbook_chart()

# ## Combined

# Note: the liquidity is USDC liquidity, not ETH liquidity. This makes the numbers somewhat harder to verify. However -- this means that liquidity can be compared across different pairs that are using the same quote token.

OB.plot_orderbook_chart(otherob=OB2)

al.plot_approx_orderbook_chart(liqr)

al.plot_approx_orderbook_chart(liq)


