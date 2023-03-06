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

# + tags=[]
from carbon.sdk import CarbonSDK, Tokens as T
#from carbon import CarbonOrderUI, CarbonSimulatorUI
from carbon.helpers.widgets import CheckboxManager, DropdownManager, PcSliderManager
from matplotlib import pyplot as plt
import numpy as np
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSDK))
# !node --version
# -

# # Single Trades [NB31]
#
# _allows to choose a market, retrieves market information, and then submits a trade_
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

# + tags=[]
SDK = CarbonSDK(disclaimer=False, verbose=False, Tokens=T)
pairs, pairs_s = SDK.pairs(inclstr=True)
SDK.version().get("msg")
# -

# ## Pair selection

# + jupyter={"source_hidden": true}
try:
    pairs_sel = [s.strip() for s in pairs_s.split(",")]
    pairs_w()
except:
    pairs_w = DropdownManager(pairs_sel, defaultval="USDC/ETH")
    pairs_w()

# + jupyter={"source_hidden": true}
try:
    inverse_w()
except:
    inverse_w = CheckboxManager(["inverse"], values=[1])
    inverse_w()

# + jupyter={"source_hidden": true}
tknb,tknq = pairs_w.value.split("/")
if inverse_w.values[0]:
    tknb,tknq = tknq, tknb
pair = f"{tknb}/{tknq}"
pair
# -

# ## Market information

# + tags=[]
m = SDK.mGetMarketByPair(pair=pair)
m

# + tags=[]
print(f"bid/mid/ask = {SDK.roundsd(m.bestBid,6)}/{SDK.roundsd(m.mid,6)}/{SDK.roundsd(m.bestAsk,6)}")
print(f"liquidity = {SDK.roundsd(m.liqBid,4)} {m.liqBidUnit} bid, {SDK.roundsd(m.liqAsk,4)} {m.liqAskUnit} ask")
# -

# ## Trading settings

# + tags=[]
m.cpair

# + jupyter={"source_hidden": true}
try:
    bq_w()
except:
    bq_w = DropdownManager(["Base Token", "Quote Token"], defaultval="Base Token")
    bq_w()
tkn = m.cpair.tknb if bq_w.value == "Base Token" else m.cpair.tknq

# + jupyter={"source_hidden": true}
try:
    buysell_w()
except:
    buysell_w = DropdownManager(["Buy", "Sell"], defaultval="Sell")
    buysell_w()
buysell = SDK.SELL if buysell_w.value == "Sell" else SDK.BUY

# + jupyter={"source_hidden": true}
print(f"Your choice: {buysell_w.value} {tkn} against {m.cpair.other(tkn)} [market = {m.pair}]")

# + tags=[]
amount = 0.01
# -

# #### `mPrepareTrade`

# + tags=[]
trade = SDK.mPrepareTrade(pair, buysell, tkn, amount)
trade
# -

trade.actionsTokenRes

# #### `mComposeTradeTransaction`

# + tags=[]
tx = SDK.mComposeTradeTransaction(**trade.cttkwargs)
tx
# -

# #### `signsubmittx`

# + tags=[]
try:
    submit_w()
except:
    submit_w = CheckboxManager(["submit"], values=[0])
    submit_w()

# + tags=[]
if submit_w.values[0]: 
    r = SDK.signsubmittx(tx, sign=True)
else:
    r = "check box above to submit"
r

# + jupyter={"source_hidden": true}

