from math import *
from testing_base import *

### INIT ###
BITS_SIGNIFICANT =  48
BITS_EXPONENT    =   6
SCALING_FACTOR   =  48

order_inputs = {        
"pa" : 3.2451855373398464095E+20,      
"pb" : 4.3980465111040007197,      
"y" : 302231454903657300000,            
"z" : 302231454903657300000000,         
"decx" : 6,            
"decy" : 18,           
}

amount = 302231454903657300000 

storage = create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, SCALING_FACTOR)
tradeByTarget = True
amount_array = [amount]
outputs = []
for amount in amount_array:
    outputs += [trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR)]


tradeByTarget = False
sourceOut = []
for output in outputs:
    if output == 0.0:
        sourceOut += ['Error']
    else:
        sourceOut += [trade(output, tradeByTarget, storage, order_inputs, SCALING_FACTOR)]

print("Trade by target:")
print(list(zip(amount_array, outputs)))
print("Trade outputs by source:")
print(list(zip(outputs, sourceOut)))
print('\n')
print("Results:")
print(list(zip(amount_array, sourceOut)))
print("Error:")
print([x[0]/x[1] for x in list(zip(amount_array, sourceOut))])


