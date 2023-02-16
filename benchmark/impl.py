from . import Decimal

ONE = 2 ** 48

def encode(rate):
    data = int(Decimal(rate).sqrt() * ONE)
    exponent = len(bin(data // ONE)) - 2
    return (data >> exponent) << exponent

def trade(test):
    y = int(test['liquidity'])
    x = int(test['inputAmount'])
    L = encode(test['lowestRate'])
    H = encode(test['highestRate'])
    M = encode(test['marginalRate'])
    f = globals()['tradeBy' + test['tradeBy']]
    z = y * (H - L) // (M - L) if H != M else y
    A = H - L
    B = L
    return f(x, y, z, A, B)

def tradeBySourceAmount(x, y, z, A, B):
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + (z * ONE) ** 2
    return n // d

def tradeByTargetAmount(x, y, z, A, B):
    n = x * (z * ONE) ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return (n + d - 1) // d
