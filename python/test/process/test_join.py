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


class TestJoin(unittest.TestCase):

    def setUp(self):
        self.lp, self.usdc, self.dai = setup_stableswap_lp()

    def test_join_sets_liquidity(self):
        self.assertGreater(self.lp.total_supply, 0)

    def test_join_sets_usdc_reserve(self):
        self.assertEqual(self.lp.get_reserve(self.usdc), 10000)

    def test_join_sets_dai_reserve(self):
        self.assertEqual(self.lp.get_reserve(self.dai), 10000)

    def test_join_provider_credited(self):
        self.assertGreater(self.lp.liquidity_providers[USER], 0)

    def test_join_already_joined_raises(self):
        with self.assertRaises(AssertionError):
            Join().apply(self.lp, USER, AMPL)


if __name__ == '__main__':
    unittest.main()
