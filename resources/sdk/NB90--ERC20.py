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

# # ERC20 [NB90]
#

SDK = CarbonSDK(disclaimer=False)
SDK.req("/addr").json()

addr = SDK.req("/addr").json()["data"]
addr

# ## Wrapped API calls

SDK.getERC20Balance([T.USDC, T.USDT, T.WBTC], addr)

SDK.getERC20Decimals([T.USDC, T.USDT, T.WBTC])

SDK.getERC20Symbol([T.USDC, T.USDT, T.WBTC])

SDK.getERC20Symbol([T.USDC.a, T.USDT.a, T.WBTC.a])

# ## Direct API calls

r = SDK.req("/erc20/hello", params={"tokens": [T.USDC.a, T.USDT.a, T.BNT.a]})
r.json()

r = SDK.req("/erc20/decimals", params={"tokens": [T.USDC.a, T.USDT.a, T.BNT.a]})
r.json()

r = SDK.req("/erc20/balance_of", params={"tokens": [T.USDC.a, T.USDT.a, T.BNT.a], "address": addr})
r.json()

r = SDK.req("/erc20/symbol", params={"tokens": [T.USDC.a, T.USDT.a, T.BNT.a]})
r.json()


