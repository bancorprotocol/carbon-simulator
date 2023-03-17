# Optimal Routing, Arbitrage and Convex Optimization


## About

Here we look at optimal routing and arbitrage amongst Carbon position as well as between Carbon positions and other AMMs, including standard constant product AMMs like Bancor and Univswap v2, and leveraged liquidty AMMs like Uniswap v3. We are using convex optimization techniques as described in _Angeris et al (2022)_ [[arxiv][arx], [code][pcode]]. 

## Installation

Some of the notebooks requires the [`cvxpy`][cvxpy] library which is not a standard Conda install, but which can be installed via `pip install cvxpy`. 

[cvxpy]:https://www.cvxpy.org/install/index.html
[arx]:https://arxiv.org/pdf/2204.05238v1.pdf
[pcode]:https://math.paperswithcode.com/paper/optimal-routing-for-constant-function-market
