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

# # Order Book [NB11]
#
# _this notebook allows to select a pair and a quote direction via the dropdown / checkbox, and then displays the order book_
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

SDK = CarbonSDK(disclaimer=False, verbose=False, Tokens=T)
pairs, pairs_s = SDK.pairs(inclstr=True)
SDK.version().get("msg")

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

liqa = SDK.mGetLiquidityByPair(pair=pair, AMMsells=tknb)
liqb = SDK.mGetLiquidityByPair(pair=pair, AMMsells=tknq)
assert liqa.amount > 0 and liqb.amount > 0, f"no liquidity in pair {liqa} {liqb}"

range_bid = SDK.mGetRangeByPair(pair=pair, AMMsells=tknq)
range_ask = SDK.mGetRangeByPair(pair=pair, AMMsells=tknb)
mid = 0.5*(range_bid.startRate+range_ask.startRate)
p_bid = np.linspace(mid, range_bid.endRate)
p_ask = np.linspace(mid, range_ask.endRate)
range_bid, range_ask, mid

db = SDK.mGetRateLiquidityDepthByPair(rate=p_bid, pair=pair, AMMsells=tknq)
da = SDK.mGetRateLiquidityDepthByPair(rate=p_ask, pair=pair, AMMsells=tknb)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.set_xlabel(f"Exchange rate ({db.pair.price_convention})")
ax1.plot(db.rate, db.amount, color="lawngreen", label="bid [LHS]")
ax1.set_ylabel(f"bid liquidity ({db.unit})")
ax2.plot(da.rate, da.amount, color="red", label="ask [RHS]")
ax2.set_ylabel(f"ask liquidity ({da.unit})")
plt.title(f"{db.pair.slashpair} asymmetric order book")
ax1.grid()

# The chart above shows the order book. Note that bid and ask books are shown on different axis and therefore **bid and ask levels are not comparable**.


