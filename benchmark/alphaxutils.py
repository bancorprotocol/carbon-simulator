from . import Decimal
Amount = Decimal

def assertAlmostEqual(actual, expected, maxError):
    actual, expected, maxError = [Decimal(x) for x in [actual, expected, maxError]]
    if actual != expected:
        error = abs(actual - expected) / expected
        assert error <= maxError, 'error = {:f}'.format(error)

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

def get_geoprice(i, orders):
    pb = orders[i].B**2
    pa = (orders[i].A + orders[i].B)**2
    return(((pa * pb)**Decimal('0.5')))

def goalseek(func, a, b, eps=None):
    """
    helper method: solves for x, a<x<b, such that func(x) == 0
    
    :func:    a function f(x), eg lambda x: x-3
    :a:       the lower bound
    :b:       the upper bound
    :eps:     precision, ie b/a value where goal seek returns
    :returns: the x value found
    """
    if eps is None:
        eps = Decimal('0.00000000001')
    if not a<b:
        raise ValueError("Bracketing value a must be smaller than b", a, b)
    fa = func(a)
    fb = func(b)
    if not fa*fb<0:
        raise ValueError("Sign of f(a) must be opposite of sign of f(b)", fa, fb, a, b)
        
    while 1:
        m = Decimal('0.5')*(a+b)
        fm = func(m)
        if fm * fa > 0:
            a = m
        else:
            b = m
        
        #print(f"m={m}, m={m}, b={b}")
        if b/a-1 < eps:
            return m

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
        self.pb = self.B * self.B
        self.pa = (self.A + self.B) ** 2
    def __iter__(self):
        y = self.y
        z = self.z
        A = self.A
        B = self.B
        yield 'liquidity'    , y
        yield 'lowestRate'   , B ** 2
        yield 'highestRate'  , (B + A) ** 2
        yield 'marginalRate' , (B + A * y / z) ** 2

    def dyfromp_f(self, p, checkbounds=True, raiseonerror=False):
        """
        returns dy = y_target - y as a function of the target marginal price

        :p:             the target marginal price, in the price convention of the pair
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the (positive!) dy value at which the marginal price is achieved
                        in cases where yfromp_f returns none, this func returns 0
        """
        if self.B == 0 and self.A == 0:
            if raiseonerror:
                raise ValueError("Can't determine trade prices from an empty curve", self.B, self.A)
            return 0
        y = self.yfromp_f(p, checkbounds, raiseonerror)
        if y is None: return 0
        return self.y-y

    def yfromp_f(self, p, checkbounds=True, raiseonerror=False):
        """
        returns y as a function of the target marginal price

        :p:             the target marginal price, in the price convention of the pair
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the y value at which the marginal price is achieved
                        if beyond the end it returns 0, if beyond start or current y None
        """
        # dydx = ((B * yint + S * y) / yint)**2 = (B + S y/yint)**2
        # y = yint * (sqrt(dydx) - B) / S
        dydx = p #if self.pair.has_quotetoken(self.tkn) else 1/p
        #print(f"[yfromp_f] pa={self.pa_raw} dydx={dydx} pb={self.pb_raw}")
        # print("1/dydx", 1/dydx)
        if checkbounds:
            if dydx > self.pa:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondStart("Price out of bounds (beyond start)", p, self.pa)
                return None
            elif dydx < self.pb:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondEnd("Price out of bounds (beyond end)", p, self.pb)
                return 0
        y = self.z * ((dydx.sqrt()) - self.B) / self.A
        if checkbounds:
            if y > self.y:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondMarg("Price out of bounds (beyond marginal), hence target y > y", y, self.y )
                return None
        return y

    def dxfromdy_f(self, dy, checkbounds=True, raiseonerror=False):
        """
        calculates the amount dx RECEIVED for a trade of dy

        :dy:            the amount of y the AMM sells (a POSITIVE number*)
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the amount of x the AMM receives (a POSITIVE number*)

        *when checkbounds is False then we can have dy<0, corresponding to the 
        AMM BUYing y. In this case it returns a negative number, corresponding
        to the AMM SELLing x.
        """
        if self.B == 0 and self.A == 0:
            if raiseonerror:
                raise ValueError("Can't trade on an empty curve", self.B, self.A)
            return 0

        if checkbounds:
            if dy < 0:
                if raiseonerror:
                    raise ValueError("AMM sell amount dy must be a non-negative number", dy)
                return None
            elif dy > self.y:
                if raiseonerror:
                    raise ValueError("AMM sell amount dy must be within available liquidity", dy, self.y)
                return None
        
        num   =                                   self.z**2
        #       ----------------------------------------------------------------------------------
        denom = (self.A*self.y+self.B*self.z) * (self.A*self.y+self.B*self.z-self.A*dy)

        return dy*(num/denom)   

    def xfromy_f(self, y, checkbounds=True, raiseonerror=False):
        """
        the invariant function, expressed as x=f(y)

        :y:             the amount of y the AMM currently holds
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the corresponding x amount*

        *in Carbon, the funds received on this curve are not kept on this curve but 
        transferred to a linked curve; the linked curve may hold different amounts
        of x, eg because it has been seeded with x>0. In other words -- it does not
        make sense to look at absolute values of x, only of differences.    
        """
        if checkbounds:
            if y > self.z:
                if raiseonerror:
                    raise ValueError("The value of y is out of bounds (y>yint)", y, self.z)
                return None
            elif y < 0:
                if raiseonerror:
                    raise ValueError("The value of y is out of bounds (y<0)", y)
                return None

        num =                          self.z * (self.z - y)
        #        -----------------------------------------------------------------------------
        denom =  self.B**2*self.z + self.B*self.A*y + self.B*self.A*self.z + self.A**2*y
        return num/denom

    def dyfromdx_f(self, dx, checkbounds=True, raiseonerror=False):
        """
        calculates the amount dy SOLD by the AMM to RECEIVE an amount dx

        :dx:            the amount of x the AMM RECEIVES (a POSITIVE number*)
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the amount dy of y the AMM SELLS (a POSITIVE number*)

        *when checkbounds is False then we can have dx<0, corresponding to the 
        AMM SELLing x. In this case it returns a negative number, corresponding
        to the AMM BUYing y.
        """
        if self.B == 0 and self.A == 0:
            if raiseonerror:
                raise ValueError("Can't trade on an empty curve", self.B, self.A)
            return 0

        if checkbounds:
            if dx < 0:
                if raiseonerror:
                    raise ValueError("AMM buy amount dx must be a non-negative number", dx)
                return None
            # elif dx > self.y:
            #     if raiseonerror:
            #         raise ValueError("AMM sell amount dx must be within available liquidity", dx, self.y)
            #     return None
        
        num   =               (self.A*self.y + self.B*self.z)**2
        #         -------------------------------------------------------------
        denom =   self.A*dx * (self.A*self.y + self.B*self.z) + self.z**2

        if checkbounds:
            if num < 0:
                if raiseonerror:
                    raise ValueError("AMM does not have enough y liquidity to purchase dx", self.y, dx, num)
                return None

        return dx * (num/denom) 

