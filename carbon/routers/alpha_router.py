"""Hybrid router class."""
from abc import ABC
import itertools
import operator
from .exact_router_x0y0n import ExactRouterX0Y0N
from .base_router import *


@dataclass
class AlphaRouter(BaseRouter):
    """
    Hybrid method - for tradeByTarget:
        a1.) Run the full inputAmount through all orders (of appropriate pairs) and
            return the hypothetical outputAmount for that order Ignore whether or
            not there is sufficient liquidity associated with these orders

        a2.) Sort the orders by maximum return (i.e. best price)

        a3.) Take the top n orders which **combined** have available liquidity > inputAmount
            I.e. cumulatively sum the available liquidity from the
            ranked orders and take the minimum number of orders required to fill the trade

        a4.) Run these n orders through the exact algo to return the optimal distribution
            for the full inputAmount By definition if you know the inputAmount
            and outputAmount for each order, you know the effective price achieved against that order

    At this point we can make decisions based on a number of parameters or user inputs:
        b1.) Get matching objects by leave-one-out-price:
            - Run the exact algo on the top 2, top 3, …, top n orders to return matching objects that show
              the trade-off between effective price and gas cost (and available liquidity at that price)
        b2.) Get matching objects by leave-out-lowest-contribution method:
            - After (4 above) evaluate the order that contributes least to fulfilling the
              trade, leave this order out and rerun the exact algo on the remaining
              orders to return matching objects that show the trade-off between effective price and gas cost
              (and available liquidity at that price)
        b3.) maxPrice
            - When maxPrice is defined, we can observe the results from the exact algo to determine the amount
              of liquidity available up to the maxPrice.
            - We can return a filtered list of matching objects that show when only a partial trade fulfillment
              would occur at the maxPrice.
            - Can be applied to any output from the exact algo - prior to assembling the matching objects
    """

    exact_router: ExactRouterX0Y0N = ExactRouterX0Y0N()

    def trade_by_src_alt(self, x: DecFloatInt, subject: int) -> DecFloatInt: #
        """
        Where x denotes the desired target amount, and f(x) denotes the required source amount.
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
    
    def trade_by_target_alt(
        self, x: DecFloatInt, subject: int
    ) -> DecFloatInt:
        """
        Where x denotes the required source amount, and f(x) denotes the desired target amount.
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
    
    def get_current_price(
        self, subject: int
    ) -> DecFloatInt:
        """
        Determines the current starting price of the subject curve.
        """
        order = self.orders[subject]
        k = Decimal(str(order.k))
        n = Decimal(str(order.n))
        x = Decimal(str(order.x))
        x0 = Decimal(str(order.x0))

        if self.use_floor_division:
            return k // (n*x+x0*(1-n))**2
        else:
            return k / (n*x+x0*(1-n))**2

    def get_current_accel(
        self, subject: int
    ) -> DecFloatInt:
        """
        Determines the current starting price of the subject curve.
        """
        order = self.orders[subject]
        k = Decimal(str(order.k))
        n = Decimal(str(order.n))
        x = Decimal(str(order.x))
        x0 = Decimal(str(order.x0))

        if self.use_floor_division:
            return -2*k*n // (n*x + x0*(1 - n))**3
        else:
            return -2*k*n / (n*x + x0*(1 - n))**3

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
        return self.match(x=x, is_by_target=is_by_target)

    def match_by_target(
        self,
        x: DecFloatInt,
        threshold_orders: int,
        is_by_target: bool = True,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        a1.) Run the full inputAmount through all orders (of appropriate pairs) and
            return the hypothetical outputAmount for that order
            - Ignore whether there is sufficient liquidity associated with these orders

        a2.) Sort the orders by maximum return (i.e. best price)

        a3.) Take the top n orders which **combined** have available liquidity > inputAmount
            I.e. cumulatively sum the available liquidity from the
            ranked orders and take the minimum number of orders required to fill the trade

        a4.) Run these n orders through the exact algo to return the optimal distribution
            for the full inputAmount
            - By definition if you know the inputAmount and outputAmount for each order,
              you know the effective price achieved against that order
        """
        # print('loop')
        # (step 1.)
        hypothetical_output_amts = {
            i: self.trade_by_target_alt(x, i) for i in self.indexes
        }
        # print(hypothetical_output_amts)

        # (step 1.)
        starting_prices = {
            i: self.get_current_price(i) for i in self.indexes
        }
        # print(starting_prices)

        # (step 1.)
        starting_accels = {
            i: self.get_current_accel(i) for i in self.indexes
        }
        # print(starting_accels)  
        # print([-1/x for x in starting_accels])        


        # (step 2.)
        ordered_amts = {
            j: hypothetical_output_amts[j]
            for j in sorted(
                self.indexes, key=lambda i: hypothetical_output_amts[i], reverse=False
            )
        }
        # print(ordered_amts)


        # (step 3.)
        top_n = lambda n: list(
            itertools.takewhile(
                lambda i: sum(ordered_amts.values()) >= x,
                itertools.islice(ordered_amts.keys(), n),
            )
        )
        # print(top_n(threshold_orders))


        # (step 4.)
        self.exact_router.orders = self.orders
        use_positions_matchlevel = top_n(threshold_orders)
        return self.exact_router.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity, 
            threshold_orders=threshold_orders, 
            use_positions_matchlevel=use_positions_matchlevel
            )
