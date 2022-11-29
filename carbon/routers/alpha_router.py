"""Hybrid router class."""
from abc import ABC
import itertools
import operator
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *
import pandas as pd
from tabulate import tabulate



@dataclass
class AlphaRouter(BaseRouter):
    """
    Alpha method - for tradeByTarget:
        a1.) Run the inputAmount divided by the threshold_orders (to scale size)
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

    exact_router: ExactRouterX0Y0N = ExactRouterX0Y0N()

    def get_geoprice(
        self, subject: int
    ) -> DecFloatInt:
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

    
    def trade_by_target_alt(
        self, x: DecFloatInt, subject: int
    ) -> DecFloatInt:
        """
        An alternative trade by target function that performs a hypothetical
        swap against a subject order not constrained by available liquidity.

        :x:         the required target amount
        :subject:   the "subject" order index 
        """
        order = self.orders[subject]
        S = Decimal(str(order.S))
        B = Decimal(str(order.B))
        y = Decimal(str(order.y))
        y_int = Decimal(str(order.y_int))

        if self.use_floor_division:
            return x * y_int**2 // ((S * y + B * y_int) * (S * y + B * y_int - S * x))
        else:
            return x * y_int**2 / ((S * y + B * y_int) * (S * y + B * y_int - S * x))

    def match_by_target(
        self,
        x: DecFloatInt,
        threshold_orders: int,
        is_by_target: bool = True,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        The match by target function specfic to the Alpha router that:

        a1.) Run the inputAmount divided by the threshold_orders (to scale size)
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
        # Scale the inputAmount x by the number of threshold orders and perform
        # the hypothetical trade
        hypothetical_output_amts = {
            i: self.trade_by_target_alt(x/threshold_orders, i) for i in self.indexes
        }

        # (step 2.)
        # Order the amounts
        ordered_amts = {
            j: hypothetical_output_amts[j]
            for j in sorted(
                self.indexes, key=lambda i: hypothetical_output_amts[i], reverse=False
            )
        }

        # (step 3.)
        # Get the available liquidity and return the minimum list of orders with
        # sufficient liquidity to fulfill the inputAmount
        ordered_associated_liquidity = [self.orders[i].y for i in ordered_amts.keys()]
        top_n = lambda n: list(
            itertools.takewhile(
                lambda i: sum(ordered_associated_liquidity) >= x,
                itertools.islice(ordered_amts.keys(), n),
            )
        )
        # print(top_n(threshold_orders))

        # (step 4.)
        # Constrain the exact router to just the top n threshold orders and match
        self.exact_router.orders = self.orders
        use_positions_matchlevel = top_n(threshold_orders)
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity, 
            threshold_orders=threshold_orders, 
            use_positions_matchlevel=use_positions_matchlevel
            )
            

    def trade_by_src_alt(self, x: DecFloatInt, subject: int) -> DecFloatInt: #
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
                x
                * (S * y + B * y_int) ** 2
                // (S * x * (S * y + B * y_int) + y_int**2)
            )
        else:
            return (
                x
                * (S * y + B * y_int) ** 2
                / (S * x * (S * y + B * y_int) + y_int**2)
            )

    def match_by_src(
        self,
        x: DecFloatInt,
        threshold_orders: int,
        is_by_target: bool = False,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        The match by target function specfic to the Alpha router that:

        a1.) Run the inputAmount divided by the threshold_orders (to scale size)
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
        # Scale the inputAmount x by the number of threshold orders and perform
        # the hypothetical trade
        # print(x)
        hypothetical_output_amts = {
            i: self.trade_by_src_alt(x, i) for i in self.indexes
        }
        # print(hypothetical_output_amts)


        # (step 2.)
        # Order the amounts
        ordered_amts = {
            j: hypothetical_output_amts[j]
            for j in sorted(
                self.indexes, key=lambda i: hypothetical_output_amts[i], reverse=True
            )
        }
        # print(ordered_amts)

        # (step 3.)
        # Get the available liquidity and return the minimum list of orders with
        # sufficient liquidity to fulfill the inputAmount
        associated_liquidity = [self.orders[i].y for i in self.indexes]

        ordered_associated_liquidity = [self.orders[i].y for i in ordered_amts.keys()]
        # print(ordered_associated_liquidity)

        amounts = []
        effective_prices = []
        available_value = []
        for k,v in hypothetical_output_amts.items():
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
            [hypothetical_output_amts.keys(), hypothetical_output_amts.values(), associated_liquidity, amounts, effective_prices, available_value],
            index = ['indexes', 'hypothetical_output_amts', 'associated_liquidity', 'amount', 'effective_prices', 'available_value']
            )
        results = results.T.copy()
        results.sort_values(by='hypothetical_output_amts', ascending=False, inplace=True)
        # print(tabulate(results,headers=list(results.columns)))

        top_n = lambda n: list(
            itertools.takewhile(
                lambda i: sum(results.available_value) >= x,
                itertools.islice(results.indexes, n),
            )
        )
        # print(top_n(threshold_orders))

        # (step 4.)
        # Constrain the exact router to just the top n threshold orders and match
        self.exact_router.orders = self.orders
        use_positions_matchlevel = top_n(threshold_orders)
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity, 
            threshold_orders=threshold_orders, 
            use_positions_matchlevel = use_positions_matchlevel
            )