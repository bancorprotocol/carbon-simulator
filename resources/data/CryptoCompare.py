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

from carbon.helpers.cryptocompare import CryptoCompare
import pandas as pd
from matplotlib import pyplot as plt
import os
print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CryptoCompare))

# # Crypto Compare
#
# https://min-api.cryptocompare.com/documentation

# ## Selection
#
# Please enter the pairs for the `SELECTION` data collection below

selection = "MIM/LTC, BNT/LINK, NMR/USD"
hourly = "DAI/USDC, USDT/USDC, DAI/USDT, USDD/USDT, MIM/USDC, wstETH/ETH, cbETH/ETH, STETH/ETH, USDC/USDT, BTC/ETH, BTC/USD, ETH/USD"
hourly_unavailable = "frxETH/ETH, rETH/ETH, ETH/sETH2"



pd.read_pickle("cryptocompare/SELECTION.pickle").head()

# +
# # !cp cryptocompare/SELECTION.pickle .
# # !cp cryptocompare/SELECTION.pickle ../../../JupyLiteCarbonSim/content/data
# # !cp cryptocompare/SELECTION.pickle ../../../BinderCarbonSimulator/Frozen/data
# -

# ## SetUp
#
# If you have a private API key, run `export CCAPIKEY=<YOURKEY>` before you launch Jupyter on the same shell. In case no key is found the free API is used. You can also provide the API key in the constructor, but this is not recommended for security reasons.

# +
try:
    CC = CryptoCompare(apikeyname="CCAPIKEY")
except:
    CC = CryptoCompare(apikey=True)

print("[CryptoCompare] key digest", CC.keydigest[:4])
# -

# ## Coin lists

# Here we populate the various coin lists that we will use to download data. They are as follows:
#
# - `coins_for_ccy`, `ccies`: creates a table for each of the currencies 
# - `coins_for_cross`: creates a single cross table
# - `usdstables`: creates a single table against USD
#
# We also define the list of items **not** to produce, `excludes`. Finally there is an `includes` list that, if present, specifies the _only_ items to be produced.

# +
coins_for_ccy ="ETH, BTC, BNB, XRP, ADA, DOGE, MATIC, SOL, OKB, DOT, LTC, TRX, AVAX, ATOM"
coins_for_cross ="ETH, BTC, BNB, XRP, ADA, DOGE, MATIC, SOL, OKB, DOT, LTC, TRX, AVAX, ATOM"
usdstables = "USDT, USDC, UST, BUSD"
ccies = "USD, BTC, ETH"

#excludes = ['COINS-CROSS', 'STABLES-USD', 'COINS-USD', 'COINS-BTC', 'COINS-ETH']
includes = ["HOURLY"]
# -

# The table `dltable0` has as keys the filename, and the data is a tuple of pairs. The table `dltable` contains the final downloads, the difference being the `excludes` to avoid redownloading data that is not needed. 
#
# **YOU MUST RESTART THE KERNEL IF YOU MAKE CHANGES TO INCLUDES OR EXCLUDES**.

dltable0 = {
    "COINS-CROSS": (CC.create_pairs(coins_for_cross), CC.query_dailypair),
    "STABLES-USD": (CC.create_pairs(usdstables, "USD"), CC.query_dailypair),
    **{
        f"COINS-{ccy}": (CC.create_pairs(coins_for_ccy, ccy), CC.query_dailypair)
        for ccy in CC.coinlist(ccies)
    },
    "SELECTION": (CC.coinlist(selection, aspt=True), CC.query_dailypair),
    "HOURLY": (CC.coinlist(hourly, aspt=True), CC.query_hourlypair),
}
try:
    dltable = {k:v for k, v in dltable0.items() if k in includes}
    print("restricted execution to the pairs in `includes`", includes)
except:
    try:
        dltable = {k:v for k, v in dltable0.items() if not k in excludes}
        print("the items in `excludes` were excluded", excludes)
    except:
        dltable = dltable0
        print("no `includes` or `excludes` info present; all tables are being process")
dltable0.keys(), dltable.keys()

# ## Data download

# ### Raw tables

for item, val in dltable.items():
    pairs, cc_query_f = val
    print("Downloading raw table", item, len(pairs))
    results = {
        #(fsym, tsym): CC.query_dailypair(fsym=fsym, tsym=tsym)
        (fsym, tsym): cc_query_f(fsym=fsym, tsym=tsym)
        for fsym, tsym in pairs
    }
    df = pd.concat(results, axis=1)
    df.to_pickle(CC.datafn(f"{item}-RAW.pickle"))

# !ls cryptocompare

# ### Reformatted tables

for item in dltable:
    print("Converting raw table", item)
    df = pd.read_pickle(CC.datafn(f"{item}-RAW.pickle"))
    df = CC.reformat_raw_df(df)
    df.to_pickle(CC.datafn(f"{item}.pickle"))

# ## Review tables

# !ls cryptocompare

df = pd.read_pickle("cryptocompare/HOURLY.pickle")
df





