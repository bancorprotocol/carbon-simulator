from . import Decimal

ONE = 2 ** 48

def bitLength(value):
    return len(bin(value).lstrip('0b')) if value > 0 else 0

def encodeRate(value):
    data = int(Decimal(value).sqrt() * ONE)
    exponent = bitLength(data // ONE)
    return (data >> exponent) << exponent

def encodeFloat(value):
    exponent = bitLength(value // ONE)
    mantissa = value >> exponent
    return mantissa | (exponent * ONE)

def expandFloat(value):
    return (value % ONE) << (value // ONE)

def trade(test):
    y = int(test['liquidity'])
    x = int(test['inputAmount'])
    L = encodeRate(test['lowestRate'])
    H = encodeRate(test['highestRate'])
    M = encodeRate(test['marginalRate'])
    f = globals()['tradeBy' + test['tradeBy']]
    z = y * (H - L) // (M - L) if H != M else y
    A = encodeFloat(H - L)
    B = encodeFloat(L)
    return f(x, y, z, A, B)

def tradeBySourceAmount(x, y, z, A, B):
    A = expandFloat(A)
    B = expandFloat(B)
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + (z * ONE) ** 2
    return n // d

def tradeByTargetAmount(x, y, z, A, B):
    A = expandFloat(A)
    B = expandFloat(B)
    n = x * (z * ONE) ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return (n + d - 1) // d
