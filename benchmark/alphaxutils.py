from benchmark.core import Decimal
from benchmark.core.trade.impl import *
Amount = Decimal

tradeBySourceAmount_impl = tradeBySourceAmount
tradeByTargetAmount_impl = tradeByTargetAmount

def tradeByTargetAmount(amount, order):
    repack_order = {}
    repack_order['y'] = int(order.y)
    repack_order['z'] = int(order.z)
    repack_order['A'] = encodeFloat(int(order.A))
    repack_order['B'] = encodeFloat(int(order.B))
    return(tradeByTargetAmount_impl(int(amount), repack_order))

def tradeBySourceAmount(amount, order):
    # print("[alphaxutils, tradeBySourceAmount], order details",
    #       order.y, order.z, order.A, order.B, amount)
    repack_order = {}
    repack_order['y'] = int(order.y)
    repack_order['z'] = int(order.z)
    repack_order['A'] = encodeFloat(int(order.A))
    repack_order['B'] = encodeFloat(int(order.B))
    return(tradeBySourceAmount_impl(int(amount), repack_order))

def encodeOrderDecimal(order):
    dec_y = Decimal(order['dec_y'])
    dec_x = Decimal(order['dec_x'])
    dec_delta = dec_y - dec_x
    y = int(Decimal(order['liquidity']) * Decimal('10')**dec_y)
    L = encodeRate(Decimal(order['lowestRate']) * Decimal('10')**dec_delta)
    H = encodeRate(Decimal(order['highestRate']) * Decimal('10')**dec_delta)
    M = encodeRate(Decimal(order['marginalRate']) * Decimal('10')**dec_delta)

    # *** ENSURING THERE ARE NO CONSTANT PRICE ***
    if H==L:
        L -= 1
        # *** ENSURING THERE ARE NO CONSTANT PRICE ***

    return {
        'y' : y,
        'z' : y if H == M else y * (H - L) // (M - L),
        'A' : encodeFloat(H - L),
        'B' : encodeFloat(L),
        'dec_y': dec_y,
        'dec_x': dec_x,
    }

def get_geoprice(i, orders):
    return(((orders[i].pa * orders[i].pb)**Decimal('0.5')))

