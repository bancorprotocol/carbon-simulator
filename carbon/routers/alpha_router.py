"""Hybrid router class."""
from abc import ABC
import itertools
import operator
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *


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

    def match_by_src(
        self,
        x: DecFloatInt,
        is_by_target: bool = False,
        check_sufficient_liquidity: bool = True,
        threshold_orders: int = 2,
    ) -> List[Action]:
        """
        ...
        """
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity, 
            threshold_orders=threshold_orders, 
            )

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
