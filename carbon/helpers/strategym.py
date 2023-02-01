"""
Carbon helper module -- encapsulate parameters for a single strategy
"""
__VERSION__ = "2.5"
__DATE__ = "31/01/2023"


from dataclasses import dataclass as _dataclass
from math import sqrt as _sqrt
from copy import copy as _copy

@_dataclass
class strategy():
    """
    class describing a Carbon strategy

    :p_sell_a:          price a (=start) of the sell/ask range*  
    :p_sell_b:          price b (=end) of the sell/ask range*  
    :p_buy_a:           price a (=start) of the buy/bid range*   
    :p_buy_b:           price b (=end) of the buy/bid range*   
    :amt_rsk:           the amount of risk asset the strategy is seeded with**
    :amt_csh:           the amount of cash the strategy is seeded with**
    :psell_marginal:    the current marginal price of the sell range
    :pbuy_marginal:     the current marginal price of the buy range
    :rsk:               risk asset name (default RSK)
    :csh:               cash name (default CSH)
    :rescale:           whether or not the strategy should be rescaled when
                        calling the rescale method
    :rescalted_fctr:    the factor this strategy was rescaled (None if not rescaled)

    *p_bid_x and p_ask_x are provided as alias properties

    **note that strategies that are seeded with 0 are instead seeded with
    `cls.MIN_SEED_AMT` which is set to 1e-10 (it can be changed in a derived
    class). The reason is that zero-seeded ranges do not allow for marginal prices.
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    p_sell_a: float
    p_sell_b: float 
    p_buy_a: float
    p_buy_b: float
    amt_rsk: float = None
    amt_csh: float = None

    psell_marginal:float = None
    pbuy_marginal:float = None

    y_int_sell:float = None
    y_int_buy:float = None
        
    rsk: str = "RSK"
    csh: str = "CSH"

    rescale: bool = True
    rescaled_fctr: float = None

    def __post_init__(self):
        pm_provided = not self.psell_marginal is None or not self.pbuy_marginal is None
        yi_provided = not self.y_int_sell is None or not self.y_int_buy is None
        if pm_provided and yi_provided:
            raise ValueError("Not both p_marginal and y_int can be provided", self.psell_marginal, self.y_int_sell, self.pbuy_marginal, self.y_int_buy)
        
    MIN_SEED_AMT = 1e-10

    def rescale_strat(self, newspot=100, oldspot=100, force=False):
        """
        rescale the strategy to another spot price (returns new object)

        :newspot:     the new spot price  to which to rescale
        :oldspot:     the old spot price basis for rescaling
        :force:       normally, strategies with rescale = False are not rescaled
                      using force = True forces a rescale
        """
        if not self.rescale:
            if not force:
                #print("[rescale_strat] not rescaling", newspot, oldspot, self)
                return _copy(self)
            else:
                print("[rescale_strat] forcing rescale", newspot, oldspot, self)

        fctr = newspot / oldspot
        #print(f"[rescale_strat] rescaling new={newspot}, old={oldspot}, fctr={fctr}", self)
        return self.__class__(
            p_sell_a = self.p_sell_a*fctr,
            p_sell_b = self.p_sell_b*fctr,
            p_buy_a  = self.p_buy_a*fctr,
            p_buy_b  = self.p_buy_b*fctr,

            amt_rsk  = self.amt_rsk,
            amt_csh  = self.amt_csh,

            psell_marginal  = self.psell_marginal*fctr if not self.psell_marginal is None else None,
            pbuy_marginal   = self.pbuy_marginal*fctr if not self.pbuy_marginal is None else None,

            # it is not really clear what to do here; strategies
            # that do set yint should probably just set "do not rescale"
            # we may come up with a better solution once we have marginal
            # prices sorted in strategy creation
            y_int_sell  = self.y_int_sell,  
            y_int_buy = self.y_int_buy*fctr if not self.y_int_buy is None else None,   # CSH number

            rsk  = self.rsk,
            csh  = self.csh,

            rescale = False,
            rescaled_fctr = fctr,
        )

    def set_tvl(self, spot, cashpc, tvl):
        """
        creates new strategy and sets amt_csh and amt_rsk based on TVL, pc cash and spot

        :spot:      the spot price (in CSH per RSK)
        :cashpc:    the percentage of the portfolio in CSH (1.0=100%)
        :tvl:       the total portfolio value in CSH (default=1,000)
        :returns:   in every case this function returns a new object;
                    provided both amt_rsk and amt_csh were None (not 0!)
                    they are changed; otherwise newobj = self
        """
        #print("[set_tvl] spot, cashpc, tvl" , spot, cashpc, tvl)
        newobj = _copy(self)
        if self.amt_rsk is None and self.amt_csh is None:
            #print("[set_tvl] setting new values for amt_rsk, amt_csh")
            newobj.amt_rsk = tvl/spot*(1-cashpc)
            newobj.amt_csh = tvl*cashpc
        else:
            #print("[set_tvl] existing values for amt_rsk, amt_csh; won't touch")
            pass
        return newobj

    def __post_init__(self):
        # the ==0 is important: do not touch None!
        # (None means: to be filled in later)
        if self.amt_rsk == 0: self.amt_risk = self.MIN_SEED_AMT
        if self.amt_csh == 0: self.amt_csh  = self.MIN_SEED_AMT
        if self.rsk is None: self.rsk = "RSK"
        if self.csh is None: self.csh = "CSH"

    @classmethod
    def from_dct(cls, dct, raiseonerror=True):
        """
        alternative constructor: reconstruct class from dict

        :dct:               a big dict, typically read from a full scenario description
        :raiseonerror:      if True, raises on error, otherwise returns None

        NOTE: the dict fields expected all start with `strat_`, and `strat_type`
        indicates which constructor to call; eg `mgw` expects data records suitable
        for the mgw constructor. For exact field names expected, please check
        the source code of this method
        """
        r = dct
        try:
            if r["strat_type"].lower() == "mgw":
                try:
                    w = (r["strat_wbuy"], r["strat_wsell"])
                except:
                    w = r["strat_w"]
                try:
                    u = (r["strat_ubuy"], r["strat_usell"])
                except:
                    u = r["strat_u"]

                return cls.from_mgw(m=r["strat_m"], g=r["strat_g"], w=w, u=u)
            else:
                raise ValueError(f"Unknown strategy {dct['strat_type']}")
        except:
            if raiseonerror:
                raise
            return None
        


    MAX_UTIL = 0.999 # all MAXUTIL < u <= 1 are set to u = MAXUTIL
    
    @classmethod
    def _validate(cls, u):
        """validates the u value for from_mgw"""
        if not u: return None
        if u<0:
            raise ValueError("Must have u >= 0", u)
        elif u>1:
            raise ValueError("Must have u < 1", u)
        elif u > cls.MAX_UTIL:
            u = cls.MAX_UTIL
        return u

    @staticmethod
    def _sorted(x1, x2, inverse=False):
        """
        returns x1,x2 in order x1<x2 (x1>x2 if inverse)
        """
        invert = (x2 > x1) ^ bool(inverse) 
        return (x1,x2) if invert else (x2,x1)
    
    @classmethod 
    def from_sb(cls, sell, buy, fixed=True, overlapping=False):
        """
        alternative constructor: create instance from sell range and buy range

        :sell:          the sell (ask) range, as tuple (start=lo, end=hi)
        :end:           the buy (bid) range, as tuple (start=him end=lo)
        :fixed:         whether the range is fixed or rescaleable
        :overlapping:   if False (default), raises on overlapping ranges
        """
        try:
            p_sell_a, p_sell_b = cls._sorted(*sell)
        except TypeError:
            p_sell_a = p_sell_b = sell

        try:
            p_buy_a, p_buy_b = cls._sorted(*buy, inverse=True)
        except TypeError:
            p_buy_a = p_buy_b = buy

        if p_buy_a > p_sell_a and not overlapping:
            raise ValueError("Must not have overlapping ranges unless overlapping True", sell, buy, p_sell_a, p_buy_a)

        return cls(
            p_sell_a = p_sell_a,
            p_sell_b = p_sell_b,
            p_buy_a = p_buy_a,
            p_buy_b = p_buy_b,  
            rescale = not fixed,    
         )

    @classmethod
    def from_mgw(cls, m=100, g=0, w=0, u=0, amt_rsk=None, amt_csh=None, rsk=None, csh=None):
        """
        alternative constructor: create instance from mid `m`, gap width `g`, and range width `w`
        
        :m:             (geometric) middle between the two ranges
        :g:             geometric gap between the two ranges
        :w:             geometric width of the range
        :u:             percentage utilization of the range (0.01=1%; 0<=u<1)**
                        note: a tuple/list is also accepted, in which case it
                        is (usell, ubuy)
        :amt_rsk:       amount of risk asset the strategy is seeded with*
        :amt_csh:       amount of cash the strategy is seeded with*
        :rsk:           risk asset name (default RSK)
        :csh:           cash name (default CSH)

        *note that strategies that are seeded with 0 are instead seeded with
        `cls.MIN_SEED_AMT` which is set to 1e-10 (it can be changed in a derived
        class). The reason is that zero-seeded ranges do not allow for marginal prices.

            p_buy_a     = m/(1+g/2)
            p_buy_b     = m/(1+g/2)/(1+w)
            p_sell_a    = m*(1+g/2)
            p_sell_b    = m*(1+g/2)*(1+w)

        **a standard range has u=0, meaning that p_marg = p_start; when u->1 we have 
        p_marg -> p_end (we can not have u=1 for y>0); p_marg = (1-u) p_s + u p_e;
        for values MAX_UTIL < u <=1, u is set to MAX_UTIL
        """
        if w==0: w=0.0001
        if g==0: g=0.0001
        try:
            # this will work on tuple / list of length 2...
            usell, ubuy = (cls._validate(uu) for uu in u)
        except:
            # ...and this for a single one
            usell = ubuy = cls._validate(u)
        #print("[from_mgw] u, usell, ubuy", u, usell, ubuy)
    
        try:
            wsell, wbuy = (cls._validate(ww) for ww in w)
        except:
            wsell = wbuy = cls._validate(w)
        #print("[from_mgw] w, wsell, wbuy", w, wsell, wbuy)
    
        
        g2 = 0.5*g
        p_buy_a     = m/(1+g2)
        p_buy_b     = m/(1+g2)/(1+wbuy)
        p_sell_a    = m*(1+g2)
        p_sell_b    = m*(1+g2)*(1+wsell)

        return cls(
            p_buy_a = p_buy_a, 
            p_buy_b = p_buy_b,
            p_sell_a = p_sell_a,
            p_sell_b = p_sell_b,
            amt_rsk = amt_rsk,
            amt_csh = amt_csh,
            rsk = rsk,
            csh = csh,
            psell_marginal = (1-usell)*p_sell_a + usell*p_sell_b if usell else None,
            pbuy_marginal = (1-ubuy)*p_buy_a + ubuy*p_buy_b if ubuy else None,
        )
    
    @classmethod
    def from_u3(cls, p_lo, p_hi, start_below, tvl_csh=None, fee_pc=None, rsk=None, csh=None):
        """
        creates a strategy equivalent to a uniswap v3 position

        :p_lo:          the low price of the range
        :p_hi:          the high price of the range
        :fee_pc:        percentage fees (0.1=1%)
        :start_below:   if True/False, the start price is below/above the range, so 
                        the combined range is 100% in RSK/CSH p_marginal at p_lo/p_hi
        :tvl_csh:       the TVL (rsk+csh) at top of the range, measured in csh (default: 1000)
        :rsk:           risk asset name (default RSK)
        :csh:           cash name (default CSH)
        """
        #assert fee_pc is None, "fees not implemented yet"
        if not p_hi >= p_lo:
            raise ValueError("Must have p_hi > p_lo", p_hi, p_lo)
        if tvl_csh is None:
            tvl_csh = 1000

        # the SELL range is always the (red) UPPER range
        # for the sell range pa < pb
        # the BUY range is always the (green) LOWER range
        # for the buy range pa > pb
        p_sell_a = p_buy_b = p_lo   
        p_sell_b = p_buy_a = p_hi

        if not fee_pc is None:
            #fee_mult = 1+0.5*fee_pc
            fee_shift = _sqrt(p_lo*p_hi)*fee_pc*0.5
            # p_sell_a *= fee_mult
            # p_sell_b *= fee_mult
            # p_buy_a  /= fee_mult
            # p_buy_b  /= fee_mult
            p_sell_a += fee_shift
            p_sell_b += fee_shift
            p_buy_a  -= fee_shift
            p_buy_b  -= fee_shift

        if start_below:
            #p_marginal = p_lo*1.0000000001
            amt_rsk = tvl_csh/_sqrt(p_lo*p_hi)
            amt_csh = 0
        else:
            #p_marginal = p_hi*0.9999999999
            amt_rsk = 0
            amt_csh = tvl_csh

        return cls(
            p_buy_a = p_buy_a, 
            p_buy_b = p_buy_b,
            p_sell_a = p_sell_a,
            p_sell_b = p_sell_b,
            amt_rsk = amt_rsk,
            amt_csh = amt_csh,
            rsk = rsk,
            csh = csh,
            # psell_marginal = p_marginal*fee_mult,
            # pbuy_marginal = p_marginal/fee_mult,
            y_int_sell = tvl_csh/_sqrt(p_lo*p_hi), # RSK NUMBER
            y_int_buy  = tvl_csh, # CSH NUMBER

            # rescale = False is extremely important as rescaling
            # typically changes the finely balanced ratios
            rescale = False,
        )

    @property
    def descr(s):
        """returns a description of the strategy"""
        bid_s = f"BID {s.p_buy_b:.1f}-{s.p_buy_a:.1f} [{s.amt_csh} {s.csh}]"
        ask_s = f"ASK {s.p_sell_a:.1f}-{s.p_sell_b:.1f} [{s.amt_rsk} {s.rsk}]"
        mid_s = f"MID {_sqrt(s.p_buy_a*s.p_sell_a):.1f}"
        return f"{bid_s} - {mid_s} - {ask_s}"
    
    @property
    def p(s):
        """DEPRECTATED returns a tuple suitable for `add_strategy (*params)`"""
        print("[strategy::p] DEPRECATED. PLEASE USE dct INSTEAD")
        return (s.rsk, s.amt_rsk, s.p_sell_a, s.p_sell_b, s.amt_csh, s.p_buy_a, s.p_buy_b)
    
    @property
    def dct(s):
        """returns a dict suitable for `add_strategy (**params)`"""
        return {
            "tkn":              s.rsk, 
            "amt_sell":         s.amt_rsk, 
            "psell_start":      s.p_sell_a, 
            "psell_end":        s.p_sell_b, 
            "amt_buy":          s.amt_csh, 
            "pbuy_start":       s.p_buy_a, 
            "pbuy_end":         s.p_buy_b,
            "pair":             s.slashpair,
            "psell_marginal":   s.psell_marginal,
            "pbuy_marginal":    s.pbuy_marginal,
            "y_int_sell":       s.y_int_sell,
            "y_int_buy":        s.y_int_buy,
        }
    
    @property
    def slashpair(self):
        """returns the slashpair as str, eg 'RSK/CSH'"""
        return f"{self.rsk}/{self.csh}"
