# stableswappy
Python package for StableSwap V1 modelling
* Currently in Beta (version 0.0.10) until fully tested and analyzed

## Install
Must first install gmpy2 python package to handle the precision within the StableSwap protocol (requires CPython 3.7 or above). To install the latest release with pip:
```
> pip install gmpy2
```
Also, in many cases will need to have required libraries (GMP, MPFR and MPC) already installed on your system, see [gmpy2 installation docs](https://gmpy2.readthedocs.io/en/latest/install.html) for more info. Once setup, to install the latest release of StableSwapPy with pip:
```
> git clone https://github.com/defipy-devs/stableswappy
> pip install .
```
or
```
> pip install StableSwapPy
```

## Basic Composable Stable Pool Overview
* See [test notebook](https://github.com/icmoore/stableswappy/blob/main/notebooks/tests/composable_stable_test.ipynb) for example implementation
* Python implementation of Composable Stable Pools 'broadly' consists of two main components
    * StableswapPoolMath.py: refactor of [StableSwap solidity contract code](https://solidity-by-example.org/defi/stable-swap-amm/), and is a slightly augmented version from [curvesim GH repos](https://github.com/curveresearch/curvesim/blob/main/curvesim/pool/stableswap/pool.py)
    * StableswapExchange.py: refactor of Curve's solidity contract code, created in-house (+ supporting classes)

