from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
SCALING_FACTOR     =  48

order_inputs = {        # EXAMPLE SHIB/WBTC - SHIB-side
"pa" : 1/0.00000000001453,      # dy/dx - SHIB per WBTC
"pb" : 1/0.00000000001555,      # dy/dx - SHIB per WBTC
"y" : 100,            # WBTC tokens raw
"z" : 100,           # WBTC tokens raw
"decx" : 18,            # WBTC decimality
"decy" : 8,             # SHIB decimality
}

# amount = 10000       # trade 10000 SHIB for WBTC
# tradeByTarget = False

amount = 0.1         # trade 1 WBTC for SHIB
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)