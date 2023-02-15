from . import Decimal

S = 48

def encode(rate):
    data = int(Decimal(rate).sqrt() * (1 << S))
    exponent = max(len(bin(data)[2:]) - S, 0)
    return (data >> exponent) << exponent

class Order:
    def __init__(self, order):
        y = int(order['liquidity'])
        L = encode(order['lowestRate'])
        H = encode(order['highestRate'])
        M = encode(order['marginalRate'])
        self.y = y
        self.z = y * (H - L) // (M - L) if H != M else y
        self.A = H - L
        self.B = L
    def tradeBySourceAmount(self, amount):
        x, y, z, A, B = [int(amount), self.y, self.z, self.A, self.B]
        n = x * (A * y + B * z) ** 2
        d = A * x * (A * y + B * z) + (z << S) ** 2
        return n // d
    def tradeByTargetAmount(self, amount):
        x, y, z, A, B = [int(amount), self.y, self.z, self.A, self.B]
        n = x * (z << S) ** 2
        d = (A * y + B * z) * (A * y + B * z - A * x)
        return (n + d - 1) // d
