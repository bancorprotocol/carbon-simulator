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

from carbon.helpers.stdimports import *
from carbon.sdk import CarbonSDK, SDKToken, Tokens, TokenContainer
from carbon import CarbonOrderUI, CarbonSimulatorUI
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonSDK))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SDKToken))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonOrderUI))
print_version(require="2.3.3")

# # CarbonSDK (NBTest 061)

# ## SDKToken

tkn = SDKToken("TKN", "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2", 18, "Token")
assert tkn.T == "TKN"
assert tkn.token == "TKN"
assert tkn.d == 18
assert tkn.a == "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2"
assert tkn.address == "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2"
assert tkn.name == "Token"
assert tuple(tkn) == ('TKN', '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2', 18, 'Token')
assert SDKToken(*tuple(tkn)) == tkn

tkn = SDKToken("tkn", "0x6B3595068778DD592e39a122f4f5a5cf09c90fe2", 18)
assert tkn.T == "TKN"
assert tkn.token == "TKN"
assert tkn.d == 18
assert tkn.a == "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2"
assert tkn.address == "0x6b3595068778dd592e39a122f4f5a5cf09c90fe2"
assert tkn.name == "TKN"
assert tuple(tkn) == ('TKN', '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2', 18, 'TKN')
assert SDKToken(*tuple(tkn)) == tkn

# Note: two tokens are equal if their address is equal

assert SDKToken("tkn", "0x6B3595068778DD592e39a122f4f5a5cf09c90fe2", 18) == SDKToken("TKN", "0x6B3595068778DD592e39a122f4f5a5cf09c90fe2", 18)

# ## TokenContainer

T = TokenContainer([
    SDKToken("AAVE", "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"),
    SDKToken("BAL", "0xba100000625a3754423978a60c9317c58a424e3d"),
])
assert len(T) == 2
assert T.AAVE.T == "AAVE"
assert T.AAVE.a == "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9"
assert T.AAVE.d is None
assert T.byaddr("0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9").T == "AAVE"
assert T.BAL.T == "BAL"
assert T.BAL.a == "0xba100000625a3754423978a60c9317c58a424e3d"
assert T.BAL.d is None
assert T.byaddr("0xba100000625a3754423978a60c9317c58a424e3d").T == "BAL"
assert TokenContainer.fromlist(T._all).AAVE.T == "AAVE"
assert len(TokenContainer.fromlist(T._all)) == len(T)

T = TokenContainer.fromcsv("""

 aave  , 0x7fc66500c84a76ad7e9c93437bfc5AC33e2ddae9  , 18
Aleph , 0x27702a26126e0b3702af63ee09ac4d1a084ef628  , 18
 ANT , 0x960b236a07cf122663c4303350609a66a7b288c0 , 18
  bAl, 0xba100000625A3754423978a60c9317c58a424e3d   , 18
  BAND  , 0xba11d00c5f74255f56a5e366F4f77f5a186d7f55   , 18

"""
)
assert len(T)==5
assert [t.T for t in T] == ['AAVE', 'ALEPH', 'ANT', 'BAL', 'BAND']
assert [t.a for t in T] == [
    '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9',
    '0x27702a26126e0b3702af63ee09ac4d1a084ef628',
    '0x960b236a07cf122663c4303350609a66a7b288c0',
    '0xba100000625a3754423978a60c9317c58a424e3d',
    '0xba11d00c5f74255f56a5e366f4f77f5a186d7f55'
]
assert [t.d for t in T] == [18]*len(T)
assert [t for t in T] == [t for t in T._all]
assert T.byaddr("0x7fc66500c84a76ad7e9c93437bfc5AC33e2ddae9").a == "0x7fc66500c84a76ad7e9c93437bfc5AC33e2ddae9".lower()
assert T.byaddr("0x7fc66500c84a76ad7e9c93437bfc5AC33e2ddae9").a == "0x7fc66500c84a76ad7e9c93437bfc5AC33e2ddae9".lower()
assert TokenContainer.fromlist(T._all).AAVE.T == "AAVE"
assert len(TokenContainer.fromlist(T._all)) == len(T)

# ## SDK helpers

SDK = CarbonSDK

