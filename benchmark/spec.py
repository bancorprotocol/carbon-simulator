from . import Decimal

Amount = Decimal

class Order:
    def __init__(self, order):
        liq = Decimal(order['liquidity'])
        min = Decimal(order['lowestRate']).sqrt()
        max = Decimal(order['highestRate']).sqrt()
        mid = Decimal(order['marginalRate']).sqrt()
        self.y = liq
        self.z = liq * (max - min) / (mid - min)
        self.A = max - min
        self.B = min
    def __iter__(self):
        y = self.y
        z = self.z
        A = self.A
        B = self.B
        yield 'liquidity'    , y
        yield 'lowestRate'   , B ** 2
        yield 'highestRate'  , (B + A) ** 2
        yield 'marginalRate' , (B + A * y / z) ** 2

def tradeBySourceAmount(x, order):
    y, z, A, B = [order.y, order.z, order.A, order.B]
    n = x * (A * y + B * z) ** 2
    d = A * x * (A * y + B * z) + z ** 2
    return x, n / d

def tradeByTargetAmount(x, order):
    y, z, A, B = [order.y, order.z, order.A, order.B]
    n = x * z ** 2
    d = (A * y + B * z) * (A * y + B * z - A * x)
    return n / d, x
