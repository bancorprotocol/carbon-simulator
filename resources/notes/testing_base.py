from math import *
from dataclasses import dataclass, asdict

mulDivF = lambda x, y, z: x * y // z
mulDivC = lambda x, y, z: (x * y + z - 1) // z
MAX = 2 ** 112

### FRONT END ###
def encode_order_inputs(pa, pb, y, z, decx, decy, xS):
    """returns (y,z,A,B,s) from prices, curve loading and capacity, decimals and scaling exponent"""
    decf = 10**(decy-decx)
    one = 2**xS
    a = sqrt(pa*decf)-sqrt(pb*decf) # p_ = dy/dx
    b = sqrt(pb*decf)               # pw_ = dyw/dxw = dy*decy / dx*decx
    return int(y*10**decy), int(z*10**decy), int(a*one), int(b*one), one, xS

### Encode for contract storage ###

def from_int(rawint, BITS_SIGNIFICANT, BITS_EXPONENT):
    """
    alternative constructor: from raw int
    
    :rawint:    the _actual_ intval to be represented in the class
    """
    assert type(rawint) == int, f"value must be int [{rawint}]"
    assert rawint >= 0, f"value must be positive [{rawint}]"
    if rawint == 0:
        return (0,0)
    
    lenval = ceil(log2(rawint+1))
    exponent = lenval - BITS_SIGNIFICANT
    assert exponent <= 2**BITS_EXPONENT, f"exponent must be <= {2**BITS_EXPONENT}, is {exponent} [{rawint}]"
    if exponent <= 0:
        return (rawint, 0)
    return (rawint >> exponent, exponent)

### How to store on contracts ###
def store_variables(user_y, user_z, user_A, user_B, xS, BITS_SIGNIFICANT, BITS_EXPONENT):
    storage = {}
    storage['y'] = int(user_y)
    storage['z'] = int(user_z)
    storage['A'] = int(from_int(user_A, BITS_SIGNIFICANT, BITS_EXPONENT)[0])
    storage['B'] = int(from_int(user_B, BITS_SIGNIFICANT, BITS_EXPONENT)[0])
    storage['xA'] = int(from_int(user_A, BITS_SIGNIFICANT, BITS_EXPONENT)[1])
    storage['xB'] = int(from_int(user_B, BITS_SIGNIFICANT, BITS_EXPONENT)[1])
    storage['xS'] = int(xS)
    return(storage)

### Read Storage from Contract ###
def readStorage(read):
    y   = read["y"]     # curve liqudity
    z   = read["z"]     # curve capacity 
    A   = read["A"]     # A coefficient, base number
    B   = read["B"]     # B coefficient, base number 
    
    xA  = read["xA"]    # ditto, exponent
    xB  = read["xB"]    # ditto, exponent
    xS  = read["xS"]    # scaling exponent
    
    S  = 2**xS
    A *= 2**xA
    B *= 2**xB
    
    return y,z,A,B,S

