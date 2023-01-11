"""Alpha Router restricts the exact algo calculation to specifically n threshold number of orders."""
import itertools
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *
import pandas as pd
from typing import Any
import numpy as np
from tabulate import tabulate
import heapq


@dataclass
class AlphaRouter(BaseRouter):
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
            assert(current_sum >= threshold)
        else:
            assert(current_sum == max_fill)

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
        passed_indexes = AlphaRouter.gen_one_order_selector(results.ordered_associated_liquidity, abs(x), threshold_orders)
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
        passed_indexes = AlphaRouter.gen_one_order_selector(results.available_value, abs(x), threshold_orders)
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
        )
