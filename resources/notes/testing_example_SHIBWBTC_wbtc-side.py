from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

order_inputs = {        # EXAMPLE SHIB/WBTC - WBTC-side
"pa" : 0.00000000001555,      # dy/dx - WBTC per SHIB
"pb" : 0.00000000001453,      # dy/dx - WBTC per SHIB
"y" : 1000000000,            # SHIB tokens raw
"z" : 1000000000,           # SHIB tokens raw
"decx" : 18,            # SHIB decimality
"decy" : 8,             # WBTC decimality
}

# amount = 1              # trade 1 WBTC for SHIB
# tradeByTarget = False

amount = 100        # trade 10000 SHIB for WBTC
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
trade(amount, tradeByTarget, storage, order_inputs)