from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

order_inputs = {        # EXAMPLE SHIB/USDC - SHIB-side
"pa" : 1/0.00001453,      # dy/dx - SHIB per USDC
"pb" : 1/0.00001555,      # dy/dx - SHIB per USDC
"y" : 100000,            # USDC tokens raw
"z" : 100000,           # USDC tokens raw
"decx" : 6,            # USDC decimality
"decy" : 18,             # SHIB decimality
}

amount = 10000       # trade 10000 SHIB for USDC
tradeByTarget = False

# amount = 1         # trade 1 USDC for SHIB
# tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
trade(amount, tradeByTarget, storage, order_inputs)