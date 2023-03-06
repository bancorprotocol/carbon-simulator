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
from carbon import CarbonOrderUI, CarbonSimulatorUI, CarbonPair as P
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSDK))
# !node --version

# # API Testing [NB02]
#
# _this is currently the main reference notebook, showcasing all API endpoints_
#
# In order to start the server, please run
#
#     source /Volumes/Private/bin/sdkserver
#     node server/sdkserver.mjs

SDK = CarbonSDK(disclaimer=True, verbose=True, Tokens=T)
SDK.version().get("msg")

# ## Generic API calls

# ### Call using `req`
# the only difference between `req` and `req0` is that the leading `api` must be omitted)

help(SDK.req)

r = SDK.req("scall/qplus", params={"a":3, "b":5}, method=SDK.POST)
r.json()

# ### Call using `call`
# call only works for the `scall` / `ascall` subapis; which one is chosen, and how results are returned, depends on the `sync` parameter; also whether to GET or POST can be implied from the existence of the `params` parameter

help(SDK.call)

r = SDK.call("qplus", params={"a":3, "b":5}, sync=True)
r.json()

# ## Market information endpoints

# #### `pairs` -- information about all available pairs
#
# The `pairs` endpoint provides a list of all available pairs, or rather their contract addresses. If a `Tokens` container is available on the object the addresses are converted into token objects (where available).

pairs, pairs_s = SDK.pairs(inclstr=True)
print(pairs_s)
pairs[:1]

# #### `hasLiquidityByPair` -- whether a given pair has any liquidity

SDK.hasLiquidityByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a)

SDK.hasLiquidityByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a)

# #### `mHasLiquidityByPair` -- whether a given pair has any liquidity (modified)

SDK.mHasLiquidityByPair(pair=P("ETH/USDC"), AMMsells="ETH")

SDK.mHasLiquidityByPair(pair=P("ETH/USDC"), AMMsells="USDC")

# #### mHasLiquidityByPairs

SDK.mHasLiquidityByPairs(pairs=[P("ETH/USDC"), P("BNT/USDT"), P("LINK/AAVE")])

SDK.mHasLiquidityByPairs(pairs=["ETH/USDC", "BNT/USDT", "LINK/AAVE"])

SDK.mHasLiquidityByPairs(pairs="ETH/USDC, BNT/USDC, LINK/AAVE")

SDK.mHasLiquidityByPairs(pairs=pairs_s)

# #### `getLiquidityByPair` -- the amount of liquidity in a pair
#
# in units of the target token

SDK.getLiquidityByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a)

SDK.getLiquidityByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a)

# #### `mGetLiquidityByPair` -- the amount of liquidity in a pair (modified)
#
# this function -- like all other `mGet` functions -- is modified to be better in line with the conventions of the Carbon Simulator; it returns a `PairLiquidity` object that is also used for `mGetRateLiquidityDepthByPair`'; to indicate that the liquidity here is the total liquidity the `rate` field is set to zero.

SDK.mGetLiquidityByPair(pair=P("ETH/USDC"), AMMsells="ETH")

SDK.mGetLiquidityByPair(pair=P("ETH/USDC"), AMMsells="USDC")

# #### `getMinRateByPair` and `getMaxRateByPair` -- get the min and max exchange rates
#
# gets the minimal and maximal rate availble in posisitions in this pair in this direction (used to determine the boundaries for the subsequenct calls to `getRateLiquidityDepthByPair`; `sourceToken` is base token and `targetToken` is quote token, ie in other words the prices are expressed in `targetToken` units
#

SDK.getMinRateByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a)

SDK.getMaxRateByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a)

SDK.getMinRateByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a)

SDK.getMaxRateByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a)

# #### `mGetRangeByPair` -- combining min and max rate
#
# The `mGetRangeByPair` combines min and max rate and uses the correct quote direction of the `CarbonPair`. It requires a `TokenContainer` object that allows to associate the ticker with the token address.

SDK.mGetRangeByPair(pair=P("ETH/USDC"), AMMsells="ETH")

SDK.mGetRangeByPair(pair=P("ETH/USDC"), AMMsells="USDC")

# #### `getRateLiquidityDepthByPair` -- get the liquidity at a certain exchange rate
#
# used to determine the liquidity depth chart; use `getMinRateByPair` and `getMaxRateByPair` to determine range; rate is given in target token per source token, and the amount in target token; the AMM buys (and trader sells) the source token

