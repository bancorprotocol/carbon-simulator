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

# +
from carbon.helpers.stdimports import *
from carbon.helpers.fls import fload, fsave
from collections import namedtuple

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
print_version(require="2.2.2")
# -


# # Carbon Simulation - Demo 3-3 (Big Orderbook)
#
# In this demo we look at an **order book**. It is very similar to 3-2 except that we now import the orderbook from a file, and that it is substantially bigger. We also trimmed down the analysis

# +
DATAPATH = "data"

DATAFN = "template.json"
DATAFN = "orders.json"
# -

# !ls {DATAPATH}

data = fload(DATAFN, DATAPATH, json=True)
prices = data.get("prices", [])
print(f'Data: {len(data["orders"])} orders, {len(prices)} prices')
#data

data["orders"][0]

meta = data["meta"]
assert meta["request"] == 'cumulative_liquidity'
assert meta["request_unit"] == 'y'
assert meta["price_unit"] == 'y/x'
assert meta["amt_unit"] == 'y'
meta

order_nt = namedtuple("order_nt", "pa, pb, pm, amt")
orders = [order_nt(**{k:int(v) for k,v in r.items()}) for r in data["orders"]]
orders[0]

minp = min(min(r.pa, r.pb) for r in orders)
maxp = max(max(r.pa, r.pb) for r in orders)
minp, maxp

if not prices:
    prices = np.linspace(minp,maxp, 100)
    prices[:4]
else:
    prices = [float(p) for p in prices]

inverted = [(r.pa, r.pb) for r in orders if r.pa <= r.pb]
if inverted:
    raise RuntimeError("Must have pa >= pb", inverted)

notfull = [(r.pa, r.pm) for r in orders if r.pa != r.pm]
if notfull:
    raise RuntimeError("Must have not have pa != pm", notfull)

plt.plot([r.pa for r in orders], [r.amt for r in orders], marker="x", label="pa")
plt.plot([r.pb for r in orders], [r.amt for r in orders], marker="o", label="pb")
plt.title("Order book")
plt.xlabel("price [dy/dx units]")
plt.ylabel("liquidity [y units]")
plt.legend()
plt.grid()

sizes = np.array([r.amt for r in orders])
maxsize = max(sizes)
plt.scatter([r.pa for r in orders], [r.pb for r in orders], s=sizes/maxsize*500)
plt.title("Order book (size = liquidity)")
plt.xlabel("pa")
plt.ylabel("pb")
plt.grid()

# +
#[r.amt for r in orders]
# -

# ## Setup

PAIR = P(tknq=meta["y"], tknb=meta["x"])
Sim = CarbonSimulatorUI(pair=PAIR, verbose=False, raiseonerror=True)
CA = cal.Analytics(Sim, verbose=True)
for o in orders:
    Sim.add_order(meta["y"], o.amt, o.pa, o.pb)

Sim.state()["orders"].query("disabled==False")

Sim.liquidity(Sim.ASDF)

curves_by_pair_bidask = CarbonOrderUI.curves_by_pair_bidask(Sim.state()["orderuis"])
print(list(curves_by_pair_bidask.keys()))

# ## Approximate liquidity

liq =  cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=True)
liqr = cal.calc_liquidity_approx(Sim.state()["orderuis"], prices, PAIR, reverse=False)

cal.plot_approx_orderbook_chart(liq)

cal.plot_approx_orderbook_chart(liqr)

# ## AMM BUYS base token (BID side)

curves = curves_by_pair_bidask[PAIR.slashpair]["BID"]
c0 = curves[0]
print(f"pair={c0.pair.slashpair} [{c0.pair.price_convention}] tkny={c0.tkny} tknx={c0.tknx}")
dy_p = lambda p: sum(c.dyfromp_f(p) for c in curves)
dx_p = lambda p: sum(c.dxfromdy_f(c.dyfromp_f(p)) for c in curves)
dy_amounts = [dy_p(p) for p in prices]
dx_amounts = [dx_p(p) for p in prices]

plt.plot(prices, dy_amounts, color="green")
plt.title(f"Cumulative BID liquidity (sell {c0.tkny}, buy {c0.tknx})")
plt.xlabel(f"Price [{c0.pair.price_convention}]")
plt.ylabel(f"Cumulative Liquidity [{c0.tkny}]")
plt.grid()

cumul_df = pd.DataFrame([prices, dy_amounts]).T
cumul_df.columns = [f"Price [{c0.pair.price_convention}]", f"Cumulative Liquidity [{c0.tkny}]"]
cumul_df

OB2 = cal.OrderBook(dx_amounts, dy_amounts, PAIR.tknb, PAIR.tknq, bidask=cal.OrderBook.BID)
print(OB2.explain())

OB2.plot_tokenamount_chart()

OB2.data_tokenamount_chart(aspandas=True)

OB2.plot_price_chart()

OB2.data_price_chart(aspandas=True)

OB2.plot_orderbook_chart()

OB2.data_orderbook_chart(aspandas=True)

# ## Create template file

orders = [
    {"pa": 2500-i*100, "pb": 2000, "pm": 2500-i*100, "amt": 100*(5-i)}
    for i in range (5)
]
#orders

prices = [int(x) for x in np.linspace(1500, 3000, 500)]
#prices

meta = {
    "x": "ETH",
    "y": "USDC",
    "request": "cumulative_liquidity",
    "request_unit": "y",
    "price_unit": "y/x",
    "amt_unit": "y",
}
#meta

data = {
    "orders": [{k:str(v) for k,v in o.items()} for o in orders],
    "prices": [str(x) for x in prices],
    "meta": meta,
}
#data

# fsave(data, "template.json", DATAPATH, json=True)

