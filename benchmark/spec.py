from . import Decimal

def encodeRate(value):
    return Decimal(value).sqrt()

def trade(test):
    y = Decimal(test['liquidity'])
    x = Decimal(test['inputAmount'])
    L = encodeRate(test['lowestRate'])
    M = encodeRate(test['marginalRate'])
    f = globals()['tradeBy' + test['tradeBy']]
    return f(x, y, L, M)

def tradeBySourceAmount(x, y, L, M):
    n = M * M * x * y
    d = M * (M - L) * x + y
    return n / d

def tradeByTargetAmount(x, y, L, M):
    n = x * y
    d = M * (L - M) * x + M * M * y
    return n / d
