"""
Base class for all routers.

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
import decimal
import json
import math
from decimal import Decimal
from abc import abstractmethod
from typing import List, Tuple, Callable
from dataclasses import field, dataclass

from ..order import Order, DecFloatInt
import logging


@dataclass
class Rate:
    """
    Represents a rate between two tokens for the FastRouter.
    """

    input: DecFloatInt = 0
    output: DecFloatInt = 0


@dataclass
class Quote:
    """
    Represents a quoted Rate in the FastRouter.
    """

    index: int = 0
    rate: Rate = Rate()


@dataclass
class Action:
    """
    Represents an action response from the FastRouter.
    """

    index: int = 0
    x: DecFloatInt = 0
    input: DecFloatInt = 0
    output: DecFloatInt = 0
    price: DecFloatInt = 0
    total_output: DecFloatInt = 0
    total_input: DecFloatInt = 0
    total_price: DecFloatInt = 0
    match_method: str = ""
    threshold_orders: int = 100
    support_partial: bool = False


@dataclass
class BaseRouter:
    """
    Base class for both Simple and Complex routers.
    """

    # A list of all curves for a given token pair.
    orders: List[Order] = field(default_factory=list)

    # Allows for toggling between floor division vs regular division
    use_floor_division: bool = False

    # Verbosity mode for logging.
    verbose: bool = False

    # Extra verbose logging mode.
    debug: bool = False

    # if False (default), errors are caught and returned in the result dict
    raiseonerror: bool = False

    assert_precision: int = 4

    @property
    def indexes(self) -> list:
        """
        Alias for position_list (used for shorthand and docs consistency).
        """
        return list(range(len(self.orders)))

    @staticmethod
    def frmt(val: DecFloatInt, num_decimals=12) -> float:
        """
        Values based on linear modelling of Barak gas estimates 20221003
        """
        return round(float(val), num_decimals)

    @staticmethod
    def prod(lst: List[DecFloatInt]) -> DecFloatInt:
        """
        Multiplies all elements in a given list in such a way that supports returning a Decimal data type.
        """
        return math.prod(lst)

    def sufficient_liquidity_exists(self, x: DecFloatInt, use_positions_matchlevel, support_partial) -> bool:
        """
        Method to check if there is sufficient liquidity to handle the trade.
        """
        if len(use_positions_matchlevel) == 0:
            use_positions_matchlevel = self.indexes
        available_liquidity = sum([self.orders[i].y for i in use_positions_matchlevel])
        try:
            assert (
                available_liquidity - abs(x) >= 0
            ), "Insufficient liquidity across all user positions to support this trade."
            return True
        except AssertionError as e:
            if support_partial:
                # print("Assuming partial fulfillment.")
                # print(f'Setting trade amount to max: {available_liquidity}')
                return available_liquidity
            else:
                raise e


    @abstractmethod
    def amt_by_target(
        self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        Enforced method to handle getting the input amount for a given target amount.
        """
        pass

    @abstractmethod
    def amt_by_src(
        self, subject: int, dx: DecFloatInt, position_subset: List[int] = None
    ) -> DecFloatInt:
        """
        Enforced method to handle getting the target amount for a given source amount.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def match_by_src(
        self,
        x: DecFloatInt,
        is_by_target: bool = False,
        check_sufficient_liquidity: bool = True,
        threshold_orders: int = None,
    ) -> List[Action]:
        """
        Alias for match method in the case of a source amount.
        """
        pass

    @abstractmethod
    def match_by_target(
        self,
        x: DecFloatInt,
        is_by_target: bool = True,
        check_sufficient_liquidity: bool = True,
        threshold_orders: int = None,
    ) -> List[Action]:
        """
        Alias for match method in the case of a target amount.
        """
        pass

    @staticmethod
    def from_json(json_file_path: str) -> dict:
        """
        Method to load a json file.
        """
        with open(json_file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def from_csv(csv_file_path: str) -> dict:
        """
        Method to load a json file.
        """
        import pandas as pd

        return pd.read_csv(csv_file_path)

    def make_orders_from_file(
        self,
        file_path: str,
        format_type: str = "nix",
        num_curves: int = None,
        file_type: str = "json",
    ) -> Tuple[List[Order], dict] or List[Order]:
        """
        Method to make curves from a json file.
        """
        if num_curves is None:
            num_curves = 10

        curves = []
        nix_format = {}
        ct = 0
        if file_type == "json":
            curve_data = BaseRouter.from_json(file_path)
            for curve in curve_data:
                if type(curve) is not dict:
                    curve = curve_data[curve]
                try:
                    curve = {
                        k: Decimal(v)
                        for k, v in curve.items()
                        if k in ["S", "B", "_y", "y_int"]
                    }
                except decimal.InvalidOperation as e:
                    self.logger.error("decimal.InvalidOperation: ", type(curve), curve)
                    raise e
                c = Order(**curve)
                if self.use_floor_division:
                    p_high = int(float(Decimal(c.p_high).sqrt())) * 2**32
                    p_low = int(float(Decimal(c.p_low).sqrt())) * 2**32
                    y_int = c.y_int
                    y = c.y
                    c = Order(
                        p_low=c.p_low,
                        p_high=c.p_high,
                        S=p_high - p_low,
                        B=p_low,
                        y_int=y_int,
                        _y=y,
                        auto_convert_variables=False,
                    )
                curves.append(c)
                nix_format[ct] = {
                    "token_1": "usdc",
                    "token_2": "eth",
                    "token_1_p_a": c.p_high,
                    "token_1_p_b": c.p_low,
                    "token_1_y_int": c.y_int,
                    "token_2_p_a": c.p_high,
                    "token_2_p_b": c.p_low,
                    "token_2_y_int": c.y_int,
                }
                ct += 1
                if len(curves) == num_curves and num_curves is not None:
                    break
            if num_curves > len(curves):
                self.logger.warning(
                    f"num_cruves={num_curves} is greater than the number of curves found in the json_file_path..."
                    "using all curves found in the json_file_path."
                )
        elif file_type == "csv":
            curve_data = BaseRouter.from_csv(file_path)

            def unpack_row(indx):
                row = curve_data.iloc[indx]
                return {
                    "p_low": Decimal(float(row["p_low"])),
                    "p_high": Decimal(float(row["p_high"])),
                    "y_int": Decimal(float(row["y_int"])),
                }

            curve_data["index"] = [i for i in range(len(curve_data))]
            for i in curve_data["index"].values:
                curve = unpack_row(i)
                c = Order(**curve)
                curves.append(c)
            nix_format = {}
        if format_type == "nix":
            return curves, nix_format
        else:
            return curves

    def __post_init__(self):
        self.logger = logging
        if self.verbose:
            self.logger.basicConfig(level=logging.INFO)
        else:
            self.logger.basicConfig(level=logging.WARNING)
