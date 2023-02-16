from math import *

# mulDivF = lambda x, y, z: (x * y) // z
# mulDiv = mulDivF
# mulDivC = lambda x, y, z: (x * y + z - 1) // z
# MAX = 2 ** 112

### FRONT END ###
def encode_order_inputs(pa, pb, y, z, decx, decy, xS):
    """returns (y,z,A,B,s) from prices, curve loading and capacity, decimals and scaling exponent"""
    decf = 10**(decy-decx)
    one = 2**xS
    a = sqrt(pa*decf)-sqrt(pb*decf) 
    b = sqrt(pb*decf)               
    return int(y*10**decy), int(z*10**decy), int(a*one), int(b*one), int(one), int(xS)

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
    
    return int(y),int(z),int(A),int(B),int(S)

# ### tradeBySource ###
# def getTradeTargetAmount_bySource(dy,storage):
#     y,z,A,B,S = readStorage(storage)
#     ONE = S
#     temp1 = z * ONE
#     temp2 = y * A + z * B
#     temp3 = temp2 * dy
#     scale = mulDivC(temp3, A, 2**256-1)
#     temp4 = mulDivC(temp1, temp1, scale)
#     temp5 = mulDivC(temp3, A, scale)
#     dx    = mulDivF(temp2, temp3 // scale, temp4 + temp5)
#     assert dx < MAX

#     # BEGIN DIAGNOSTICS
#     warnings, errors = [], []

#     if log2(temp1) > 255: errors += [f"temp1: overflow ({log2(temp1)})"]
#     elif log2(temp1) > 220: warnings += [f"temp1: critical length ({log2(temp1)})"]
    
#     if log2(temp2) > 255: errors += [f"temp2: overflow ({log2(temp2)})"]
#     elif log2(temp2) > 220: warnings += [f"temp2: critical length ({log2(temp2)})"]
    
#     if log2(temp3) > 255: errors += [f"temp3: overflow ({log2(temp3)})"]
#     elif log2(temp3) > 220: warnings += [f"temp3: critical length ({log2(temp3)})"]

#     if log2(temp4) < 8: errors += [f"temp4: underflow ({log2(temp4)})"]
#     elif log2(temp4) < 16: warnings += [f"temp4: close to underflow ({log2(temp4)})"]

#     if log2(temp5) < 8: errors += [f"temp5: underflow ({log2(temp5)})"]
#     elif log2(temp5) < 16: warnings += [f"temp5: close to underflow ({log2(temp5)})"]
    
#     diagnostics = {
#         "success": True if len(errors) == 0 else False,
#         "type":  "bySource",
#         "yaABS": (y,z,A,B,S),
#         "dy":  dy,
#         "len": {
#             "temp1": log2(temp1),
#             "temp2": log2(temp2),
#             "temp3": log2(temp3), 
#             "temp4": log2(temp4), 
#             "temp5": log2(temp5),  
#         "warnings": warnings,
#         "error": errors,
#         }
#     }
#     # END DIAGNOSTICS
    
#     return dy, int(dx), diagnostics

# ### tradeByTarget ###
# def getTradeSourceAmount_byTarget(dx,storage):
#     y,z,A,B,S = readStorage(storage)
#     ONE = S
#     temp1 = z * ONE
#     temp2 = y * A + z * B
#     temp3 = temp2 - dx * A
#     scale = mulDivC(temp2, temp3, 2**256-1)
#     temp4 = mulDivC(temp1, temp1, scale)
#     temp5 = mulDivF(temp2, temp3, scale)
#     dy    = mulDivC(dx, temp4, temp5)
#     assert dy < MAX
    
#     # BEGIN DIAGNOSTICS
#     warnings, errors = [], []
    
#     if log2(temp1) > 255: errors += [f"temp1: overflow ({log2(temp1)})"]
#     elif log2(temp1) > 220: warnings += [f"temp1: critical length ({log2(temp1)})"]
    
