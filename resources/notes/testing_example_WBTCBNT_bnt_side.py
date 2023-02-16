from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {        # EXAMPLE WBTC/BNT - BNT-side
"pa" : 50000,           # dy/dx - BNT per WBTC
"pb" : 49709,           # dy/dx - BNT per WBTC
"y" : 100000,           # BNT tokens raw
"z" : 100000,           # BNT tokens raw
"decx" : 8,             # WBTC decimality
"decy" : 18,            # BNT decimality
}

# amount = 1      # trade 1 WBTC for BNT
# tradeByTarget = False

amount = 100000        # trade 100000 BNT for WBTC
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)