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

from carbon import CarbonSimulatorUI
from carbon import __version__ as cversion
import numpy as np
from matplotlib import pyplot as plt
from collections import namedtuple
print (f"Carbon Version v{cversion}")

# # Carbon Simulation - Demo 3-2
#
# In this demo we look at an **order book**

# Set up the similation, with the pair ETHUSDC as default

TKNB = "ETH"
TKNQ = "USDC"

# A number of other preparations here

orders_nt = namedtuple("orders_nt", 'tkn, amt, p_start, p_end')


def midpoints(r):
    """
    calculates the midpoints: (r0, r1, r2, ...) -> (avg(r0,r1), avg(r1,r2), ...)
    """
    return np.array([0.5*(s1+s2) for s1,s2 in zip(r, r[1:])])


def safemul(x1, x2):
    "returns x1*x2, or 0 if raise"
    try:
        return x1*x2
    except:
        print("[safemul] error", x1, x2)
        return 0


def effective_price_f(tkn, size):
    """
    returns the price at which `tkn` can be sold in `size` (None if out of liquidity)
    """
    try:
        result = Sim.amm_sells(tkn, size, execute=False)
        price = result["trades"].iloc[0]["price"]
        print(f"[effective_price_f] trading size={size} price={price}")
        return price
    except:
        return None


def run_calculation():
    """helper function: runs the calculation using global variables"""
    effective_prices = [
        effective_price_f("ETH", size) for size in trade_sizes
    ]
    print(effective_prices)
    token_amounts = [
        safemul(size, price) for size, price in zip(trade_sizes, effective_prices)
    ]
    marg_token_amounts = np.diff(token_amounts)
    marg_prices = [
        amt / size for amt, size in zip(marg_token_amounts, marg_trade_sizes)
    ]
    return effective_prices, token_amounts, marg_token_amounts, marg_prices


def plot_token_amount_chart():
    """helper function: plots the chart using global variables"""
    plt.plot(trade_sizes, token_amounts, label="Token amount")
    plt.plot(trade_sizes2, marg_token_amounts, label="Marginal token amount")
    plt.title("Token amount against trade size")
    plt.xlabel(f"Trade Size ({TKNB})")
    plt.ylabel(f"Token Amount ({TKNQ})")
    plt.grid()
    plt.legend()
    return "plotted marginal and total tokens received against trade size"


def plot_price_chart():
    """helper function: plots the chart using global variables"""
    plt.plot(trade_sizes, effective_prices, label="Effective price")
    plt.plot(trade_sizes2, marg_prices, label="Marginal price")
    plt.title("Price against trade size")
    plt.xlabel(f"Trade Size ({TKNB})")
    plt.ylabel(f"Effective Price ({TKNQ} per {TKNB})")
    plt.grid()
    plt.legend()
    return "plotted marginal and effective price against trade size"


def plot_reverse_price_chart():
    """helper function: plots the chart using global variables"""
    plt.plot(effective_prices, trade_sizes, label="Effective price")
    plt.title("Trade size against effective price")
    plt.xlabel(f"Effective Price ({TKNQ} per {TKNB})")
    plt.ylabel(f"Trade Size ({TKNB})")
    plt.grid()
    #plt.legend()
    return "plotted trade size against effective price"


def plot_reverse_marg_price_chart():
    """helper function: plots the chart using global variables"""
    plt.plot(marg_prices, trade_sizes2, label="Marginal price")
    plt.title("Trade size against marginal price")
    plt.xlabel(f"Marginal Price ({TKNQ} per {TKNB})")
    plt.ylabel(f"Trade Size ({TKNB})")
    plt.grid()
    #plt.legend()
    return "plotted trade size against effective price"


def plot_orderbook_chart(xmin, xmax, ymax):
    """helper function: plots the chart using global variables"""
    dp = np.diff(marg_prices)
    y = midpoints(marg_token_amounts) / dp
    plt.plot(midpoints(marg_prices), y, label="Orders")
    plt.title("Order Book")
    plt.xlabel(f"Marginal Price ({TKNQ} per {TKNB})")
    plt.ylabel(f"Liquidity Size ({TKNB})")
    plt.grid()
    #plt.legend()
    plt.xlim(xmin,xmax)
    plt.ylim(0,ymax)
    return "plotted order book"


# ## Order book calculations

Sim = CarbonSimulatorUI(pair=f"{TKNB}{TKNQ}", verbose=False, raiseonerror=True)
Sim

orders = tuple(
    orders_nt("ETH", 10, 2000, 2000+x*25) for x in range(21)
)
orders[:2]

orders = tuple([
    orders_nt("ETH", 100, 2000, 3000),
    orders_nt("ETH", 30, 2400, 2500),
])

max_liquidity = 0.99*sum(o.amt for o in orders)
print("max liquidity", max_liquidity)
trade_sizes = np.linspace(0,max_liquidity, 51)
marg_trade_sizes = np.diff(trade_sizes)
trade_sizes2 = midpoints(trade_sizes)
trade_sizes[0] = 0.0000001
#trade_sizes[:3]

for o in orders:
    Sim.add_order(o.tkn, o.amt, o.p_start, o.p_end)
Sim.state()["orders"]

Sim.amm_sells("ETH", trade_sizes[3], execute=False)

effective_prices, token_amounts, marg_token_amounts, marg_prices = run_calculation()

trade_sizes

# +
#Sim.state()["trades"].query("aggr==True")
# -

effective_prices

plot_token_amount_chart()

plot_price_chart()


# +
#plot_reverse_price_chart()

# +
#plot_reverse_marg_price_chart()
# -

plot_orderbook_chart(2000, 3000, None)