assert SDK.join("https://example.com", "url") == 'https://example.com/url'
assert SDK.join("https://example.com/", "url") == 'https://example.com/url'
assert SDK.join("https://example.com/", "/url") == 'https://example.com/url'
assert SDK.join("https://example.com", "/url") == 'https://example.com/url'

assert SDK.c2s("thisIsACamelCaseString")=='this_is_a_camel_case_string'
assert SDK.c2s("thisIsACamel1CaseString")=='this_is_a_camel1_case_string'
assert SDK.c2s("123 ThisIsACamel1CaseString")=='123 _this_is_a_camel1_case_string'

assert SDK.s2c("this_is_a_snake_case_string")=="thisIsASnakeCaseString"
assert SDK.s2c("This_is_a_snake_case_string")=="ThisIsASnakeCaseString"

x=0.11111111111111111
assert SDK.roundsd(x,0) == 0.0
assert SDK.roundsd(x,1) == 0.1
assert SDK.roundsd(x,2) == 0.11
assert SDK.roundsd(x,5) == 0.11111
assert SDK.roundsd(x*10000,0) == 1000.0
assert SDK.roundsd(x*10000,1) == 1100.0
assert SDK.roundsd(x*10000,2) == 1110.0
assert SDK.roundsd(x*10000,5) == 1111.1

x=0.9999
assert SDK.roundsd(x,0) == 1
assert SDK.roundsd(x,1) == 1
assert SDK.roundsd(x,2) == 1
assert SDK.roundsd(x,3) == 1
assert SDK.roundsd(x,4) == 0.9999
assert SDK.roundsd(x*1000,0) == 1000
assert SDK.roundsd(x*1000,1) == 1000
assert SDK.roundsd(x*1000,2) == 1000
assert SDK.roundsd(x*1000,3) == 1000
assert SDK.roundsd(x*1000,4) == 999.9

assert SDK.bn2int(1) == 1
assert SDK.bn2int("1") == "1"
assert SDK.bn2int([1,2,3]) == [1,2,3]
assert SDK.bn2int({1:2, 3:4}) == {1:2, 3:4}
assert SDK.bn2int({"type": "BigNumber", "hex": "0xff"}) == 255
assert SDK.bn2intd({1:1, 2:"2", 3:[1,2,3], 4:{1:2, 3:4}, 5:{"type": "BigNumber", "hex": "0xff"}}) == {1: 1, 2: '2', 3: [1, 2, 3], 4: {1: 2, 3: 4}, 5: 255}

assert SDK.int2str(1) == "1"
assert SDK.int2str("1") == "1"
assert SDK.int2str(1.23) == 1.23
assert SDK.int2strd({1:1, 2:"2", 3:2.34}) == {1: '1', 2: '2', 3: 2.34}

assert SDK.int2bn(2**100) == {'type': 'BigNumber', 'hex': '0x10000000000000000000000000'}
assert SDK.int2bn(10**40) == {'type': 'BigNumber', 'hex': '0x1d6329f1c35ca4bfabb9f5610000000000'}
assert SDK.int2bn(1000000000000000.11) == SDK.int2bn(1000000000000000)
assert SDK.bn2int(SDK.int2bn(10**27))==10**27

# ## CarbonOrderUI helpers

OUI = CarbonOrderUI

x=0.11111111111111111
assert OUI.roundsd(x,None) == x
assert OUI.roundsd(x,0) == 0.0
assert OUI.roundsd(x,1) == 0.1
assert OUI.roundsd(x,2) == 0.11
assert OUI.roundsd(x,5) == 0.11111
assert OUI.roundsd(x*10000,0) == 1000.0
assert OUI.roundsd(x*10000,1) == 1100.0
assert OUI.roundsd(x*10000,2) == 1110.0
assert OUI.roundsd(x*10000,5) == 1111.1

x=0.9999
assert OUI.roundsd(x,0) == 1
assert OUI.roundsd(x,1) == 1
assert OUI.roundsd(x,2) == 1
assert OUI.roundsd(x,3) == 1
assert OUI.roundsd(x,4) == 0.9999
assert OUI.roundsd(x*1000,0) == 1000
assert OUI.roundsd(x*1000,1) == 1000
assert OUI.roundsd(x*1000,2) == 1000
assert OUI.roundsd(x*1000,3) == 1000
assert OUI.roundsd(x*1000,4) == 999.9

