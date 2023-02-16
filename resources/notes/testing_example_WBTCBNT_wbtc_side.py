from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {        # EXAMPLE BNT/WBTC - WBTC-side
"pa" : 1/49709,         # dy/dx - WBTC per BNT
"pb" : 1/50000,         # dy/dx - WBTC per BNT
"y" : 1,                # WBTC tokens raw
"z" : 1,                # WBTC tokens raw
"decx" : 18,            # BNT decimality
"decy" : 8,             # WBTC decimality
}

amount = 40000      # trade 40000 BNT for WBTC
tradeByTarget = False

# amount = 1        # trade 1 WBTC for BNT
# tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)