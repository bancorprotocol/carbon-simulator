"""Alpha Router restricts the exact algo calculation to specifically n threshold number of orders."""
import itertools
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *
import pandas as pd
from typing import Any
import numpy as np


@dataclass
class AlphaRouter(BaseRouter):
    """
    Alpha method - Restricts the exact algo calculation to specifically n threshold number of orders.
    """

    use_positions_matchlevel: List[int] = None
    exact_router: ExactRouterX0Y0N = ExactRouterX0Y0N()

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
        ordered_associated_liquidity = [self.orders[i].y for i in ordered_amts.keys()]

        results = pd.DataFrame(
            [
                hypothetical_output_amts.keys(),
                hypothetical_output_amts.values(),
                ordered_associated_liquidity,
            ],
            index=[
                "indexes",
                "hypothetical_output_amts",
                "ordered_associated_liquidity",
            ],
        )
        results = results.T.copy()
        results.sort_values(
            by=["hypothetical_output_amts", 'indexes'], ascending=[False, True], inplace=True
        )

        results.loc[:, 'sliding_index'] = [np.array(win.values.tolist(), dtype=object) for win in
                                           results.indexes.rolling(threshold_orders, min_periods=threshold_orders)]
        results.loc[:, 'sliding_available_value'] = results.ordered_associated_liquidity.rolling(threshold_orders,
                                                                                                 min_periods=threshold_orders).sum()

        results.fillna(0, inplace=True)
        results.reset_index(inplace=True, drop=True)
        # print(tabulate(results,headers=list(results.columns)))
        top_n_threshold_orders = \
        [results.sliding_index[i] for i in results.index if results.sliding_available_value[i] >= abs(x)][0]

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
        # print(x)
        hypothetical_output_amts = {i: self.amt_by_src(dx=x, subject=i) for i in self.indexes}
        # print(hypothetical_output_amts)

        # (step 3.)
        # Get the available liquidity and return the minimum list of orders with
        # sufficient liquidity to fulfill the inputAmount
        associated_liquidity = [self.orders[i].y for i in self.indexes]

        # ordered_associated_liquidity = [self.orders[i].y for i in ordered_amts.keys()]
        # print(ordered_associated_liquidity)

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

        results.loc[:, 'sliding_index'] = [np.array(win.values.tolist(), dtype=object) for win in
                                           results.indexes.rolling(threshold_orders, min_periods=threshold_orders)]
        results.loc[:, 'sliding_available_value'] = results.available_value.rolling(threshold_orders,
                                                                                    min_periods=threshold_orders).sum()

        results.fillna(0, inplace=True)
        results.reset_index(inplace=True, drop=True)
        # print(tabulate(results,headers=list(results.columns)))\
        top_n_threshold_orders = \
        [results.sliding_index[i] for i in results.index if results.sliding_available_value[i] >= abs(x)][0]

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