assert OUI.bn2int(1) == 1
assert OUI.bn2int("1") == "1"
assert OUI.bn2int([1,2,3]) == [1,2,3]
assert OUI.bn2int({1:2, 3:4}) == {1:2, 3:4}
assert OUI.bn2int({"type": "BigNumber", "hex": "0xff"}) == 255
assert OUI.bn2intd({1:1, 2:"2", 3:[1,2,3], 4:{1:2, 3:4}, 5:{"type": "BigNumber", "hex": "0xff"}}) == {1: 1, 2: '2', 3: [1, 2, 3], 4: {1: 2, 3: 4}, 5: 255}

# ## CarbonOrderUI

sdkstrategy = {'id': {'type': 'BigNumber', 'hex': '0x53'},
 'baseToken': 'ETH',
 'quoteToken': 'USDC',
 'buyPriceLow': '1499.999999795006131230270249480266202369446401111707789510774091468192636966705322265625',
 'buyPriceHigh': '1599.99999987885530572613908948335161402097039096137365277172648347914218902587890625',
 'buyBudget': '500',
 'sellPriceLow': '2500',
 'sellPriceHigh': '2600.000000000011469981186957619896170942620083990429606213754278889677960415165669457991666380074129',
 'sellBudget': '1',
 'encoded': {'id': {'type': 'BigNumber', 'hex': '0x53'},
  'token0': 'ETH',
  'token1': 'USDC',
  'order0': {'y': {'type': 'BigNumber', 'hex': '0x6f05b59d3b20000'},
   'z': {'type': 'BigNumber', 'hex': '0x0de0b6b3a7640000'},
   'A': {'type': 'BigNumber', 'hex': '0x09c23178611340'},
   'B': {'type': 'BigNumber', 'hex': '0x0f99373a1e7bb3'}},
  'order1': {'y': {'type': 'BigNumber', 'hex': '0x9ef21aa'},
   'z': {'type': 'BigNumber', 'hex': '0x1dcd6500'},
   'A': {'type': 'BigNumber', 'hex': '0x154f52e1'},
   'B': {'type': 'BigNumber', 'hex': '0x0289c75e3b'}}}}

obuy, osell = CarbonOrderUI.from_SDK(sdkstrategy, 6)
assert osell.linked == obuy
assert obuy.linked == osell
osell, obuy

assert osell.tkn=="ETH"
assert osell.id=="83-s"
assert abs(osell.pa/2500-1) < 1e-10
assert abs(osell.pb/2600-1) < 1e-10
assert abs(osell.yint/1-1) < 1e-10
assert abs(osell.y/0.5-1) < 1e-10

assert obuy.tkn=="USDC"
assert obuy.id=="83-b"
assert abs(obuy.pa/1600-1) < 1e-10
assert abs(obuy.pb/1500-1) < 1e-10
assert abs(obuy.yint/500-1) < 1e-10
assert abs(obuy.y/166.666666-1) < 1e-10

Sim = CarbonSimulatorUI()
o = Sim.add_fromsdk(sdkstrategy, 6)["orders"]
o

assert o.iloc[0]["pair"] == "ETHUSDC"
assert o.iloc[0]["p_unit"] == "USDC per ETH"
assert o.iloc[0]["tkn"] == "ETH"
assert abs(o.iloc[0]["p_start"]/2500-1) < 1e-10
assert abs(o.iloc[0]["p_end"]/2600-1) < 1e-10
assert abs(o.iloc[0]["y_int"]/1-1) < 1e-10
assert abs(o.iloc[0]["y"]/0.5-1) < 1e-10

assert o.iloc[1]["pair"] == "ETHUSDC"
assert o.iloc[1]["p_unit"] == "USDC per ETH"
assert o.iloc[1]["tkn"] == "USDC"
assert abs(o.iloc[1]["p_start"]/1600-1) < 1e-10
assert abs(o.iloc[1]["p_end"]/1500-1) < 1e-10
assert abs(o.iloc[1]["y_int"]/500-1) < 1e-10
assert abs(o.iloc[1]["y"]/166.666666-1) < 1e-10


