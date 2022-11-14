"""
Abstract base class for `exact` routers.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
from abc import ABC

from .base_router import *


@dataclass
class ExactBase(BaseRouter, ABC):
    """
    Abstract base class for both ExactRouterSBY and ExactRouterX0Y0N routers.
    """

    def dxdy(self, subject: int, dy: DecFloatInt) -> DecFloatInt:
        """
        Calculates delta-x (dx) contribution for y
        """
        x0 = self.orders[subject].x0
        y0 = self.orders[subject].y0
        n = self.orders[subject].n
        y = self.orders[subject].y
        self.logger.debug(
            f"y: {self.frmt(y)}, dy: {self.frmt(dy)}, y0: {self.frmt(y0)}, x0: {self.frmt(x0)}, n: {self.frmt(n)} \n"
        )
        return -x0 * y0 * dy / ((n * y + y0 * (1 - n)) * (n * (y + dy) + y0 * (1 - n)))

    @staticmethod
    def check_partial_swaps(partial_swaps):
        """
        Check whether trade routing is complete.
        """
        if partial_swaps:
            return all(swap <= 0 for swap in partial_swaps.values())
        else:
            return False

    def match_by_src(
        self,
        x: DecFloatInt,
        is_by_target: bool = False,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        Alias for match method in the case of a source amount.
        """
        return self.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity,
        )

    def match_by_target(
        self,
        x: DecFloatInt,
        is_by_target: bool = True,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        Alias for match method in the case of a target amount.
        """
        return self.match(
            x=x,
            is_by_target=is_by_target,
            check_sufficient_liquidity=check_sufficient_liquidity,
        )

    def match(
        self,
        x: DecFloatInt,
        is_by_target: bool = True,
        completed_trade: bool = False,
        trade: Callable = None,
        cmp: Callable = None,
        check_sufficient_liquidity: bool = True,
    ) -> List[Action]:
        """
        Main logic for the exact methods (both SBY and Y0X0N variable implementations).
        This method determines the ideal distribution of the input, and calculates the corresponding output.
        """
        if is_by_target:
            if check_sufficient_liquidity:
                self.sufficient_liquidity_exists(x)

        partial_swaps = final_swaps = {}
        dropped_indices = []
        while not completed_trade:

            dropped_indices = list(final_swaps.keys())

            if is_by_target:
                delta = sum([i for i in final_swaps.values()])
            else:
                delta = sum([self.dxdy(k, v) for k, v in final_swaps.items()])

            amt = x - delta

            self.logger.info(
                f"amt: {self.frmt(amt)}, delta: {self.frmt(delta)}, x: {x}, dropped_indices: {dropped_indices}, final_swaps: {[(k, self.frmt(v)) for k, v in final_swaps.items()]} \n"
            )

            self.logger.info(
                f"amt: {self.frmt(amt)}, delta: {self.frmt(delta)}, x: {x} \n"
            )

            partial_swaps = {}
            while not self.check_partial_swaps(partial_swaps):
                dropped_indices += [k for k, v in partial_swaps.items() if v > 0] + [
                    i for i in self.indexes if self.orders[i].y == 0
                ]
                position_subset = [i for i in self.indexes if i not in dropped_indices]
                if len(position_subset) == 0:
                    # this happens when there are no liquidity positions left
                    # this does not merit a forced warning
                    #print("[match] ----Warning: empty subset-----")
                    break
                partial_swaps.clear()
                for i in position_subset:
                    if is_by_target:
                        partial_swap_amount = self.amt_by_target(
                            i, amt, position_subset
                        )
                    else:
                        partial_swap_amount = self.amt_by_src(i, amt, position_subset)

                    self.logger.debug(
                        f"partial_swap_amount: {i}, {self.frmt(partial_swap_amount)} \n"
                    )

                    partial_swaps[i] = partial_swap_amount

            completed_trade = True
            for index, trade_target in partial_swaps.items():
                position_liquidity = self.orders[index].y
                test_liquidity = position_liquidity + trade_target < 0

                self.logger.debug(
                    f"index: {index}, test_liquidity: {test_liquidity}, position_liquidity: {self.frmt(position_liquidity)}, trade_target: {self.frmt(trade_target)}\n"
                )

                if test_liquidity:
                    final_swaps[index] = -position_liquidity
                    completed_trade = False

            self.logger.debug(
                f"final_swaps: {[(k, self.frmt(v)) for k, v in final_swaps.items()]} \n"
            )

        # Format Results
        final_swaps = {**final_swaps, **partial_swaps}
        outputs = {k: v for k, v in final_swaps.items() if v != 0}
        inputs = {k: self.dxdy(k, v) for k, v in outputs.items()}
        ttl_values = {}
        ttl_inputs = {}
        indices = [i for i in inputs.keys()]
        indexes = [i for i in range(len(indices))]
        for i in indexes:
            ttl = outputs[indices[i]]
            inpts = inputs[indices[i]]
            if i > 0:
                ttl_values[i] = ttl_values[i - 1] + ttl
                ttl_inputs[i] = ttl_inputs[i - 1] + inpts
            else:
                ttl_values[i] = ttl
                ttl_inputs[i] = inpts

## Assert that input matches output - i.e no partial trades
        if is_by_target:
            try:
                assert (
                    round(ttl_values[i], 12) == x
                ), "In and out don't match."
            except AssertionError as e:
                #self.logger.error(e)
                raise e
        else:
            try:
                assert (
                    round(ttl_inputs[i], 12) == x
                ), "In and out don't match."
            except AssertionError as e:
                #self.logger.error(e)
                raise e

## Assert that there is sufficient liquidity for by source
        if not is_by_target:
            try:
                assert (
                    round(ttl_inputs[i], 12) - x >= 0
                ), "Insufficient liquidity across all user positions to support this trade."
            except AssertionError as e:
                #self.logger.error(e)
                raise e

        # Package Results
        match_method = "by_src" if not is_by_target else "by_target"
        actions = [
            Action(
                match_method=match_method,
                index=indices[i],
                x=x,
                input=self.frmt(inputs[indices[i]]),
                output=self.frmt(outputs[indices[i]]),
                total_output=self.frmt(ttl_values[i]),
                total_input=self.frmt(ttl_inputs[i]),
            )
            for i in indexes
        ]
        return actions
