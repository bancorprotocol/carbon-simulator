"""
represents a Carbon order book position

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
__version__ = "1.0"
__date__ = "8/Dec/2022"

import pprint
from dataclasses import dataclass
from decimal import Decimal
from decimal import getcontext
from math import sqrt
from typing import NewType

from .pair import CarbonPair


getcontext().prec = 128

pp = pprint.PrettyPrinter(indent=4)

DecFloatInt = NewType("value", int or Decimal or float)


@dataclass
class Order:
    """
    Curve class to represent a curve on the market maker's order book
    """

    __VERSION__ = __version__
    __DATE__    = __date__

    # Production variables
    B: DecFloatInt = None       # = sqrt(price_low)
    S: DecFloatInt = None       # = sqrt(price_high) - sqrt(price_low)
    y_int: DecFloatInt = None   # the initial intercept of the curve

    # Original variables
    p_high: DecFloatInt = None  # = high price, also p_a, p_start
    p_low: DecFloatInt = None   # = low price, also p_b, p_low
    p_marginal: DecFloatInt = None  # = marginal price, also p_c, p_mid
    disabled: bool = False      # if True, prices used to be None
    _y: DecFloatInt = None      # the current balance of the curve

    # Alternate variables
    D: DecFloatInt = None       # the current intercept of the curve
    _C: DecFloatInt = None      # the current balance of the curve

    pair: CarbonPair = None
    tkn: str = None
    pair_name: str = None
    adj_n_mode: bool = False
    auto_convert_variables: bool = True
    id: int = 0
    linked_to_id: int = 0
    _reverseq: bool = False
    verbose: bool = False

    @property
    def y(self) -> Decimal:
        """
        The current balance of the curve... Equal to y_int upon genesis.
        """
        return self.y_int if self._y is None else self._y

    @y.setter
    def y(self, value: Decimal) -> None:
        """
        Setter for the current balance of the curve...
        """
        self._y = value

    @property
    def C(self) -> Decimal:
        """
        The current balance of the curve... Equal to D upon genesis.
        """
        return self.D if self._C == 0 else self._C

    @C.setter
    def C(self, value: Decimal) -> None:
        """
        Setter for the current balance of the curve...
        """
        self._C = value

    @property
    def p(self) -> Decimal:
        p_high: Decimal = self.p_high
        p_low: Decimal = self.p_low
        return (p_high * p_low).sqrt()

    @property
    def x0(self) -> Decimal:
        n: Decimal = self.n
        p: Decimal = self.p
        y_int: Decimal = max(self.y_int, Decimal("1"))
        return (y_int * (1 - n)) / (p * (2 - n))

    @property
    def k(self) -> Decimal:
        x0 = self.x0
        y0 = self.y0
        return x0 * y0

    @property
    def a(self):
        return self.k * (self.n - 1) - self.n * self.x0 * self.y

    @property
    def x(self) -> Decimal:
        x0: Decimal = self.x0
        n: Decimal = self.n
        y: Decimal = self.y
        y0: Decimal = self.y0
        return x0 * (n * y - y + y0 * (2 - n)) / (n * y + y0 * (1 - n))

    @property
    def y0(self) -> Decimal:
        y_int: Decimal = max(self.y_int, Decimal("1"))
        n: Decimal = self.n
        return (y_int * (1 - n)) / (2 - n)

    @property
    def n(self) -> Decimal:
        p_high: Decimal = self.p_high
        p_low: Decimal = self.p_low
        return (
            1 - (p_low / p_high) ** Decimal(".25")
            if not self.adj_n_mode
            else Decimal("0.000000000000000001")
        )

    @property
    def reverseq(self):
        return self._reverseq

    @reverseq.setter
    def reverseq(self, value):
        self._reverseq = value

    # Use the dataclass post-init method to initialize all variable sets
    def __post_init__(self):

        if self.p_high is not None and self.p_low is not None:
            self.p_high = Decimal(self.p_high)
            self.p_low = Decimal(self.p_low)

        if self.y_int is not None:
            self.y_int = Decimal(self.y_int)

        if self.p_marginal is not None:
            self.p_marginal = Decimal(self.p_marginal)

        if self.auto_convert_variables:

            # Init original variables if alternate variables are set
            if self.B is not None and self.S is not None:
                self.B = Decimal(self.B)
                self.S = Decimal(self.S)
                self.pb_raw = self.B * self.B
                self.pa_raw = (self.S + self.B) ** 2
                self.pa = 1 / self.pa_raw if self.reverseq else self.pa_raw
                self.pb = 1 / self.pb_raw if self.reverseq else self.pb_raw
                if self.pa < self.pb:
                    self.p_low = self.pa
                    self.p_high = self.pb
                else:
                    self.p_low = self.pb
                    self.p_high = self.pa

            # Init alternate variables if original variables are set
            elif self.p_low is not None and self.p_high is not None:

                if self.p_high < self.p_low:
                    paa = self.p_high
                    self.p_high = self.p_low
                    self.p_low = paa

                self.B = sqrt(self.p_low)
                self.S = sqrt(self.p_high) - sqrt(self.p_low)

            if self.y_int is not None:
                self.D = self.C = self._y = self.y_int

            elif self.y_int is None and self.p_marginal is not None:
                if type(self.p_marginal) is Decimal:
                    self.y_int = self._y * (self.p_high.sqrt() - self.p_low.sqrt()) / (self.p_marginal.sqrt() - self.p_low.sqrt())
                else:
                    self.y_int = float(self._y) * (sqrt(self.p_high) - sqrt(self.p_low)) / (sqrt(self.p_marginal) - sqrt(self.p_low))

            elif self.D is not None:
                self.y_int = self.C = self._y = self.D

            if self.p_high == self.p_low:
                self.adj_n_mode = True