#     if log2(temp2) > 255: errors += [f"temp2: overflow ({log2(temp2)})"]
#     elif log2(temp2) > 220: warnings += [f"temp2: critical length ({log2(temp2)})"]
    
#     if log2(temp3) > 255: errors += [f"temp3: overflow ({log2(temp3)})"]
#     elif log2(temp3) > 220: warnings += [f"temp3: critical length ({log2(temp3)})"]

#     if log2(temp4) < 8: errors += [f"temp4: underflow ({log2(temp4)})"]
#     elif log2(temp4) < 16: warnings += [f"temp4: close to underflow ({log2(temp4)})"]

#     if log2(temp5) < 8: errors += [f"temp5: underflow ({log2(temp5)})"]
#     elif log2(temp5) < 16: warnings += [f"temp5: close to underflow ({log2(temp5)})"]

#     diagnostics = {
#         "success": True if len(errors) == 0 else False,
#         "type":  "byTarget",
#         "yaABS": (y,z,A,B,S),
#         "dy":  dy,
#         "len": {
#             "temp1": log2(temp1),
#             "temp2": log2(temp2),
#             "temp3": log2(temp3),
#             "temp4": log2(temp4),
#             "temp5": log2(temp5),
#         "warnings": warnings,
#         "error": errors,
#         }
#     }
#     # END DIAGNOSTICS
#     return dx, int(dy), diagnostics

def unpack_order_inputs(order_inputs):
    pa = order_inputs['pa']
    pb = order_inputs['pb']
    y = order_inputs['y']
    z = order_inputs['z']
    decx = order_inputs['decx']
    decy = order_inputs['decy']
    return(pa, pb, y, z, decx, decy)

def create_order(order_inputs, BITS_SIGNIFICANT, BITS_EXPONENT, ONE_EXPONENT):
    pa, pb, input_y, input_z, decx, decy = unpack_order_inputs(order_inputs)
    enc_y,enc_z,enc_A,enc_B,enc_S,xS = encode_order_inputs(pa, pb, input_y, input_z, decx, decy, ONE_EXPONENT) ## USDC-side order
    storage = store_variables(enc_y,enc_z,enc_A,enc_B,xS, BITS_SIGNIFICANT, BITS_EXPONENT)
    y,z,A,B,S = readStorage(storage)
    print('\nUser input')
    print("pa(user)", pa)
    print("pb(user)", pb)
    print("y(user) ", input_y)
    print("z(user) ", input_z)

    print('\nStandard variables encoded from user input')
    print("A(S)    ", enc_A)
    print("B(B)    ", enc_B)
    print("y(y)    ", enc_y)
    print("z(y_int)", enc_z)
    # print(user_y,user_z,user_A,user_B,user_S)
    print("A contract encoded", from_int(enc_A, BITS_SIGNIFICANT, BITS_EXPONENT))
    print("B contract encoded", from_int(enc_B, BITS_SIGNIFICANT, BITS_EXPONENT))
    print('Standard variables read from contract')
    # print(y,z,A,B,S)
    print("A(S)    ", A)
    print("B(B)    ", B)
    print("y(y)    ", y)
    print("z(y_int)", z)
    print("\n")
    return(storage)

# def trade_by_source_act(dy, storage):
#     y,z,A,B,s = readStorage(storage)
#     assert dy <= y, 'Insufficient Liquidity'
#     ONE = s
#     temp1 = z * ONE               
#     temp2 = y * A + z * B      
#     temp3 = temp2 - dy * A      
#     scale = mulDiv(temp2, temp3, 2**255)+1
#     temp1s = temp1//scale
#     temp2s = temp2//scale
#     dx = mulDiv(dy*temp1s, temp1, temp2s*temp3)
#     print('dy', 'dy*temp1s', 'temp1', 'temp2s*temp3', 'dx')
#     print(dy, dy*temp1s, temp1, temp2s*temp3, dx)
#     return dx

