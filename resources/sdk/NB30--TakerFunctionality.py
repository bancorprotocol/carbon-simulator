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

# # Taker Functionality [NB30]
#
# _this Notebook gives an overview over the taker functionality; for more streamlined examples see the following notebooks_
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

SDK = CarbonSDK(disclaimer=False, verbose=True, Tokens=T)
pairs, pairs_s = SDK.pairs(inclstr=True)
SDK.version().get("msg")

# ## Pair selection

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

# ## Market information

m = SDK.mGetMarketByPair(pair=pair)
m

# ## Trading examples

# #### `mPrepareTrade`

approx_price = SDK.roundsd(m.mid,3)
amount_tknb = 1000
approx_price, amount_tknb


r1 = SDK.mPrepareTrade(pair, SDK.SELL, tknb, amount_tknb/approx_price)
r1

r2 = SDK.mPrepareTrade(pair, SDK.BUY, tknb, amount_tknb/approx_price)
r2

r3 = SDK.mPrepareTrade(pair, SDK.SELL, tknq, amount_tknb)
r3

r4 = SDK.mPrepareTrade(pair, SDK.BUY, tknq, amount_tknb)
r4


# #### `mComposeTradeTransaction`

tx1 = SDK.mComposeTradeTransaction(**r1.cttkwargs)
tx1

tx2 = SDK.mComposeTradeTransaction(**r2.cttkwargs)
tx2

tx3 = SDK.mComposeTradeTransaction(**r3.cttkwargs)
tx3

tx4 = SDK.mComposeTradeTransaction(**r4.cttkwargs)
tx4

# #### Submit transactions

SDK.signsubmittx(tx1, sign=True)

SDK.signsubmittx(tx2, sign=True)

SDK.signsubmittx(tx3, sign=True)

SDK.signsubmittx(tx4, sign=True)


