from math import *
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {    # EXAMPLE BNT/DAI - DAI-side
"pa" : 0.25,        # dy/dx - DAI per BNT
"pb" : 0.25,        # dy/dx - DAI per BNT
"y" : 100000000000,      # DAI tokens raw
"z" : 100000000000,      # DAI tokens raw
"decx" : 18,        # BNT decimality
"decy" : 18,        # DAI decimality
}

amount = 100000      # trade 6600000000 BNT for DAI
tradeByTarget = False

# amount = 100000        # trade 100000 DAI for BNT
# tradeByTarget = True

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)