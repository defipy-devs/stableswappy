# stableswappy
Python package for StableSwap V1 modelling
* Currently in Beta (version 0.0.1) until fully tested and analyzed

## Install
To install package:
```
> git clone https://github.com/icmoore/stableswappy
> pip install .
```
or
```
> pip install StableSwapPy
```

## Basic Composable Stable Pool Overview
* See [test notebook](hhttps://github.com/icmoore/stableswappy/blob/main/notebooks/tests/composable_stable_test.ipynb) for example implementation
* Python implementation of Composable Stable Pools 'broadly' consists of two main components
    * StableswapPoolMath.py: refactor of [StableSwap solidity contract code](https://solidity-by-example.org/defi/stable-swap-amm/), and is a slightly augmented version from [curvesim GH repos](https://github.com/curveresearch/curvesim/blob/main/curvesim/pool/stableswap/pool.py)
    * StableswapExchange.py: refactor of Curve's solidity contract code, created in-house (+ supporting classes)

