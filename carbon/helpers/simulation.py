"""
Carbon helper module - run the simulation
"""
__VERSION__ = "3.0"
__DATE__ = "28/01/2023"

from collections import namedtuple
import numpy as _np
import pandas as _pd
from math import sqrt
from matplotlib import pyplot as _plt
import pickle as _pickle
from dataclasses import dataclass as _dataclass

from .. import CarbonSimulatorUI as _CarbonSimulatorUI
from .params import Params
from .strategy import strategy as _strategy


pair_nt = namedtuple("pair", "tknb, tknq")

@_dataclass
class simresults():
    strat       : any
    spot_r      : any
    rskamt_r    : any
    cshamt_r    : any
    value_r     : any
    hodl_r      : any
    margpbuy_r  : any
    margpsell_r : any


def run_sim(strat, path, shift):
    """
    runs the simulation

    :strat:     the strategy object, or a list thereof
    :path:      the path as pandas or np series
    :shift:     the strategy shift [strat centered at (1+shift)*spot]
    :returns:   simresults tuple (rskamt_r, cshamt_r, value_r) where
                each of the ranges numpy vectors
    """

    #print("[run_sim] strat", strat)
    if isinstance(strat, _strategy):
        strat = (strat,)
    slashpair = strat[0].slashpair
    for ix, strat_ in enumerate(strat):
        if not strat_.slashpair == slashpair:
            raise ValueError("All pairs must be the same", ix, slashpair, strat_.slashpair, strat[0], strat_)
    
    path_first_date =min(path.index)
    path_first_data_above_0 = min(path.index[path>0])
    if path_first_data_above_0 > path_first_date:
        print(f"[run_sim] warning: zero price data below {path_first_data_above_0} (path start {path_first_date})")
        path = path[path>0]
    
    spot = path.iloc[0]
    #print("[run_sim] rescaling", strat)
    strat = tuple(s.rescale_strat(spot*(1+shift)) for s in strat)
    
    Sim = _CarbonSimulatorUI(pair=slashpair)
    #print("[run_sim] strategies", strat)
    for strat_ in strat:
        r = Sim.add_strategy(**strat_.dct)
        #print("[run_sim] add_strategy", r)
        assert r["success"] == True, f"error adding strategy {r}"
    ouis = Sim.state()["orderuis"]

    # FACTS:
    # ouis[0].pair.tknb == ouis[0].tkn  -> buy/bid
    # ouis[1].pair.tknq == ouis[1].tkn  -> sell/ask
    # in other words
    # oui.tkn == tknb --> buy/bid
    # oui.tkn == tknq --> sell/ask
    # of course oui also has the bidask property...
    
    ouis_buy  = tuple(o for _,o in ouis.items() if o.bidask == "BID") # 0
    ouis_sell = tuple(o for _,o in ouis.items() if o.bidask == "ASK") # 1
    
    assert len(ouis_buy) + len(ouis_sell) == len(ouis), f"wrong numbers {ouis_buy}{ouis_sell}{ouis}"
    assert len(ouis) > 0, "don't have any positions"
    #print("[run_sim] ouis", ouis, ouis_buy, ouis_sell)

    rskamt_r     = _np.array([sum(o.y for o in ouis_buy),])
    cshamt_r     = _np.array([sum(o.y for o in ouis_sell),])
    margpbuy_rz  = [tuple(o.p_marg for o in ouis_buy),]
    margpsell_rz = [tuple(o.p_marg for o in ouis_sell),]
    for spot in path[1:]:
        for oui in ouis.values():
            oui.tradeto(spot)
        rskamt_r      = _np.append(rskamt_r, [sum(o.y for o in ouis_buy),])
        cshamt_r      = _np.append(cshamt_r, [sum(o.y for o in ouis_sell),])
        
        margpbuy_rz  += [tuple(o.p_marg for o in ouis_buy),]
        margpsell_rz += [tuple(o.p_marg for o in ouis_sell),]
            # this creates margpbuy_r0 as a single series of n-tuples
            # once we are done we want to splice this into n series of singles
            # remember, if z = zip(a,b,c) then a,b,c = zip(*z)

    margpbuy_r  = tuple(zip(*margpbuy_rz))
    margpsell_r = tuple(zip(*margpsell_rz))
    value_r = rskamt_r * path + cshamt_r
    hodl_r = rskamt_r[0]*path+cshamt_r[0]
    #print(f"f[run_sim] initial amounts RSK={rskamt_r[0]}, CSH={cshamt_r[0]}", )

    return simresults(
        strat       = strat,
        spot_r      = path,
        rskamt_r    = rskamt_r, 
        cshamt_r    = cshamt_r, 
        value_r     = value_r,
        hodl_r      = hodl_r,
        margpbuy_r  = margpbuy_r,
        margpsell_r = margpsell_r
    ) 

