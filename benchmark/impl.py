from . import Decimal

Amount = int

ONE = 2 ** 32

def encode(x): return x.sqrt() * ONE
def decode(x): return (x / ONE) ** 2

def mulDivF(x, y, z): return x * y // z
def mulDivC(x, y, z): return (x * y + z - 1) // z

class Order:
    def __init__(self, order):
        liq = int(Decimal(order['liquidity']))
        min = int(encode(Decimal(order['lowestRate'])))
        max = int(encode(Decimal(order['highestRate'])))
        mid = int(encode(Decimal(order['marginalRate'])))
        self.y = liq
        self.z = liq * (max - min) // (mid - min)
        self.A = max - min
        self.B = min
    def __iter__(self):
        y = Decimal(self.y)
        z = Decimal(self.z)
        A = Decimal(self.A)
        B = Decimal(self.B)
        yield 'liquidity'    , y
        yield 'lowestRate'   , decode(B)
        yield 'highestRate'  , decode(B + A)
        yield 'marginalRate' , decode(B + A * y / z)

def tradeBySourceAmount(x, order):
    y, z, A, B = [order.y, order.z, order.A, order.B]
    temp1 = y * A + z * B
    temp2 = temp1 * x // ONE
    temp3 = temp2 * A + z * z * ONE
    return x, mulDivF(temp1, temp2, temp3)

def tradeByTargetAmount(x, order):
    y, z, A, B = [order.y, order.z, order.A, order.B]
    temp1 = z * ONE
    temp2 = y * A + z * B
    temp3 = temp2 - x * A
    return mulDivC(x * temp1, temp1, temp2 * temp3), x
