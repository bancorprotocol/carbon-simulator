from . import Decimal

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
    data = int(Decimal(value).sqrt() * ONE)
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

def trade(test):
    y = int(test['liquidity'])
    x = int(test['inputAmount'])
    L = encodeRate(test['lowestRate'])
    H = encodeRate(test['highestRate'])
    M = encodeRate(test['marginalRate'])
    f = globals()['tradeBy' + test['tradeBy']]
    z = y if H == M else y * (H - L) // (M - L)
    A = decodeFloat(encodeFloat(H - L))
    B = decodeFloat(encodeFloat(L))
    return uint128(f(x, y, z, A, B))

#
#      x * (A * y + B * z) ^ 2
# ---------------------------------
#  A * x * (A * y + B * z) + z ^ 2
#
def tradeBySourceAmount(x, y, z, A, B):
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
def tradeByTargetAmount(x, y, z, A, B):
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