import sys, os, types

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)

_prod = os.path.join(_root, "python", "prod")

# Pre-register python.prod as a namespace package so that
# 'from python.prod.erc import ERC20' works without triggering
# python/prod/__init__.py (which imports from the installed package).
for _ns in ("python", "python.prod"):
    if _ns not in sys.modules:
        _m = types.ModuleType(_ns)
        _m.__path__ = [os.path.join(_root, *_ns.split("."))]
        _m.__package__ = _ns
        sys.modules[_ns] = _m


# Pre-import modules that use relative imports BEFORE any test file runs.
# This prevents the submodule-shadowing-class problem: when a test imports
# ``from python.prod.cst.exchg import StableswapPoolMath``, Python registers
# ``python.prod.cst.exchg.StableswapExchange`` in sys.modules as a *module*.
# Later, ``from ..exchg import StableswapExchange`` in StableswapFactory.py
# picks up the module instead of the class re-exported by __init__.py.
# By importing the factory first (before any test triggers the exchg
# __init__.py), the relative import resolves correctly.
import python.prod.cst.factory.StableswapFactory
import python.prod.process.join
import python.prod.process.swap
import python.prod.process.liquidity
