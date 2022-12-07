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

from carbon import CarbonSimulatorUI, CarbonPair, P
from carbon.simulators.carbon_simulator import __version__ as uiversion, __date__ as uidate
from carbon.pair import __version__ as pversion, __date__ as pdate
from jupyformat import *

print("[carbon_simulator] version", uiversion, uidate)
print("[pair] version", pversion, pdate)
jp()

# # Carbon Simulation - Test 38 - CarbonPair
#
# Testing the new CarbonPair interface -- **BREAKING CHANGE**

# +
#help(CarbonPair)
# -

def test_test038_carbonpair():

    assert(P==CarbonPair)
    assert(str(P("ETH/USDC"))=="CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    try:
        p = CarbonPair()
    except ValueError as e:
        print(e)
        assert(str(e)=="('If pair is None must provide tknb, tknq', None, None, None)")

    try:
        p = CarbonPair("ETH", "USDC")
    except ValueError as e:
        print(e)
        assert(str(e)=="""("Parameters are pair, tknb, tknq; did you mean `tknb='ETH', tknq='USDC'` ?", 'ETH', 'USDC', None)""")

    p = CarbonPair("", "ETH", "USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    p = CarbonPair(tknb="ETH", tknq="USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    p = CarbonPair(tknq="USDC", tknb="ETH")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    try:
        p = CarbonPair("ETHUSDC")
    except ValueError as e:
        print(e)
        assert(str(e)=="""('Illegal slashpair', 'ETHUSDC')""")

    p = CarbonPair("ETH/USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "ETH")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    try:
        p = CarbonPair.from_isopair_and_tkn("ETHUSDC", "WBTC")
    except ValueError as e:
        print(e)
        assert(str(e) == "('Invalid token specification (tkn not part of isopair)', 'ETHUSDC', 'WBTC')")

    p = CarbonPair.create("ETH/USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    p = CarbonPair.create("ETH", "USDC")
    print(p)
    assert(str(p) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")

    pp = CarbonPair.create(p)
    print(pp)
    assert(str(pp) == "CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC')")
    assert(not pp is p)

    try:
        pp = CarbonPair.create(p, "ETH")
    except ValueError as e:
        print(e)
        assert(str(e) == "('Second argument must be None if arg1 is pair', CarbonPair(slashpair='ETH/USDC', tknb='ETH', tknq='USDC'), 'ETH')")

    assert(p.tknb=="ETH")
    assert(p.tknq=="USDC")
    assert(p.basetoken=="ETH")
    assert(p.quotetoken=="USDC")
    assert(p.slashpair=="ETH/USDC")
    assert(p.pair_slash=="ETH/USDC")
    assert(p.pair_iso=="ETHUSDC")
    assert(p.price_convention=="USDC per ETH")
    assert(str(p.reverse)=="CarbonPair(slashpair='USDC/ETH', tknb='USDC', tknq='ETH')")

    assert(p.has_token("ETH"))
    assert(p.has_token("USDC"))
    assert(not p.has_token("WBTC"))

    assert(not p.has_quotetoken("ETH"))
    assert(p.has_quotetoken("USDC"))
    assert(not p.has_quotetoken("WBTC"))

    assert(p.has_basetoken("ETH"))
    assert(not p.has_basetoken("USDC"))
    assert(not p.has_basetoken("WBTC"))

    assert(p.other("ETH")=="USDC")
    assert(p.other("USDC")=="ETH")
    assert(p.other("WBTC") is None)

    # Convert an ETH amount into a USDC amount with the price in the price convention of the pair

    p.convert(1, "ETH", "USDC", 2000)

    # ditto ETH -> ETH (trivial)

    p.convert(1, "ETH", "ETH", 2000)

    # ditto USDC -> ETH (inverse rate!)

    p.convert(2000, "USDC", "ETH", 2000)

    assert(p.convert(1, "ETH", "USDC", 2000) == 2000)
    assert(p.convert(1, "ETH", "ETH", 2000) == 1)
    assert(p.convert(2000, "USDC", "ETH", 2000) == 1)
    assert(p.convert(1, "USDC", "USDC", 2000) == 1)

    assert(p.convert_price(2000, "USDC")==2000)
    assert(p.convert_price(1/2000, "ETH")==2000)

    help(p.limit_is_met)

    p.limit_is_met("ETH", 2000, p.BUY, 1000, asphrase=True)

    p.limit_is_met("ETH", 2000, p.SELL, 1000, asphrase=True)

    p.limit_is_met("USDC", 2000, p.BUY, 1000, asphrase=True)

    p.limit_is_met("USDC", 2000, p.SELL, 1000, asphrase=True)

    assert(p.limit_is_met("ETH", 2000, p.BUY, 1000))
    assert(not p.limit_is_met("ETH", 2000, p.SELL, 1000))
    assert(not p.limit_is_met("USDC", 2000, p.BUY, 1000))
    assert(p.limit_is_met("USDC", 2000, p.SELL, 1000))



