from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

order_inputs = {        # EXAMPLE WBTC/BNT - BNT-side
"pa" : 50000,           # dy/dx - BNT per WBTC
"pb" : 49709,           # dy/dx - BNT per WBTC
"y" : 100000,              # BNT tokens raw
"z" : 100000,              # BNT tokens raw
"decx" : 8,             # WBTC decimality
"decy" : 18,            # BNT decimality
}

# amount = 1      # trade 1 WBTC for BNT
# tradeByTarget = False

amount = 100000        # trade 100000 BNT for WBTC
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
trade(amount, tradeByTarget, storage, order_inputs)