SIM_DEFAULT_PARAMS = Params(
    plotPrice           = True,      # whether to plot the price
    plotValueCsh        = False,     # whether to plot the cash portion of the portfolio value
    plotValueRsk        = False,     # whether to plot the risk asset portion of the portfolio value
    plotValueTotal      = True,      # whether to plot the aggregate portfolio value
    plotValueHODL       = True,     # whether to plot the HODL value of the initial portfolio
    plotRanges          = True,      # whether to shade the ranges
    plotMargP           = True,      # whetger to plot the marginal price for the ranges
    plotBid             = True,      # whether to plot buy (bid) ranges and marginal prices
    plotAsk             = True,      # whether to plot sell (ask) ranges and marginal prices
    plotInterpolated    = True,      # whether to plot interpolated data
)

def plot_sim(simresults, simresults0, dataid, params, pair=None):
    """
    plots the simulation chart

    :simresults:    the simresults returned by run_sim running with path 
    :simresults0:   ditto, but for path0 (the uninterpolated path)
                    if path is path0 then simresults is simresults0
    :dataid:        a description of the data the will be used in the title
    :params:        the parameter object (can be a dict; defaults SIM_DEFAULT_PARAMS)
    :pair:          the pair as pair_nt or tuple (tknb,tknq)
    """

    has_interpolated_results = not simresults is simresults0
    strat = simresults.strat
    path = simresults.spot_r
    path0 = simresults0.spot_r
    if not pair is None: 
        pair = pair_nt(*pair)

    p = Params.construct(params, defaults=SIM_DEFAULT_PARAMS.params)
    
    if isinstance(strat, _strategy):
        strat = (strat,)
    slashpair = strat[0].slashpair
    for ix, strat_ in enumerate(strat):
        if not strat_.slashpair == slashpair:
            raise ValueError("All pairs must be the same", ix, slashpair, strat_.slashpair, strat[0], strat_)
    
    p_buy_a  = max(strat_.p_buy_a  for strat_ in strat)
    p_buy_b  = min(strat_.p_buy_b  for strat_ in strat)
    p_sell_a = min(strat_.p_sell_a for strat_ in strat)
    p_sell_b = max(strat_.p_sell_b for strat_ in strat)
    amt_rsk  = sum(strat_.amt_rsk  for strat_ in strat)
    amt_csh  = sum(strat_.amt_csh  for strat_ in strat)
    rsk      = strat[0].rsk if not pair else pair.tknb
    csh      = strat[0].csh if not pair else pair.tknq
    mid      = sqrt(p_buy_a*p_sell_a)

    descr = strat[0].descr if len(strat)==1 else f"strategy portfolio ({len(strat)} items)"
    descr = f"BID {p_buy_b:.1f}-{p_buy_a:.1f} [{amt_csh:.0f} {csh}] - MID {mid:.1f} - ASK {p_sell_a:.1f}-{p_sell_b:.1f} [{amt_rsk:.1f} {rsk}]"
    
    rskamt_r    = simresults.rskamt_r 
    cshamt_r    = simresults.cshamt_r 
    value_r     = simresults.value_r 
    value0_r    = simresults0.value_r 
    hodl_r      = simresults.hodl_r 
    margpbuy_r  = simresults.margpbuy_r 
    margpsell_r = simresults.margpsell_r

    fig, ax1 = _plt.subplots()
    ax2 = ax1.twinx()
    plots = []
    if p.plotRanges:
        for s in strat:
            if p.plotBid:
                [ax1.fill_between(path.index, s.p_buy_a, s.p_buy_b, color="lightgreen", alpha=0.1, label="bid range [lhs]")]
            if p.plotAsk:
                [ax1.fill_between(path.index, s.p_sell_a, s.p_sell_b, color="lightcoral", alpha=0.1, label="ask range [lhs]")]
            
    if p.plotMargP:
        for margpsell_ri, margpbuy_ri, ix in zip(margpsell_r, margpbuy_r, range(len(margpsell_r))):
            if p.plotBid:
                plots += ax1.plot(path.index, margpsell_ri, color="green", linestyle="dotted", linewidth=0.8, label="bid [lhs]" if not ix else None)
            if p.plotAsk:
                plots += ax1.plot(path.index, margpbuy_ri, color="red", linestyle="dotted", linewidth=0.8, label="ask [lhs]" if not ix else None)
            
    if p.plotPrice:
        plots += ax1.plot(path0, color="darkorange", alpha=0.4, label="price [lhs]")
        if has_interpolated_results and p.plotInterpolated:
            plots += ax1.plot(path, color="darkorange", alpha=0.6, linewidth=0.4)
    
    if p.plotValueHODL:
        plots += ax2.plot(value_r.index, hodl_r, color="cyan", linestyle="dotted", linewidth=1, label=f"HODL value [rhs]")
    
    if p.plotValueCsh:
        plots += ax2.plot(value_r.index, cshamt_r, color="blue", linestyle="dashed", linewidth=0.8, alpha=0.7, label=f"{csh} portion [rhs]")

    if p.plotValueRsk:
        plots += ax2.plot(value_r.index, rskamt_r*path, color="blue", linestyle="dotted", linewidth=1.2, alpha=1, label=f"{rsk} portion [rhs]")
    
    if p.plotValueTotal:
        plots += ax2.plot(value0_r, color="blue", label="portfolio value [rhs]")
        if has_interpolated_results and p.plotInterpolated:
            plots += ax2.plot(value_r, linewidth=0.2, color="royalblue", label="portfolio value [rhs]")
        
    ax2.set_ylabel(f"portfolio value ({csh})")
    ax1.set_ylabel(f"price ({csh} per {rsk})")
    #ax1.set_xlabel("date")
    _plt.title(f"{descr} on {dataid}")
    labels=[p.get_label() for p in plots]
    plots_labels=[(p,l) for l,p in zip(labels[::-1], plots[::-1]) if not l[0] == "_"]
    #_plt.legend(plots[::-1], labels[::-1])
    _plt.legend(*zip(*plots_labels))


