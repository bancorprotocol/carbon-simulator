"""
Carbon helper module - run the simulation
"""

from collections import namedtuple as _nt
import numpy as _np
from matplotlib import pyplot as _plt
from .. import CarbonSimulatorUI as _CarbonSimulatorUI

simresults_nt = _nt("simresults", "rskamt_r, cshamt_r, value_r")

def run_sim(strat, path):
    """
    runs the simulation

    :strat:     the strategy object
    :path:      the path as pandas or np series
    :returns:   simresults_nt tuple (rskamt_r, cshamt_r, value_r) where
                each of the ranges numpy vectors
    """
    Sim = _CarbonSimulatorUI(pair=strat.slashpair)
    Sim.add_strategy(*strat.p)
    ouis = Sim.state()["orderuis"]
    
    rskamt_r  = _np.array([ouis[0].y])
    cshamt_r = _np.array([ouis[1].y])
    for spot in path[1:]:
        for oui in ouis.values():
            oui.tradeto(spot)
        rskamt_r = _np.append(rskamt_r, [ouis[0].y])
        cshamt_r = _np.append(cshamt_r, [ouis[1].y])
    
    value_r = rskamt_r * path + cshamt_r
    return simresults_nt(rskamt_r, cshamt_r, value_r) 


def plot_sim(strat, path, simresults, dataid):
    """
    plots the simulation chart

    :strat:         the strategy object
    :path:          the spot path used in the simulation, as pandas series
    :simresults:    the simresults_nt returned by run_sim (rskamt_r, cshamt_r, value_r)
    :dataid:        a description of the data used in the title
    """

    rskamt_f, cshamt_r, value_r = simresults
    
    #rskamt_f  = rskamt_r[-1]
    #cshamt_f  = cshamt_r[-1]

    fig, ax1 = _plt.subplots()
    ax2 = ax1.twinx()
    plots = []
    plots += ax1.plot(path, color="0.7", label="price [lhs]")
    plots += [ax1.fill_between(path.index, strat.p_buy_a, strat.p_buy_b, color="lightgreen", alpha=0.1, label="bid [lhs]")]
    plots += [ax1.fill_between(path.index, strat.p_sell_a, strat.p_sell_b, color="lightcoral", alpha=0.1, label="ask [lhs]")]
    plots += ax2.plot(value_r.index, cshamt_r, color = "skyblue", label="cash [rhs]")
    plots += ax2.plot(value_r, color = "blue", label="value [rhs]")
    ax2.set_ylabel("portfolio value (USDC)")
    ax1.set_ylabel("price")
    ax1.set_xlabel("date")
    _plt.title(f"{strat.descr} on {dataid}")
    labels = [p.get_label() for p in plots]
    _plt.legend(plots, labels)