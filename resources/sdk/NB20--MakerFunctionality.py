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
from carbon import CarbonOrderUI, CarbonSimulatorUI
from carbon.helpers.widgets import CheckboxManager, DropdownManager, PcSliderManager
from matplotlib import pyplot as plt
import numpy as np
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSDK))
# !node --version

# # Maker Functionality [NB20]
#
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

SDK = CarbonSDK(disclaimer=False, verbose=False, Tokens=T)
pairs, pairs_s = SDK.pairs(inclstr=True)
sdkaddr = SDK.addr()
print(sdkaddr)
SDK.version().get("msg")

# ## Pair selection

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

SDK.roundsd(m.lastBid,6), SDK.roundsd(m.bestBid,6), SDK.roundsd(m.mid,6), SDK.roundsd(m.bestAsk,6), SDK.roundsd(m.lastAsk,6)

(SDK.roundsd(m.liqBid,4), m.liqBidUnit, SDK.roundsd(m.liqAsk,4), m.liqAskUnit)

# ## Create strategy

# #### `mCreateStrategy`

try:
    strat_w()
except:
    strat_w = PcSliderManager(choices=["buyStart", "buyEnd", "sellStart", "sellEnd"], values=[0, 1, 0, 1])
    strat_w()

sellAmountTknB =     5
buyAmountTknQ  = 10000
x = strat_w.values
print(f"pair = {pair}, TknB={tknb}, TknQ={tknq}")
print(f"buy  {tknb} {SDK.roundsd(m.ibid(x[0]),6)} down to {SDK.roundsd(m.ibid(x[1]),6)}   [{sellAmountTknB} {tknq}] ")
print(f"sell {tknb} {SDK.roundsd(m.iask(x[2]),6)}      to {SDK.roundsd(m.iask(x[3]),6)}   [{buyAmountTknQ} {tknb}] ")

x = strat_w.values
tx = SDK.mCreateStrategy(
    pair, 
    buyRangeStart  = m.ibid(x[0]), buyRangeEnd  = m.ibid(x[1]), buyAmountTknQ = buyAmountTknQ, 
    sellRangeStart = m.iask(x[2]), sellRangeEnd = m.iask(x[3]), sellAmountTknB = sellAmountTknB, 
    overrides = None)
tx

try:
    submit_w()
except:
    submit_w = CheckboxManager(["submit"], values=[0])
    submit_w()

if submit_w.values[0]: 
    r = SDK.signsubmittx(tx, sign=True)
else:
    r = "check box above to submit"
r

# ## Review strategies

# + tags=[]
data = SDK.mGetUserStrategies(user=sdkaddr)
data[0]
# -

d, de=data[0], data[0].encoded
print(de.order1.descr)
print(de.descr[1])
print(d.descr[1])
f"buying {d.baseToken} @", de.order1.p_start, de.order1.p_end, f"{d.quoteToken} per {d.baseToken}"

d, de=data[0], data[0].encoded
print(de.order0.descr)
print(de.descr[0])
print(d.descr[0])
f"selling {d.baseToken} @", 1/de.order0.p_start, 1/de.order0.p_end, f"{d.quoteToken} per {d.baseToken}"

print(f"Number of strategies: {len(data)}")

Sim = CarbonSimulatorUI(verbose=False, raiseonerror=True)
for d in data:
    Sim.add_fromsdk(d, 6)
Sim.state()["orders"]

# ## Delete strategies

stratids = [d["id"] for d in data]
try:
    delete_w()
except:
    delete_w = CheckboxManager(stratids)
    delete_w()

try:
    submitd_w()
except:
    submitd_w = CheckboxManager(["submit delete"], values=[0])
    submitd_w()

for cid, ds in zip(stratids, delete_w.values):
    if ds:
        data = SDK.deleteStrategy(strategyId=cid)
        #print(data)
        if submitd_w.values[0]:
            result = SDK.signsubmittx(data, sign=True)
            print(f"Deleteting strategy {cid}: ", result)
            delete_w = None
        else:
            print(f"Would delete strategy {cid} if box was ticked ")



