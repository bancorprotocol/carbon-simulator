##########################
# Implementation (below) #

MIN = 0
MAX = 2**256-1

def check(val): assert MIN <= val <= MAX; return val

def add(a, b): return check(a + b)
def sub(a, b): return check(a - b)
def mul(a, b): return check(a * b)
def mulDivF(a, b, c): return check(a * b // c)
def mulDivC(a, b, c): return check((a * b + c - 1) // c)

SCALING_FACTOR = 2**48

def tradeBySourceAmountSolidity(
    posDx: any, 
    y_int: any, 
    B: any, 
    S: any, 
    y: any
) -> int:
    posDx, y, y_int, S, B = [int(val) for val in [posDx, y, y_int, S, B]]

    temp1 = mul(y_int, SCALING_FACTOR)
    temp2 = add(mul(y, S), mul(y_int, B))
    temp3 = mul(temp2, posDx)

    truncator = max(mulDivC(temp3, S, MAX), 1)

    temp4 = mulDivC(temp1, temp1, truncator)
    temp5 = mulDivC(temp3, S, truncator)
    negDy = mulDivF(temp2, temp3 // truncator, add(temp4, temp5))

    return negDy

def tradeByTargetAmountSolidity(
    negDy: any, 
    y_int: any, 
    B: any, 
    S: any, 
    y: any
) -> int:
    negDy, y, y_int, S, B = [int(val) for val in [negDy, y, y_int, S, B]]

    temp1 = mul(y_int, SCALING_FACTOR)
    temp2 = add(mul(B, y_int), mul(S, y))
    temp3 = sub(temp2, mul(negDy, S))

    truncator = max(mulDivC(temp2, temp3, MAX), 1)

    temp4 = mulDivC(temp1, temp1, truncator)
    temp5 = mulDivF(temp2, temp3, truncator)
    posDx = mulDivC(negDy, temp4, temp5)

    return posDx

# Implementation (above) #
##########################

###################################################################################################

#########################
# Specification (below) #

from decimal import Decimal
from decimal import getcontext

getcontext().prec = 100

def tradeBySourceAmountPython(
    posDx: any, 
    y_int: any, 
    B: any, 
    S: any, 
    y: any
) -> Decimal:
    x, y, z, A, B = [Decimal(val) for val in [posDx, y, y_int, S, B]]
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + z ** 2
    return n / d

def tradeByTargetAmountPython(
    negDy: any, 
    y_int: any, 
    B: any, 
    S: any, 
    y: any
) -> Decimal:
    x, y, z, A, B = [Decimal(val) for val in [negDy, y, y_int, S, B]]
    n = x * z ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return n / d

# Specification (above) #
#########################
