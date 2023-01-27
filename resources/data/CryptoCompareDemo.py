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

print( "{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CryptoCompare))
# -

# # Crypto Compare
#
# https://min-api.cryptocompare.com/documentation

CC, CCA = CryptoCompare(), CryptoCompare(apikey=True)
print("[CryptoCompare] key digest", CC.keydigest[:4], CCA.keydigest[:4])

# ## Rate limit

CC.query_ratelimit()

CCA.query_ratelimit()

# ## Exchanges and pairs

data = CC.cache_allexchanges()
data["exchanges"].keys()

", ".join([x for x in data["exchanges"] if data["exchanges"][x].get("isTopTier")])

", ".join([x for x in data["exchanges"] if data["exchanges"][x].get("isActive")])

exchange = "Coinbase"
print(data["exchanges"][exchange].keys())
", ".join(data["exchanges"][exchange]["pairs"].keys())

data["exchanges"][exchange]["isTopTier"]

# ## Coinlist

data = CC.cache_coinlist()
data_keys = list(data.keys())
len(data_keys)

", ". join(data_keys[100:120])

data["BTC"].keys()

# ## ISO currency symbols

",".join(CCA.ccycodes())

CCA.ccycodes(symonly=False).head()

# ## Index list

data = CC.cache_indexlist()
data.keys()

data["ETHB"]

# ## Daily pair

df = CCA.query_dailypair(fsym="BTC", tsym="KRW")
df.head()

data = CCA.query_dailypair(fsym="BTC", aspandas=False)
data.keys()








