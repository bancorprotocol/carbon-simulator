"""
Carbon -- data generation library
"""

from math import sqrt, exp, log
from datetime import timedelta as _timedelta, datetime as _datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class PathGenerator():
    """
    generate random lognormal paths
    
    :mu:       drift parameter; eg 0.05 = 5%
    :sig:      volatility parameter; eg 0.2 = 20%
    :s0:       spot value at time zero
    :time:     time period (in years)
    :N:        number of steps (excluding t=0)
    """
    
    DEFAULTS = {
        "mu": 0,
        "sig": 0.5,
        "s0": 100,
        "time": 1,
        "N": 200,
        "startdt": (2020, 1, 1),
        "numpaths": 100,
        "colname": "p{sig100:03d}-{mu100:02d}-{ix:03d}",
    }
    
    def __init__(self, mu=None, sig=None, s0=None, time=None, N=None, startdt=None, colname=None):
        
        if mu is None: 
            mu = self.DEFAULTS["mu"]
        if sig is None: 
            sig = self.DEFAULTS["sig"]
        if s0 is None: 
            s0 = self.DEFAULTS["s0"]        
        if time is None: 
            time = self.DEFAULTS["time"] 
        if N is None: 
            N = self.DEFAULTS["N"]  
        if startdt is None: 
            startdt = self.DEFAULTS["startdt"]  
        if colname is None:
            colname = self.DEFAULTS["colname"] 
            
        self.mu = mu
        self.sig =sig
        self.s0 = s0
        self.time = time
        self.N = N
        self.startdt = startdt
        self.colname = colname
        
        self.dt = time/N
        self.dt_td = _timedelta(days=self.dt*365.25)
        self.mudt = self.mu*self.dt
        self.halfsig2dt = 0.5*self.sig*self.sig*self.dt
        self.volsqrtdt = self.sig*sqrt(self.dt)
        self.times = np.array([i*self.dt for i in range(self.N+1)])
        self.datetimes = self._datetime_r(self.startdt)
            

    def path(self, plot=False):
        """
        generates a new random path
        
        :plot:     if True, plot the path
        """
        increments = np.random.default_rng().lognormal(
                        mean=        self.mudt - self.halfsig2dt, 
                        sigma=       self.volsqrtdt, 
                        size=        self.N)
        
        path = np.cumprod(np.insert(increments, 0, self.s0))
        if plot:
            self._plot(path)
        return path
    
    def _plot(self, path=None, datetimes=None):
        """
        plots the path with maplotlib
        """
        if path is None: path = self.path()
        if datetimes is None: datetimes = self.datetimes
        
        plt.title(f"random path (sig={self.sig*100:.0f}%, mu={self.mu*100:.0f}%, N={self.N})")
        plt.xlabel("time")
        plt.ylabel("spot")
        plt.plot(datetimes, path)
        plt.grid()
    
    def _datetime_r(self, startdt=None):
        """
        generates a datetime range
        
        :startdt:    either a datetime object, or tuple (day, month, year)
        """
        if startdt is None: 
            startdt = self.startdt
        if not isinstance(startdt, _datetime):
            if not len(startdt) == 3:
                raise ValueError("startdate must be a tuple of lenght 3", startdt)
            startdt = _datetime(*startdt)
        return np.array([startdt+i*self.dt_td for i in range(self.N+1)])
    
    @staticmethod
    def vec2ar(paths):
        """concatenates list of vectors into a single numpy array"""
        return np.concatenate([p.reshape(-1,1) for p in paths], axis=1)
    
    def pathdf(self, numpaths=None, colname=None):
        """
        generate a pandas dataframe with newly generated paths
        
        :numpaths:    number of paths to generate
        :colname:     column name (format string; {i} is the path index)
        """
        
        if numpaths is None: numpaths = self.DEFAULTS["numpaths"]
        if colname is None: colname = self.DEFAULTS["colname"]
        
        paths = [self.path() for _ in range(numpaths)]
        #df0 = pd.DataFrame(data=self.vec2ar([self.times, self.datetimes]), columns=["time", "datetime"])
        df0 = pd.DataFrame(data=self.vec2ar([self.datetimes]), columns=["datetime"])
        cols = [
            colname.format(
                sig100 = int(self.sig*100),
                mu100  = int(self.mu*100),   
                ix     = ix
                ) 
            for ix in range(len(paths))
        ]
        df1 = pd.DataFrame(data=self.vec2ar(paths), columns=cols)
        df = pd.concat([df0, df1], axis=1).set_index("datetime")
        return df
    
    def __call__(self):
        """
        alias for path
        """
        return self.path()
