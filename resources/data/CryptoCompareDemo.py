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

# Note: `CryptoCompare` expects the API in an environment variable called `CCAPIKEY`. To set in bash, run
#
#     export CCAPIKEY=<value>
#     jupyter notebook
#     
# Alternatively you can supply the API key directly to the object (via `apikey=XXX`), but this is not recommended because of its security implications.

CCA = CryptoCompare(apikey=True)
try:
    CCA = CryptoCompare()
except RuntimeError as e:
    CC = CCA
    print(e)
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

CCA.ccycodes()

CCA.ccycodes(symonly=False).head()

# ## Index list

data = CC.cache_indexlist()
data.keys()

data["ETHB"]


# ## Freqly pair (= daily, hourly, minutely pair)

# ### daily

df = CCA.query_freqlypair(freq=CCA.FREQ_DAILY, fsym="BTC", tsym="USD")
df.head()

df = CCA.query_dailypair(fsym="BTC", tsym="USD")
df.head()

# ### hourly

df = CCA.query_freqlypair(freq=CCA.FREQ_HOURLY, fsym="BTC", tsym="USD")
df.head()

df = CCA.query_hourlypair(fsym="BTC", tsym="USD")
df.head()

# ### minutely

df = CCA.query_freqlypair(freq=CCA.FREQ_MINUTELY, fsym="BTC", tsym="USD")
df.head()

df = CCA.query_minutelypair(fsym="BTC", tsym="USD")
df.head()

# ### docs

help(CCA.query_freqlypair)

help(CCA.query_minutelypair)

# ## Aggregate query


r = CCA.aggr_query(
    "ETC/USD, BTC/USD", 
    fields=[CCA.FIELD_OPEN, CCA.FIELD_CLOSE], 
    freq=CCA.FREQ_HOURLY)
r.keys()

r["rawaggr"]

r["raw"]["ETC/USD"]

r["aggr"]["close"]

r["gaggr"]

help(CCA.aggr_query)


