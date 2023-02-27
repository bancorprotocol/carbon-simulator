from .. import Decimal

ONE = 2 ** 48

MAX_UINT128 = 2 ** 128 - 1
MAX_UINT256 = 2 ** 256 - 1

def check(val, max): assert 0 <= val <= max; return val

def uint128(n): return check(n, MAX_UINT128)
def add(a, b): return check(a + b, MAX_UINT256)
def sub(a, b): return check(a - b, MAX_UINT256)
def mul(a, b): return check(a * b, MAX_UINT256)
def mulDivF(a, b, c): return check(a * b // c, MAX_UINT256)
def mulDivC(a, b, c): return check((a * b + c - 1) // c, MAX_UINT256)

def bitLength(value):
    return len(bin(value).lstrip('0b')) if value > 0 else 0

def encodeRate(value):
    data = int(value.sqrt() * ONE)
    length = bitLength(data // ONE)
    return (data >> length) << length

def decodeRate(value):
  return (value / ONE) ** 2

def encodeFloat(value):
    exponent = bitLength(value // ONE)
    mantissa = value >> exponent
    return mantissa | (exponent * ONE)

def decodeFloat(value):
    return (value % ONE) << (value // ONE)

def encodeOrder(order):
    y = int(order['liquidity'])
    L = encodeRate(Decimal(order['lowestRate']))
    H = encodeRate(Decimal(order['highestRate']))
    M = encodeRate(Decimal(order['marginalRate']))
    return {
        'y' : y,
        'z' : y if H == M else y * (H - L) // (M - L),
        'A' : encodeFloat(H - L),
        'B' : encodeFloat(L),
    }

def decodeOrder(order):
    y = Decimal(order['y'])
    z = Decimal(order['z'])
    A = Decimal(decodeFloat(order['A']))
    B = Decimal(decodeFloat(order['B']))
    return {
        'liquidity'    : y,
        'lowestRate'   : decodeRate(B),
        'highestRate'  : decodeRate(B + A),
        'marginalRate' : decodeRate(B + A if y == z else B + A * y / z),
    }

#
#      x * (A * y + B * z) ^ 2
# ---------------------------------
#  A * x * (A * y + B * z) + z ^ 2
#
def tradeBySourceAmountFunc(x, y, z, A, B):
    if (A == 0):
        return mulDivF(x, mul(B, B), mul(ONE, ONE))

    temp1 = mul(z, ONE)
    temp2 = add(mul(y, A), mul(z, B))
    temp3 = mul(temp2, x)

    factor1 = mulDivC(temp1, temp1, MAX_UINT256)
    factor2 = mulDivC(temp3, A, MAX_UINT256)
    factor = max(factor1, factor2)

    temp4 = mulDivC(temp1, temp1, factor)
    temp5 = mulDivC(temp3, A, factor)
    return mulDivF(temp2, temp3 // factor, add(temp4, temp5))

#
#                  x * z ^ 2
# -------------------------------------------
#  (A * y + B * z) * (A * y + B * z - A * x)
#
def tradeByTargetAmountFunc(x, y, z, A, B):
    if (A == 0):
        return mulDivC(x, mul(ONE, ONE), mul(B, B))

    temp1 = mul(z, ONE)
    temp2 = add(mul(y, A), mul(z, B))
    temp3 = sub(temp2, mul(x, A))

    factor1 = mulDivC(temp1, temp1, MAX_UINT256)
    factor2 = mulDivC(temp2, temp3, MAX_UINT256)
    factor = max(factor1, factor2)

    temp4 = mulDivC(temp1, temp1, factor)
    temp5 = mulDivF(temp2, temp3, factor)
    return mulDivC(x, temp4, temp5)

def tradeFunc(amount, order, func, fallback):
    x = amount
    y = order['y']
    z = order['z']
    A = decodeFloat(order['A'])
    B = decodeFloat(order['B'])
    try:
        return uint128(func(x, y, z, A, B))
    except AssertionError:
        return fallback

def tradeBySourceAmount(amount, order):
    return tradeFunc(amount, order, tradeBySourceAmountFunc, 0)

def tradeByTargetAmount(amount, order):
    return tradeFunc(amount, order, tradeByTargetAmountFunc, MAX_UINT256)

def execute(method, amount, order):
    return globals()[method](int(amount), encodeOrder(order))