class StartConditions():
    def __init__(self, rawdata=None):
        self._d = rawdata
        self.start_dt = _pd.Timestamp("2020-01-01")
        self.end_dt   = _pd.Timestamp("2021-01-01")
    
    @classmethod
    def load(cls, fn):
        with open(fn, 'rb') as f:
            SC=StartConditions(_pickle.load(f))
        return SC
    
    @property
    def strategy_carbon(self):
        p_sell_b, p_sell_a, p_buy_a, p_buy_b = self.carbon_ranges_raw
        psell_marginal, pbuy_marginal = self.carbon_prices
        w0, w1 = self.carbon_order_weights
        fctr = self.starting_portfolio_valuation/(w0+w1)
        amt_rsk, amt_csh = fctr*w0/self.path_raw[0], fctr*w1
        return _strategy(
            p_sell_a=p_sell_a,
            p_sell_b=p_sell_b,
            p_buy_a=p_buy_a,
            p_buy_b=p_buy_b,
            psell_marginal=psell_marginal,
            pbuy_marginal=pbuy_marginal,
            amt_rsk=amt_rsk,
            amt_csh=amt_csh,
        )
        
    @property
    def num_points(self):
        return len(self.path_raw)
    
    @property
    def time_period(self):
        return self.end_dt-self.start_dt
    
    @property
    def time_step(self):
        return self.time_period / (self.num_points-1)
    
    @property
    def path_raw(self):
        return [float(x) for x in self._d["filtered price chart"]]
    
    @property
    def path(self):
        df = _pd.DataFrame(zip(self.datetime,self.path_raw), columns=["datetime", "spot"]).set_index("datetime")
        return df["spot"]

    @property
    def datetime(self):
        dt = self.time_step
        return [self.start_dt+i*dt for i in range(self.num_points+1)]
    
    @property
    def carbon_order_weights(self):
        return [float(x) for x in self._d["carbon order weights"]]

    @property
    def carbon_ranges_raw(self):
        return [float(x) for x in self._d["carbon order boundaries"]]
    
    @property
    def carbon_prices(self):
        return [float(x) for x in self._d["carbon starting prices"]]  
   
    @property
    def starting_portfolio_valuation(self):
        return [float(x) for x in self._d["starting portfolio valuation"]][0]
    
    @property
    def uni_ranges_raw(self):
        return [float(x) for x in self._d["uniswap range boundaries"]]
    