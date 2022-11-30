<p align="center">
<img width="100%" src="https://drive.google.com/uc?export=view&id=10y3NKbbk7yt7cZDMszMt04g6NquTEa4p" alt="Carbon Logo" />
</p>

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# Carbon Simulator
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

[![PyPI version](https://badge.fury.io/py/carbon-simulator.svg)](https://badge.fury.io/py/carbon-simulator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Binder main](https://img.shields.io/badge/binder-main-blue)](https://mybinder.org/v2/gh/bancorprotocol/carbon-simulator/main?labpath=CarbonSim-LitepaperExamples.ipynb)
[![Binder beta](https://img.shields.io/badge/binder-beta-blue)](https://mybinder.org/v2/gh/bancorprotocol/carbon-simulator/beta?labpath=CarbonSim-LitepaperExamples.ipynb)

**Warning**

_The simulator is a work in progress with potentially broken features, unfinished sections, and a non-exhaustive overview of commands and example usage. Moreover, the entirety of the codebase and documentation is subject to change without warning. Having said this -- we will make an effort to keep the interface backwards compatible so that existing code will not break._

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


## About Carbon

Carbon is decentralized exchange infrastructure that gives users the ability to create automated flexible trading strategies on-chain. Its key technical features are adjustable parametric bonding curves, asymmetric concentrated liquidity, and an efficient routing algorithm.

This simulator has been developed by **Bancor Research** to assist in the design, testing, and validation of Carbon strategies. It can be run interactively in a Jupyter notebook environment, or via Python scripting.

The permament URL for this repo is [github.com/bancorprotocol/carbon-simulator][repo], and there is also a [PyPi package][pypi]. The Carbon project website is at [carbondefi.xyz][carbon]. On this site you will find in particular the [Litepaper][litepaper] and the [patent application][patent]. 

[carbon]:https://carbondefi.xyz
[litepaper]:https://carbondefi.xyz/r/LitePaper.pdf
[patent]:https://carbondefi.xyz/r/Patent.pdf
[repo]:https://github.com/bancorprotocol/carbon-simulator/
[pypi]:https://pypi.org/project/carbon-simulator/

## Getting started

If you already have Python and Jupyter installed, you can launch a Jupyter instance in the root directory of the project by running `jupyter notebook` and then opening the notebook [`CarbonSim-Example.ipynb`][cse], or any of the other notebooks in that directory. 

You may run into missing modules that need to be installed via pip. In this case, either install them manually based on the list in the [`requirements.txt`][rqt] or refer to the instructions below. We also recommend to install [JupyText][jupytext].

[cse]:https://github.com/bancorprotocol/carbon-simulator/blob/main/CarbonSim-Example.ipynb
[rqt]:https://github.com/bancorprotocol/carbon-simulator/blob/main/requirements.txt


## Project setup

The project should be able to run in any [Python3 environment][python] with the correct dependencies [installed via pip][pip]. If you start from a [Conda installation][conda], most dependencies should already be available. Nevertheless we recommend [setting up a virtual environment][venv] to ensure libraries installed for this project do not collide with other Python modules installed on the system.

Whilst this simulation is designed to run in any Python environment, we strongly recommend running it in [Jupyter Notebooks][jupyter] for the convenience they provide.

[venv]:https://docs.python.org/3/library/venv.html
[jupyter]:https://docs.jupyter.org/en/latest/start/index.html#next-step-install-jupyter-locally
[python]:https://www.python.org/downloads/
[conda]:https://conda.io/projects/conda/en/latest/user-guide/install/index.html
[pip]:https://pip.pypa.io/en/stable/cli/pip_install/
[jupytext]:https://jupytext.readthedocs.io/en/latest/




### Method 1. Quick setup

Navigate to the top level project directory and start the Jupyter server:

````{tab} PyPI
$ jupyter notebook
````

Then run the notebook [`CarbonSim-Example.ipynb`][cse] or any of the other notebooks. If you are getting import errors, make sure all modules from [`requirements.txt`][rqt] are installed, eg by running


````{tab} PyPI
$ pip install -r requirements.txt
````

or by installing the required modules manually. 

The upside of this method is that you get started quickly and easily. The downside is that the `carbon` library may only work for notebooks and scripts located in the root directory of this project.


### Method 2. Pip install

We are publishing this repo to [pypi:carbon-simulator][pypi] so you can install it with the usual

````{tab} PyPI
$ pip install carbon-simulator
````

This installs the latest version published on the `main` branch of the repo, as well as all dependencies. We also recommend installing [JupyText][jupytext] for easier management of the notebooks. In the unexpected case of conflicts with your local installation, consider using a [virtual environment][venv].

When installing this way there will not be any example workbooks provided. We recommend downloading the workbooks from [here][repo] to get started, starting with [`CarbonSim-Example.ipynb`][cse].


### Method 3. Installation via setup

This method will install the `carbon` package as well as all its dependencies on your system. We highly recommend to do this [in a virtual environment][venv], in which case no permanent changes will be made. To install the simulator, navigate to the top level project directory, and run the installation process via
````{tab} PyPI
$ python setup.py install
````

Then again you launch a Jupyter session running the following command
````{tab} PyPI
$ jupyter notebook
````

As the `carbon` library is now installed on your system, you can run the simulation code from anywhere whilst the virtual environment is active.


## Usage

There are numerous usage examples in the Jupyter notebooks in the root directory of this project, and we refer to those for more elaborate examples. A very basic example for a simulation is the one from [`CarbonSim-Example.ipynb`][cse]:

````{tab} PyPI
from carbon import CarbonSimulatorUI

# Set up a simulator instance, with default pair ETHUSDC
Sim = CarbonSimulatorUI(pair="ETHUSDC")

# Add a strategy. This strategy is initially seeded with 10 ETH
# and 10000 USDC. It will selling ETH between 2000-2500 USDC per ETH,
# making the received USDC available for sale. It will also be buying ETH 
# between 1000-750 USDC per ETH.
Sim.add_strategy("ETH", 10, 2000, 2500, 10000, 1000, 750)

# We can look at this order by examining the simulator state
Sim.state()["orders"]

# Someone is now trading against the pool, BUYING 1 ETH.
# The price will be driven by the 2000-2500 range.
Sim.trader_buys("ETH", 1)

# We see that that 1 ETH disappeared from the ETH curve,
# and reappeared as USDC on the other curve
Sim.state()["orders"]

# Someone is trading against the pool, SELLING 1 ETH.
# The price will be driven by the 1000-750 range
Sim.trader_sells("ETH", 1)

# Now the ETH curve is at 10 ETH, where it was initially.
# We have however taken profits of about USD 2021 on the 
# USDC account.
Sim.state()["orders"]
````
# Branches and versioning

## Branches
This repo contains two key branches, `main`, and `beta`. Their respective properties are as follows:

- `main`. The main branch is the main release branch of this project. It may not contain all bleeding edge features, but it has been tested thoroughly (but see the disclaimer on top). The main branch will never be rewritten.

- `beta`. The beta branch is the branch to go for if you are interested in the latest features of the project. It will have usually passed the test suite, so should not be broken in obvious ways. The beta branch may be rewritten from time to time.


## Versioning

We attempt to use [semantic versioning][semver] (`major.minor.patch`), so the major number is changed on backward incompatible API changes, the minor number on compatible changes, and the patch number for minor patches.

The API in this respect is defined as _"all public methods in the `SimulationUI`"_ object, as well as those in the objects it returns (currently `CarbonPair` and `CarbonOrderUI`). 

The in-library location of those objects is _not_ part of the API, they need to be imported from the top level. There may be additional objects in the top-level of the library that are not currently considered part of the API. As of version 1.0, those objects are `ExactRouterX0Y0N` and `analytics` which we do not currently consider in a state suitable for semantic versioning. 

Modules may have version numbers of their own. Those are mostly for use of the dev team and they do not follow any specific policies.

[semver]:https://semver.org/

# Change log

- **v1.3** - more order books, alpha router, thresholds; demo 3-2 and 4-1
- **v1.2** - order books
- **v1.1** - more advanced analytics
- **v1.0** - initial release