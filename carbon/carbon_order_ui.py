"""
represents a single, unidirectional carbon order and provides convenience methods for UI access

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT

VERSION HISTORY
- v1.3: order book helper functions (p_marg_f, yfromp_f, dyfromp_f, dyfromdx_f, dyfromdx_f, goalseek)
- v1.4: new methods: fromQxy, Q, Gamma, sellx, selly; yfromx_f, xfromy_f, p_eff_f, xint (1.3.1)
- v1.5: linked curves (beta); bidask, curves_by_pair_bidask, checks for B,S=0 (1.4.1)
- v1.6: linked curves incl trading (final), addliqy, tradeto; minor formula improvement (1.5.1)
- v1.7: integration with solidity testing (yzABS); bugfix (1.6.1)
- v1.8: from_SDK, bn2int, roundsd; some prettification
- v1.9: various additional properties representing curve parameters; used dataclass for yzABS; as_cpc
- v1.9.1: minor bugfix
- v1.9.2: minor additions to yzABSdata
"""
__version__ = "1.9.2"
__date__ = "30/Mar/2023"

try:
    from .pair import CarbonPair
except:
    from pair import CarbonPair

from dataclasses import dataclass
from math import sqrt, floor, log10
from collections import namedtuple
from .sdk import Tokens
from .tools.cpc import ConstantProductCurve as CPC

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
    :reverseq: True if the pair is quoted in reverse order (ie pa_raw = 1/pa etc)
    
    NOTES
    - natively, prices are quoted in the convention dy/dx, where tkn is the quote asset;
    tkn is also the asset being sold, so the numeraire is always the asset being sold
    - pa, pb are read at the intercepts "left to right", so pa=py is is the y intercept price,
    and pb=px is the x intercept price 
    - the properties pa_raw and pb_raw correspond to the native pa, pb; the properties pa, pb
    are quoted in the correct currency conventions
    - the properties p_start = py = pa and p_end = px = pb are aliases
    - the property A is an alias of S (we use A in the smart contracts)
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
            raise ValueError("token not part of pair", self.tkn, self.pair)
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
        """sets curve index; raises if curve ID already set (returns self)"""
        if not self.id is None:
            raise ValueError("Curve ID has already been set", id, self.id)
        self.id = id
        return self
    
    @property
    def lid(self):
        """returns ID of linked curve, or None"""
        if self.linked is None:
            return None
        return self.linked.id
        
    def set_linked(self, linked):
        """
        sets linked object

        :linked:            the linked curve (CarbonOrderUI object)
        :returns:           self
        """
        if not self.linked is None:
            #msg = f"Linked object has already been set {linked.id} {self.linked.id}"
            #print ("[set_linked]", msg)
            #print ("[set_linked] DEPRECIATION WARNING -- THIS WILL LEAD TO RAISE IN THE FUTURE")
            raise ValueError("Linked object has already been set", linked.id, self.linked.id)
            
        self.linked = linked
        # this code setting backlinks breaks previous assertions
        # if linked.linked is None:
        #     linked.linked = self
        return self

    @classmethod
    def from_BSy(cls, pair, tkn, B, S, yint, y):
        """
        alternative* constructor, taking B,S,y

        :pair:    the corresponding token pair (specifically, its CarbonPair record)
        :tkn:     the token that this order is selling
        :B:       the B-parameter; B = sqrt pb_raw
        :S:       the S-parameter; S = sqrt pa_raw - Sqrt pb_raw (also called A)
        :yint:    the y-intercept of the curve (also its current maximum capacity)
        :y:       the current y-coordinate on the curve (also current token holdings)

        *technically this is the same as the constructor, but use of `from_BSy` is recommended
        over use of the native class constructor in case of future implementation changes
        """
        return cls(
            pair=pair, 
            tkn=tkn, 
            B=B, 
            S=S, 
            yint=yint, 
            y=y
        )

    @classmethod
    def from_prices(cls, pair, tkn, pa, pb, yint, y, id=None):
        """
        alternative constructor, taking prices pa, pb and curve capacity yint
        
        :pair:    the corresponding token pair (specifically, its CarbonPair record)
        :tkn:     the token that this order is selling
        :pa:      the price at the y intercept, in quotation corresponding to the pair*
        :pb:      the price at the x intercept, in quotation corresponding to the pair*
        :yint:    the y-intercept of the curve (also its current maximum capacity)
        :y:       the current y-coordinate on the curve (also current token holdings)
        :id:      the curve ID (optional)
        
        *in their native quotation, pa, pb = -dy/dx at the y-intercept and x-intercept
        respectively; as the function y(x) is convex we must have pa >= pb; as this can
        be confusing in reverse quotation, so we correct by exchanging pa, pb if pb < pa
        """
        pair = CarbonPair(pair)
        if yint<0:
            raise ValueError(f"yint must be non-negative (yint={yint})", pair, tkn, pa, pb, yint, y)
        if y>yint:
            raise ValueError(f"y must not be bigger than yint (y={y}, yint={yint})", pair, tkn, pa, pb, yint, y)
        if y<0:
            raise ValueError(f"y must be non-negative (y={y})", pair, tkn, pa, pb, yint, y)

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
            y=y,
            id=id,
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

    @classmethod 
    def _from_SDK0(cls, encodedorder, pair, tkn, dec, sx=None):
        """
        NOTAPI - alternative constructor, from a single order object coming from the SDK

        :encodedorder:    encoded order (AByz) object returned by the SDK, eg calling `getUserStrategies`
        :pair:            corresponding token pair (specifically, its CarbonPair record)    
        :tkn:             token that this order is selling
        :dec:             number of decimals to use for tkn
        :sx:              the scaling exponent to use (default: 48)
        :returns:         corresponding CarbonOrderUI object
        """
        if not encodedorder.get("encoded") is None:
            encodedorder = encodedorder["encoded"]
        AByz = cls.bn2intd(encodedorder)
        if sx is None: sx=48
        scalefctr = 2**sx
        decimalfctr = 10**dec
        S = AByz['A']/scalefctr  # S = A
        B = AByz['B']/scalefctr
        y = AByz['y']/decimalfctr
        z = AByz['z']/decimalfctr
        return cls.from_BSy(pair=pair, tkn=tkn, S=S, B=B, y=y, z=z)
    
    @classmethod
    def from_SDK(cls, sdkStrategy, nsd=None):
        """
        double constructor, returning two strategies from the SDK

        :sdkStrategy:   SDK strategy dict, eg returned by `getUserStrategies`
        :nsd:           number of significant decimals to round to (None=no rounding)
        :returns:       a tuple of two linked CarbonOrderUI objects
        """
        s = {k:cls.roundsd(float(sdkStrategy[k]), nsd) 
            for k in ['buyPriceLow', 'buyPriceHigh', 'buyBudget', 'sellPriceLow', 'sellPriceHigh', 'sellBudget']}
        sid = cls.bn2int(sdkStrategy["id"])
        if not {sdkStrategy["baseToken"], sdkStrategy["quoteToken"]} == {sdkStrategy["encoded"]["token0"], sdkStrategy["encoded"]["token1"]}:
            raise ValueError("tokens do not match encoded tokens", sdkStrategy)
        if sdkStrategy["baseToken"] == sdkStrategy["encoded"]["token0"]:
            tknbe = sdkStrategy["encoded"]["order0"]
            tknqe = sdkStrategy["encoded"]["order1"]
        else:
            tknbe = sdkStrategy["encoded"]["order1"]
            tknqe = sdkStrategy["encoded"]["order0"]
        tknqa = sdkStrategy["quoteToken"]
        tknqo = Tokens.byticker(tknqa, raiseonerror=False, returnnultkn=False)
        tknq = tknqo.T if not tknqo is None else "TKNQ"
        tknql = cls.bn2int(tknqe["y"]) / cls.bn2int(tknqe["z"])
        tknba = sdkStrategy["baseToken"]
        tknbo = Tokens.byticker(tknba, raiseonerror=False, returnnultkn=False)
        tknb = tknbo.T if not tknbo is None else "TKNB"
        tknbl = cls.bn2int(tknbe["y"]) / cls.bn2int(tknbe["z"])
        
        pair = CarbonPair(tknq=tknq, tknb=tknb)
        # the tkn in the constructor is the one that is being sold
        o_selltknb = cls.from_prices(pair=pair, tkn=tknb, pa=s["sellPriceLow"], 
            pb=s["sellPriceHigh"], yint=s["sellBudget"], y=s["sellBudget"]*tknbl, id=f"{sid}-s")
        o_buytknb  = cls.from_prices(pair=pair, tkn=tknq, pa=s["buyPriceHigh"], 
            pb=s["buyPriceLow"], yint=s["buyBudget"], y=s["buyBudget"]*tknql, id=f"{sid}-b")
        o_buytknb.set_linked(o_selltknb)
        o_selltknb.set_linked(o_buytknb)
        return o_buytknb, o_selltknb

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
        """
        DONOTUSE -- returns BID or ASK depending on what type curve it is
        
        NOTE: BID sells base token, ASK sells quote token; this seems to be the wrong
        way round; however, if we change this we probably need to update the simulator
        sheet so we need to be careful -- DONOTUS
        """
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
    def A(self):
        """alias for S (notation used in smart contracts)"""
        return self.S
    
    @property
    def z(self):
        """alias for y (notation used in smart contracts)"""
        return self.yint

    @property
    def Q(self):
        """Q parameter = sqrt(Px/Py) < 1"""
        return sqrt(self.pb_raw/self.pa_raw)

    @property
    def Gamma(self):
        """Gamma parameter (also known as n) = 1 - sqrt(Q)"""
        return 1 - sqrt(self.Q)

    @staticmethod
    def Q_from_Gamma(Gamma):
        """Q(Gamma) = (1 - Gamma)^2"""
        return (1 - Gamma)**2
    
    @staticmethod
    def Gamma_from_Q(Q):
        """Gamma(Q) = 1 - sqrt(Q)"""
        return 1 - sqrt(Q)
    
    @staticmethod
    def asym_over_0(Gamma):
        """xasym/x0 or yasym/y0 = 1-1/Gamma < 0"""
        return 1 - 1/Gamma
    
    @staticmethod
    def int_over_0(Gamma):
        """xint/x0 or yint/y0 = (2-Gamma)/(1-Gamma) > 0"""
        return (2-Gamma)/(1-Gamma)
    
    @property
    def x0(self):
        """
        x0 alternative parameter (x0 y0 = p0)
        
        x0 = xint * (1-Gamma)/(2-Gamma)
        """
        return self.xint * (1-self.Gamma)/(2-self.Gamma)
    
    @property
    def y0(self):
        """
        alternative parameter (x0 y0 = p0)
        
        y0 = xint * (1-Gamma)/(2-Gamma)
        """
        return self.yint * (1-self.Gamma)/(2-self.Gamma)
    
    @property
    def p0_raw(self):
        """
        alternative parameter (x0 y0 = p0)
        """
        return self.y0 / self.x0
    
    @property
    def xasym(self):
        """
        alternative parameter (x asymptote); it is < 0
        """
        return self.x0 * (1-1/self.Gamma)

    @property
    def yasym(self):
        """
        alternative parameter (y asymptote); it is < 0
        """
        return self.y0 * (1-1/self.Gamma)
    
    @property
    def kappa(self):
        """
        alternative parameter x0 y0 / Gamma^2; see also kappa_bar

        Note: the invariant equation can be written as

        (x-xasym)*(y-yasym) = kappa
        """
        return self.x0*self.y0/(self.Gamma**2)
    
    @property
    def kappa_bar(self):
        """
        alternative parameter sqrt(x0 y0) / Gamma

        Note: the properly scaling invariant equation can be written as

        sqrt((x-xasym)*(y-yasym)) = kappa_bar
        """
        return sqrt(self.x0*self.y0)/self.Gamma
    
    @property
    def leverage_fctr(self):
        """
        leverage_fctr = 1/Gamma (see definition of kappa_bar)
        """
        return 1/self.Gamma
    
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
        """
        return self.pair.price_convention

    @property
    def price_convention_raw(self):
        """
        the price convention of pa_raw, pb_raw (ie dy/dx)
        """
        return f"{self.tkny} per {self.tknx}"

    def descr(self, full=False):
        """provides a description of the order and curve"""
        s1 = f"Sell {self.tkn} buy {self.pair.other(self.tkn)}"
        s2 = f"from {self.pa:.4f} to {self.pb:.4f} {self.price_convention}"
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

    EPSILON = 1e-10
    def selly(self, dy, execute=True, allowneg=True, expandcurve=False, raiseonerror=False):
        """
        executes a trade selling dy for dx (dy given)

        :dy:            the amount of y to sell (a positive number)
        :execute:       if False, only display results but do not update the object
        :allowneg:      if True, negative dy numbers (=buying) are allowed
        :expandcurve:   if True, purchasing y beyond yint [sic] expands the curve to yint = y
                        only meaningful with allowneg = True
        :raiseonerror:  if True, error lead to raising on exception
        :returns:       a dict containing extensive information about the tx
        """
        if dy < 0:
            if not allowneg:
                if dy < -self.EPSILON:
                    if raiseonerror:
                        raise ValueError(f"Negative dy is not allowed (allowneg={allowneg})", dy)
                    return None
                else:
                    dy = 0

        if abs(dy) < self.EPSILON:
            dy = 0
            execute = False

        yold = self.y
        pold = self.p_marg
        ynew = self.y - dy
        pnew = self.p_marg_f(dy, checkbounds=False)

        if ynew < -self.EPSILON:
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
            if ynew<0: ynew = 0  # see if ynew < -self.EPSILON

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
        :returns:       a dict containing extensive information about the tx
        """
        dy = self.dyfromdx_f(dx, checkbounds=False, raiseonerror=True)
        result = self.selly(dy, execute, allowneg, expandcurve, raiseonerror)
        result["action"] = "bytarget[buyx]"
        return result

    def tradeto(self, p_marg, execute=True):
        """
        executes a trade dy for dx (target marginal price p_marg given)

        :p:             the target marginal price
        :execute:       if False, only display results, but do not update the object
        :returns:       a dict containing extensive information about the tx
        """
        if self.yint == 0:
            self.yint = 1e-50 # selly fails on a fully empty curve, even with dy=0
        try:
            dy = self.dyfromp_f(p_marg, checkbounds=True, raiseonerror=True)
        except (self.PriceOutOfBoundsErrorBeyondStart, 
                self.PriceOutOfBoundsErrorBeyondMarg):
            dy = 0
        except self.PriceOutOfBoundsErrorBeyondEnd:
            dy = self.dyfromp_f(self.p_end, checkbounds=False, raiseonerror=False)
        result = self.selly(dy, execute, allowneg=False, expandcurve=False, raiseonerror=True)
        if result is None:
            raise RuntimeError(f"Unexpected None value at {p_marg}", dy, self.yint, self.y, self.p_marg, p_marg, self)
        result["action"] = "byprice[tradeto]"
        return result
        
    def addliqy(self, dy, expandcurve=True):
        """
        adds liquidity to the curve (typically called on a linked curve)

        :dy:            the amount of liquidity to be added (must be positive)
        :expandcurve:   if True (default), expand yint=y if need be
        :returns:       a dict containing extensive information about the tx
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
        DONOTUSE - sorts curves by pair, and then by bid/ask

        :curves:        an iterable of CarbonOrderUI curves
        :returns:       dict {
                            "pair": {
                                "ALL": [curve, ...],
                                "BID": [curve, ...],
                                "ASK": [curve, ...]
                            }
                            ...
                        }
        
        NOTE: apparently bidask is the wrong way round, but this is the way how currently
        the simulator expects it so we need to be careful changing it
        """
        pairs = set(r.pair.slashpair for r in curves.values())
        result = {
            pair:{ 
                "ALL": [v for v in curves.values() if v.pair.slashpair == pair],
                # NOTE THAT ASK AND BID HERE ARE EXCHANGED, SO IN PRINCIPLE WE COULD JUST CORRECT 
                # THE BIDASK FUNCTION AND CHANGE THEM BACK HERE...
                "ASK": [v for v in curves.values() if v.pair.slashpair == pair and v.bidask=="BID"],
                "BID": [v for v in curves.values() if v.pair.slashpair == pair and v.bidask=="ASK"],
            }
            for pair in pairs
        }            
        return result
    
    @property
    def as_cpc(self):
        """
        returns an equivalent constant product / virtual liquidity curve

        :returns:       a ConstantProductCurve object
        """
        p = self.p_marg
        if self.pair.has_basetoken(self.tkn): # we could also use self.bidask but this is broken at the moment TODO
            # selling the base token [ask curve?], therefore p=p_min and range ends add p_max
            p_min = p
            p_max = self.p_end
            #print("[as_cpc: ask curve]")
        else:
            # buying the base token [bid curve?], therefore p=p_max and range ends at p_min
            p_max = p
            p_min = self.p_end
            #print("[as_cpc: bid curve]")
    
        #print(p, p_min, p_max)

        return CPC.from_pkpp(
            p=p,
            k=self.kappa,
            p_min=p_min,
            p_max=p_max,
            pair=self.pair.slashpair
        )

    def yzABS(self, sx=0, verbose=False):
        """
        returns the parameters y,z,A,B,S needed for the smart contract*

        :sx:        the scaling exponent, scaling factor = 2**sx
        :verbose:   if True, prints detailed description of the calculation for audit
        :returns:   dataclass of ints (y,z,A,B,S)
                        :y:     y * 10**decy
                        :z:     yint * 10**decy
                        :A:     sqrt(10**(dec-dec)) * S * A
                        :B:     sqrt(...) * S * B
                        :S:     2**sx    

        *Important note: the parameter A in the return values corresponds to 
        the value S (or A) in this object; the value S in the return values
        corresponds to the scaling factor (!) 2**sx; it has nothing to do
        with the value S in this object      
        """
        if not self.pair.has_decimals:
            raise ValueError("pair must have decimals", self.pair)

        tkny = self.tkny
        tknx = self.tknx
        scale = 2**sx
        dec  = self.pair.decimals
        decy = dec[tkny]
        decx = dec[tknx]
        y_wei = self.y*10**decy
        z_wei = self.yint*10**decy
        B_ns = self.B * 10 ** ( (decy-decx)/2)
        A_ns = self.S * 10 ** ( (decy-decx)/2)
        yzABS = yzABSdata(y_wei, z_wei, int(A_ns*scale), int(B_ns*scale), scale)

        if verbose:
            print(f"[yzABS] pair={self.pair}, y={tkny}({decy}), x={tknx}({decx})")
            print(f"[yzABS] scale = 2**{sx} = {scale}")
            print(f"[yzABS] y={self.y} -> y_wei={y_wei} [{tkny}-wei]")
            print(f"[yzABS] yint={self.yint} -> z_wei={z_wei} [{tkny}-wei]")
            print(f"[yzABS] pa_raw={self.pa_raw} {tkny} per {tknx} -> {int(self.pa_raw*10**(decy-decx))} {tkny}-wei per {tknx}-wei")
            print(f"[yzABS] pb_raw={self.pb_raw} {tkny} per {tknx} -> {int(self.pb_raw*10**(decy-decx))} {tkny}-wei per {tknx}-wei")
            print(f"[yzABS] a={self.S} -> {A_ns} * scale = {yzABS.A}")
            print(f"[yzABS] b={self.B} -> {B_ns} * scale = {yzABS.B}")
            print(f"[yzABS] yzABS = {yzABS}")
        
        return yzABS

    @staticmethod
    def bn2int(item):
        """
        converts BigNumber to int (if item is a BND; else returns item)

        :returns: int(item) if bn BigNumber dict, else item
        """
        if not isinstance(item, dict): return item
        if not item.get("type") == 'BigNumber': return item
        return int(item["hex"], 16) 
    
    @classmethod
    def bn2intd(cls, dct):
        """
        applies bn2int to all values in a dict

        :returns: dict with int(item) if bn BigNumber dict, else item
        """
        return {k:cls.bn2int(v) for k,v in dct.items()}

    @staticmethod
    def roundsd(x, nsd=None):
        """
        rounds the value to significant decimals (returns x unmodified if not a number or zero)
        
        :x:      the value to be rounded
        :nsd:    number of significant decimals (None: don't round)
        """
        if nsd is None: return x
        try:
            magnitude = floor(log10(x))
        except:
            return x
        if magnitude <= nsd:
            return round(x,nsd-magnitude-1)
        else:
            shift = 10**(magnitude-nsd)
            return shift*round(x/shift,0)
    
    def __repr__(self):
        s1 = f"pair={str(self.pair)}, tkn={self.tkn}, B={self.B}, S={self.S}, yint={self.yint}, y={self.y}, id={self.id}"
        s2 = f"linked=<{self.linked.id}>" if self.linked else "linked=None"
        return f"{self.__class__.__name__}({s1}, {s2})"

@dataclass
class yzABSdata():
    """
    dataclass for yzABS data

    :y:     curve loading
    :z:     curve capacity
    :A:     curve parameter A, scaled by S
    :B:     curve parameter B, scaled by S
    :S:     scaling factor
    """
    y: int
    z: int
    A: int
    B: int
    S: int

    @property
    def astuple(self):
        return (self.y, self.z, self.A, self.B, self.S)
    
    @property
    def asdict(self):
        return dict(y=self.y, z=self.z, A=self.A, B=self.B, S=self.S)
    
    @property
    def A_unscaled(self):
        """uncscaled A"""
        return self.A / self.S
    
    @property
    def B_unscaled(self):
        """uncscaled B"""
        return self.B / self.S
    
    @property
    def A_scaled(self):
        """scaled A (alias for A)"""
        return self.A
    
    @property
    def B_scaled(self):
        """scaled B (alias for B)"""
        return self.B
    
    @property
    def scaling_factor(self):
        """scaling factor (alias for S)"""
        return self.S
