"""
Carbon helper module -- encapsulate parameters for a single strategy
"""
__VERSION__ = "1.0.1"
__DATE__ = "24/01/2023"

from dataclasses import dataclass as _dataclass
from math import sqrt

@_dataclass
class strategy():
    """
    class describing a Carbon strategy

    :p_buy_a:       price a (=start) of the buy/bid range*   
    :p_buy_b:       price b (=end) of the buy/bid range*   
    :p_sell_a:      price a (=start) of the sell/ask range*  
    :p_sell_b:      price b (=end) of the sell/ask range*  
    :amt_rsk:       the amount of risk asset the strategy is seeded with**
    :amt_csh:       the amount of cash the strategy is seeded with**
    :rsk:           risk asset name (default RSK)
    :csh:           cash name (default CSH)

    *p_bid_x and p_ask_x are provided as alias properties

    **note that strategies that are seeded with 0 are instead seeded with
    `cls.MIN_SEED_AMT` which is set to 1e-10 (it can be changed in a derived
    class). The reason is that zero-seeded ranges do not allow for marginal prices.
    """
    p_buy_a: float
    p_buy_b: float
    p_sell_a: float
    p_sell_b: float 

    amt_rsk: float = 0
    amt_csh: float = 0
        
    rsk: str = "RSK"
    csh: str = "CSH"

    MIN_SEED_AMT = 1e-10

    @property
    def p_bid_a(self):
        """alias for p_buy_a"""
        return self.p_buy_a
    
    @property
    def p_ask_a(self):
        """alias for p_sell_a"""
        return self.p_sell_a
    
    @property
    def p_bid_b(self):
        """alias for p_buy_b"""
        return self.p_buy_b

    @property
    def p_ask_b(self):
        """alias for p_sell_b"""
        return self.p_sell_b

    def __post_init__(self):
        if self.amt_rsk == 0: self.amt_risk = self.MIN_SEED_AMT
        if self.amt_csh == 0: self.amt_csh  = self.MIN_SEED_AMT

    @classmethod
    def from_mgw(cls, m=100, g=0, w=0, amt_rsk=0, amt_csh=0, rsk="RSK", csh="CSH"):
        """
        create instance from mid `m`, gap width `g`, and range width `w`
        
        :m:             the (geometric) middle between the two ranges
        :g:             the geometric gap between the two ranges
        :w:             the geometric width of the range
        :amt_rsk:       the amount of risk asset the strategy is seeded with*
        :amt_csh:       the amount of cash the strategy is seeded with*
        :rsk:           risk asset name (default RSK)
        :csh:           cash name (default CSH)

        *note that strategies that are seeded with 0 are instead seeded with
        `cls.MIN_SEED_AMT` which is set to 1e-10 (it can be changed in a derived
        class). The reason is that zero-seeded ranges do not allow for marginal prices.


            p_buy_a     = m/(1+g/2)
            p_buy_b     = m/(1+g/2)/(1+w)
            p_sell_a    = m*(1+g/2)
            p_sell_b    = m*(1+g/2)*(1+w)

        
        """
        if w==0: w=0.0001
        if g==0: g=0.0001
        g2 = 0.5*g
        p_buy_a     = m/(1+g2)
        p_buy_b     = m/(1+g2)/(1+w)
        p_sell_a    = m*(1+g2)
        p_sell_b    = m*(1+g2)*(1+w)

        return cls(p_buy_a, p_buy_b, p_sell_a, p_sell_b, amt_rsk, amt_csh, rsk, csh)
    
    
    @property
    def descr(s):
        """returns a description of the strategy"""
        bid_s = f"BID {s.p_buy_b:.1f}-{s.p_buy_a:.1f} [{s.amt_csh} {s.csh}]"
        ask_s = f"ASK {s.p_sell_a:.1f}-{s.p_sell_b:.1f} [{s.amt_rsk} {s.rsk}]"
        mid_s = f"MID {sqrt(s.p_buy_a*s.p_sell_a):.1f}"
        return f"{bid_s} - {mid_s} - {ask_s}"
    
    @property
    def p(s):
        """returns a tuple suitable for `add_strategy (*params)`"""
        return (s.rsk, s.amt_rsk, s.p_sell_a, s.p_sell_b, s.amt_csh, s.p_buy_a, s.p_buy_b)
    
    @property
    def slashpair(self):
        """returns the slashpair as str, eg 'RSK/CSH'"""
        return f"{self.rsk}/{self.csh}"
