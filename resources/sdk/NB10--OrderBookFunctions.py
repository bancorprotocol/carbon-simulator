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
# _this notebook is showcasing key order-book related functions; the actual order book code is in NB11_
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

try:
    pairs_sel = [s.strip() for s in pairs_s.split(",")]
    pairs_w()
except:
    pairs_w = DropdownManager(pairs_sel, defaultval="USDC/ETH")
    pairs_w()


try:
    inverse_w()
except:
    inverse_w = CheckboxManager(["inverse"], values=[1])
    inverse_w()

tknb,tknq = pairs_w.value.split("/")
if inverse_w.values[0]:
    tknb,tknq = tknq, tknb
pair = f"{tknb}/{tknq}"
pair

# #### `mHasLiquidityByPair` and `mHasLiquidityByPairs`

help(SDK.mHasLiquidityByPair)

help(SDK.mHasLiquidityByPairs)

SDK.mHasLiquidityByPair(pair=pair, AMMsells=tknb)

SDK.mHasLiquidityByPairs(pairs=pair)

SDK.mHasLiquidityByPairs(pairs="ETH/USDC, WBTC/USDC, WBTC/BNT")

# #### `mGetLiquidityByPair`

help(SDK.mGetLiquidityByPair)

(SDK.mGetLiquidityByPair(pair=pair, AMMsells=tknb),
 SDK.mGetLiquidityByPair(pair=pair, AMMsells=tknq))

SDK.mGetLiquidityByPair(pair="WBTC/BNT", AMMsells="BNT")

# #### `mGetRangeByPair`
#

help(SDK.mGetRangeByPair)

(SDK.mGetRangeByPair(pair=pair, AMMsells=tknb),
 SDK.mGetRangeByPair(pair=pair, AMMsells=tknq))

# #### `mGetRateLiquidityDepthByPair`

help(SDK.mGetRateLiquidityDepthByPair)

SDK.mGetRateLiquidityDepthByPair(rate=2400, pair=pair, AMMsells=tknb)

r = SDK.mGetRateLiquidityDepthByPair(rate=np.linspace(2400, 800), pair=pair, AMMsells=tknq)
plt.plot(r.rate, r.amount, color="red" if r.bidAsk=="ask" else "lawngreen")
plt.xlabel(f"{r.pair.slashpair} price ({r.pair.price_convention})")
plt.ylabel(f"liquidity ({r.unit})")
plt.title(r.bidAsk)
plt.grid()
r

r = SDK.mGetRateLiquidityDepthByPair(rate=np.linspace(2400, 3000), pair=pair, AMMsells=tknb)
plt.plot(r.rate, r.amount, color="red" if r.bidAsk=="ask" else "lawngreen")
plt.xlabel(f"{r.pair.slashpair} price ({r.pair.price_convention})")
plt.ylabel(f"liquidity ({r.unit})")
plt.title(r.bidAsk)
plt.grid()
r

# #### `mGetMarketByPair`
#
# The `mGetMarketByPair` endpoint is a summary endpoint allowing to retrieve key market information for a single pair at once. Note that the returned `MarketByPair` contains numerous properties over and beyond the primary data in the class.

# +
#help(SDK.mGetMarketByPair)

# +
#help(SDK.MarketByPair)
# -

m = SDK.mGetMarketByPair(pair=pair)
m

m.cpair, m.price_convention

m.mid, m.spread, m.spreadpc, m.inverted

m.liqBid, m.liqBidUnit, m.bidAMMSells, m.bidTraderSells 

m.liqAsk, m.liqAskUnit, m.askAMMSells, m.askTraderSells 


