"""
Carbon -- representing a levered constant product curve

(c) Copyright Bprotocol foundation 2022. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.

v1.0: ConstantProductCurve class
v1.1: added CPCContainer class
"""
__VERSION__ = "1.1"
__DATE__ = "16/Mar/2023"

from dataclasses import dataclass, field
import random
from math import sqrt
import numpy as np

try:
    dataclass_ = dataclass(frozen=True, kw_only=True)
except:
    dataclass_ = dataclass(frozen=True)
    
@dataclass_
class ConstantProductCurve():
    """
    represents a, potentially levered, constant product curve
    
    :k:        pool constant k = xy [x=k/y, y=k/x]
    :x:        (virtual) pool state x (virtual number of base tokens for sale)
    :x_act:    actual pool state x (actual number of base tokens for sale)
    :y_act:    actual pool state y (actual number of quote tokens for sale)
    :pair:     token pair in slash notation ("TKNB/TKNQ")
    :cid:      unique id (optional)
    
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
    def from_pkpp(cls, p, k, p_min=None, p_max=None, pair=None):
        "constructor: from k, p, p_min, p_max (default for last two is p)"
        if p_min is None: p_min = p
        if p_max is None: p_max = p
        x0 = sqrt(k/p)
        y0 = sqrt(k*p)
        xa = x0 - sqrt(k/p_max)
        ya = y0 - sqrt(k*p_min)
        return cls(k=k, x=x0, x_act=xa, y_act=ya, pair=pair)
    
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
    def descr(self):
        "description of the pool"
        s1 = f"tknx = {self.x_act} [virtual: {self.x}] {self.tknx}\n"
        s2 = f"tkny = {self.y_act} [virtual: {self.y}] {self.tkny}\n"
        s3 = f"p    = {self.p} [min={self.p_min}, max={self.p_max}] {self.tknq} per {self.tknb}"
        return s1+s2+s3
    
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

    curves: list = field(default_factory=list, repr=False)
        
    def __post_init__(self):
        pass
    
    def add(self, item):
        """adds a single ConstantProductCurve item to the container"""
        assert isinstance(item, ConstantProductCurve)
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
            "x": [i for i,c in enumerate(self) if c.tknq == tkn], 
            "y": [i for i,c in enumerate(self) if c.tknb == tkn]
            }
            for tkn in self.tkns
        }