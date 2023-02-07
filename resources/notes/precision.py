MAX = 2 ** 112

def readStorage():
    y   = read("y")
    z   = read("z")
    A   = read("A")
    B   = read("B")
    sx  = read["sx"]
    abx = read["abx"]

    s  = 2**sx
    a *= 2**abx
    b *= 2**abx
    return y,z,A,B,s
    
def getTradeTargetAmount(x):
    """
    trade by source

                        x * z ^ 2
        -------------------------------------------
        (A * y + B * z) * (A * y + B * z - A * x)
    """
    y,z,A,B,s = readStorage()
    ONE = s
    temp1 = y * A + z * B               # 177 bits at most; cannot overflow
    temp2 = temp1 * x / ONE             # 224 bits at most; can overflow; some precision loss
    temp3 = temp2 * A + z * z * ONE     # 256 bits at most; can overflow
    res = mulDiv(temp1, temp2, temp3)
    assert res < MAX
    return res

def getTradeSourceAmount(x):
    """
    trade by target

            x * (A * y + B * z) ^ 2
        ---------------------------------
        A * x * (A * y + B * z) + z ^ 2   
    """
    y,z,A,B,s = readStorage()
    ONE = s
    temp1 = z * ONE                                 # 144 bits at most; cannot overflow
    temp2 = y * A + z * B                           # 177 bits at most; cannot overflow
    temp3 = temp2 - x * A                           # 177 bits at most; can underflow
    res = mulDiv(x * temp1, temp1, temp2 * temp3)   # each multiplication can overflow
    assert res < MAX
    return res