# def trade_by_target_act(dx, storage):
#     y,z,A,B,s = readStorage(storage)
#     ONE = s
#     temp1 = y * A + z * B               # 177 bits at most; cannot overflow
#     temp2 = temp1 * dx / ONE            # 224 bits at most; can overflow; some precision loss
#     temp3 = temp2 * A + z * z * ONE     # 256 bits at most; can overflow
#     dy = mulDiv(temp1, temp2, temp3)
#     assert dy <= y, 'Insufficient Liquidity'
#     print(dx, temp1, temp2, temp3, dy)
#     return dy

MIN = 0
MAX = 2**256-1

def check(val): assert MIN <= val <= MAX; return val

def add(a, b): return check(a + b)
def sub(a, b): return check(a - b)
def mul(a, b): return check(a * b)
def mulDivF(a, b, c): return check(a * b // c)
def mulDivC(a, b, c): return check((a * b + c - 1) // c)

# SCALING_FACTOR = 40

def tradeBySourceAmountSolidity(
    posDx: any, 
    storage: any,
    SCALING_FACTOR,
) -> int:
    y,y_int,S,B,s = readStorage(storage)
    posDx, y, y_int, S, B = [int(val) for val in [posDx, y, y_int, S, B]]

    temp1 = mul(y_int, 2**SCALING_FACTOR)
    temp2 = add(mul(y, S), mul(y_int, B))
    temp3 = mul(temp2, posDx)

    truncator = max(mulDivC(temp3, S, MAX), 1)

    temp4 = mulDivC(temp1, temp1, truncator)
    temp5 = mulDivC(temp3, S, truncator)
    negDy = mulDivF(temp2, temp3 // truncator, add(temp4, temp5))

    return negDy

def tradeByTargetAmountSolidity(
    negDy: any, 
    storage: any,
    SCALING_FACTOR,
) -> int:
    y,y_int,S,B,s = readStorage(storage)
    negDy, y, y_int, S, B = [int(val) for val in [negDy, y, y_int, S, B]]

    temp1 = mul(y_int, 2**SCALING_FACTOR)
    temp2 = add(mul(B, y_int), mul(S, y))
    temp3 = sub(temp2, mul(negDy, S))

    truncator = max(mulDivC(temp2, temp3, MAX), 1)
    # print('temp1', 'temp2', 'temp3', 'truncator')
    # print(temp1, temp2, temp3, truncator)
    temp4 = mulDivC(temp1, temp1, truncator)
    temp5 = mulDivF(temp2, temp3, truncator)
    # print('negDy', 'temp4', 'temp5')
    # print(negDy, temp4, temp5)
    posDx = mulDivC(negDy, temp4, temp5)

    return posDx



def trade(amount, tradeByTarget, storage, order_inputs, SCALING_FACTOR):
    pa, pb, y, z, decx, decy = unpack_order_inputs(order_inputs)  # just to bring in the correct decimals
    if not tradeByTarget:
        try:
            dy = tradeBySourceAmountSolidity(amount * 10**decx , storage, SCALING_FACTOR)
        except AssertionError as e:
            print('\n**TradeByTarget Trade Errror**\n')
            return("AssertionError")
        print('TradeByTarget', amount)
        print('inputAmount', amount * 10**decx, 'outputAmount', dy)
        print("Effective rate    :", (dy / 10**decy)/(amount))
        print("Scaled by decimals:", dy / 10**decy)
        # print(diagnostics)
        # if len(diagnostics['len']['error']) > 0:
        #     raise
        print("\n")
        return(dy / 10**decy)
    else:
        try:
            dx = tradeByTargetAmountSolidity(amount * 10**decy, storage, SCALING_FACTOR)
        except AssertionError as e:
            print('\n**TradeBySource Trade Errror**\n')
            return("AssertionError")
        print('TradeBySource', amount)
        print('inputAmount', amount * 10**decy, 'outputAmount', dx)
        print("Effective rate    :", (dx / 10**decx)/(amount))
        print("Scaled by decimals:", dx / 10**decx)
        # print(diagnostics)
        # if len(diagnostics['len']['error']) > 0:
        #     raise
        print("\n")
        return(dx / 10**decx)
