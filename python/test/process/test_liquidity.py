# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2025 Ian Moore
# Email: defipy.devs@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).split('/python/')[0])

from python.prod.erc import ERC20
from python.prod.vault import StableswapVault
from python.prod.cst.factory import StableswapFactory
from python.prod.utils.data import StableswapExchangeData
from python.prod.process.join import Join
from python.prod.process.liquidity import AddLiquidity, RemoveLiquidity

USER = 'user0'
AMPL = 200


def setup_stableswap_lp():
    usdc = ERC20("USDC", "0x01", 6)
    usdc.deposit(USER, 10000)
    dai = ERC20("DAI", "0x02", 18)
    dai.deposit(USER, 10000)

    vault = StableswapVault()
    vault.add_token(usdc)
    vault.add_token(dai)

    factory = StableswapFactory("Stableswap factory", "0x3")
    exch_data = StableswapExchangeData(vault=vault, symbol="CST", address="0x011")
    lp = factory.deploy(exch_data)
    Join().apply(lp, USER, AMPL)
    return lp, usdc, dai


class TestLiquidity(unittest.TestCase):

    def setUp(self):
        self.lp, self.usdc, self.dai = setup_stableswap_lp()

    def test_add_liquidity_usdc_returns_positive(self):
        out = AddLiquidity().apply(self.lp, self.usdc, USER, 1000)
        self.assertGreater(out['liquidity_amt_in'], 0)

    def test_add_liquidity_increases_total_supply(self):
        supply_before = self.lp.total_supply
        AddLiquidity().apply(self.lp, self.usdc, USER, 1000)
        self.assertGreater(self.lp.total_supply, supply_before)

    def test_add_liquidity_usdc_reserve_increases(self):
        reserve_before = self.lp.get_reserve(self.usdc)
        AddLiquidity().apply(self.lp, self.usdc, USER, 1000)
        reserve_after = self.lp.get_reserve(self.usdc)
        self.assertGreater(reserve_after, reserve_before)

    def test_remove_liquidity_returns_token(self):
        out = RemoveLiquidity().apply(self.lp, self.usdc, USER, 100)
        self.assertGreater(out['tkn_out_amt'], 0)

    def test_remove_liquidity_decreases_total_supply(self):
        supply_before = self.lp.total_supply
        RemoveLiquidity().apply(self.lp, self.usdc, USER, 100)
        self.assertLess(self.lp.total_supply, supply_before)


if __name__ == '__main__':
    unittest.main()