(SDK.getLiquidityByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a),
 SDK.getRateLiquidityDepthByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a, rate=800),
 SDK.getRateLiquidityDepthByPair(sourceTokenAddr=T.ETH.a, targetTokenAddr=T.USDC.a, rate=2000))

(
 SDK.getLiquidityByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a),    
 SDK.getRateLiquidityDepthByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a, rate=1/3000),
 SDK.getRateLiquidityDepthByPair(sourceTokenAddr=T.USDC.a, targetTokenAddr=T.ETH.a, rate=1/2550))

# #### `mGetRateLiquidityDepthByPair` -- get the liquidity at a certain exchange rate (modified)
#
# returns a `PairLiquidity` object like `mGetLiquidityByPair`

SDK.mGetRateLiquidityDepthByPair(rate=3000, pair=P("ETH/USDC"), AMMsells="ETH")

SDK.mGetRateLiquidityDepthByPair(rate=2550, pair="ETH/USDC", AMMsells="ETH")

SDK.mGetRateLiquidityDepthByPair(rate=2000, pair=P("ETH/USDC"), AMMsells="USDC")

SDK.mGetRateLiquidityDepthByPair(rate=800, pair=P("ETH/USDC"), AMMsells="USDC")

SDK.mGetRateLiquidityDepthByPair(rate=[800, 1000, 1100], pair=P("ETH/USDC"), AMMsells="USDC")

# ## Maker-user information endpoints
#
# _Maker users_ are user that provide liquidity to the market, ie who create strategies. Those endpoint look at their portfolio information.

# #### `addr` -- get the address of the wallet in the SDK server (effectively user address)

SDK.req("addr").json()

sdkaddr = SDK.addr()
sdkaddr,

# #### `getUserStrategies` -- get all strategies of the user
#
# returns all strategies for a given user (default: the waller related to the SDK server); use `reformatStrategy` to convert the returned value into types more reasonable for Python analysis (notably, `BigNumber` dicts to `int`)

data = SDK.getUserStrategies(user=sdkaddr)
print("Number of strategies:", len(data))
print("Strategy ids", [SDK.bn2int(d["id"]) for d in data])
data[0]

# The strategies can be imported into the Carbon Simulator into the `CarbonOrderUI` class and into the `CarbonSimulatorUI` class

obuy, osell = CarbonOrderUI.from_SDK(data[0])
obuy, osell

Sim = CarbonSimulatorUI()
o = Sim.add_fromsdk(data[0], 6)["orders"]
o

data

# #### `mGetUserStrategies` -- get all strategies of the user (modified)
#
# applies `reformateStrategy` to all strategies

data = SDK.mGetUserStrategies(user=sdkaddr)
data

SDK.reformatStrategy(data[0])["encoded"]

# ## Maker-user action endpoints
#
# Those endpoints allow maker users to create, modify and delete their strategies. Note that all active endpoints return unsigned transactions. Those are then submitted to the endpoint `signsubmittx` to be signed and submitted. If `sign` is `True`, the transaction is signed using the server wallet private key (with the obvious security implications). Alternatively an already signed transaction can be submitted. 

# #### `createBuySellStrategy` -- creates a strategy
#
#

data = SDK.createBuySellStrategy(baseToken=T.ETH.a, quoteToken=T.USDC.a, 
                              buyPriceLow =1500, buyPriceHigh =1600, buyBudget =500,    # buy 500 USDC worth of ETH from 1500..1600
                              sellPriceLow=2500, sellPriceHigh=2600, sellBudget=   1,   # sell 1 ETH from 2500..2600
                              overrides=None)

SDK.signsubmittx(data, sign=True)

# #### check user strategy IDs

data = SDK.getUserStrategies(user=sdkaddr)
ids = [SDK.bn2int(d["id"]) for d in data]
print("Number of strategies:", len(data))
print("Strategy ids", ids)

# #### `updateStrategy` -- updates a strategy [yet to be connected]

r = SDK.updateStrategy(strategyId=None, encoded=None, baseToken=None, quoteToken=None, update=None, 
                       buyMarginalPrice=None, sellMarginalPrice=None, overrides=None, sync=True)
r.json()

# #### `deleteStrategy` -- deletes a strategy
#
# Note: this deletes the strategy that has been created above. If this fails with an out-of-gas error then the reason may be that the strategy has not been created yet. Note that in this case the server may crash which is something we are working on. The last cell below shows, again, the user strategies.

data = SDK.deleteStrategy(strategyId=ids[-1])
data

