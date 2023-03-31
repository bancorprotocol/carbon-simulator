"""
Carbon -- representing a levered constant product curve

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.

v1.0: ConstantProductCurve class
v1.1: added CPCContainer class
v1.1.1: bugfix
v1.2: UniV2, UniV3, and Carbon constructors; serialization
v1.3: plot
"""
__VERSION__ = "1.3"
__DATE__ = "31/Mar/2023"

from dataclasses import dataclass, field, asdict
import random
from math import sqrt
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from carbon.tools.params import Params

try:
    dataclass_ = dataclass(frozen=True, kw_only=True)
except:
    dataclass_ = dataclass(frozen=True)

class AttrDict(dict):
    """
    A dictionary that allows for attribute-style access
    
    see https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

@dataclass_
class ConstantProductCurve():
    """
    represents a, potentially levered, constant product curve
    
    :k:        pool constant k = xy [x=k/y, y=k/x]
    :x:        (virtual) pool state x (virtual number of base tokens for sale)
    :x_act:    actual pool state x (actual number of base tokens for sale)
    :y_act:    actual pool state y (actual number of quote tokens for sale)
    :pair:     token pair in slash notation ("TKNB/TKNQ"); TKNB is on the x-axis, TKNQ on the y-axis
    :cid:      unique id (optional)
    :fee:      fee (optional); eg 0.01 for 1%
    :descr:    description (optional; eg. "UniV3 0.1%")
    :params:   additional parameters (optional)
    
    NOTE: use the alternative constructors `from_xx` rather then the canonical one 
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    k: float
    x: float
    x_act: float = None
    y_act: float = None
    pair: str = None
    cid: any=None
    fee: float=None
    descr: str=None
    params: AttrDict = field(default_factory=lambda: AttrDict())
        
    def __post_init__(self):
        
        if self.x_act is None: 
            super().__setattr__('x_act', self.x) # required because class frozen
        
        if self.y_act is None: 
            super().__setattr__('y_act', self.y) # ditto
            
        if self.pair is None:
            super().__setattr__('pair', "TKNB/TKNQ")
            
        super().__setattr__('pair', self.pair.upper())
            
        if self.x_act > self.x:
            print("[ConstantProductCurve] x_act > x:", self.x_act, self.x)
            
        if self.y_act > self.y:
            print("[ConstantProductCurve] y_act > y:", self.y_act, self.y)
    
    def asdict(self):
        "returns a dict representation of the curve"
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d):
        "returns a curve from a dict representation"
        return cls(**d)
    
    def setcid(self, cid):
        """sets the curve id [can only be done once]"""
        assert self.cid is None, "cid can only be set once"
        super().__setattr__('cid', cid)
        return self

    @classmethod
    def from_kx(cls, k, x, x_act=None, y_act=None, pair=None):
        "constructor: from k,x (and x_act, y_act)"
        return cls(k=k, x=x, x_act=x_act, y_act=y_act, pair=pair)
   
    @classmethod
    def from_ky(cls, k, y, x_act=None, y_act=None, pair=None):
        "constructor: from k,y (and x_act, y_act)"
        return cls(k=k, x=k/y, x_act=x_act, y_act=y_act, pair=pair) 
    
    @classmethod
    def from_xy(cls, x, y, x_act=None, y_act=None, pair=None):
        "constructor: from x,y (and x_act, y_act)"
        return cls(k=x*y, x=x, x_act=x_act, y_act=y_act, pair=pair)
    
    @classmethod
    def from_pk(cls, p, k, x_act=None, y_act=None, pair=None):
        "constructor: from k,p (and x_act, y_act)"
        return cls(k=k, x=sqrt(k/p), x_act=x_act, y_act=y_act, pair=pair)
    
    @classmethod
    def from_px(cls, p, x, x_act=None, y_act=None, pair=None):
        "constructor: from x,p (and x_act, y_act)"
        return cls(k=x*x*p, x=x, x_act=x_act, y_act=y_act, pair=pair)
    
    @classmethod
    def from_py(cls, p, y, x_act=None, y_act=None, pair=None):
        "constructor: from y,p (and x_act, y_act)"
        return cls(k=y*y/p, x=y/p, x_act=x_act, y_act=y_act, pair=pair)
    
    @classmethod
    def from_pkpp(cls, p, k, p_min=None, p_max=None, pair=None, cid=None, fee=None, descr=None):
        "constructor: from k, p, p_min, p_max (default for last two is p)"
        if p_min is None: p_min = p
        if p_max is None: p_max = p
        x0 = sqrt(k/p)
        y0 = sqrt(k*p)
        xa = x0 - sqrt(k/p_max)
        ya = y0 - sqrt(k*p_min)
        return cls(k=k, x=x0, x_act=xa, y_act=ya, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_univ2(cls, x_tknb=None, y_tknq=None, k=None, pair=None, fee=None, cid=None, descr=None):
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)
        
        :x_tknb:    current pool liquidity in token x (base token of the pair)*
        :y_tknq:    current pool liquidity in token y (quote token of the pair)*
        :k:         uniswap liquidity parameter (k = xy)*
        
        *exactly one of k,x,y must be None; all other parameters must not be None;
        a reminder that x is TKNB and y is TKNQ
        """
        x = x_tknb
        y = y_tknq

        assert not pair is None, "pair must not be None"
        assert not cid is None, "cid must not be None"
        assert not descr is None, "descr must not be None"
        assert not fee is None, "fee must not be None"

        if k is None:
            assert x is not None and y is not None, "k is None, so x,y must not"
            k = x * y
        elif x is None:
            assert y is not None, "x is None, so y must not"
            x = k/y
        elif y is None:
            y = k/x
        else:
            assert False, "exactly one of k,x,y must be None"
        
        return cls(k=k, x=x, x_act=x, y_act=y, pair=pair, cid=cid, fee=fee, descr=descr)
    
    @classmethod
    def from_univ3(cls, Pmarg, uniL, uniPa, uniPb, pair, cid, fee, descr):
        """
        constructor: from Uniswap V3 pool (see class docstring for other parameters)
        
        :Pmarg:     current pool marginal price
        :uniL:      uniswap liquidity parameter (L**2 == k)
        :uniPa:     uniswap price range lower bound Pa (Pa < P < Pb)
        :uniPb:     uniswap price range upper bound Pb (Pa < P < Pb)
        """

        P = Pmarg
        assert uniPa < uniPb, f"uniPa < uniPb required ({uniPa}, {uniPb})"
        assert uniPa < P < uniPb, f"uniPa < Pmarg < uniPb required ({uniPa}, {P}, {uniPb})"
        k = uniL * uniL
        return cls.from_pkpp(
            p=P, 
            k=k, 
            p_min=uniPa, 
            p_max=uniPb, 
            pair=pair, 
            cid=cid, 
            fee=fee, 
            descr=descr,
            params = AttrDict(L=uniL),
            )
    
    @classmethod
    def from_carbon(cls, yint=None, y=None, pa=None, pb=None, A=None, B=None, pair=None, tkny=None, fee=None, cid=None, descr=None, isdydx=True):
        """
        constructor: from a single Carbon order (see class docstring for other parameters)*
        
        :yint:      current pool y-intercept**
        :y:         current pool liquidity in token y
        :pa:        carbon price range left bound (higher price in dy/dx)
        :pb:        carbon price range right bound (lower price in dy/dx)
        :A:         alternative to pa, pb: A = sqrt(pa) - sqrt(pb) in dy/dy
        :B:         alternative to pa, pb: B = sqrt(pb) in dy/dy
        :tkny:      token y
        :isdydx:    if True prices in dy/dx, if False in quote direction of the pair

        *Note that ALL parameters are mandatory, except that EITHER pa, bp OR A, B 
        must be given but not both; we do not correct for incorrect assignment of
        pa and pb, so if pa <= pb IN THE DY/DX DIRECTION, MEANING THAT THE NUMBERS
        ENTERED MAY SHOW THE OPPOSITE RELATIONSHIP, then an exception will be raised

        **note that the result does not depend on yint, and for the time being we
        allow to omit yint (in which case it is set to y, but this does not make
        a difference for the result)
        """
        assert not yint is None, "yint must not be None"
        assert not y is None, "y must not be None"
        assert not pair is None, "pair must not be None"
        assert not tkny is None, "tkny must not be None"
        #assert not fee is None, "fee must not be None"
        #assert not cid is None, "cid must not be None"
        #assert not descr is None, "descr must not be None"

        # if yint is None:
        #     yint = y
        assert y <= yint, "y must be <= yint"
        assert y >= 0, "y must be >= 0"

        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx  
            #print("[from_carbon] A, B:", A, B, pa, pb)
            assert A is None and B is None, "A or B is None, so both must be None"
            assert pa is not None and pb is not None, "A,B is None, so pa,pb must not"
            
        if pa is None or pb is None:
            # pa,pb is None, so we look at A,B and isdydx must be True
            #print("[from_carbon] pa, pb:", A, B, pa, pb)
            assert pa is None and pb is None, "pa or pb is None, so both must be None"
            assert A is not None and B is not None, "pa,pb is None, so A,B must not"
            assert isdydx is True, "we look at A,B so isdydx must be True"
            assert A >= 0, "A must be non-negative" # we only check for this one as it is a difference

        assert not (A is not None and B is not None and pa is not None and pb is not None), "either A,B or pa,pb must be None"
            
        tknb, tknq = pair.split("/")
        assert tkny in (tknb, tknq), f"tkny must be in pair ({tkny}, {pair})"
        tknx = tknb if tkny == tknq else tknq
        
        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx  
            
            # pair quote direction is tknq per tknb; dy/dx is tkny per tknx
            # therefore, dy/dx equals pair quote direction if tkny == tknq, otherwise reverse
            if not isdydx:
                if not tkny == tknq:
                    pa, pb = 1/pa, 1/pb

            # zero-width ranges are somewhat extended for numerical stability
            if pa == pb:
                pa *= 1.0000001
                pb /= 1.0000001
            
            # validation
            assert pa > pb, f"pa > pb required ({pa}, {pb})"

            # finally set A, B
            A = sqrt(pa) - sqrt(pb)
            B = sqrt(pb)
        
        # set some intermediate parameters (see handwritten notes in repo)
        yasym = yint * B/A
        kappa = yint**2 / A**2

        # finally instantiate the pool
        return cls(
            k = kappa,
            x = kappa/(y + yasym),
            x_act = 0,
            y_act = y,
            pair = f"{tknx}/{tkny}",
            cid = cid,
            fee = fee,
            descr = descr,
            params = AttrDict(y=y, yint=yint, A=A, B=B),
        )

    @property
    def tknb(self):
        "base token"
        return self.pair.split("/")[0]
    tknx = tknb
    
    @property
    def tknq(self):
        "quote token"
        return self.pair.split("/")[1]
    tkny = tknq

    @property
    def description(self):
        "description of the pool"
        s1 = f"tknx = {self.x_act} [virtual: {self.x}] {self.tknx}"
        s2 = f"tkny = {self.y_act} [virtual: {self.y}] {self.tkny}"
        s3 = f"p    = {self.p} [min={self.p_min}, max={self.p_max}] {self.tknq} per {self.tknb}"
        s4 = f"fee  = {self.fee}, cid = {self.cid}, descr = {self.descr}"
        return "\n".join([s1,s2,s3,s4])
    
    @property
    def y(self):
        "(virtual) pool state x (virtual number of base tokens for sale)"
        return self.k/self.x
    
    @property
    def p(self):
        "pool price (in dy/dx)"
        return self.y/self.x

    @property
    def kbar(self):
        "kbar = sqrt(k); kbar scales linearly with the pool size"
        return sqrt(self.k)
    
    @property
    def x_min(self):
        "minimum (virtual) x value"
        return self.x - self.x_act
    
    @property
    def y_min(self):
        "minimum (virtual) y value"
        return self.y - self.y_act
    
    @property
    def x_max(self):
        "maximum (virtual) x value"
        if self.y_min > 0:
            return self.k/self.y_min
        else:
            return None
    
    @property
    def y_max(self):
        "maximum (virtual) y value"
        if self.x_min > 0:
            return self.k/self.x_min
        else:
            return None
    
    @property
    def p_max(self):
        "maximum pool price (in dy/dx; None if unlimited) = y_max/x_min"
        if not self.x_min is None and self.x_min > 0:
            return self.y_max/self.x_min
        else:
            return None
    
    @property
    def p_min(self):
        "minimum pool price (in dy/dx; None if unlimited) = y_min/x_max"
        if not self.x_max is None and self.x_max > 0:
            return self.y_min/self.x_max
        else:
            return None
        
    def yfromx_f(self, x, ignorebounds=False):
        "y value for given x value (if in range; None otherwise)"
        y = self.k/x
        if ignorebounds:
            return y
        if not self.inrange(y, self.y_min, self.y_max):
            return None
        return y
    
    def xfromy_f(self, y, ignorebounds=False):
        "x value for given y value (if in range; None otherwise)"
        x = self.k/y
        if ignorebounds:
            return x
        if not self.inrange(x, self.x_min, self.x_max):
            return None
        return x
    
    def dyfromdx_f(self, dx, ignorebounds=False):
        "dy value for given dx value (if in range; None otherwise)"
        y = self.yfromx_f(self.x + dx, ignorebounds=ignorebounds)
        if y is None:
            return None
        return y-self.y
    
    def dxfromdy_f(self, dy, ignorebounds=False):
        "dx value for given dy value (if in range; None otherwise)"
        x = self.xfromy_f(self.y + dy, ignorebounds=ignorebounds)
        if x is None:
            return None
        return x-self.x
    
    @staticmethod
    def inrange(v, minv=None, maxv=None):
        "True if minv <= v <= maxv; None means no boundary"
        if not minv is None:
            if v < minv:
                return False
        if not maxv is None:
            if v > maxv:
                return False
        return True
    
@dataclass
class CPCContainer():
    """
    container for ConstantProductCurve objects (use += to add items)
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    curves: list = field(default_factory=list)

    def __post_init__(self):
        for i, c in enumerate(self.curves):
            if c.cid is None:
                c.setcid(i)
        
    def asdicts(self):
        """returns list of dictionaries representing the curves"""
        return [c.asdict() for c in self.curves]
    
    def asdf(self):
        """returns pandas dataframe representing the curves"""
        return pd.DataFrame.from_dict(self.asdicts()).set_index("cid")
    
    @classmethod
    def from_dicts(cls, dicts):
        """creates a container from a list of dictionaries"""
        return cls([ConstantProductCurve.from_dict(d) for d in dicts])
       
    @classmethod
    def from_df(cls, df):
        "creates a container from a dataframe representation"
        if "cid" in df.columns:
            df = df.set_index("cid")
        return cls.from_dicts(df.reset_index().to_dict("records"))
    
    def add(self, item):
        """adds a single ConstantProductCurve item to the container"""
        assert isinstance(item, ConstantProductCurve), f"item must be a ConstantProductCurve object {item}"
        if item.cid is None:
            item.setcid(len(self))
        self.curves += [item]
        return self
    
    def __iadd__(self, other):
        """alias for either add"""
        return self.add(other)
    
    def __iter__(self):
        return iter(self.curves)
    
    def __len__(self):
        return len(self.curves)
    
    def __getitem__(self, key):
        return self.curves[key]
    
    @property
    def tknys(self):
        """returns set of all base tokens used by the curves"""
        return {c.tknb for c in self.curves}
    
    @property
    def tknxs(self):
        """returns set of all quote tokens used by the curves"""
        return {c.tknq for c in self.curves}
    
    @property
    def tkns(self):
        """returns set of all tokens used by the curves"""
        return self.tknxs.union(self.tknys)
    
    @property
    def pairs(self):
        """returns set of all pairs"""
        return {c.pair for c in self}
    
    def bypair(self, pair):
        """returns all curves by (directed!) pair"""
        return tuple(c for c in self if c.pair==pair)
    
    def bytknx(self, tknx):
        """returns all curves by quote token tknx"""
        return tuple(c for c in self if c.tknq==tknx)
    
    def bytkny(self, tkny):
        """returns all curves by base token tkny"""
        return tuple(c for c in self if c.tknb==tkny)
    
    @staticmethod                      
    def u(minx, maxx):
        """helper: returns uniform random var"""
        return random.uniform(minx, maxx)
    
    @property                      
    def u1(self):
        """helper: returns uniform [0,1] random var"""
        return random.uniform(0, 1)
    
    @dataclass
    class xystatsd():
        mean: any
        minv: any
        maxv: any
        sdev: any
            
    def xystats(self, curves=None):
        """calculates mean, min, max, stdev of x and y"""
        if curves is None:
            curves = self.curves
        tknx = {c.tknq for c in curves}
        tkny = {c.tknb for c in curves}
        assert len(tknx)==1 and len(tkny)==1, "all curves must have same tknq and tknb"
        x = [c.x for c in curves]
        y = [c.y for c in curves]
        return (
            self.xystatsd(np.mean(x), np.min(x), np.max(x), np.std(x)), 
            self.xystatsd(np.mean(y), np.min(y), np.max(y), np.std(y))
        )
    
    @property
    def tokentable(self):
        """returns dict associating tokens with the curves on which they appeay"""
        return {tkn: {
            "x": [i for i,c in enumerate(self) if c.tknb == tkn], 
            "y": [i for i,c in enumerate(self) if c.tknq == tkn]
            }
            for tkn in self.tkns
        }
    
    Params = Params
    PLOTPARAMS = Params(
        printline = "pair = {pair}",                                            # print line before plotting; {pair} is replaced
        title = "{pair}",                                                       # plot title; {pair} and {c} are replaced
        xlabel = "{c.tknx}",                                                    # x axis label; ditto
        ylabel = "{c.tkny}",                                                    # y axis label; ditto
        label =  "[{c.cid}-{c.descr}]: p={c.p:.1f}, k={c.k:.1f}",               # label for legend; ditto
        grid = True,                                                            # plot grid if True
        legend = True,                                                          # plot legend if True
        show = True,                                                            # finish with plt.show() if True
    )

    def plot(self, pairs=None, curves=None, params=None):
        """
        plots the curves in curvelist or all curves if None

        :pairs:      list of pairs to plot
        :curves:     list of curves to plot
        :params:     plot parameters, as params struct (see PLOTPARAMS)
        """
        p = Params.construct(params, defaults=self.PLOTPARAMS.params)
        
        if pairs is None:
            pairs = self.pairs

        assert curves is None, "restricting curves not implemented yet"

        for pair in pairs:
            print(p.printline.format(pair=pair))
            curves = self.bypair(pair)
            statx, staty = self.xystats(curves)
            xr = np.linspace(0.0000001, statx.maxv*1.2,500)
            for i, c in enumerate(curves):
                plt.plot(xr, [c.yfromx_f(x_, ignorebounds=True) for x_ in xr], color="lightgrey", linestyle="dotted")
                plt.plot(xr, [c.yfromx_f(x_) for x_ in xr], color="grey")

            for c in curves:
                plt.plot(c.x, c.y, marker="*", label=p.label.format(pair=pair, c=c))  

            plt.title(p.title.format(pair=pair, c=c))
            plt.ylim((0, staty.maxv*2))
            plt.xlabel(p.xlabel.format(pair=pair, c=c))
            plt.ylabel(p.ylabel.format(pair=pair, c=c))
            if p.legend:
                plt.legend()
            if p.grid:
                plt.grid()
            
            if p.show:
                plt.show()
        