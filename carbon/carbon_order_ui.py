"""
represents a single, unidirectional carbon order and provides convenience methods for UI access

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT

VERSION HISTORY
- v1.3: order book helper functions (p_marg_f, yfromp_f, dyfromp_f, dyfromdx_f, dyfromdx_f, goalseek)
- v1.4: new methods: fromQxy, Q, Gamma, sellx, selly; yfromx_f, xfromy_f, p_eff_f, xint (1.3.1)
- v1.5: linked curves (beta); bidask, curves_by_pair_bidask, checks for B,S=0 (1.4.1)
- v1.6: linked curves incl trading (final), addliqy, tradeto; minor formula improvement (1.5.1)
"""
__version__ = "1.6"
__date__ = "20/Jan/2023"

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
    :id:      id of this curve*
    :linked:  the linked curve object*

    *Beta; interace may still change in respect to ix, lix and linked as well 
    as the associated functions
    
    other properties set by the constructor
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
    id: any = None
    linked: any = None

    def __post_init__(self):
        self.pair = CarbonPair(self.pair)
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
    
    def set_id(self, id):
        """sets curve index; raises if curve ID already set"""
        if not self.id is None:
            raise ValueError("Curve ID has already been set", id, self.id)
        self.id = id
    
    @property
    def lid(self):
        """returns ID of linked curve, or None"""
        if self.linked is None:
            return None
        return self.linked.id
        
    def set_linked(self, linked=None):
        """
        sets linked object and index

        :linked:    the linked curve (CarbonOrderUI object)
        """
        if not self.linked is None:
            raise ValueError("Linked object has already been set", linked.id, self.linked.id)
        self.linked = linked

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
        alternative constructor, taking prices pa, pb and curve capacity yint
        
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
        pair = CarbonPair(pair)
        if yint<0:
            raise ValueError("yint must be non-negative", yint)
        if y>yint:
            raise ValueError("y must not be bigger than yint (y={y}, yint={yint})", yint, y)
        if y<0:
            raise ValueError("y must be non-negative", y)

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
            S=S, 
            yint=yint, 
            y=y
        )
    
    @classmethod
    def from_Qxy(cls, pair, tkn, Q, xint, yint, y):
        """
        alternative constructor, taking convexity Q and curve capacities xint, yint
        """
        pair = CarbonPair(pair)
        if not pair.has_token(tkn):
            raise ValueError("token not part of the pair", tkn, pair)
        if xint<=0:
            raise ValueError("xint must be positive", xint)
        if yint<=0:
            raise ValueError("yint must be positive", yint)
        if y>yint:
            raise ValueError("y must not be bigger than yint (y={y}, yint={yint})", yint, y)
        if y<0:
            raise ValueError("y must be non-negative", y)

        p0 = yint/xint
        B = sqrt(p0*Q)
        S = sqrt(p0/Q) - B

        return cls(
            pair=pair, 
            tkn=tkn, 
            B=B, 
            S=S, 
            yint=yint, 
            y=y
        )

    @classmethod
    def from_order(cls, order):
        """
        alternative constructor, from an Order object

        :order:     the Order or CarbonOrderUI object
        """
        try: 
            yint = order.y_int
        except:
            yint = order.yint

        return cls(
            pair=order.pair, 
            tkn=order.tkn, 
            B=float(order.B), 
            S= float(order.S), 
            yint=float(yint), 
            y=float(order.y),
            id=order.id,
        )

    @property 
    def tkny(self):
        """the token on the y-axis (alias for tkn)"""
        return self.tkn
    
    @property 
    def tknx(self):
        """the token on the x-axis"""
        return self.pair.other(self.tkn)

    @property
    def bidask(self):
        """returns BID or ASK depending on what type curve it is"""
        if self.tkny == self.pair.basetoken:
            return "BID"
        else:
            return "ASK"
    
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
    p_end = px

    @property
    def py(self):
        """alias for pa"""
        return self.pa
    p_start = py
    
    @property
    def Q(self):
        """Q parameter = sqrt(Px/Py) < 1"""
        return sqrt(self.pb_raw/self.pa_raw)

    @property
    def Gamma(self):
        """Gamma parameter (also known as n) = 1 - sqrt(Q)"""
        return 1 - sqrt(self.Q)

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
        the current marginal price of the range (alias for p_margf)
        """
        return self.p_marg_f(0)


    def p_marg_f(self, dy=0, fullcurve=False, checkbounds=True, raiseonerror=False):
        """
        the marginal price function of the range

        :dy:            the negative(!) change in liquidity value, expressed as 
                        positive number; y* = y - dy
        :fullcurve:     if True, ignore curve state y and use yint, ie y* = yint - dy
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises on all errors; otherwise (default) may return None
        :returns:       marginal price a y*, p(y*) in the price convention of the pair
        """
        #dydx = ((self.B * self.yint + self.S * self.y) / self.yint)**2
        if self.disabled:
            return None

        y = self.yint - dy if fullcurve else self.y - dy
        #print(f"[p_marg_f] dy={dy} y={y} s.y={self.y} s.yint={self.yint}", fullcurve)
        if checkbounds:
            if dy < 0:
                if raiseonerror:
                    raise ValueError("Trade size dy must be a non-negative number", dy)
                return None
            if y < 0:
                if raiseonerror:
                    raise ValueError("Trade size dy too big, results in y<0", dy, y, self.y)
                return None
        
        if self.yint == 0:
            if not self.y == 0 and dy == 0:
                raise ValueError("If yint=0 you must also have y,dy=0", yint, y, dy)
            dydx = ((self.B + self.S))**2
        else:
            dydx = ((self.B + self.S * y/self.yint))**2
        result = dydx if self.pair.has_quotetoken(self.tkn) else 1/dydx
        return result
    
    def p_eff_f(self, dy=0, fullcurve=False, checkbounds=True, raiseonerror=False):
        """
        the effective price function of the range

        :dy:            the negative(!) change in liquidity value, expressed as 
                        positive number; y* = y - dy
        :fullcurve:     if True, ignore curve state y and use yint, ie y* = yint - dy
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises on all errors; otherwise (default) may return None
        :returns:       effective price between y (or yint) and y* in the price convention of the pair
       """
        #dydx = ((self.B * self.yint + self.S * self.y) / self.yint)**2
        if self.disabled:
            return None

        y0 = self.yint if fullcurve else self.y
        y = y0 - dy
        if checkbounds:
            if dy < 0:
                if raiseonerror:
                    raise ValueError("Trade size dy must be a non-negative number", dy)
                return None
            if y < 0:
                if raiseonerror:
                    raise ValueError("Trade size dy too big, results in y<0", dy, y, self.y)
                return None

        if self.yint == 0:
            if not y0 == 0 and dy == 0:
                raise ValueError("If yint=0 you must also have y,dy=0", yint, y, dy)
            dydx = ((self.B + self.S))**2
        else:
            if dy==0:
                return self.p_marg_f(self.yint-y, checkbounds=False, fullcurve=True)
            dydx = dy / (self.xfromy_f(y) - self.xfromy_f(y0))
        
        result = dydx if self.pair.has_quotetoken(self.tkn) else 1/dydx
        return result
    
    class PriceOutOfBoundsError(ValueError): pass
    class PriceOutOfBoundsErrorBeyondStart(PriceOutOfBoundsError): pass
    class PriceOutOfBoundsErrorBeyondEnd(PriceOutOfBoundsError): pass
    class PriceOutOfBoundsErrorBeyondMarg(PriceOutOfBoundsError): pass

    def yfromp_f(self, p, checkbounds=True, raiseonerror=False):
        """
        returns y as a function of the target marginal price

        :p:             the target marginal price, in the price convention of the pair
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the y value at which the marginal price is achieved
                        if beyond the end it returns 0, if beyond start or current y None
        """
        # dydx = ((B * yint + S * y) / yint)**2 = (B + S y/yint)**2
        # y = yint * (sqrt(dydx) - B) / S
        dydx = p if self.pair.has_quotetoken(self.tkn) else 1/p
        #print(f"[yfromp_f] pa={self.pa_raw} dydx={dydx} pb={self.pb_raw}")

        if checkbounds:
            if dydx > self.pa_raw:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondStart("Price out of bounds (beyond start)", p, self.pa)
                return None
            elif dydx < self.pb_raw:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondEnd("Price out of bounds (beyond end)", p, self.pb)
                return 0
        y = self.yint * (sqrt(dydx) - self.B) / self.S
        if checkbounds:
            if y > self.y:
                if raiseonerror:
                    raise self.PriceOutOfBoundsErrorBeyondMarg("Price out of bounds (beyond marginal), hence target y > y", y, self.y )
                return None
        return y

    @property
    def xint(self):
        """
        x intercept, ie max x liquidity, ie x at y=0
        """
        #return self.yint**2 / (self.B**2*self.yint + self.B*self.S*self.yint)
        return self.yint / (self.B**2 + self.B*self.S)
        
    def dyfromp_f(self, p, checkbounds=True, raiseonerror=False):
        """
        returns dy = y_target - y as a function of the target marginal price

        :p:             the target marginal price, in the price convention of the pair
        :checkbounds:   if True (default), check that y is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the (positive!) dy value at which the marginal price is achieved
                        in cases where yfromp_f returns none, this func returns 0
        """
        if self.B == 0 and self.S == 0:
            if raiseonerror:
                raise ValueError("Can't determine trade prices from an empty curve", self.B, self.S)
            return 0
        y = self.yfromp_f(p, checkbounds, raiseonerror)
        if y is None: return 0
        return self.y-y

    def dyfromdx_f(self, dx, checkbounds=True, raiseonerror=False):
        """
        calculates the amount dy SOLD by the AMM to RECEIVE an amount dx

        :dx:            the amount of x the AMM RECEIVES (a POSITIVE number*)
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the amount dy of y the AMM SELLS (a POSITIVE number*)

        *when checkbounds is False then we can have dx<0, corresponding to the 
        AMM SELLing x. In this case it returns a negative number, corresponding
        to the AMM BUYing y.
        """
        if self.B == 0 and self.S == 0:
            if raiseonerror:
                raise ValueError("Can't trade on an empty curve", self.B, self.S)
            return 0

        if checkbounds:
            if dx < 0:
                if raiseonerror:
                    raise ValueError("AMM buy amount dx must be a non-negative number", dx)
                return None
            # elif dx > self.y:
            #     if raiseonerror:
            #         raise ValueError("AMM sell amount dx must be within available liquidity", dx, self.y)
            #     return None
        
        num   =               (self.S*self.y + self.B*self.yint)**2
        #         -------------------------------------------------------------
        denom =   self.S*dx * (self.S*self.y + self.B*self.yint) + self.yint**2

        if checkbounds:
            if num < 0:
                if raiseonerror:
                    raise ValueError("AMM does not have enough y liquidity to purchase dx", y, dx, num)
                return None

        return dx * (num/denom) 


    def dxfromdy_f(self, dy, checkbounds=True, raiseonerror=False):
        """
        calculates the amount dx RECEIVED for a trade of dy

        :dy:            the amount of y the AMM sells (a POSITIVE number*)
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the amount of x the AMM receives (a POSITIVE number*)

        *when checkbounds is False then we can have dy<0, corresponding to the 
        AMM BUYing y. In this case it returns a negative number, corresponding
        to the AMM SELLing x.
        """
        if self.B == 0 and self.S == 0:
            if raiseonerror:
                raise ValueError("Can't trade on an empty curve", self.B, self.S)
            return 0

        if checkbounds:
            if dy < 0:
                if raiseonerror:
                    raise ValueError("AMM sell amount dy must be a non-negative number", dy)
                return None
            elif dy > self.y:
                if raiseonerror:
                    raise ValueError("AMM sell amount dy must be within available liquidity", dy, self.y)
                return None
        
        num   =                                   self.yint**2
        #       ----------------------------------------------------------------------------------
        denom = (self.S*self.y+self.B*self.yint) * (self.S*self.y+self.B*self.yint-self.S*dy)

        return dy*(num/denom)     
    
    def xfromy_f(self, y, checkbounds=True, raiseonerror=False):
        """
        the invariant function, expressed as x=f(y)

        :y:             the amount of y the AMM currently holds
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the corresponding x amount*

        *in Carbon, the funds received on this curve are not kept on this curve but 
        transferred to a linked curve; the linked curve may hold different amounts
        of x, eg because it has been seeded with x>0. In other words -- it does not
        make sense to look at absolute values of x, only of differences.    
        """
        if checkbounds:
            if y > self.yint:
                if raiseonerror:
                    raise ValueError("The value of y is out of bounds (y>yint)", y, self.yint)
                return None
            elif y < 0:
                if raiseonerror:
                    raise ValueError("The value of y is out of bounds (y<0)", y)
                return None

        num =                          self.yint * (self.yint - y)
        #        -----------------------------------------------------------------------------
        denom =  self.B**2*self.yint + self.B*self.S*y + self.B*self.S*self.yint + self.S**2*y
        return num/denom

    @property
    def x(self):
        """
        the current x value of the curve (=xfromy_f(self.y))
        """
        return self.xfromy_f(self.y)
    

    def yfromx_f(self, x, checkbounds=True, raiseonerror=False):
        """
        the invariant function, expressed as y=f(x)

        :x:             the theoretical* amount of x the AMM currently holds
        :checkbounds:   if True (default), check that dy is in the right range
        :raiseonerror:  if True, raises upon error, else return None
        :returns:       the corresponding      

        *in Carbon, the funds received on this curve are not kept on this curve but 
        transferred to a linked curve; the linked curve may hold different amounts
        of x, eg because it has been seeded with x>0. In other words -- it does not
        make sense to look at absolute values of x, only of differences.
        """
        if checkbounds:
            if x < 0:
                if raiseonerror:
                    raise ValueError("The value of x is out of bounds (x<0)", x)
                return None
            # if x < self.xint:
            #     if raiseonerror:
            #         raise ValueError("The value of x is out of bounds (x>xint; y<0)", x, result)
            #     return None 

        num =    self.yint*(-self.B**2*x - self.B*self.S*x + self.yint)
        #        ------------------------------------------------------
        denom =        self.B*self.S*x + self.S**2*x + self.yint

        y = num/denom
        if checkbounds:
            if y < 0:
                if raiseonerror:
                    raise ValueError("The value of x is out of bounds (x>xint; y<0)", x, xint, y)
                return None 
        return y

    
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
        if self.disabled:
            return 0
            
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
    
    @staticmethod
    def goalseek(func, a, b, eps=None):
        """
        helper method: solves for x, a<x<b, such that func(x) == 0
        
        :func:    a function f(x), eg lambda x: x-3
        :a:       the lower bound
        :b:       the upper bound
        :eps:     precision, ie b/a value where goal seek returns
        :returns: the x value found
        """
        if eps is None:
            eps = 0.0000001
        if not a<b:
            raise ValueError("Bracketing value a must be smaller than b", a, b)
        fa = func(a)
        fb = func(b)
        if not fa*fb<0:
            raise ValueError("Sign of f(a) must be opposite of sign of f(b)", fa, fb, a, b)
            
        while 1:
            m = 0.5*(a+b)
            fm = func(m)
            if fm * fa > 0:
                a = m
            else:
                b = m
            
            #print(f"m={m}, m={m}, b={b}")
            if b/a-1 < eps:
                return m

    def selly(self, dy, execute=True, allowneg=True, expandcurve=False, raiseonerror=False):
        """
        executes a trade selling dy for dx (dy given)

        :dy:            the amount of y to sell (a positive number)
        :execute:       if False, only display results but do not update the object
        :allowneg:      if True, negative dy numbers (=buying) are allowed
        :expandcurve:   if True, purchasing y beyond yint [sic] expands the curve to yint = y
                        only meaningful with allowneg = True
        :raiseonerror:  if True, error lead to raising on exception
        """
        if dy < 0:
            if not allowneg:
                if raiseonerror:
                    raise ValueError(f"Negative dy is not allowed (allowneg={allowneg})", dy)
                return None

        if dy == 0:
            execute = False

        yold = self.y
        pold = self.p_marg
        ynew = self.y - dy
        pnew = self.p_marg_f(dy, checkbounds=False)

        if ynew < 0:
            if raiseonerror:
                raise ValueError(f"Traded beyond capacity (yold={yold}, ynew={ynew}, dy={dy})")
            return None

        elif ynew > self.yint:
            if not expandcurve:
                if raiseonerror:
                    raise ValueError(f"Curve needs expanding and expanding not allowed (yold={yold}, ynew={ynew}, dy={dy}, expandcurve={expandcurve})")
                return None
            else:
                yintold = self.yint
                yint = ynew
                if execute:
                    self.yint = ynew
                curve_expanded = True
        
        else:
            curve_expanded = False
            yint = self.yint

        dx = self.dxfromdy_f(dy, checkbounds=False, raiseonerror=True)
        if execute:
            self.y = ynew

        if self.linked:
            result_linked = self.linked.addliqy(dx)
        else:
            result_linked = None

        result = {
            "action":       "bysource[selly]",
            "executed":     execute,
            "y_old":        yold,
            "y":            ynew,
            "dy":           dy,
            "yint_old":     yintold if curve_expanded else None,
            "y_int":        yint,
            "expanded":     curve_expanded,
            "x":            self.xfromy_f(ynew),
            "dx":           dx,
            "tkny":         self.tkny,
            "tknx":         self.tknx,
            "tx":           f"Sell {abs(dy)} {self.tkny} buy {self.tknx}" if dx>0 else f"Buy {abs(dy)} {self.tkny} sell {self.tknx}",
            "dx/dy":        dx/dy if dy != 0 else None,
            "dy/dx":        dy/dx if dx != 0 else None,
            "pmarg_old":    pold,
            "pmarg":        pnew,
            "linked":       result_linked,
            "p":            None,
        } 
        result["p"] = result["dx/dy"] if self.pair.has_basetoken(self.tkny) else result["dy/dx"]
        return result

    def buyx(self, dx, execute=True, allowneg=True, expandcurve=False, raiseonerror=False):
        """
        executes a trade dy for dx (dx given)

        :dx:            the amount of x to buy (a positive number)
        :execute:       if False, only display results but do not update the object
        :allowneg:      if True, negative dy numbers (=buying) are allowed
        :expandcurve:   if True, purchasing y beyond yint [sic] expands the curve to yint = y
                        only meaningful with allowneg = True
        :raiseonerror:  if True, error lead to raising on exception
        """
        dy = self.dyfromdx_f(dx, checkbounds=False, raiseonerror=True)
        result = self.selly(dy, execute, allowneg, expandcurve, raiseonerror)
        result["action"] = "bytarget[buyx]"
        return result

    def tradeto(self, p_marg, execute=True, raiseonerror=False):
        """
        executes a trade dy for dx (target marginal price p_marg given)

        :p:             the target marginal price
        :execute:       if False, only display results, but do not update the object
        :raiseonerror:  if True, error lead to raising on exception
        """
        try:
            dy = self.dyfromp_f(p_marg, checkbounds=True, raiseonerror=True)
        except (self.PriceOutOfBoundsErrorBeyondStart, 
                self.PriceOutOfBoundsErrorBeyondMarg):
            dy = 0
        except self.PriceOutOfBoundsErrorBeyondEnd:
            dy = self.dyfromp_f(self.p_end, checkbounds=False, raiseonerror=False)
        result = self.selly(dy, execute, allowneg=False, expandcurve=False, raiseonerror=raiseonerror)
        result["action"] = "byprice[tradeto]"
        return result
        
    def addliqy(self, dy, expandcurve=True):
        """
        adds liquidity to the curve (typically called on a linked curve)

        :dy:            the amount of liquidity to be added (must be positive)
        :expandcurve:   if True (default), expand yint=y if need be
        """
        if dy < 0:
            raise ValueError("Liquidity amount dy must not be < 0", dy)
        
        newy = self.y + dy
        result = {
            "y_old":        self.y,
            "y":            newy,
            "dy":           dy,
            "yint_old":     self.yint,
            "yint":         self.yint,
            "tkny":         self.tkn,
            "pmarg_old":    self.p_marg,
            "pmarg":        None,
            "expanded":     False,
        }
        if newy > self.yint:
            if not expandcurve:
                raise ValueError("Must expand curve and expandcurve=False", self.y, dy, newy, self.yint)
            self.yint = newy
            result["yint"] = newy
            result["expanded"] = True
        self.y = newy
        result["pmarg"] = self.p_marg
        return result
        
    @staticmethod
    def curves_by_pair_bidask(curves):
        """
        sorts curves by pair, and then by bid/ask

        :curves:        an iterable of CarbonOrderUI curves
        :returns:       dict {
                            "pair": {
                                "ALL": [curve, ...],
                                "BID": [curve, ...],
                                "ASK": [curve, ...]
                            }
                            ...
                        }
        """
        pairs = set(r.pair.slashpair for r in curves.values())
        result = {
            pair:{ 
                "ALL": [v for v in curves.values() if v.pair.slashpair == pair],
                "ASK": [v for v in curves.values() if v.pair.slashpair == pair and v.bidask=="BID"],
                "BID": [v for v in curves.values() if v.pair.slashpair == pair and v.bidask=="ASK"],
            }
            for pair in pairs
        }            
        return result
    
    def __repr__(self):
        s1 = f"pair={self.pair.slashpair}, tkn={self.tkn}, B={self.B}, S={self.S}, yint={self.yint}, y={self.y}, id={self.id}"
        s2 = f"linked=<{self.linked.id}>" if self.linked else "linked=None"
        return f"{self.__class__.__name__}({s1}, {s2})" 