### tradeBySource ###
def getTradeTargetAmount_bySource(dy,storage): ## trade by target
    y,z,A,B,S = readStorage(storage)
    ONE = S
    temp1 = z * ONE
    temp2 = y * A + z * B
    temp3 = temp2 * dy
    print("A", log2(A))
    print("B", log2(B))
    print("temp2", log2(temp2))
    print("temp3", log2(temp3))
    # scale = mulDivC(temp3, A, 2**256-1)
    scale = mulDivF(temp3, A, 2**255) + 1
    temp4 = mulDivC(temp1, temp1, scale)
    temp5 = mulDivC(temp3, A, scale)
    dx    = mulDivF(temp2, temp3 // scale, temp4 + temp5)
    assert dx < MAX

    # BEGIN DIAGNOSTICS
    warnings, errors = [], []

    if log2(temp1) > 255: errors += [f"temp1: overflow ({log2(temp1)})"]
    elif log2(temp1) > 220: warnings += [f"temp1: critical length ({log2(temp1)})"]
    
    if log2(temp2) > 255: errors += [f"temp2: overflow ({log2(temp2)})"]
    elif log2(temp2) > 220: warnings += [f"temp2: critical length ({log2(temp2)})"]
    
    if log2(temp3) > 255: errors += [f"temp3: overflow ({log2(temp3)})"]
    elif log2(temp3) > 220: warnings += [f"temp3: critical length ({log2(temp3)})"]

    if log2(temp4) < 8: errors += [f"temp4: underflow ({log2(temp4)})"]
    elif log2(temp4) < 16: warnings += [f"temp4: close to underflow ({log2(temp4)})"]

    if log2(temp5) < 8: errors += [f"temp5: underflow ({log2(temp5)})"]
    elif log2(temp5) < 16: warnings += [f"temp5: close to underflow ({log2(temp5)})"]
    
    diagnostics = {
        "success": True if len(errors) == 0 else False,
        "type":  "bySource",
        "yaABS": (y,z,A,B,S),
        "dy":  dy,
        "len": {
            "temp1": log2(temp1),
            "temp2": log2(temp2),
            "temp3": log2(temp3), 
            "temp4": log2(temp4), 
            "temp5": log2(temp5),  
        "warnings": warnings,
        "error": errors,
        }
    }
    # END DIAGNOSTICS
    
    return dy, int(dx), diagnostics

### tradeByTarget ###
def getTradeSourceAmount_byTarget(dx,storage):   ## trade by source
    y,z,A,B,S = readStorage(storage)
    ONE = S
    temp1 = z * ONE
    temp2 = y * A + z * B
    temp3 = temp2 - dx * A
    print("A", log2(A))
    print("B", log2(B))
    print("temp2", log2(temp2))
    print("temp3", log2(temp3))
    # scale = mulDivC(temp2, temp3, 2**256-1)
    scale = mulDivF(temp2, temp3, 2**255) + 1
    temp4 = mulDivC(temp1, temp1, scale)
    temp5 = mulDivF(temp2, temp3, scale)
    dy    = mulDivC(dx, temp4, temp5)
    assert dy < MAX
    
    # BEGIN DIAGNOSTICS
    warnings, errors = [], []
    
    if log2(temp1) > 255: errors += [f"temp1: overflow ({log2(temp1)})"]
    elif log2(temp1) > 220: warnings += [f"temp1: critical length ({log2(temp1)})"]
    
    if log2(temp2) > 255: errors += [f"temp2: overflow ({log2(temp2)})"]
    elif log2(temp2) > 220: warnings += [f"temp2: critical length ({log2(temp2)})"]
    
    if log2(temp3) > 255: errors += [f"temp3: overflow ({log2(temp3)})"]
    elif log2(temp3) > 220: warnings += [f"temp3: critical length ({log2(temp3)})"]

    if log2(temp4) < 8: errors += [f"temp4: underflow ({log2(temp4)})"]
    elif log2(temp4) < 16: warnings += [f"temp4: close to underflow ({log2(temp4)})"]

    if log2(temp5) < 8: errors += [f"temp5: underflow ({log2(temp5)})"]
    elif log2(temp5) < 16: warnings += [f"temp5: close to underflow ({log2(temp5)})"]

    diagnostics = {
        "success": True if len(errors) == 0 else False,
        "type":  "byTarget",
        "yaABS": (y,z,A,B,S),
        "dy":  dy,
        "len": {
            "temp1": log2(temp1),
            "temp2": log2(temp2),
            "temp3": log2(temp3),
            "temp4": log2(temp4),
            "temp5": log2(temp5),
        "warnings": warnings,
        "error": errors,
        }
    }
    # END DIAGNOSTICS
    return dx, int(dy), diagnostics

def unpack_order_inputs(order_inputs):
    pa = order_inputs['pa']
    pb = order_inputs['pb']
    y = order_inputs['y']
    z = order_inputs['z']
    decx = order_inputs['decx']
    decy = order_inputs['decy']
    return(pa, pb, y, z, decx, decy)

def create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT):
    pa, pb, y, z, decx, decy = unpack_order_inputs(order_inputs)
    user_y,user_z,user_A,user_B,user_S,xS = encode_order_inputs(pa, pb, y, z, decx, decy, ONE_EXPONENT) ## USDC-side order
    storage = store_variables(user_y, user_z, user_A, user_B, xS, BITS_SIGNIFICANT, BITS_EXPONENT)
    y,z,A,B,S = readStorage(storage)
    print('\nStandard variables encoded from user input')
    print(user_y,user_z,user_A,user_B,user_S)
    print("A contract encoded", from_int(user_A, BITS_SIGNIFICANT, BITS_EXPONENT))
    print("B contract encoded", from_int(user_B, BITS_SIGNIFICANT, BITS_EXPONENT))
    print('Standard variables read from contract')
    print(y,z,A,B,S)
    print("\n")
    return(storage)

def trade(amount, tradeByTarget, storage, order_inputs):
    pa, pb, y, z, decx, decy = unpack_order_inputs(order_inputs)  # just to bring in the correct decimals
    if not tradeByTarget:
        dx, dy, diagnostics = getTradeSourceAmount_byTarget(amount * 10**decy ,storage)
        print('TradeBySource', amount)
        print('inputAmount', dx, 'outputAmount', dy)
        print("Scaled by decimals:", dy / 10**decx)
        print(diagnostics)
        if len(diagnostics['len']['error']) > 0:
            raise
        if len(diagnostics['len']['warnings']) > 0:
            raise
        print("\n")
    else:
        dx, dy, diagnostics = getTradeTargetAmount_bySource(amount * 10**decx ,storage)
        print('TradeByTarget', amount)
        print('inputAmount', dx, 'outputAmount', dy)
        print("Scaled by decimals:", dy / 10**decy)
        print(diagnostics)
        if len(diagnostics['len']['error']) > 0:
            raise
        if len(diagnostics['len']['warnings']) > 0:
            raise
        print("\n")
