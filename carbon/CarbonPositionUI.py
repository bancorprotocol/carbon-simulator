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

from pair import CarbonPair, __version__ as pair_v
from carbon_position_ui import CarbonPositionUI, __version__ as posn_v
print("CarbonPairStatic version", pair_v)
print("CarbonPositionUI version", posn_v)


# # Carbon Position UI

ETHUSDC = CarbonPair("ETH", "USDC")

pos1 = CarbonPositionUI.from_prices(ETHUSDC, "ETH", 2100, 2500, 100, 50)
pos1.descr()


pos1.B, pos1.S, pos1.reverseq

pos1.widthr, pos1.widthpc

pos1.pa, pos1.p0, pos1.pb

pos1.py, pos1.p0, pos1.px

pos1.pa_raw, 1/pos1.p0, pos1.pb_raw

pos2 = CarbonPositionUI.from_prices(ETHUSDC, "USDC", 1000, 500, 1000, 700)
pos2.descr(True)

pos2.B, pos2.S, pos2.reverseq

pos2.pa, pos2.p0, pos2.pb

pos2.pa_raw, pos2.p0, pos2.pb_raw

pos2.py, pos2.p0, pos2.px
