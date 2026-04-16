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

from python.prod.cst.exchg import StableswapPoolMath


def setup_math_pool():
    rates = [10**30, 10**18]
    balances = [10000 * 10**6, 10000 * 10**18]
    return StableswapPoolMath(A=200, D=balances, n=2, rates=rates)


class TestStableswapMath(unittest.TestCase):

    def setUp(self):
        self.pool = setup_math_pool()

    def test_D_invariant_positive(self):
        self.assertGreater(self.pool.D(), 0)

    def test_D_invariant_stable_after_small_swap(self):
        D_before = self.pool.D()
        dx = 100 * 10**6
        self.pool.exchange(0, 1, dx)
        D_after = self.pool.D()
        pct_change = abs(D_after - D_before) / D_before
        self.assertLess(pct_change, 0.0001)

    def test_get_y_positive(self):
        xp = self.pool._xp()
        small_amount = 100 * 10**6 * self.pool.rates[0] // 10**18
        x_new = xp[0] + small_amount
        y = self.pool.get_y(0, 1, x_new, xp)
        self.assertGreater(y, 0)

    def test_exchange_output_positive(self):
        dx = 100 * 10**6
        dy, fee = self.pool.exchange(0, 1, dx)
        self.assertGreater(dy, 0)

    def test_exchange_fee_positive(self):
        pool = setup_math_pool()
        dx = 100 * 10**6
        dy, fee = pool.exchange(0, 1, dx)
        self.assertGreater(fee, 0)

    def test_virtual_price_near_one(self):
        vp = self.pool.get_virtual_price()
        self.assertAlmostEqual(vp / 10**18, 1.0, places=3)

    def test_dydx_near_one_at_peg(self):
        price = self.pool.dydx(0, 1)
        self.assertAlmostEqual(price, 1.0, places=2)

    def test_calc_token_amount_positive(self):
        amt = self.pool.calc_token_amount([1000 * 10**6, 0])
        self.assertGreater(amt, 0)


if __name__ == '__main__':
    unittest.main()
