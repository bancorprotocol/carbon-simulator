from . import Decimal

def encode(rate):
    return Decimal(rate).sqrt()

def trade(test):
    y = Decimal(test['liquidity'])
    x = Decimal(test['inputAmount'])
    L = encode(test['lowestRate'])
    M = encode(test['marginalRate'])
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
