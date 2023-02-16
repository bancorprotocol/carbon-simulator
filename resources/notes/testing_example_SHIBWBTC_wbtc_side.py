from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {            # EXAMPLE SHIB/WBTC - WBTC-side
"pa" : 0.00000000001555,    # dy/dx - WBTC per SHIB
"pb" : 0.00000000001453,    # dy/dx - WBTC per SHIB
"y" : 1,                    # WBTC tokens raw
"z" : 1,                    # WBTC tokens raw
"decx" : 18,                # SHIB decimality
"decy" : 8,                 # WBTC decimality
}

# amount = 6600000000      # trade 6600000000 SHIB for WBTC
# tradeByTarget = False

amount = 0.1        # trade 1 WBTC for SHIB
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)