# +
#SDK.signsubmittx(data, sign=True)
# -

data = SDK.getUserStrategies(user=sdkaddr)
ids = [SDK.bn2int(d["id"]) for d in data]
print("Number of strategies:", len(data))
print("Strategy ids", ids)

# **Note the weird error message if you try to delete a strategy that does not exist**

data = SDK.deleteStrategy(strategyId=1234567890)
rr = SDK.signsubmittx(data, sign=True)
rr

# ## Taker-user (trader) action endpoints
#
# Those endpoints allow taker users (ie traders) to trade against existing liquidity
#

# ### Integrated endpoint

# #### `getTradeData` -- integrated function (here used "by source")
#
# The endpoint `getTradeData` is the only endpoint usually needed to compose a trade. It internally calls the functions `tbd`. Those functions are also exposed as individual endpoints which allows to optimized the process and to obtain a more reactive code.
#

data = SDK.getTradeData(sourceToken=T.WBTC.a, targetToken=T.USDC.a, amount=0.001, tradeByTargetAmount=False, filter=None)
tradeActions = [SDK.bn2intd(d) for d in data["tradeActions"]]
print(tradeActions)
data

# #### `composeTradeBySourceTransaction` -- create transaction "by source"
#
# Important: if this one fails there may be an issue with the approval. Need to approve the token first which can be done on the web app.
#
# **TODO:HOW DO I SEND ETH WITH THE TRANSACTION?**

data = SDK.composeTradeBySourceTransaction(sourceToken=T.WBTC.a, targetToken=T.USDC.a, tradeActions=tradeActions, 
                                        deadline=None, minReturn=None, overrides=None)
data

data = SDK.signsubmittx(data, sign=True)
data 

data = SDK.composeTradeByTargetTransaction(sourceToken=T.WBTC.a, targetToken=T.USDC.a, tradeActions=tradeActions, 
                                        deadline=None, maxInput=None, overrides=None)
data

# #### `getTradeData` -- integrated function (here used "by target")
#
# **TODO**

# #### `composeTradeByTargetTransaction` -- create transaction "by target"
#
# **TODO**

# ### Step-by-step endpoints
#
# **THE BELOW DESCRIPTION IS NOT CORRECT, BUT YOU DO NOT GENERALLY NEED THE STEP BY STEP ANYWAY**

# #### `getMatchParams` -- order matching step 1
#
# This is the first step in the matching process executed by `getTradeData`. It takes the desired trade, and returns amongst other data the dict of `orders` against which to much. This dict has as key the `orderid` and as value the order parameters `AByz`. The `orders` part of the returned dict can be formatted into Python suitable values (notably, `BigNumber` to `int`) using `reformatOrders`. A single order (and any dict for that matter) can be converted using `bn2intd`.

r = SDK.getMatchParams(sourceToken=T.ETH.a, targetToken=T.USDC.a, amount=1, tradeByTargetAmount=False, sync=True)
d = r.json()["data"]
d

SDK.reformatOrders(d["orders"])

SDK.bn2intd(tuple(d["orders"].values())[0])

# #### `getMatchActions` -- order matching step 2
#
# the parameter `orders` is a list of encoded strategies (yzAB), in the same format as the one returned by `getMatchParams`. `tradeByTargetAmount` determines whether by source or by target, and `amountWei` is the respective source or target amount in token wei. It returns an array of trade actions `[{id, input, output}, ...]`. This function does work on arbitrary order data which does not necessarily correspond to actual orders on-chain. This function returns the trade actions.

r = SDK.getMatchActions(amountWei=10000, tradeByTargetAmount=None, orders=None, sync=True)
r.json()

# #### `composeTradeByTargetTransaction` and `composeTradeBySourceTransaction` -- order matching step 3
#
# Those functions take the trade actions returned from `getMatchActions` and it returns `????`

data = SDK.composeTradeByTargetTransaction(sourceToken=T.ETH.a, targetToken=T.USDC.a, tradeActions={}, 
                                        deadline=None, maxInput=None, overrides=None)
data

SDK.composeTradeBySourceTransaction(sourceToken=T.ETH.a, targetToken=T.USDC.a, tradeActions={}, 
                                        deadline=None, minReturn=None, overrides=None)

# #### `getTradeDataFromActions` -- order matching step 4
#
# ???

SDK.getTradeDataFromActions(sourceToken=T.ETH.a, targetToken=T.USDC.a, tradeByTargetAmount=False, actionsWei=[])


