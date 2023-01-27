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
from carbon.helpers.fls import *
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime
from random import randint
from os.path import join as j

# # CoinGecko
# https://pypi.org/project/requests/
#
# https://docs.google.com/spreadsheets/d/1wTTuxXt8n9q7C4NDXqQpI3wpKu1_5bGVmP9Xz0XGSyU/edit#gid=0
#
#
# https://api.coingecko.com/api/v3/coins/list
#
# https://www.coingecko.com/en/api/documentation
#

CGPATH = "coingecko"
CGFN = lambda fn: j(CGPATH, fn)
# !ls {CGFN("")}

# #### Download coins list

# +
# r = requests.get('https://api.coingecko.com/api/v3/coins/list')
# data = r.json()
# df = pd.DataFrame.from_records(data)
# df.to_pickle(j("coingecko_coins_list.pickle"))

# +
# r = requests.get('https://api.coingecko.com/api/v3/simple/supported_vs_currencies')
# data = r.json()
# fsave(data, "supported_vs_currencies.json", json=True)
# -

COINGECKO_CURRENCIES = fload("supported_vs_currencies.json", json=True)
COINGECKO_CURRENCIES[:5]

COINGECKO_COINSLIST = pd.read_pickle("coingecko_coins_list.pickle")
COINGECKO_COINSLIST
COINGECKO_COINSLIST.query("symbol in ['bnt', 'btc', 'eth']")

# +
# r = requests.get("https://api.coingecko.com/api/v3/simple/price", params={"ids":"bitcoin", "vs_currencies":"eth"})
# r.json()
# -

id="bancor"
r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{id}/market_chart", 
        params={"days":f"{int(365*5)}", "vs_currency":"usd"})
data = r.json()
prices_t = tuple((pd.Timestamp(datetime.fromtimestamp(ts/1000)), p) for ts, p in data["prices"])
prices_df = pd.DataFrame.from_records(prices_t, columns=["datetime", "price"])
#prices_df.set_index("datetime").plot()

# +
def coingecko_id_from_symbol(symbol):
    """
    get coingecko id from symbol
    """
    COINGECKO_COINSLIST = pd.read_pickle("coingecko_coins_list.pickle")
    rec = COINGECKO_COINSLIST.query(f"symbol == '{symbol}'")
    if len(rec) == 0:
        return None
    return rec["id"].iloc[0]
coingecko_id_from_symbol("bnt")   

def coingecko_check_ccy(ccy):
    """
    checks for valid coingecko currency
    """
    ccy = ccy.lower()
    COINGECKO_CURRENCIES = fload("supported_vs_currencies.json", json=True, quiet=True)
    return True if ccy in COINGECKO_CURRENCIES else None


# -

def get_coingecko_data(dataid, ccyid, colheader, years):
    """
    call coingecko api to get data
    
    :dataid:    the id column from /api/v3/coins/list
    :ccyid:     one of /api/v3/simple/supported_vs_currencies
    :colheader: the column header of the price columns (eg "ETH/USD")
    :years:     number of years of data to get
    :returns:   pandas data frame
    """
    r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{dataid}/market_chart", 
        params={"days":f"{int(365.25*years)}", "vs_currency":f"{ccyid}"})
    data = r.json()
    prices_t = tuple((pd.Timestamp(datetime.fromtimestamp(ts/1000)), p) for ts, p in data["prices"])
    prices_df = pd.DataFrame.from_records(prices_t, columns=["datetime", f"{colheader}"])
    #prices_df.set_index("datetime").plot()
    return prices_df


def get_coingecko_data_pair(slashpair, years):
    """
    preprocess pair and call get_coingecko_data to get data
    
    :pair:    the desired pair, eg "eth/usd"
    :years:   number of years of data to get
    :returns: pandas data frame
    """
    slashpair1 = slashpair.lower()
    tknsym, ccysym = slashpair1.split("/")
    tknid = coingecko_id_from_symbol(tknsym)
    
    if tknid is None:
        raise ValueError(f"Unknown token {tknsym}", slashpair)
    
    if coingecko_check_ccy(ccysym) is None:
        raise ValueError(f"Unknown currency {ccysym}", slashpair)
        
    return get_coingecko_data(tknid, ccysym, slashpair, years).set_index("datetime")


# +
# #pairs = "ETH/USD, ETH/EUR, ETH/GBP, BTC/JPY, BTC/EUR, BTC/GBP, BTC/ETH, BNB/USD, BNB/ETH, BNT/BTC, XRP/USD, XRP/ETH, XRP/BTC, ADA/USD, ADA/ETH, ADA/BTC, DOGE/USD, DOGE/ETH, DOGE/BTC".split(",")
# pairs = "BTC/USD, BTC/EUR, BTC/GBP, BTC/JPY".split(",")
# result_df = pd.DataFrame()
# for pair in pairs:
#     pair = pair.strip()
#     print(pair)
#     try:
#         df = get_coingecko_data_pair(pair, 5)
#         result_df = pd.concat([result_df, df], axis=1)
#         print("OK   ", pair)
#     except:
#         print("ERROR", pair)
# fn = f"data_{randint(0,1000):03d}.pickle"
# print(f"saving as {fn}")
# result_df.to_pickle(fn)
# result_df.to_pickle("btc_ccy.pickle")
# -

def coingecko_download(pairs, fn):
    """
    downloads given pairs from coingecko
    
    :pairs:         comma-separated list of pairs, eg "ETH/USD, BTC/ETH"
    :fn:            the filename under which to save the dataframe (no extension)
                    note: also saves under a random name
    :returns:       tuple (df, random_fn)
    """

    result_df = pd.DataFrame()
    pairs = pairs.split(",")
    for pair in pairs:
        pair = pair.strip()
        print(pair)
        try:
            df = get_coingecko_data_pair(pair, 5)
            result_df = pd.concat([result_df, df], axis=1)
            print("OK   ", pair)
        except:
            print("ERROR", pair)
    random_fn = f"data_{randint(0,1000):03d}"
    print(f"saving as {random_fn}")
    result_df.to_pickle(f"{random_fn}.pickle")
    print(f"saving as {fn}")
    result_df.to_pickle(f"{fn}.pickle")
    return result_df, random_fn


pd.read_pickle("data_28.pickle")

# !ls

# pairs = "ETH/USD, ETH/EUR, ETH/GBP, BTC/JPY, BTC/EUR, BTC/GBP, BTC/ETH, BNB/USD, BNB/ETH, BNT/BTC, XRP/USD, XRP/ETH, XRP/BTC, ADA/USD, ADA/ETH, ADA/BTC, DOGE/USD, DOGE/ETH, DOGE/BTC".split(",")


# +
# pairs = "BTC/USD, BTC/EUR, BTC/GBP, BTC/JPY"
# df_btc_ccy, _ = coingecko_download(pairs, "btc_ccy")

# +
# pairs = "ETH/USD, BNB/USD, XRP/USD, ADA/USD, DOGE/USD"
# df, _ = coingecko_download(pairs, "coins1_usd")
# df

# +
# pairs = "OKB/USD, MATIC/USD, SOL/USD, DOT/USD, SHIB/USD"
# df, _ = coingecko_download(pairs, "coins2_usd")
# df

# +
# pairs = "LTC/USD, TRX/USD, AVAX/USD, UNI/USD, ATOM/USD"
# df, _ = coingecko_download(pairs, "coins3_usd")
# df

# +
# pairs = "LINK/USD, XMR/USD, ETC/USD, BCH/USD, XLM/USD"
# df, _ = coingecko_download(pairs, "coins4_usd")
# df
# -


