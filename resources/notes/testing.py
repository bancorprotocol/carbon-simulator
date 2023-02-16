from math import *
import numpy as np
from dataclasses import dataclass, asdict
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

# from testing_example_SHIBUSDC_shib_side import order_inputs
# from testing_example_SHIBUSDC_usdc_side import order_inputs

# from testing_example_WBTCBNT_wbtc_side import order_inputs
# from testing_example_WBTCBNT_bnt_side import order_inputs

from testing_example_SHIBWBTC_shib_side import order_inputs
# from testing_example_SHIBWBTC_wbtc_side import order_inputs

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
tradeByTarget = True
amount_array = np.logspace(-5,log10(order_inputs['y']),int(log10(order_inputs['y'])+6))
outputs = []
for amount in amount_array:
    try:
        trade_output = trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)
    except AssertionError as e:
        trade_output = e.text
    outputs += [trade_output]


tradeByTarget = False
sourceOut = []
for output in outputs:
    if output == 0.0:
        sourceOut += ['Error']
    else:
        try:
            trade_output = trade(output, tradeByTarget, storage, order_inputs, SCALING_FACTOR)
        except AssertionError as e:
            trade_output = e.text
        sourceOut += [trade_output]

print("Trade by target:")
print(list(zip(amount_array, outputs)))
print("Trade outputs by source:")
print(list(zip(outputs, sourceOut)))
print('\n')
# print("Results:")
# print(list(zip(amount_array, sourceOut)))
# print("Error:")
# print([x[0]/x[1] for x in list(zip(amount_array, sourceOut))])