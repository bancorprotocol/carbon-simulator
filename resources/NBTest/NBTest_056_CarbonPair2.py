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

from carbon import CarbonSimulatorUI, CarbonOrderUI, CarbonPair, __version__, __date__
from carbon.helpers import SharedVar, print_version
from math import floor, ceil, trunc
print("{0.__name__} {0.__VERSION__} ({0.__DATE__})".format(CarbonPair))
print_version(require="2.3.2")

# # Carbon pair amendments (NBTest 56)

# ## Ensure capitalisation

assert CarbonPair("usd/eth").tknb == "USD"
assert CarbonPair("usd/eth").tknq == "ETH"
assert CarbonPair("usd/eth").slashpair == "USD/ETH"
assert CarbonPair("bnBNT/eth").tknb == "BNBNT"

assert CarbonPair(tknb="usd", tknq="eth").tknb == "USD"
assert CarbonPair(tknb="usd", tknq="eth").tknq == "ETH"
assert CarbonPair(tknb="usd", tknq="eth").slashpair == "USD/ETH"
assert CarbonPair(tknb="bnBNT", tknq="eth").tknb == "BNBNT"

# ## Ensure originals are preserved

assert CarbonPair("usd/eth").tknb_o == "usd"
assert CarbonPair("usd/eth").tknq_o == "eth"
assert CarbonPair("usd/eth").slashpair_o == "usd/eth"
assert CarbonPair("bnBNT/eth").tknb_o == "bnBNT"
assert CarbonPair("bnBNT/eth").slashpair_o == "bnBNT/eth"

assert CarbonPair(tknb="usd", tknq="eth").tknb_o == "usd"
assert CarbonPair(tknb="usd", tknq="eth").tknq_o == "eth"
assert CarbonPair(tknb="usd", tknq="eth").slashpair_o == "usd/eth"
assert CarbonPair(tknb="bnBNT", tknq="eth").tknb_o == "bnBNT"
assert CarbonPair(tknb="bnBNT", tknq="eth").slashpair_o == "bnBNT/eth"

# ## Ensure display values are correct

# ### display_orig = Default

assert CarbonPair("usd/eth").tknb_d == "USD"
assert CarbonPair("usd/eth").tknq_d == "ETH"
assert CarbonPair("usd/eth").slashpair_d == "USD/ETH"
assert CarbonPair("bnBNT/eth").tknb_d == "BNBNT"

assert CarbonPair(tknb="usd", tknq="eth").tknb_d == "USD"
assert CarbonPair(tknb="usd", tknq="eth").tknq_d == "ETH"
assert CarbonPair(tknb="usd", tknq="eth").slashpair_d == "USD/ETH"
assert CarbonPair(tknb="bnBNT", tknq="eth").tknb_d == "BNBNT"


# ### display_orig = False

assert CarbonPair("usd/eth", display_orig=False).tknb_d == "USD"
assert CarbonPair("usd/eth", display_orig=False).tknq_d == "ETH"
assert CarbonPair("usd/eth", display_orig=False).slashpair_d == "USD/ETH"
assert CarbonPair("bnBNT/eth", display_orig=False).tknb_d == "BNBNT"

assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).tknb_d == "USD"
assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).tknq_d == "ETH"
assert CarbonPair(tknb="usd", tknq="eth", display_orig=False).slashpair_d == "USD/ETH"
assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=False).tknb_d == "BNBNT"


# ### display_orig = True

assert CarbonPair("usd/eth", display_orig=True).tknb_d == "usd"
assert CarbonPair("usd/eth", display_orig=True).tknq_d == "eth"
assert CarbonPair("usd/eth", display_orig=True).slashpair_d == "usd/eth"
assert CarbonPair("bnBNT/eth", display_orig=True).tknb_d == "bnBNT"
assert CarbonPair("bnBNT/eth", display_orig=True).slashpair_d == "bnBNT/eth"

assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).tknb_d == "usd"
assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).tknq_d == "eth"
assert CarbonPair(tknb="usd", tknq="eth", display_orig=True).slashpair_d == "usd/eth"
assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=True).tknb_d == "bnBNT"
assert CarbonPair(tknb="bnBNT", tknq="eth", display_orig=True).slashpair_d == "bnBNT/eth"


