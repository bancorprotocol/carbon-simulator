from .. import Decimal

def encodeOrder(order):
    return {
        'y' : Decimal(order['liquidity']),
        'L' : Decimal(order['lowestRate']).sqrt(),
        'H' : Decimal(order['highestRate']).sqrt(),
        'M' : Decimal(order['marginalRate']).sqrt(),
    }

def decodeOrder(order):
    return {
        'liquidity'    : Decimal(order['y']),
        'lowestRate'   : Decimal(order['L']) ** 2,
        'highestRate'  : Decimal(order['H']) ** 2,
        'marginalRate' : Decimal(order['M']) ** 2,
    }

def tradeBySourceAmountFunc(x, y, L, M):
    n = M * M * x * y
    d = M * (M - L) * x + y
    return n / d

def tradeByTargetAmountFunc(x, y, L, M):
    n = x * y
    d = M * (L - M) * x + M * M * y
    return n / d

def tradeFunc(amount, order, func):
    x = amount
    y = order['y']
    L = order['L']
    M = order['M']
    return func(x, y, L, M)

def tradeBySourceAmount(amount, order):
    return tradeFunc(amount, order, tradeBySourceAmountFunc)

def tradeByTargetAmount(amount, order):
    return tradeFunc(amount, order, tradeByTargetAmountFunc)

def execute(method, amount, order):
    return globals()[method](Decimal(amount), encodeOrder(order))