class AlphaRouter:
    """
    Alpha method - Restricts the exact algo calculation to specifically n threshold number of orders.
    """

    # returns an enumerated list with only values >= val
    def bigger_than(lst, val):
        return([(i,c) for i,c in lst if c >= val])

    # returns the sum of the values in an enumerated list
    def sum_me(lst):
        return(sum([c for i,c in lst]))

    # returns the first single min value in an enumerated list
    def min_item(lst):
        min_c = min([c for i,c in lst])
        min_c_list = [(i,c) for i,c in lst if c == min_c]
        if len(min_c_list) > 1:
            return(min_c_list[0])
        else:
            return(min_c_list[0])

    # returns the first single max value in an enumerated list
    def max_item(lst):
        max_c = max([c for i,c in lst])
        max_c_list = [(i,c) for i,c in lst if c == max_c]
        if len(max_c_list) > 1:
            return(max_c_list[0])
        else:
            return(max_c_list[0])

    def get_i(lst, wanted_i):
        return([(i,c) for i,c in lst if i == wanted_i][0])

    def sum_list_indexes(lst):
        return(sum([i for i,c in lst]))

    def list_indexes(lst):
        return([i for i,c in lst])

    def assertion_checks(full_fill, current_sum, threshold, max_fill, threshold_list, num_values):
        if full_fill == True:
            assert(round(current_sum, 12) >=  round(threshold, 12))
        else:
            assert(round(current_sum, 12) ==  round(max_fill, 12))

        if len(threshold_list) < num_values:
            pass
        else:
            assert(len(set([i for i,c in threshold_list])) == num_values)

    
    def gen_one_order_selector(numbers, threshold, num_values):
        count = 0
        current_sum = 0
        indexed_values = list(enumerate(numbers))
        max_index, max_val = AlphaRouter.max_item(indexed_values)
        threshold_list = indexed_values[:num_values]
        max_fill = sum(sorted(numbers, reverse=True)[:num_values])
        full_fill = False

        # liquidity check to determine partial fill
        if threshold <= max_fill:
            full_fill = True
            # print('Full fulfillment expected')
        else:
            # print(f'Partial fulfillment expected of {max_fill}')
            pass

        # loop over the remaining values
        while indexed_values:
            count += 1
            # set i based on the the value of the first item in the list, offset by the number of values selected
            i = indexed_values[0][0]+num_values-1
            current_sum = AlphaRouter.sum_me(threshold_list)

            # early exit when a partial fill is met
            if (not full_fill) & (current_sum==max_fill):
                # print('1')
                AlphaRouter.assertion_checks(full_fill, current_sum, threshold, max_fill, threshold_list, num_values)
                sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, threshold, count, sum_threshold_list_indexes)#
                return(AlphaRouter.list_indexes(threshold_list))

            # early exit when we filled the order
            if current_sum >= threshold:
                # print('2')
                AlphaRouter.assertion_checks(full_fill, current_sum, threshold, max_fill, threshold_list, num_values)
                sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, threshold, count, sum_threshold_list_indexes)#
                return(AlphaRouter.list_indexes(threshold_list))
            else:
                # else iterate over the remaining values dont exceed the the total number of inputs
                if i < len(numbers) - 1:
                    min_index, min_val = AlphaRouter.min_item(threshold_list)
                    next_val = AlphaRouter.get_i(indexed_values, i+1)[1]

                    # if the order hasn't been filled more liquidity is needed so swap out the minimum value and take the next in the list
                    # if the min_val in the threshold list is greater than the max_val in the full list things can't get any better
                    if min_val >= max_val:
                        # print('3')
                        AlphaRouter.assertion_checks(full_fill, current_sum, threshold, max_fill, threshold_list, num_values)
                        sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                        # return(threshold_list, current_sum, threshold, count, sum_threshold_list_indexes)#
                        return(AlphaRouter.list_indexes(threshold_list))
                    
                    # however, the next value to insert must be greater than the current value
                    elif next_val > min_val:
                        threshold_list.remove(AlphaRouter.min_item(threshold_list))
                        threshold_list.append(AlphaRouter.get_i(indexed_values, i+1))
                    else:
                        pass
                else:
                    # print('4')
                    AlphaRouter.assertion_checks(full_fill, current_sum, threshold, max_fill, threshold_list, num_values)
                    sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                    # return(threshold_list, current_sum, threshold, count, sum_threshold_list_indexes)#
                    return(AlphaRouter.list_indexes(threshold_list))
                indexed_values = indexed_values[1:]

