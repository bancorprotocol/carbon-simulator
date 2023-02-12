from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

order_inputs = {        # EXAMPLE SHIB/USDC - USDC-side
"pa" : 0.00001555,      # dy/dx - USDC per SHIB
"pb" : 0.00001453,      # dy/dx - USDC per SHIB
"y" : 100000,            # USDC tokens raw
"z" : 100000,           # USDC tokens raw
"decx" : 18,            # SHIB decimality
"decy" : 6,             # USDC decimality
}

# amount = 1              # trade 1 USDC for SHIB
# tradeByTarget = False

amount = 1        # trade 100000 SHIB for USDC
tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
trade(amount, tradeByTarget, storage, order_inputs)