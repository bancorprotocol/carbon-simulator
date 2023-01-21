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

from carbon import P, CarbonOrderUI, CarbonSimulatorUI, analytics as cal, __version__, __date__
from carbon.helpers.fls import fload, fsave
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from collections import namedtuple
print(f"Carbon Version v{__version__} ({__date__})", )
print (f"Analytics Version v{cal.__version__} ({cal.__date__})")


# # Carbon Simulation - Demo 3-3 (Big Orderbook) NW
#
# In this demo we look at an **order book**. It is very similar to 3-2 except that we now import the orderbook from a file, and that it is substantially bigger. We also trimmed down the analysis
#
# **Added `sellDepthByBuckets()` and `sellDepthByTicks()`**

# +
DATAPATH = "data"

DATAFN = "template.json"
DATAFN = "orders.json"
# DATAFN = "EthUsdcOrders.json"
# -

def import_orders(DATAFN, DATAPATH, json=True):
    data = fload(DATAFN, DATAPATH, json=True)
    meta = data["meta"]
    assert meta["request"] == 'cumulative_liquidity'
    assert meta["request_unit"] == 'y'
    assert meta["price_unit"] == 'y/x'
    assert meta["amt_unit"] == 'y'
    order_nt = namedtuple("order_nt", "pa, pb, pm, amt")
    orders = [order_nt(**{k:int(v) for k,v in r.items()}) for r in data["orders"]]
    minp = min(min(r.pa, r.pb) for r in orders)
    maxp = max(max(r.pa, r.pb) for r in orders)
    inverted = [(r.pa, r.pb) for r in orders if r.pa <= r.pb]
    if inverted:
        raise RuntimeError("Must have pa >= pb", inverted)
    notfull = [(r.pa, r.pm) for r in orders if r.pa != r.pm]
    if notfull:
        raise RuntimeError("Must have not have pa != pm", notfull)
    PAIR = P(tknq=meta["y"], tknb=meta["x"])
    Sim = CarbonSimulatorUI(pair=PAIR, verbose=False, raiseonerror=True)
    CA = cal.Analytics(Sim, verbose=True)
    for o in orders:
        Sim.add_order(meta["y"], o.amt, o.pa, o.pb)
    return(Sim, PAIR, CA, data, minp, maxp)


# ## Setup

Sim, PAIR, CA, data, minp, maxp = import_orders(DATAFN, DATAPATH, json=True)
curves_by_pair_bidask = CarbonOrderUI.curves_by_pair_bidask(Sim.state()["orderuis"])
curves = curves_by_pair_bidask[PAIR.slashpair]["BID"]
c0 = curves[0]
print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)


Sim.state()["orders"].query("disabled==False")

Sim.liquidity(Sim.ASDF)


# +
def calc_new_buckets(maxp, minp, tickSize):
    newmax = maxp
    rem = (maxp - minp +1) % tickSize
    newmax += (tickSize - rem)+1
    range = newmax - minp
    buckets = int(range/tickSize +1)
    return(newmax, buckets)

def sellDepthByBuckets(Sim, buckets = 100):
    prices = np.linspace(minp,maxp, buckets)  
    liq =  cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=True)
    liqr = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=False)
    dy_amounts = [dy_p(p) for p in prices]
    dx_amounts = [dx_p(p) for p in prices]
    cumul_df = pd.DataFrame([prices, dy_amounts]).T
    cumul_df.columns = [f"Price [{c0.pair.price_convention}]", f"Cumulative Liquidity [{c0.tkny}]"]
    OB2 = cal.OrderBook(dx_amounts, dy_amounts, PAIR.tknb, PAIR.tknq, bidask=cal.OrderBook.BID)
    return(prices, dy_amounts, dx_amounts, cumul_df, OB2)

def sellDepthByTick(Sim, tickSize = 1):
    newmax, buckets = calc_new_buckets(maxp, minp, tickSize)
    prices = np.linspace(minp, newmax, buckets)  
    liq =  cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=True)
    liqr = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=False)
    dy_amounts = [dy_p(p) for p in prices]
    dx_amounts = [dx_p(p) for p in prices]
    cumul_df = pd.DataFrame([prices, dy_amounts]).T
    cumul_df.columns = [f"Price [{c0.pair.price_convention}]", f"Cumulative Liquidity [{c0.tkny}]"]
    OB2 = cal.OrderBook(dx_amounts, dy_amounts, PAIR.tknb, PAIR.tknq, bidask=cal.OrderBook.BID)
    return(prices, dy_amounts, dx_amounts, cumul_df, OB2)

def decumulate(cumul_df):
    standard_df = cumul_df.copy()
    cols = [x.split('[')[1].split(']')[0] for x in standard_df.columns]
    standard_df.columns = ['tickEnd', 'cumul_liquidity']
    total_amt = standard_df.cumul_liquidity[0]
    standard_df['tickStart'] = list(standard_df.tickEnd)[1:] + list(standard_df.tickEnd)[-1:]
    standard_df[['tickStart', 'tickEnd', 'cumul_liquidity']]
    newliquidity = []
    for i in standard_df.index[:-1]:
        newliquidity += [standard_df.cumul_liquidity[i] - standard_df.cumul_liquidity[i+1]]
    standard_df['liquidity'] = newliquidity + [0]
    standard_df = standard_df[['tickStart', 'tickEnd', 'liquidity']].copy()
    standard_output = standard_df.to_dict(orient='tight')['data']
    # print(total_amt)
    # print(standard_df.liquidity.sum())
    # assert(f"{standard_df.liquidity.sum():.6f}" == f"{total_amt:.6f}")
    standard_df.columns = [f'tickStart ({cols[0]})', f'tickEnd ({cols[0]})', f'liquidity ({cols[1]})']
    return(standard_df, standard_output)


# -

prices, dy_amounts, dx_amounts, cumul_df_sellDepthByBuckets, OB2 = sellDepthByBuckets(Sim, buckets = 21)
cumul_df_sellDepthByBuckets

standard_df_sellDepthByBuckets, standard_output_sellDepthByBuckets = decumulate(cumul_df_sellDepthByBuckets)
standard_df_sellDepthByBuckets

standard_output_sellDepthByBuckets

prices, dy_amounts, dx_amounts, cumul_df_sellDepthByTick, OB2 = sellDepthByTick(Sim, tickSize = 10)
cumul_df_sellDepthByTick

standard_df_sellDepthByTick, standard_output_sellDepthByTick  = decumulate(cumul_df_sellDepthByTick)
standard_df_sellDepthByTick

standard_output_sellDepthByTick

plt.plot(prices, dy_amounts, color="green")
plt.title(f"Cumulative BID liquidity (sell {c0.tkny}, buy {c0.tknx})")
plt.xlabel(f"Price [{c0.pair.price_convention}]")
plt.ylabel(f"Cumulative Liquidity [{c0.tkny}]")
plt.grid()

OB2.plot_tokenamount_chart()

OB2.data_orderbook_chart(aspandas=True)
