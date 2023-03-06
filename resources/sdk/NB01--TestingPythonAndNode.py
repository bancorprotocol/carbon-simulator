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

import requests
from carbonsdk import CarbonSDK, Tokens
print("{0.__name__} v{0.VERSION} ({0.DATE})".format(CarbonSDK))
# !node --version

# # Testing Python and Node [NB01]
#
# - https://nodejs.org/en/download/
# - https://www.makeuseof.com/nodejs-api-server-without-framework/
# - https://requests.readthedocs.io/en/latest/

# ## Endpoints

SDK = CarbonSDK(disclaimer=False)
n = SDK.c2s # camel case to snake case

# ### Example code

# #### Call using `req`
# the only difference between `req` and `req0` is that the leading `api` must be omitted)

help(SDK.req)

r = SDK.req("scall/qplus", params={"a":3, "b":5}, method=SDK.POST)
r.json()

# #### Call using `call`
# call only works for the `scall` / `ascall` subapis; which one is chosen, and how results are returned, depends on the `sync` parameter; also whether to GET or POST can be implied from the existence of the `params` parameter

help(SDK.call)

r = SDK.call("qplus", params={"a":3, "b":5}, sync=True)
r.json()

# ### Endpoints that have already been wrapped

r = SDK.getMatchActions(amountWei=None, tradeByTargetAmount=None, orders=None, sync=True)
r.json()

r = SDK.startDataSync(sync=True)
r.json()

r = SDK.isInitialized(sync=True)
r.json()

r = SDK.pairs(sync=True)
r.json()

r = SDK.hasLiquidityByPair(sourceToken=None, targetToken=None, sync=True)
r.json()

r = SDK.getLiquidityByPair(sourceToken=None, targetToken=None, sync=True)
r.json()

r = SDK.getUserStrategies(user=None, sync=True)
r.json()

r = SDK.getMatchParams(sourceToken=None, targetToken=None, amount=None, tradeByTargetAmount=None, sync=True)
r.json()

r = SDK.getTradeData(sourceToken=None, targetToken=None, amount=None, tradeByTargetAmount=None, filter=None, sync=True)
r.json()

r = SDK.getTradeDataFromActions(sourceToken=None, targetToken=None, tradeByTargetAmount=None, actionsWei=None, sync=True)
r.json()

r = SDK.composeTradeByTargetTransaction(sourceToken=None, targetToken=None, tradeActions=None, 
                                        deadline=None, maxInput=None, overrides=None, sync=True)
r.json()

r = SDK.composeTradeBySourceTransaction(sourceToken=None, targetToken=None, tradeActions=None, 
                                        deadline=None, minReturn=None, overrides=None, sync=True)
r.json()

r = SDK.createBuySellStrategy(baseToken=None, quoteToken=None, buyPriceLow=None, buyPriceHigh=None, buyBudget=None, 
                              sellPriceLow=None, sellPriceHigh=None, sellBudget=None, overrides=None, sync=True)
r.json()

r = SDK.updateStrategy(strategyId=None, encoded=None, baseToken=None, quoteToken=None, update=None, 
                       buyMarginalPrice=None, sellMarginalPrice=None, overrides=None, sync=True)
r.json()

r = SDK.deleteStrategy(strategyId=None, sync=True)
r.json()

r = SDK.getRateLiquidityDepthByPair(sourceToken=None, targetToken=None, rate=None, sync=True)
r.json()

r = SDK.getMinRateByPair(sourceToken=None, targetToken=None, sync=True)
r.json()

r = SDK.getMaxRateByPair(sourceToken=None, targetToken=None, sync=True)
r.json()

# ### Endpoints not yet wrapped

# +
#raise
# -

# ## Testing the SDK Class

SDK = CarbonSDK(disclaimer=False)

r = SDK.version()
r.json()

r = SDK.req("scall/meh", params={})
r.json()

rid = SDK.mul(3,5)
rid

rid = SDK.plus(3,5)
rid

r = SDK.qmul(3,5, sync=True)
r.json()

rid = SDK.qmul(3,5)
rid

r = SDK.qplus(3,5, sync=True)
r.json()

rid = SDK.qplus(3,5)
rid

result = SDK.result(rid)
result

result = SDK.result(rid)
result

try:
    result = SDK.result("123")
except SDK.UnknownReqIdError as e:
    print(e)

r = SDK.req0("api/result/1677857523771")
r.json()

# +
#raise
# -

# ## Testting the SDKToken Class
#

Tokens["CREAM"]

str(Tokens.YFI)

Tokens.ETH

# +
#Tokens._all

# +
#Tokens
# -

str(Tokens)


# ## Testing the Server


import requests
PORT="3118"
TOKEN = "carbontoken"

r = requests.get(f"http://localhost:{PORT}/")
r.json()

# ### Authorization

r = requests.post(f"http://localhost:{PORT}/api/scall/meh")
r

r = requests.post(f"http://localhost:{PORT}/api/ascall/meh")
r

r = requests.get(f"http://localhost:{PORT}/api/scall/result/123")
r

r = requests.post(f"http://localhost:{PORT}/api/scall/meh", headers={"token": TOKEN})
r

r = requests.post(f"http://localhost:{PORT}/api/ascall/meh", headers={"token": TOKEN})
r

r = requests.get(f"http://localhost:{PORT}/api/scall/result/123", headers={"token": TOKEN})
r

# ### Sync

r = requests.post(f"http://localhost:{PORT}/api/scall/meh", headers={"token": TOKEN}, json={"a":1})
r.json()

r = requests.post(f"http://localhost:{PORT}/api/scall/plus", headers={"token": TOKEN}, json={"a":1, "b":2})
r.json()

r = requests.post(f"http://localhost:{PORT}/api/scall/mul", headers={"token": TOKEN}, json={"a":3, "b":5})
r.json()

# ### Async

r = requests.post(f"http://localhost:{PORT}/api/ascall/meh", headers={"token": TOKEN}, json={"a":1, "b":2})
r.json()

r = requests.post(f"http://localhost:{PORT}/api/ascall/plus", headers={"token": TOKEN}, json={"a":1, "b":2})
r.json()

r = requests.post(f"http://localhost:{PORT}/api/ascall/mul", headers={"token": TOKEN}, json={"a":3, "b":4})
r.json()

r = requests.post(f"http://localhost:{PORT}/api/ascall/plus", headers={"token": TOKEN}, json={"a":3, "b":4})
r.json()

rr = requests.get(f"http://localhost:{PORT}/api/result/{r.json()['reqid']}", headers={"token": TOKEN})
rr.json()


# ## Converting token addresses to symbols

fa = Tokens.byaddr

pairs_raw = [
  [
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    '0xdAC17F958D2ee523a2206206994597C13D831ec7'
  ],
  [
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
  ],
  [
    '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    '0xdAC17F958D2ee523a2206206994597C13D831ec7'
  ],
  [
    '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
  ],
  [
    '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
  ],
  [
    '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
  ],
  [
    '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0'
  ],
  [
    '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
  ],
  [
    '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
  ]
]

pairs = [ [fa(pair[0]).T, fa(pair[1]).T] for pair in pairs_raw]
pairs

tokens = {fa(tkn).T for pair in pairs_raw for tkn in pair}
tokens

for t in tokens:
    print(f"const {t:5} = '{Tokens[t].a}'")



raise




