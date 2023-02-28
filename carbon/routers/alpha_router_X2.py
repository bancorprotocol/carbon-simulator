"""Alpha Router restricts the exact algo calculation to specifically n threshold number of orders."""
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *
import pandas as pd
import numpy as np


@dataclass
class AlphaRouterX2(BaseRouter):
    """
    Alpha method - Restricts the exact algo calculation to specifically n threshold number of orders.
    """

    use_positions_matchlevel: List[int] = None
    exact_router: ExactRouterX0Y0N = ExactRouterX0Y0N()

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
        max_index, max_val = AlphaRouterX2.max_item(indexed_amounts)
        threshold_list = indexed_amounts[:threshold_orders]    # set the initial threshold_list as the first orders in the list
        max_fill = sum(sorted(amounts, reverse=True)[:threshold_orders])  # identify the maximum return possible given the threshold_orders limitation
        current_sum = AlphaRouterX2.sum_me(threshold_list)
        print("[gen_two_order_selector] max_fill", max_fill)

        # liquidity check to determine partial fill
        full_fill = True if requested_trade_amount<=max_fill else False

        # you have already populated the threshold_list so you can start counting at the next item in the amounts list
        for i in range(threshold_orders,len(amounts)+1):
            count += 1
            current_sum = AlphaRouterX2.sum_me(threshold_list)

            # early exit when a partial fill is met
            if (not full_fill) & (current_sum==max_fill): # this works because a partial fill requires that the requested_trade_amount is <= max_fill, and max_fill is the n biggest values in the amounts, and thus the current_sum must include the biggest
                exit_summary = 1
                AlphaRouterX2.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
                sum_threshold_list_indexes = AlphaRouterX2.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
                return(AlphaRouterX2.list_indexes(threshold_list))

            # early exit when we filled the order
            if current_sum >= requested_trade_amount:
                exit_summary = 2
                AlphaRouterX2.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
                sum_threshold_list_indexes = AlphaRouterX2.sum_list_indexes(threshold_list)
                # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
                return(AlphaRouterX2.list_indexes(threshold_list))
            else:
                min_index, min_val = AlphaRouterX2.min_item_last(threshold_list)
                next_val = AlphaRouterX2.get_i(indexed_amounts, i)[1]

                # the next value to insert must be greater than the current value
                if next_val > min_val:
                    threshold_list.remove(AlphaRouterX2.min_item_last(threshold_list))
                    threshold_list.append(AlphaRouterX2.get_i(indexed_amounts, i))
                else:
                    pass
        exit_summary = 4
        current_sum = AlphaRouterX2.sum_me(threshold_list)
        AlphaRouterX2.assertion_checks(full_fill, current_sum, requested_trade_amount, max_fill, threshold_list, threshold_orders)
        sum_threshold_list_indexes = AlphaRouterX2.sum_list_indexes(threshold_list)
        # return(threshold_list, current_sum, requested_trade_amount, sum_threshold_list_indexes, count, exit_summary)#
        return(AlphaRouterX2.list_indexes(threshold_list))

    def get_geoprice(self, subject: int) -> DecFloatInt:
        """
        Determines the geometric price of the subject curve.
        """
        order = self.orders[subject]
        x0 = Decimal(str(order.x0))
        y0 = Decimal(str(order.y0))

        if self.use_floor_division:
            return x0 // y0
        else:
            return x0 / y0

    def amt_by_target(
            self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        An alternative trade by target function that performs a hypothetical
        swap against a subject order not constrained by available liquidity.

        :dx:         the required target amount
        :subject:   the "subject" order index
        """
        order = self.orders[subject]
        S = Decimal(str(order.S))
        B = Decimal(str(order.B))
        y = Decimal(str(order.y))
        y_int = Decimal(str(order.y_int))

        if self.use_floor_division:
            return (
                    dx * y_int ** 2 // ((S * y + B * y_int) * (S * y + B * y_int - S * dx))
            )
        else:
            return (
                    dx * y_int ** 2 / ((S * y + B * y_int) * (S * y + B * y_int - S * dx))
            )

    def match_by_target(
            self,
            x: DecFloatInt,
            is_by_target: bool = True,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            support_partial: bool = False,
    ) -> List[Action]:
        """
        The match by target function specfic to the Alpha router that:

        a1.) Run the inputAmount
             through all orders of appropriate pairs and return the hypothetical
             outputAmount for that order. Ignores whether or not there is
             sufficient liquidity associated with these orders.

        a2.) Sort the orders by maximum return (i.e. best price)

        a3.) Take the top n orders which **combined** have available liquidity
             greater than the inputAmount. I.e. cumulatively sum the available
             liquidity from the ranked orders and take the minimum number of
             orders required to fill the trade.

        a4.) Restrict the exact algo calculation to specifically these n orders
             to return the optimal distribution for the full inputAmount
             evaluated within the threshold number of orders.
        """
        if threshold_orders == None:
            threshold_orders = 10

        # (step 1.)

        hypothetical_output_amts = {
            i: self.amt_by_target(dx=x, subject=i) for i in self.indexes
        }

        # (step 2.)
        # Order the amounts
        ordered_amts = {
            j: hypothetical_output_amts[j]
            for j in sorted(
                self.indexes, key=lambda i: hypothetical_output_amts[i], reverse=True
            )
        }

        # (step 3.)
        # Get the available liquidity and return the minimum list of orders with
        # sufficient liquidity to fulfill the inputAmount
        ordered_associated_liquidity = {i:self.orders[i].y for i in ordered_amts.keys()}

        results = pd.DataFrame(
            [
                hypothetical_output_amts.keys(),
                hypothetical_output_amts.values(),
            ],
            index=[
                "indexes",
                "hypothetical_output_amts",
            ],
        )
        results = results.T.copy()
        results.sort_values(
            by=["hypothetical_output_amts", 'indexes'], ascending=[False, True], inplace=True
        )

        results2 = pd.DataFrame(
            [
                ordered_associated_liquidity.keys(),
                ordered_associated_liquidity.values(),
            ],
            index=[
                "ordered_associated_liquidity_keys",
                "ordered_associated_liquidity",
            ],
        )
        results2 = results2.T.copy()

        results = pd.merge(results, results2, how='left', left_on = 'indexes', right_on='ordered_associated_liquidity_keys')

        results.fillna(0, inplace=True)
        results.reset_index(inplace=True, drop=True)
        # print(f'is_by_target {is_by_target}') # True
        # print(tabulate(results,headers=list(results.columns)))
        if support_partial & (results.ordered_associated_liquidity.sum() < abs(x)):
            if x < 0:
                x = -results.ordered_associated_liquidity.sum() + Decimal('0.0000000001')
            else:
                x = results.ordered_associated_liquidity.sum() - Decimal('0.0000000001')
        # if support_partial:
        #     top_n_threshold_orders = results[:threshold_orders].indexes.values
        # else:
        passed_indexes = AlphaRouterX2.gen_two_order_selector(results.ordered_associated_liquidity, abs(x), threshold_orders)
        top_n_threshold_orders = [results.indexes[i] for i in passed_indexes]

        # (step 4.)
        # Constrain the exact router to just the top n threshold orders and match
        self.exact_router.orders = self.orders
        use_positions_matchlevel = top_n_threshold_orders  # top_n(threshold_orders)
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity,
            threshold_orders=threshold_orders,
            use_positions_matchlevel=use_positions_matchlevel,
            support_partial=support_partial,
        )

    def amt_by_src(
            self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        An alternative trade by source function that performs a hypothetical
        swap against a subject order not constrained by available liquidity.

        :x:         the required source amount
        :subject:   the "subject" order index
        """
        order = self.orders[subject]
        S = Decimal(str(order.S))
        B = Decimal(str(order.B))
        y = Decimal(str(order.y))
        y_int = Decimal(str(order.y_int))

        if self.use_floor_division:
            return (
                    dx
                    * (S * y + B * y_int) ** 2
                    // (S * dx * (S * y + B * y_int) + y_int ** 2)
            )
        else:
            return (
                    dx
                    * (S * y + B * y_int) ** 2
                    / (S * dx * (S * y + B * y_int) + y_int ** 2)
            )

    def match_by_src(
            self,
            x: DecFloatInt,
            is_by_target: bool = False,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            support_partial: bool = False,
    ) -> List[Action]:
        """
        The match by target function specfic to the Alpha router that:

        a1.) Run the inputAmount
             through all orders of appropriate pairs and return the hypothetical
             outputAmount for that order. Ignores whether or not there is
             sufficient liquidity associated with these orders.

        a2.) Sort the orders by maximum return (i.e. best price)

        a3.) Take the top n orders which **combined** have available liquidity
             greater than the inputAmount. I.e. cumulatively sum the available
             liquidity from the ranked orders and take the minimum number of
             orders required to fill the trade.

        a4.) Restrict the exact algo calculation to specifically these n orders
             to return the optimal distribution for the full inputAmount
             evaluated within the threshold number of orders.
        """
        # (step 1.)
        hypothetical_output_amts = {i: self.amt_by_src(dx=x, subject=i) for i in self.indexes}

        # (step 3.)
        # Get the available liquidity and return the minimum list of orders with
        # sufficient liquidity to fulfill the inputAmount
        associated_liquidity = [self.orders[i].y for i in self.indexes]

        amounts = []
        effective_prices = []
        available_value = []
        for k, v in hypothetical_output_amts.items():
            if v > self.orders[k].y:
                price = self.get_geoprice(k)
                amount = self.orders[k].y
                amounts += [amount]
                effective_prices += [price]
                available_value += [price * amount]
            else:
                amounts += [v]
                price = x / v
                effective_prices += [price]
                available_value += [price * v]

        results = pd.DataFrame(
            [
                hypothetical_output_amts.keys(),
                hypothetical_output_amts.values(),
                associated_liquidity,
                amounts,
                effective_prices,
                available_value,
            ],
            index=[
                "indexes",
                "hypothetical_output_amts",
                "associated_liquidity",
                "amount",
                "effective_prices",
                "available_value",
            ],
        )
        results = results.T.copy()
        results.sort_values(
            by=["hypothetical_output_amts", 'indexes'], ascending=[False, True], inplace=True
        )

        results.fillna(0, inplace=True)
        results.reset_index(inplace=True, drop=True)
        # print(f'is_by_target {is_by_target}') #False
        # print(tabulate(results,headers=list(results.columns)))
        if support_partial & (results.available_value.sum() < abs(x)):
            if x < 0:
                x = -results.available_value.sum() + Decimal('0.0000000001')
            else:
                x = results.available_value.sum() - Decimal('0.0000000001')
        # if support_partial:
        #     top_n_threshold_orders = results[:threshold_orders].indexes.values
        # else:
        passed_indexes = AlphaRouterX2.gen_two_order_selector(results.available_value, abs(x), threshold_orders)
        top_n_threshold_orders = [results.indexes[i] for i in passed_indexes]

        # (step 4.)
        # Constrain the exact router to just the top n threshold orders and match
        self.exact_router.orders = self.orders
        self.use_positions_matchlevel = top_n_threshold_orders  # top_n(threshold_orders)
        return self.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity,
            threshold_orders=threshold_orders,
            support_partial=support_partial,
        )

    def match(
            self,
            x: DecFloatInt,
            is_by_target: bool = True,
            completed_trade: bool = False,
            trade: Callable = None,
            cmp: Callable = None,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            support_partial: bool = False,
    ) -> List[Action]:
        """
        Main algorithm to handle matching a trade amount against the curves/orders.
        """
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity,
            threshold_orders=threshold_orders,
            use_positions_matchlevel=self.use_positions_matchlevel,
            support_partial=support_partial,
        )
