"""
Carbon -- data random interpolation library
"""
__VERSION__ = "1.0"
__DATE__ = "28/01/2023"

import numpy as _np
import pandas as _pd
from math import sqrt as _sqrt



class PathInterpolation():
    """
    interpolating path with additional data points respecting series volatility
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    @classmethod
    def gaussian_bridge(cls, a, b, sig, numsegs):
        """
        create a Gaussian bridge between two values
        
        :a:         the start value of the bridge
        :b:         the end value of the bridge
        :sig:       the lognormal volatility (0.1=10%); it is converted into
                    a standard deviation multiplying it with (a+b)/2
        :numsegs:   the number of segments to generate
        :returns:   numpy array of length numsegs+2, connecting the points a,b with
                    a path of numsegs segments, and a normal volatility of sig*(a+b)/2
        """
        if numsegs == 0:
            return _np.array([a, b])
        #stepsd = _sqrt(1/numsegs)
        increments  = _np.random.default_rng().normal(loc=0, scale=_sqrt(1/numsegs)*sig*(a+b)/2, size=numsegs)
        increments += (-sum(increments)+b-a)/numsegs
        increments  = _np.cumsum(_np.insert(increments, 0, a))
        assert abs(increments[-1]/b-1) < 1e-8, f"numerical divergence too large [{increments[-1]/b-1}]"
        increments[-1] = b
        return increments

    @classmethod
    def estimate_vol_np(cls, path, time_period=1):
        """
        estimates the volatility of a numpy path
        
        :path:          a numpy array of the path
        :time_period:   the time period covered by the path; default = 1
        :returns:       tuple normal volatility (stdev), lognormal volatility (sigma)
                        this is normalised that sd*dZ and sig*S*dZ where dZ is N(0,dt)
                        are suitable generating numbers for a path
        """
        steps = len(path)-1
        dt = time_period/steps
        sqrt_dt = _sqrt(dt)
        sd  = _np.std(_np.diff(path))/sqrt_dt
        sig = _np.std(_np.diff(_np.log(path)))/sqrt_dt
        return sd, sig

    @classmethod
    def estimate_vol(cls, path):
        """
        estimates the volatility of a pandas time series
        
        :path:          a pandas series whose index is a pandas timestamp
        :returns:       tuple normal volatility (stdev), lognormal volatility (sigma)
                        this is normalised that sd*dZ and sig*S*dZ where dZ is N(0,dt)
                        are suitable generating numbers for a path
        """
        time_period = (path.index[-1]-path.index[0])/_pd.Timedelta(days=1)/365.25
        return cls.estimate_vol_np(path, time_period)

    @classmethod
    def interpolate_segment(cls, path_segment, sig, period):
        """
        interpolates a path segment (exactly two points) with high frequency data
        
        :path_segment:    a pandas series of exactly two points, with timestamp index
        :sig:             the volatility sigma to use for the interpolation
        :period:          the desired length of the resampling period (as pandas Timedelta)
        :returns:         the resampled pandas series containing the first point and
                          the last point (must be removed for concatenation)
        """
        assert len(path_segment)==2, "path segment MUST be of length 2"
        path_td = path_segment.index[1]-path_segment.index[0]
        path_td_yrs = path_td/_pd.Timedelta(days=1)/365.25
        if period > path_td:
            print("[interpolate_segment] sample period too large; returning original")
            return path_segment.iloc[:1]
        numsegments = int(round(path_td/period,0))
        period_act = path_td/numsegments
        sample_path_np = cls.gaussian_bridge(path_segment[0], path_segment[1], sig*_sqrt(path_td_yrs), numsegments)
        sample_path_index = [path_segment.index[0] + i*period_act for i in range(numsegments+1)]
        return _pd.Series(sample_path_np, index=sample_path_index)

    @classmethod
    def interpolate(cls, path, period, sig=None, sigfctr=None, enable=True):
        """
        interpolates the path with high frequency data
        
        :path:         the path, as pandas series with pandas timestamps as index
        :obsperiod:    the desired resampling period, as pandas Timedelta (eg pd.Timedelta(minutes=1))
        :sig:          the sampling volatility (if None, estimated from the path)
        :sigfctr:      the factor by which the estimated vol is multiplied (default=1)
        :enable:       if False, simply returns `path` (allows use of this function in filter)
        :returns:      the interpolated path (or original, if enable=False)
        """
        if not enable:
            return path
        if sig is None:
            _, sig = cls.estimate_vol(path)
            if not sigfctr is None:
                sig *= sigfctr
            
        pathsegs     = (path.iloc[ix:ix+2] for ix in range(len(path)-1))
        interpolated = (cls.interpolate_segment(seg, sig, period)[:-1] for seg in pathsegs)
        newpath = _pd.concat([_pd.concat(interpolated), path.iloc[-1:]])
        return newpath 

    @staticmethod
    def Timedelta(*args, **kwargs):
        """alias for pd.Timedelta"""
        return _pd.Timedelta(*args, **kwargs)

    @classmethod
    def days(cls, days):
        """alias for Timedelta(days=days)"""
        return cls.Timedelta(days=days)

    @classmethod
    def hours(cls, hours):
        """alias for Timedelta(hours=hours)"""
        return cls.Timedelta(hours=hours)

    @classmethod
    def minutes(cls, minutes):
        """alias for Timedelta(minutes=minutes)"""
        return cls.Timedelta(minutes=minutes)

interpolate = PathInterpolation.interpolate
