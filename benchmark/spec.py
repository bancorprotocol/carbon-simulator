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

#
#     M * M * x * y
# ---------------------
#  M * (M - L) * x + y
#
def tradeBySourceAmount(x, y, L, M):
    n = M * M * x * y
    d = M * (M - L) * x + y
    return n / d

#
#             x * y
# -----------------------------
#  M * (L - M) * x + M * M * y
#
def tradeByTargetAmount(x, y, L, M):
    n = x * y
    d = M * (L - M) * x + M * M * y
    return n / d
