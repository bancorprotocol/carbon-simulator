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

# +
from carbon.helpers.cryptocompare import CryptoCompare
import pandas as pd
from matplotlib import pyplot as plt
import os

print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CryptoCompare))
# -

# # Crypto Compare
#
# https://min-api.cryptocompare.com/documentation

CC, CCA = CryptoCompare(), CryptoCompare(apikey=True)
print("[CryptoCompare] key digest", CC.keydigest[:4], CCA.keydigest[:4])

# +
#CC.query_ratelimit()
#CCA.query_ratelimit()
# -

# ## Get daily data

CCNE = CryptoCompare(raiseonerror=False)

coins ="ETH, BTC, BNB, XRP, ADA, DOGE, MATIC, SOL, OKB, DOT, LTC, TRX, AVAX, ATOM"
usdstables = "USDT, USDC, UST, BUSD"
ccies = "USD, BTC, ETH"

# +
# fsyms = CC.unjoin(usdstables)
# tsyms = ["USD",]
# results = {
#     (fsym, tsym): CCNE.query_dailypair(fsym=fsym, tsym=tsym)
#     for fsym in fsyms
#     for tsym in tsyms
# }
# df = pd.concat(results, axis=1)
# df.to_pickle(CC.datafn("USD-STABLES-RAW.pickle"))

# df = pd.read_pickle(CC.datafn("USD-STABLES-RAW.pickle"))
# df = CC.reformat_raw_df(df)
# df.to_pickle(CC.datafn("USD-STABLES.pickle"))
# df = pd.read_pickle(CC.datafn("USD-STABLES.pickle"))
# df

# +
#pd.read_pickle("cryptocompare/USD-STABLES-RAW.pickle")

# +
# fsyms = CC.unjoin(coins)
# tsyms = ["USD",]
# results = {
#     (fsym, tsym): CCNE.query_dailypair(fsym=fsym, tsym=tsym)
#     for fsym in fsyms
#     for tsym in tsyms
# }
# df = pd.concat(results, axis=1)
# df.to_pickle(CC.datafn("USD-COINS-RAW.pickle"))

# df = pd.read_pickle(CC.datafn("USD-COINS-RAW.pickle"))
# df = CC.reformat_raw_df(df)
# df.to_pickle(CC.datafn("USD-COINS.pickle"))
# df = pd.read_pickle(CC.datafn("USD-COINS.pickle"))
# df

# +
#pd.read_pickle("cryptocompare/USD-COINS-RAW.pickle")

# +
# fsyms = CC.unjoin(coins)
# tsyms = ["BTC",]
# results = {
#     (fsym, tsym): CCNE.query_dailypair(fsym=fsym, tsym=tsym)
#     for fsym in fsyms
#     for tsym in tsyms
# }
# df = pd.concat(results, axis=1)
# df.to_pickle(CC.datafn("BTC-COINS-RAW.pickle"))

# df = pd.read_pickle(CC.datafn("BTC-COINS-RAW.pickle"))
# df = CC.reformat_raw_df(df)
# df.to_pickle(CC.datafn("BTC-COINS.pickle"))
# df = pd.read_pickle(CC.datafn("BTC-COINS.pickle"))
# df
# -