def handle_wei_discrepancy(sorted_actions, orders, over, tradeByTarget):
    if tradeByTarget:
        for k,v in sorted_actions.items():
            if over > 0:
                remainder = v['dy_specified'] % 10
                if (over - remainder) >= 0:
                    over -= remainder
                    sorted_actions[k]['dy_specified'] = int(v['dy_specified'] - remainder)
            assert(orders[k].y >= sorted_actions[k]['dy_specified'])

        for k,v in sorted_actions.items():
            if over < 0:
                remainder = v['dy_specified'] % 10
                left_over = 10 - remainder
                if (over + left_over) <= 0:
                    over += left_over
                    sorted_actions[k]['dy_specified'] = int(v['dy_specified'] + left_over)
            assert(orders[k].y >= sorted_actions[k]['dy_specified'])

        assert(over <= 10)
        k = list(sorted_actions.keys())[-1]
        sorted_actions[k]['dy_specified'] = int(sorted_actions[k]['dy_specified']-over)

        for k,v in sorted_actions.items():
            assert(orders[k].y >= sorted_actions[k]['dy_specified'])
    return(sorted_actions)

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
        eps = Decimal('1e-20')
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
        order = encodeOrderDecimal(order)
        self.y = Decimal(order['y'])
        self.z = Decimal(order['z'])
        self.A = Decimal(decodeFloat(order['A']))
        self.B = Decimal(decodeFloat(order['B']))
        self.dec_y = Decimal(order['dec_y'])
        self.dec_x = Decimal(order['dec_x'])
        self.pmarg = decodeRate(self.B + self.A if self.y == self.z else self.B + self.A * self.y / self.z)
        self.pb = decodeRate(self.B)
        self.pa = decodeRate(self.B + self.A)

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
        dydx = p 

        if checkbounds:
            if dydx > self.pa:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondStart("Price out of bounds (beyond start)", p, self.pa)
                return None
            elif dydx < self.pb:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondEnd("Price out of bounds (beyond end)", p, self.pb)
                return 0
        y = self.z * (dydx.sqrt() - self.pb.sqrt()) / (self.pa.sqrt()-self.pb.sqrt())
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
        
        # num   =                                   self.z**2
        # #       ----------------------------------------------------------------------------------
        # denom = (self.A*self.y+self.B*self.z) * (self.A*self.y+self.B*self.z-self.A*dy)

        newA = self.pa.sqrt()-self.pb.sqrt()
        newB = self.pb.sqrt()

        num   =                                   self.z**2
        #       ----------------------------------------------------------------------------------
        denom = (newA*self.y+newB*self.z) * (newA*self.y+newB*self.z-newA*dy)

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

        # num =                          self.z * (self.z - y)
        # #        -----------------------------------------------------------------------------
        # denom =  self.B**2*self.z + self.B*self.A*y + self.B*self.A*self.z + self.A**2*y

        newA = self.pa.sqrt()-self.pb.sqrt()
        newB = self.pb.sqrt()

        num =                          self.z * (self.z - y)
        #        -----------------------------------------------------------------------------
        denom =  newB**2*self.z + newB*newA*y + newB*newA*self.z + newA**2*y
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
        
        # num   =               (self.A*self.y + self.B*self.z)**2
        # #         -------------------------------------------------------------
        # denom =   self.A*dx * (self.A*self.y + self.B*self.z) + self.z**2

        newA = self.pa.sqrt()-self.pb.sqrt()
        newB = self.pb.sqrt()

        num   =               (newA*self.y + newB*self.z)**2
        #         -------------------------------------------------------------
        denom =   newA*dx * (newA*self.y + newB*self.z) + self.z**2

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
        
    # returns the last single min value in an enumerated list
    def min_item_last(lst):
        min_c = min([c for i,c in lst])
        min_c_list = [(i,c) for i,c in lst if c == min_c]
        if len(min_c_list) > 1:
            return(min_c_list[-1])
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

    def gen_two_order_selector(amounts, requested_trade_amount, threshold_orders):
        '''
        GenII is an improvement on GenI both in terms of readability and performance.
        The performance comes from a minor bug fix where (in GenI) the minimum valued item in the threshold list was preferentially low index value as opposed to high index value.
        The improvement results in a lower sum_threshold_list_indexes which indicates a better price ranking.
        GenII results in a better trade rate in approximately 1% of cases.

        Amounts should have been sorted into best-price-first order

        :amounts:                       the input amounts that need to be sorted and optimized
        :requested_trade_amount:        the minimum requested_trade_amount that need to be met by sorting the amounts
        :threshold_orders:              the number of amounts that are permitted to be used in order to meet the requested_trade_amount 


        ## WHAT IS KNOWN
        1. The maximum ouput amount is limited by the threshold_orders.
        2. If the maximum output amount is less than the requested_trade_amount then this is a partial fill
        3. The maximum number of amounts that make it into the final list is n-1 occuring only when the 
            requested_trade_amount is the sum of all but the final amount in the amounts list. 
            Else the process would have finished early with a partial fill
        4. The process ends if:
            a) Partial fill is supported and the sum(amounts) < requested_trade_amount
            b) If the sum(threshold_list) >= requested_trade_amount
        5. We should not get to the point where:
            a) We have iterated through every amount and the trade has not been met, as it should have been completed with partial or insufficient liquidity

        

        ### Order of operations
        1. Check if max_fill >= requested_trade_amount to determine if the request will be fully fulfilled
        2. For each value added to the threshold list check if trade is met
        3. When adding a new amount to the list it must be greater than the minimum amount already in the list
        
        '''
        exit_summary = 0
        count = 0
        indexed_amounts = list(enumerate(amounts))
        max_index, max_val = AlphaRouter.max_item(indexed_amounts)
        threshold_list = indexed_amounts[:threshold_orders]    # set the initial threshold_list as the first orders in the list
        max_fill = sum(sorted(amounts, reverse=True)[:threshold_orders])  # identify the maximum return possible given the threshold_orders limitation
        current_sum = AlphaRouter.sum_me(threshold_list)

        # liquidity check to determine partial fill
        full_fill = True if requested_trade_amount<=max_fill else False

        # you have already populated the threshold_list so you can start counting at the next item in the amounts list
        for i in range(threshold_orders,len(amounts)):
            count += 1
            current_sum = AlphaRouter.sum_me(threshold_list)

            # early exit when a partial fill is met
            if (not full_fill) & (current_sum==max_fill): # this works because a partial fill requires that the requested_trade_amount is <= max_fill, and max_fill is the n biggest values in the amounts, and thus the current_sum must include the biggest
                exit_summary = 1
                AlphaRouter.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
                sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
                return(AlphaRouter.list_indexes(threshold_list))

            # early exit when we filled the order
            if current_sum >= requested_trade_amount:
                exit_summary = 2
                AlphaRouter.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
                sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
                return(AlphaRouter.list_indexes(threshold_list))
            else:
                min_index, min_val = AlphaRouter.min_item_last(threshold_list)
                # print(i)
                # print(indexed_amounts)
                next_val = AlphaRouter.get_i(indexed_amounts, i)[1]

                # the next value to insert must be greater than the current value
                if next_val > min_val:
                    threshold_list.remove(AlphaRouter.min_item_last(threshold_list))
                    threshold_list.append(AlphaRouter.get_i(indexed_amounts, i))
                else:
                    pass

        exit_summary = 4
        current_sum = AlphaRouter.sum_me(threshold_list)
        AlphaRouter.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
        sum_threshold_list_indexes = AlphaRouter.sum_list_indexes(threshold_list)
        # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
        return(AlphaRouter.list_indexes(threshold_list))