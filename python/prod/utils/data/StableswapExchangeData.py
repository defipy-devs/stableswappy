# Copyright [2024] [Ian Moore]
# Distributed under the MIT License (license terms are at http://opensource.org/licenses/MIT).
# Email: defipy.devs@gmail.com

from dataclasses import dataclass
from .ExchangeData import ExchangeData
from ...vault import StableswapVault

@dataclass
class StableswapExchangeData(ExchangeData):
    vault: StableswapVault