"""
The Carbon Simulator, a simulation engine for the Carbon protcol

see https://carbondefi.xyz for details and more documentation
see https://github.com/bancorprotocol/carbon-simulator for the repo

(c) Copyright Bprotocol foundation 2022.
Licensed under MIT
"""
from .routers import (
    ExactRouterX0Y0N,
)
from .pair import CarbonPair
from .simulators import CarbonSimulatorUI
from .simulators import sim_analytics as analytics

P = CarbonPair

__version__ = "2.0-beta1"
__date__ = "7/Dec/2022"
