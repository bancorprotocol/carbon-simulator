"""
represents a single, unidirectional carbon order and provides convenience methods for UI access

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT
"""
__version__ = "1.2"
__date__ = "8/Dec/2022"

try:
    from .pair import CarbonPair
except:
    from pair import CarbonPair

from dataclasses import dataclass
from math import sqrt

@dataclass
class CarbonOrderUI:
    """
    current state of a single Carbon order, for UI purposes
    
    properties that are parameters of the constructor
    :pair:    the corresponding token pair (specifically, its CarbonPair record)
    :tkn:     the token that this position is selling
    :B:       the B-parameter; B = sqrt pb_raw
    :S:       the S-parameter; S = sqrt pa_raw - Sqrt pb_raw
    :yint:    the y-intercept of the curve (also its current maximum capacity)
    :y:       the current y-coordinate on the curve (also current token holdings)
    other properties
    :pa_raw:   the pa parameter in native quotation (dy/dx)
    :pb_raw:   ditto pb
    :pa:       the pa paramter in the quotation appropriate for the pair
    :pb:       ditto pb
    :pmin:     the min of pa, pb (in the quotation appropriate for the pair)
    :pmax:     the max of pa, pb (in the quotation appropriate for the pair)
    
    NOTES
    - natively, prices are quoted in the convention dy/dx, where tkn is the quote asset;
    tkn is also the asset being sold, so the numeraire is always the asset being sold
    - pa, pb are read at the intercepts "left to right", so pa=py is is the y intercept price,
    and pb=px is the x intercept price 
    - the properties pa_raw and pb_raw correspond to the native pa, pb; the prperties pa, pb
    are quoted in the correct currency conventions
    - the properties py = pa and px = pb are aliases
    """
    __VERSION__ = __version__
    __DATE__    = __date__
    
    pair: CarbonPair
    tkn: str
    B: float
    S: float
    yint: float
    y: float
    def __post_init__(self):
        self.tkn = self.tkn.upper()
        if not self.pair.has_token(self.tkn):
            raise RuntimeError("token not part of pair", self.tkn, self.pair)
        self.pb_raw = self.B * self.B
        self.pa_raw = (self.S + self.B)**2
        if self.pa_raw == 0 and self.pb_raw == 0:
            self.pa_raw = None
            self.pa_raw = None
            self.disabled = True
        else:
            self.disabled = False
        self.reverseq = True if self.pair.has_basetoken(self.tkn) else False

        if not self.disabled:
            self.pa = 1./self.pa_raw if self.reverseq else self.pa_raw
            self.pb = 1./self.pb_raw if self.reverseq else self.pb_raw
            if self.pa < self.pb:
                self.pmin = self.pa
                self.pmax = self.pb
            else:
                self.pmin = self.pb
                self.pmax = self.pa  
        else:
            self.pmin = None
            self.pmax = None        
    
    @classmethod
    def from_BSy(cls, pair, tkn, B, S, yint, y):
        """
        alternative* constructor, taking B,S,y

        :pair:    the corresponding token pair (specifically, its CarbonPair record)
        :tkn:     the token that this order is selling
        :B:       the B-parameter; B = sqrt pb_raw
        :S:       the S-parameter; S = sqrt pa_raw - Sqrt pb_raw
        :yint:    the y-intercept of the curve (also its current maximum capacity)
        :y:       the current y-coordinate on the curve (also current token holdings)

        *technically this is the same as the constructor, but use of `from_BSy` is recommended
        over use of the native class constructor in case of future implementation changes
        """
        return cls(
            pair=pair, 
            tkn=tkn, 
            B=B, 
            S= S, 
            yint=yint, 
            y=y
        )

    @classmethod
    def from_prices(cls, pair, tkn, pa, pb, yint, y):
        """
        alternative constructor, taking prices pa, pb
        
        :pair:    the corresponding token pair (specifically, its CarbonPair record)
        :tkn:     the token that this order is selling
        :pa:      the price at the y intercept, in quotation corresponding to the pair*
        :pb:      the price at the x intercept, in quotation corresponding to the pair*
        :yint:    the y-intercept of the curve (also its current maximum capacity)
        :y:       the current y-coordinate on the curve (also current token holdings)
        
        *in their native quotation, pa, pb = -dy/dx at the y-intercept and x-intercept
        respectively; as the function y(x) is convex we must have pa >= pb; as this can
        be confusing in reverse quotation we correct by exchanging pa, pb if pb < pa
        """
        if pair.has_basetoken(tkn):
            pa = 1./pa
            pb = 1./pb
        
        if pa < pb:
            print("[from_prices] exchanging pa, pb")
            paa = pa
            pa = pb
            pb = paa
            
        B = sqrt(pb)
        S = sqrt(pa) - sqrt(pb)
        return cls(
            pair=pair, 
            tkn=tkn, 
            B=B, 
            S= S, 
            yint=yint, 
            y=y
        )
    
    @classmethod
    def from_order(cls, order):
        """
        alternative constructor, from an Order object

        :order:     the order object
        """
        return cls(
            pair=order.pair, 
            tkn=order.tkn, 
            B=float(order.B), 
            S= float(order.S), 
            yint=float(order.y_int), 
            y=float(order.y)
        )

    @property
    def p0(self):
        """
        the average or effective price of the range, p0 = sqrt(pa, pb)
        """
        return sqrt(self.pa*self.pb)
    
    @property
    def px(self):
        """alias for pb"""
        return self.pb 
    
    @property
    def py(self):
        """alias for pa"""
        return self.pa  
    
    @property
    def widthr(self):
        """the width ratio of the range, widthr = pmax/pmin"""
        return self.pmax/self.pmin
    
    @property
    def widthpc(self):
        """the percentage width of the range, widthpc = (pmax-pmin)/p0"""
        return (self.pmax-self.pmin)/self.p0

    @property
    def price_convention(self):
        """
        the price convention of the prices quoted
        
        :raw:   if False (default) return convention for all prices except 
                pa_raw and pb_raw which is returned for raw=True
        """
        if raw:
            return self.pair.price_convention(self.reverseq)
        return self.pair.price_convention()

    def descr(self, full=False):
        """provides a description of the order and curve"""
        s1 = f"Sell {self.tkn} buy {self.pair.other(self.tkn)}"
        s2 = f"from {self.pa:.4f} to {self.pb:.4f} {self.price_convention()}"
        s2 = f"from {self.pa:.4f} to {self.pb:.4f} {self.price_convention}"
        if full:
            s3 = f" ({self.y} {self.tkn} on curve, {self.y/self.yint*100:.0f}% of capacity)"
        else:
            s3 = ""
        return f"{s1} {s2}{s3}"

    @property
    def p_marg(self):
        """
        the current marginal price of the range
        """
        #dydx = ((self.B * self.yint + self.S * self.y) / self.yint)**2
        if self.disabled:
            return None

        if self.yint == 0:
            if not self.y == 0:
                raise ValueError("If yint=0 you must also have y=0", yint, y)
            dydx = ((self.B + self.S))**2
        else:
            dydx = ((self.B + self.S * self.y/self.yint))**2
        result = dydx if self.pair.has_quotetoken(self.tkn) else 1/dydx
        return result
    
    @property
    def total_liquidity(self):
        """
        returns the total liquidity of the position, and the token in which it is quoted

        :returns:       (liquidity, token)
        """
        return self.y, self.tkn
    
    def liquidity_approx(self, price1, price2, tkn=None, asperc=False):
        """
        returns the approximate liquidity between start and end, in tkn

        :price1/2:      the start and end price of the range (in any order; quoted in price convention of pair)
        :tkn:           the token in which the liquidity is quoted (if None: base token)
        :asperc:        if True, return percentage total liquidity rather than tkn number; default is False
        :returns:       the liquidity in [price1, price2], quoted in tkn (or percent)
        """

        # ensure that price1 <= price2
        if price1 > price2:
            pp = price2
            price2 = price1
            price1 = pp

        if tkn is None:
            tkn = self.pair.basetoken
            #print(f"[liquidity_approx] token set to {tkn}")
            
        # # now we need to go through all the different arrangements of the range
        # # we first compute the percentage coverage, which simply is the percentage
            
        # # price1>pmax -> completely above the range
        # if price1 > self.pmax:
        #     perc = 0.
        
        # # price2<pmin -> completely below the range
        # elif price2 < self.pmin:
        #     perc = 0.

        # # price1 <= pmin
        # elif price1 <= self.pmin:

        #     # price1 <= min and price2 >= max -> 100%
        #     if price2 >= self.pmax:
        #         perc = 1.
        #     else:
        #         perc = (price2 - self.pmin)/(self.pmax - self.pmin)

        # # price2 >= pmax and price1>pmin
        # elif price2 >= self.pmax:

        #     perc = (self.pmax - price1)/(self.pmax - self.pmin)

        # # price2 < pmax and price1 > pmin
        # else:

        #     perc = (price2 - price1)/(self.pmax - self.pmin)

        # self.pmax == self.pmin -> 100% in range, otherwise out
        if self.pmax == self.pmin:
            if price1 == price2:
                perc2 = 1. if price1 == self.pmax else 0
            else:
                perc2 = 1. if price1 <= self.pmax and price2 > self.pmax else 0
            price = self.pmax
            #print(f"perc2={perc2}, price={price}", price1, price2, self.pmin, price1==self.pmax, price2==self.pmax)
        
        # price1 > self.pmax or price2 < self.pmin -> completely above or below the range
        elif price1 >= self.pmax or price2 <= self.pmin:
            perc2 = 0
        
        # alternatively: restrict p1,p2 to the ranges and calculate the coverage
        else:
            if price1 < self.pmin: price1 = self.pmin
            if price2 > self.pmax: price2 = self.pmax
            perc2 = (price2 - price1)/(self.pmax - self.pmin)
            price = sqrt(price1*price2)
        
        if asperc:
            return perc2
        
        if perc2 == 0:
            return 0

        # liquidity
        liq0 = self.y
        liq0_tkn = self.tkn

        # convert price into the correct quantity
        liq = self.pair.convert(amtfrom=liq0, tknfrom=liq0_tkn, tknto=tkn, price=price)
        
        return liq*perc2
        