from . import Decimal

def encode(rate):
    return Decimal(rate).sqrt()

class Order:
    def __init__(self, order):
        self.y = Decimal(order['liquidity'])
        self.L = encode(order['lowestRate'])
        self.M = encode(order['marginalRate'])
    def tradeBySourceAmount(self, amount):
        x, y, L, M = [Decimal(amount), self.y, self.L, self.M]
        n = M * M * x * y
        d = M * (M - L) * x + y
        return n / d
    def tradeByTargetAmount(self, amount):
        x, y, L, M = [Decimal(amount), self.y, self.L, self.M]
        n = x * y
        d = M * (L - M) * x + M * M * y
        return n / d
