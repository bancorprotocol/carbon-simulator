"""
Carbon helper module - run the simulation
"""
__VERSION__ = "1.0"
__DATE__ = "23/01/2023"

from collections import namedtuple as _nt
import numpy as _np
from math import sqrt
from matplotlib import pyplot as _plt
from .. import CarbonSimulatorUI as _CarbonSimulatorUI
from .params import Params
from .strategy import strategy as _strategy

simresults_nt = _nt("simresults", "rskamt_r, cshamt_r, value_r, margpbuy_r, margpsell_r")

def run_sim(strat, path):
    """
    runs the simulation

    :strat:     the strategy object, or a list thereof
    :path:      the path as pandas or np series
    :returns:   simresults_nt tuple (rskamt_r, cshamt_r, value_r) where
                each of the ranges numpy vectors
    """
    if isinstance(strat, _strategy):
        strat = (strat,)
    slashpair = strat[0].slashpair
    for ix, strat_ in enumerate(strat):
        if not strat_.slashpair == slashpair:
            raise ValueError("All pairs must be the same", ix, slashpair, strat_.slashpair, strat[0], strat_)
    
    Sim = _CarbonSimulatorUI(pair=slashpair)
    for strat_ in strat:
        Sim.add_strategy(*strat_.p)
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
    return simresults_nt(rskamt_r, cshamt_r, value_r, margpbuy_r, margpsell_r) 

SIM_DEFAULT_PARAMS = Params(
    plotPrice       = True,      # whether to plot the price
    plotValueCsh    = False,     # whether to plot the cash portion of the portfolio value
    plotValueRsk    = False,     # whether to plot the risk asset portion of the portfolio value
    plotValueTotal  = True,      # whether to plot the aggregate portfolio value
    plotRanges      = True,      # whether to shade the ranges
    plotMargP       = True,      # whetger to plot the marginal price for the ranges
    plotBid         = True,      # whether to plot buy (bid) ranges and marginal prices
    plotAsk         = True,      # whether to plot sell (ask) ranges and marginal prices
)

def plot_sim(strat, path, simresults, dataid, params):
    """
    plots the simulation chart

    :strat:         the strategy object, or a list thereof in case of multiple strategies
    :path:          the spot path used in the simulation, as pandas series
    :simresults:    the simresults_nt returned by run_sim (rskamt_r, cshamt_r, value_r, ...)
    :dataid:        a description of the data the will be used in the title
    :params:        the parameter object (can be a dict; defaults SIM_DEFAULT_PARAMS)
    """

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
    rsk      = strat[0].rsk
    csh      = strat[0].csh
    mid      = sqrt(p_buy_a*p_sell_a)

    descr = strat[0].descr if len(strat)==1 else f"strategy portfolio ({len(strat)} items)"
    descr = f"BID {p_buy_b:.1f}-{p_buy_a:.1f} [{amt_csh:.0f} {csh}] - MID {mid:.1f} - ASK {p_sell_a:.1f}-{p_sell_b:.1f} [{amt_rsk:.1f} {rsk}]"
    
    rskamt_f, cshamt_r, value_r, margpbuy_r, margpsell_r = simresults

    fig, ax1 = _plt.subplots()
    ax2 = ax1.twinx()
    plots = []
    if p.plotPrice:
        plots += ax1.plot(path, color="0.7", label="price [lhs]")
    if p.plotMargP:
        for margpsell_ri, margpbuy_ri in zip(margpsell_r, margpbuy_r):
            if p.plotBid:
                plots += ax1.plot(path.index, margpsell_ri, color="green", linestyle="dotted", linewidth=0.8, label="bid [lhs]")
            if p.plotAsk:
                plots += ax1.plot(path.index, margpbuy_ri, color="red", linestyle="dotted", linewidth=0.8, label="ask [lhs]")
    if p.plotRanges:
        for s in strat:
            if p.plotBid:
                [ax1.fill_between(path.index, s.p_buy_a, s.p_buy_b, color="lightgreen", alpha=0.1, label="bid range [lhs]")]
            if p.plotAsk:
                [ax1.fill_between(path.index, s.p_sell_a, s.p_sell_b, color="lightcoral", alpha=0.1, label="ask range [lhs]")]
                # use plots += [ax1.plot(...)] to add the above plots to the legend
    
    if p.plotValueTotal:
        plots += ax2.plot(value_r, color = "blue", label="portfolio value [rhs]")

    if p.plotValueCsh:
        plots += ax2.plot(value_r.index, cshamt_r, color="blue", linestyle="dashed", linewidth=0.8, label=f"{csh} portion [rhs]")

    if p.plotValueRsk:
        plots += ax2.plot(value_r.index, value_r-cshamt_r, color="blue", linestyle="dotted", linewidth=1, label=f"{rsk} portion [rhs]")
    
    ax2.set_ylabel(f"portfolio value ({csh})")
    ax1.set_ylabel(f"price ({csh} per {rsk})")
    #ax1.set_xlabel("date")
    _plt.title(f"{descr} on {dataid}")
    labels = [p.get_label() for p in plots]
    _plt.legend(plots, labels)