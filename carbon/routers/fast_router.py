"""Non-exact "fast" router class."""
from decimal import Decimal
from functools import cmp_to_key
from .base_router import *


@dataclass
class FastRouter(BaseRouter):
    """
    This router ranks individual orders by their potential to deliver the best price, and a resultant list of
    “matching objects” is distributed across various orders - sorted by best-to-worst price (and worst-to-best gas
    cost).

    Note: The result of this method is not guaranteed to be optimal, but is typically "close enough" to optimal
    when accounting for gas savings. Additionally, it is simpler and easier to comprehend.
    """

    filter_map = {
        False: {
            'input': 0,
            'output': 0
        },
        True: {
            'input': 0,
            'output': 0
        }
    }

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

    def get_trade_amounts_by_source_amount(
            self, source_amount: DecFloatInt, subject: int
    ) -> Rate:
        order = self.orders[subject]

        target_amount = self.amt_by_target(dx=source_amount, subject=subject)
        output = min(target_amount, order.y)
        _input = self.amt_by_src(dx=output, subject=subject)
        # self.logger.debug(
        #     f"get_trade_amounts_by_source_amount: {source_amount} -> {output} ({_input})"
        # )
        return Rate(_input, output)

    def get_trade_amounts_by_target_amount(
            self, target_amount: DecFloatInt, subject: int
    ) -> Rate:
        order = self.orders[subject]
        _input = min(target_amount, order.y)
        output = self.amt_by_src(dx=_input, subject=subject)
        # self.logger.debug(
        #     f"get_trade_amounts_by_target_amount: {target_amount} -> {_input} ({output})"
        # )
        return Rate(_input, output)

    @staticmethod
    def cmp_min(x: Quote, y: Quote) -> DecFloatInt:
        lhs = x.rate.output * y.rate.input
        rhs = y.rate.output * x.rate.input
        lt = lhs < rhs
        gt = lhs > rhs
        eq = not lt and not gt
        is_lt = lt or (eq and x.rate.output < y.rate.output)
        is_gt = gt or (eq and x.rate.output > y.rate.output)
        # self.logger.debug(f"cmp_min: {x} {y} -> {is_lt} {is_gt}")
        return is_lt - is_gt

    def cmp_max(self, x: Quote, y: Quote) -> DecFloatInt:
        # self.logger.debug(f"cmp_max: {x} {y}")
        return self.cmp_min(y, x)

    def _filter(self, rate: Rate, is_by_target: bool) -> bool:
        filter_input = self.filter_map[is_by_target]['input']
        filter_output = self.filter_map[is_by_target]['output']
        return rate.input > filter_input and rate.output > filter_output

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
        * Compute a list of {order index, trade amount} tuples:
        * - Let 'n' denote the initial input amount
        * - Iterate the orders from the highest rate to the lowest rate:
        *   - Let 'm' denote the maximum tradable amount not larger than 'n'
        *   - Add the index of the order along with 'm' to the output matching
        *   - If 'm < n' then subtract 'm' from 'n' and continue, otherwise break
        *
        * Sorting the orders from the highest rate to the lowest rate:
        * - Computing the rate of an order:
        *   - Let 'x' denote the maximum tradable amount not larger than 'n'
        *   - Let 'y' denote the output amount of trading 'x'
        *   - The rate is determined as 'y / x'
        * - Comparing the rates of two orders:
        *   - If the rates are different, then the higher one wins
        *   - If the rates are identical, then the one with a higher value of 'y' wins
        """
        use_positions_matchlevel = []
        # if check_sufficient_liquidity:
        #     self.sufficient_liquidity_exists(x, use_positions_matchlevel)

        actions = []
        x = abs(x)
        for quote in sorted(
                [Quote(n, trade(x, n)) for n in self.indexes], key=cmp_to_key(cmp)
        ):
            if x > quote.rate.input:
                if self._filter(quote.rate, is_by_target):
                    actions.append(
                        Action(
                            index=quote.index,
                            input=quote.rate.input,
                            output=quote.rate.output,
                        )
                    )
                    x -= quote.rate.input
            elif x == quote.rate.input:
                if self._filter(quote.rate, is_by_target):
                    actions.append(
                        Action(
                            index=quote.index,
                            input=quote.rate.input,
                            output=quote.rate.output,
                        )
                    )
                    break
            else:
                if self._filter(quote.rate, is_by_target):
                    actions.append(
                        Action(
                            index=quote.index, input=x, output=trade(x, quote.index).output
                        )
                    )
                    break

        # Format the output
        match_method = "by_src" if not is_by_target else "by_target"
        actions[0].total_output = actions[0].output
        actions[0].total_input = actions[0].input
        for i in range(1, len(actions)):
            actions[i].match_method = match_method
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
            support_partial: bool = False,

    ) -> List[Action]:
        return self.match(
            x=x,
            trade=self.get_trade_amounts_by_source_amount,
            cmp=self.cmp_min,
            is_by_target=is_by_target,
            completed_trade=False,
            check_sufficient_liquidity=check_sufficient_liquidity,
        )

    def match_by_target(
            self,
            x: DecFloatInt,
            is_by_target: bool = True,
            check_sufficient_liquidity: bool = True,
            threshold_orders: int = None,
            support_partial: bool = False,
    ) -> List[Action]:
        return self.match(
            x=x,
            trade=self.get_trade_amounts_by_target_amount,
            cmp=self.cmp_max,
            is_by_target=is_by_target,
            completed_trade=False,
            check_sufficient_liquidity=check_sufficient_liquidity,
        )

    def __post_init__(self):
        if not self.use_floor_division:
            self.ONE = Decimal("1")
            self.MIN = Decimal("0")
            self.MAX = Decimal(str(2 ** 128 - 1))
