from math import *
import numpy as np
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  40
BITS_EXPONENT    =   8
ONE_EXPONENT     =  48

from testing_example_SHIBUSDC_shib_side import order_inputs
# from testing_example_SHIBUSDC_usdc_side import order_inputs

# from testing_example_WBTCBNT_wbtc_side import order_inputs
# from testing_example_WBTCBNT_bnt_side import order_inputs

# from testing_example_SHIBWBTC_shib_side import order_inputs
# from testing_example_SHIBWBTC_wbtc_side import order_inputs

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT)
tradeByTarget = True
amount_array = np.logspace(-5,log10(order_inputs['y']),int(log10(order_inputs['y'])+6))
outputs = []
for amount in amount_array:
    outputs += [trade(amount, tradeByTarget, storage, order_inputs)]


tradeByTarget = False
sourceOut = []
for output in outputs:
    if output == 0.0:
        sourceOut += ['Error']
    else:
        sourceOut += [trade(output, tradeByTarget, storage, order_inputs)]

print("Trade by target:")
print(list(zip(amount_array, outputs)))
print("Trade outputs by source:")
print(list(zip(outputs, sourceOut)))
print('\n')
print("Results:")
print(list(zip(amount_array, sourceOut)))
