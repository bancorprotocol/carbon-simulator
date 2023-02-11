from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

order_inputs = {        # EXAMPLE BNT/WBTC - WBTC-side
"pa" : 1/49709,           # dy/dx - WBTC per BNT
"pb" : 1/50000,           # dy/dx - WBTC per BNT
"y" : 100000,              # BNT tokens raw
"z" : 100000,              # BNT tokens raw
"decx" : 18,             # BNT decimality
"decy" : 8,            # WBTC decimality
}

# amount = 1              # trade 1 WBTC for BNT
# tradeByTarget = False

amount = 50000        # trade 50000 BNT for WBTC
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
trade(amount, tradeByTarget, storage, order_inputs)