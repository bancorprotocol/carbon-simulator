"""
Manual router class to isolate testing for trades without consideration of routing/matching logic.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
from decimal import Decimal

from typing import List, Callable

from dataclasses import dataclass

from carbon.order import DecFloatInt
from carbon.routers.base_router import BaseRouter, Action


@dataclass
class ManualRouter(BaseRouter):
    """
    Manual router class for both Simple and Complex routers.
    """

    ONE: DecFloatInt = 2 ** 32
    MIN: DecFloatInt = 0
    MAX: DecFloatInt = 2 ** 128 - 1

    def mul_div_f(self, x: DecFloatInt, y: DecFloatInt, z: DecFloatInt) -> DecFloatInt:
        # #self.logger.debug(f"mul_div_f: {x} {y} {z}")
        if self.use_floor_division:
            return x * y // z
        else:
            return x * y / z

    def mul_div_c(self, x: DecFloatInt, y: DecFloatInt, z: DecFloatInt) -> DecFloatInt:
        # #self.logger.debug(f"mul_div_c: {x} {y} {z}")
        if self.use_floor_division:
            return (x * y + z - 1) // z
        else:
            return x * y / z

    def amt_by_src(
            self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        * Return:
        *
        *                  x * z ^ 2
        * -------------------------------------------
        *  (A * y + B * z) * (A * y + B * z - A * x)
        *
        """
        order = self.orders[subject]
        y, z, A, B = [Decimal(order.y), Decimal(order.y_int), Decimal(order.S), Decimal(order.B)]
        temp1 = z * self.ONE
        temp2 = y * A + z * B
        temp3 = temp2 - dx * A
        res = self.mul_div_c(dx * temp1, temp1, temp2 * temp3)
        # self.logger.debug(
        #     f"amt_by_src: {subject} {dx} -> {res} ({order.y} {order.y_int} {order.S} {order.B})"
        # )
        return res

    def amt_by_target(
            self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        * Return:
        *
        *      x * (A * y + B * z) ^ 2
        * ---------------------------------
        *  A * x * (A * y + B * z) + z ^ 2
        *
        """
        order = self.orders[subject]
        y, z, A, B = Decimal(order.y), Decimal(order.y_int), Decimal(order.S), Decimal(order.B)
        temp1 = y * A + z * B
        temp2 = temp1 * dx // self.ONE
        temp3 = temp2 * A + z * z * self.ONE
        res = self.mul_div_f(temp1, temp2, temp3)
        # self.logger.debug(
        #     f"amt_by_target: {subject} {dx} -> {res} ({order.y} {order.y_int} {order.S} {order.B})"
        # )
        return res

    def match(
            self,
            x: DecFloatInt,
            is_by_target: bool = True,
            completed_trade: bool = False,
            trade: Callable = None,
            cmp: Callable = None,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            use_routes: List[dict] = None
    ) -> List[Action]:
        """
        Main algorithm to handle matching a trade amount against the curves/orders.
        """
        actions = [
            Action(
                match_method="by_src" if not is_by_target else "by_target",
                index=indx,
                x=x,
                input=self.frmt(trade(indx, dx)),
                output=self.frmt(dx)
            )
            for indx, dx in use_routes
        ]

        # Format the output
        actions[0].total_output = actions[0].output
        actions[0].total_input = actions[0].input
        for i in range(1, len(actions)):
            actions[i].total_output = actions[i - 1].total_output + actions[i].output
            actions[i].total_input = actions[i - 1].total_input + actions[i].input

        for i in range(len(actions)):
            actions[i].total_output = self.frmt(actions[i].total_output)
            actions[i].total_input = self.frmt(actions[i].total_input)
            actions[i].input = self.frmt(actions[i].input)
            actions[i].output = self.frmt(actions[i].output)

        actions[-1].total_output = -actions[-1].total_output
        return actions

    def match_by_src(
            self,
            x: DecFloatInt,
            is_by_target: bool = False,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            use_routes: List[dict] = None
    ) -> List[Action]:
        """
        Alias for match method in the case of a source amount.
        """
        return self.match(
            x=x,
            trade=self.amt_by_target,
            cmp=None,
            is_by_target=is_by_target,
            completed_trade=False,
            check_sufficient_liquidity=check_sufficient_liquidity,
            use_routes=use_routes
        )

    def match_by_target(
            self,
            x: DecFloatInt,
            is_by_target: bool = True,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            use_routes: List[dict] = None
    ) -> List[Action]:
        """
        Alias for match method in the case of a target amount.
        """
        return self.match(
            x=x,
            trade=self.amt_by_src,
            cmp=None,
            is_by_target=is_by_target,
            completed_trade=False,
            check_sufficient_liquidity=check_sufficient_liquidity,
            use_routes=use_routes
        )
