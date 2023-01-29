"""
Carbon helper module -- describing a strategy intention
"""
__VERSION__ = "0.1"
__DATE__ = "29/01/2023"

from math import sqrt as _sqrt


class Strategy():
    """
    describes a Carbon strategy intention that can be converted into a strategy supplying eg spot price
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    DEFAULTS = {
        "tkn":              True, 
        "amt_sell":         None,
        "psell_start":      None, 
        "psell_end":        None, 
        "amt_buy":          None,  
        "pbuy_start":       None, 
        "pbuy_end":         None,
        "pair":             None,
        "psell_marginal":   None,
        "pbuy_marginal":    None,
        "y_int_sell":       None,
        "y_int_buy":        None,
    }

    def __init__(self):
        pass

    def set_tkns(self, rsk=None, csh=None):
        """sets the (names) of the tokens (returns self)"""
        if rsk is None: rsk = "RSK"
        if csh is None: csh = "CSH"
        self.rsk = rsk
        self.csh = csh
        return self
    
    def scale(self, spot=100):
        """"scales the strategy to an initial spot value of `spot`; returns self"""
        raise NotImplementedError("to be implemente in derived class")

    def set_tvl(self, spot, cashpc, tvl):
        """sets that strategy amounts based on spot, cash, and tvl"""
        raise NotImplementedError("to be implemente in derived class")

    # @classmethod
    # def from_mgw(cls, m=100, g=0, w=0, u=0, amt_rsk=None, amt_csh=None, rsk=None, csh=None):
    #     pass

    # @classmethod
    # def from_u3(cls, p_lo, p_hi, start_below, tvl_csh=None, fee_pc=None, rsk=None, csh=None):
    #     pass

    @property
    def descr(s):
        pass

    @property
    def data(s):
        """returns a dict suitable for add_strategy(**s.data)"""
        raise NotImplementedError("to be implemente in derived class")
    
class StrategyFixed(Strategy):
    """
    a strategy where all ranges are fixed
    """
    def __init__(self, psell_start=None, psell_end=None, pbuy_start=None, pbuy_end=None):
        self.psell_start = psell_start
        self.psell_end = psell_end
        self.pbuy_start = pbuy_start
        self.pbuy_end = pbuy_end

class StrategyFromMGW(Strategy):
    """
    a strategy defined set based on its 
    """


    DEFAULTS = {
        "tkn":              True, 
        "amt_sell":         None,
        "psell_start":      None, 
        "psell_end":        None, 
        "amt_buy":          None,  
        "pbuy_start":       None, 
        "pbuy_end":         None,
        "pair":             None,
        "psell_marginal":   None,
        "pbuy_marginal":    None,
        "y_int_sell":       None,
        "y_int_buy":        None,
    }
