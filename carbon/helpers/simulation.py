"""
Carbon helper module - run the simulation
"""

from collections import namedtuple as _nt
import numpy as _np
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
    
    rskamt_r    = _np.array([ouis[0].y])
    cshamt_r    = _np.array([ouis[1].y])
    margpbuy_r  = _np.array([ouis[0].p_marg])
    margpsell_r = _np.array([ouis[1].p_marg])
    for spot in path[1:]:
        for oui in ouis.values():
            oui.tradeto(spot)
        rskamt_r      = _np.append(rskamt_r, [ouis[0].y])
        cshamt_r      = _np.append(cshamt_r, [ouis[1].y])
        
        margpbuy_r    = _np.append(margpbuy_r, [ouis[0].p_marg])
        margpsell_r   = _np.append(margpsell_r, [ouis[1].p_marg])
            # NOTE: THIS IS BROKEN FOR STRATEGY PORTOFOLIOS
            # WE NEED TO USE THE MAX OF THE BID, AND MIN OF ASK INSTEAD
            # ALTERNATIVELY WE CHANGE IT WHENEVER TRADETO WORKED IN THE RIGHT DIRECTION
    
    value_r = rskamt_r * path + cshamt_r
    return simresults_nt(rskamt_r, cshamt_r, value_r, margpbuy_r, margpsell_r) 

_DEFAULT_PARAMS = Params(
    plotRanges      = True,      # whether to shade the ranges
    plotBuy         = True,      # whether to plot buy (bid) ranges and marginal prices
    plotSell        = True,      # whether to plot sell (ask) ranges and marginal prices
    plotMargP       = True,      # whetger to plot the marginal price for the ranges
    plotPrice       = True,      # whether to plot the price
    plotValueTotal  = True,      # whether to plot the aggregate portfolio value
    plotValueCsh    = True,      # whether to plot the cash portion of the portfolio value
    plotValueRsk    = False,     # whether to plot the risk asset portion of the portfolio value
)

def plot_sim(strat, path, simresults, dataid, params):
    """
    plots the simulation chart

    :strat:         the strategy object
    :path:          the spot path used in the simulation, as pandas series
    :simresults:    the simresults_nt returned by run_sim (rskamt_r, cshamt_r, value_r)
    :dataid:        a description of the data used in the title
    :params:        the parameter object (can be a dict)
    """

    p = Params.construct(params, defaults=_DEFAULT_PARAMS.params)
    
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
    
    descr = strat[0].descr if len(strat)==1 else f"strategy portfolio ({len(strat)} items)"
    descr = f"BID {p_buy_b:.2f}-{p_buy_a:.2f} [{amt_csh:.2f} {csh}] -- ASK {p_sell_a:.2f}-{p_sell_b:.2f} [{amt_rsk:.2f} {rsk}]"
    
    rskamt_f, cshamt_r, value_r, margpbuy_r, margpsell_r = simresults
    
    #rskamt_f  = rskamt_r[-1]
    #cshamt_f  = cshamt_r[-1]

    fig, ax1 = _plt.subplots()
    ax2 = ax1.twinx()
    plots = []
    if p.plotPrice:
        plots += ax1.plot(path, color="0.7", label="price [lhs]")
    if len(strat) == 1:
        if p.plotMargP:
            # this is temporary; marginal prices are broken for multiple strategies
            if p.plotBuy:
                plots += ax1.plot(path.index, margpsell_r, color="green", linestyle="dotted", linewidth=0.8, label="bid [lhs]")
            if p.plotSell:
                plots += ax1.plot(path.index, margpbuy_r, color="red", linestyle="dotted", linewidth=0.8, label="ask [lhs]")
    if p.plotRanges:
        if p.plotBuy:
            [ax1.fill_between(path.index, p_buy_a, p_buy_b, color="lightgreen", alpha=0.1, label="bid range [lhs]")]
        if p.plotSell:
            [ax1.fill_between(path.index, p_sell_a, p_sell_b, color="lightcoral", alpha=0.1, label="ask range [lhs]")]
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