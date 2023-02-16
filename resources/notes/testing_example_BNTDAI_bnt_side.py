from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {    # EXAMPLE BNT/DAI - BNT-side
"pa" : 4,           # dy/dx - BNT per DAI
"pb" : 4,           # dy/dx - BNT per DAI
"y" : 1000000000000,      # BNT tokens raw
"z" : 1000000000000,      # BNT tokens raw
"decx" : 18,        # DAI decimality
"decy" : 18,        # BNT decimality
}

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)

amount = 1              # trade 1 DAI for BNT
tradeByTarget = False
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)

amount = 1000000000       # trade 100000 BNT for DAI
tradeByTarget = True
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)