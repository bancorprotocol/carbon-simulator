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

from carbon.sdk import CarbonSDK, Tokens as T
#from carbon import CarbonOrderUI, CarbonSimulatorUI
from carbon.helpers.widgets import CheckboxManager, DropdownManager, PcSliderManager
from matplotlib import pyplot as plt
import numpy as np
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSDK))
# !node --version

# # Order Book [NB10]
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

SDK = CarbonSDK(disclaimer=False, verbose=False, Tokens=T)
SDK.version().get("msg")

# ## Order book related functions

# #### `pairs`
#

pairs, pairs_s = SDK.pairs(inclstr=True)
pairs_s

# #### `mHasLiquidityByPair` and `mHasLiquidityByPairs`

help(SDK.mHasLiquidityByPair)

help(SDK.mHasLiquidityByPairs)

SDK.mHasLiquidityByPair(pair="ETH/USDC", AMMsells="ETH")

SDK.mHasLiquidityByPairs(pairs="ETH/USDC")

SDK.mHasLiquidityByPairs(pairs="ETH/USDC, WBTC/USDC, WBTC/BNT")

# #### `mGetLiquidityByPair`

help(SDK.mGetLiquidityByPair)

(SDK.mGetLiquidityByPair(pair="ETH/USDC", AMMsells="ETH"),
 SDK.mGetLiquidityByPair(pair="ETH/USDC", AMMsells="USDC"))

SDK.mGetLiquidityByPair(pair="WBTC/BNT", AMMsells="BNT")

# #### `mGetRangeByPair`
#

help(SDK.mGetRangeByPair)

(SDK.mGetRangeByPair(pair="ETH/USDC", AMMsells="ETH"),
 SDK.mGetRangeByPair(pair="ETH/USDC", AMMsells="USDC"))

# #### `mGetRateLiquidityDepthByPair`

help(SDK.mGetRateLiquidityDepthByPair)

SDK.mGetRateLiquidityDepthByPair(rate=2400, pair="ETH/USDC", AMMsells="ETH")

r = SDK.mGetRateLiquidityDepthByPair(rate=np.linspace(2400, 800), pair="ETH/USDC", AMMsells="USDC")
# plt.plot(r.rate, r.amount, color="red" if r.bidAsk=="ask" else "lawngreen")
# plt.xlabel(f"{r.pair.slashpair} price ({r.pair.price_convention})")
# plt.ylabel(f"liquidity ({r.unit})")
# plt.title(r.bidAsk)
# plt.grid()
r

r = SDK.mGetRateLiquidityDepthByPair(rate=np.linspace(2400, 3000), pair="ETH/USDC", AMMsells="ETH")
# plt.plot(r.rate, r.amount, color="red" if r.bidAsk=="ask" else "lawngreen")
# plt.xlabel(f"{r.pair.slashpair} price ({r.pair.price_convention})")
# plt.ylabel(f"liquidity ({r.unit})")
# plt.title(r.bidAsk)
# plt.grid()
r

# ## Order book examples

try:
    pairs_sel = [s.strip() for s in pairs_s.split(",")]
    pairs_w()
except:
    pairs_w = DropdownManager(pairs_sel)
    pairs_w()


try:
    inverse_w()
except:
    inverse_w = CheckboxManager(["inverse"])
    inverse_w()

tknb,tknq = pairs_w.value.split("/")
if inverse_w.values[0]:
    tknb,tknq = tknq, tknb
pair = f"{tknb}/{tknq}"
pair

range_ask = SDK.mGetRangeByPair(pair=pair, AMMsells=tknq)
range_bid = SDK.mGetRangeByPair(pair=pair, AMMsells=tknq)
mid = 0.5*(range_bid.startRate+range_ask.startRate)
p_bid = np.linspace(mid, range_bid.endRate)
p_ask = np.linspace(mid, range_ask.endRate)
#range_bid, range_ask, mid

db = SDK.mGetRateLiquidityDepthByPair(rate=p_bid, pair=pair, AMMsells=tknq)
da = SDK.mGetRateLiquidityDepthByPair(rate=p_ask, pair=pair, AMMsells=tknq)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.set_xlabel(f"Exchange rate ({db.pair.price_convention})")
ax1.plot(db.rate, db.amount, color="lawngreen", label="bid [LHS]")
ax1.set_ylabel(f"bid liquidity ({db.unit})")
ax2.plot(da.rate, da.amount, color="red", label="ask [RHS]")
ax2.set_ylabel(f"ask liquidity ({da.unit})")
plt.title(f"{db.pair.slashpair}")
ax1.grid()


