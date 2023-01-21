"""
Carbon helper module -- encapsulate paramters for a single strategy
"""
__VERSION__ = "1.0"
__DATE__ = "21/01/2023"

from dataclasses import dataclass


@dataclass
class strategy():
    
    p_buy_a: float
    p_buy_b: float
    p_sell_a: float
    p_sell_b: float 

    amt_rsk: float = 0
    amt_csh: float = 0
        
    rsk: str = "RSK"
    csh: str = "CSH"

    @classmethod
    def from_mwh(cls, m=100, g=0, w=0, amt_rsk=0, amt_csh=0, rsk="RSK", csh="CSH"):
        """
        create class from mid and widths
        
        :m:             the (geometric) middle between the two ranges
        :g:             the geometric gap between the two ranges
        :w:             the geometric width of the range
        :amt_rsk:       the amount of risk asset the strategy is seeded with
        :amt_csh:       the amount of cash the strategy is seeded with
        :rsk:           risk asset name (default RSK)
        :csh:           cash name (default CSH)

            p_buy_a     = m/(1+g)
            p_buy_b     = m/(1+g)/(1+w)
            p_sell_a    = m*(1+g)
            p_sell_b    = m*(1+g)*(1+w)
        """
        p_buy_a     = m/(1+g)
        p_buy_b     = m/(1+g)/(1+w)
        p_sell_a    = m*(1+g)
        p_sell_b    = m*(1+g)*(1+w)

        return cls(p_buy_a, p_buy_b, p_sell_a, p_sell_b, amt_rsk, amt_csh, rsk, csh)
    
    @property
    def descr(s):
        bid_s = f"BID {s.p_buy_b:.1f}-{s.p_buy_a:.1f} [{s.amt_csh} {s.csh}]"
        ask_s = f"ASK {s.p_sell_a:.1f}-{s.p_sell_b:.1f} [{s.amt_rsk} {s.rsk}]"
        return f"{bid_s} -- {ask_s}"
    
    @property
    def p(s):
        """returns a tuple suitable for `add_strategy (*params)`"""
        return (s.rsk, s.amt_rsk, s.p_sell_a, s.p_sell_b, s.amt_csh, s.p_buy_a, s.p_buy_b)
    
    @property
    def slashpair(self):
        return f"{self.rsk}/{self.csh}"

strategy.from_mwh(2000, 0.1, 0.05, amt_rsk=1, rsk="ETH", csh="USD").p