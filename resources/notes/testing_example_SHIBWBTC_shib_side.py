from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {                # EXAMPLE SHIB/USDC - SHIB-side
"pa" : 1/0.00000000001453,      # dy/dx - SHIB per WBTC
"pb" : 1/0.00000000001555,      # dy/dx - SHIB per WBTC
"y" : 10000000000,              # SHIB tokens raw
"z" : 10000000000,              # SHIB tokens raw
"decx" : 8,                     # WBTC decimality
"decy" : 18,                    # SHIB decimality
}

amount = 0.000001       # trade 0.000001 WBTC for SHIB
tradeByTarget = False

# amount = 100000000000000       # trade 100000 SHIB for WBTC
# tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs,SCALING_FACTOR)
