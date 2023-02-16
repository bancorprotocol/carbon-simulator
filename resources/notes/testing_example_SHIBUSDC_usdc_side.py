from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {        # EXAMPLE SHIB/USDC - USDC-side
"pa" : 0.00001555,      # dy/dx - USDC per SHIB
"pb" : 0.00001453,      # dy/dx - USDC per SHIB
"y" : 100000,           # USDC tokens raw
"z" : 100000,           # USDC tokens raw
"decx" : 18,            # SHIB decimality
"decy" : 6,             # USDC decimality
}

amount = 6600000000      # trade 6600000000 SHIB for USDC
tradeByTarget = False

# amount = 100000        # trade 100000 USDC for SHIB
# tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)