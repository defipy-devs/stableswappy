# ─────────────────────────────────────────────────────────────────────────────
# Apache 2.0 License (DeFiPy)
# ─────────────────────────────────────────────────────────────────────────────
# Copyright 2023–2026 Ian Moore
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

import sys, os, math, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).split('/python/')[0])

from python.prod.erc import ERC20
from python.prod.vault import StableswapVault
from python.prod.cst.factory import StableswapFactory
from python.prod.utils.data import StableswapExchangeData
from python.prod.process.join import Join
from python.prod.process.swap import Swap
from python.prod.analytics.risk import (
    StableswapImpLoss, DepegUnreachableError,
)

USER = 'user0'


def _build_pool(ampl, n_assets = 2, suffix = 's1'):
    """Build a balanced stableswap pool for testing.

    Returns (lp, tokens_list, lp_init_amt).
    """
    usdc = ERC20("USDC", "0x01", 6)
    usdc.deposit(USER, 10000)
    dai = ERC20("DAI", "0x02", 18)
    dai.deposit(USER, 10000)

    vault = StableswapVault()
    vault.add_token(usdc)
    vault.add_token(dai)

    tokens = [usdc, dai]
    if n_assets == 3:
        usdt = ERC20("USDT", "0x03", 6)
        usdt.deposit(USER, 10000)
        vault.add_token(usdt)
        tokens.append(usdt)

    factory = StableswapFactory(
        "Factory {}".format(suffix), "0x{}".format(suffix),
    )
    exch_data = StableswapExchangeData(
        vault = vault, symbol = "CST{}".format(suffix),
        address = "0x0{}".format(suffix),
    )
    lp = factory.deploy(exch_data)
    Join().apply(lp, USER, ampl)
    return lp, tokens, lp.liquidity_providers[USER]


# ═══════════════════════════════════════════════════════════════════════════
# Shape & construction
# ═══════════════════════════════════════════════════════════════════════════

class TestStableswapImpLossShape(unittest.TestCase):

    def test_constructor_captures_A(self):
        lp, _, amt = _build_pool(ampl = 100, suffix = 'sh1')
        il = StableswapImpLoss(lp, amt)
        self.assertEqual(il.A, 100)

    def test_constructor_captures_D(self):
        # Balanced pool with 10000 USDC + 10000 DAI → D ≈ 20000.
        lp, _, amt = _build_pool(ampl = 100, suffix = 'sh2')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.D, 20000, delta = 50)

    def test_constructor_captures_lp_share(self):
        # USER owns 100% of the pool after joining.
        lp, _, amt = _build_pool(ampl = 100, suffix = 'sh3')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.lp_share_frac, 1.0, places = 6)

    def test_per_token_init_captured(self):
        lp, _, amt = _build_pool(ampl = 100, suffix = 'sh4')
        il = StableswapImpLoss(lp, amt)
        self.assertEqual(len(il.per_token_init), 2)
        # Each token ≈ 10000 at 100% pool ownership.
        for t in il.per_token_init:
            self.assertAlmostEqual(t, 10000, delta = 50)

    def test_apply_returns_float(self):
        lp, _, amt = _build_pool(ampl = 100, suffix = 'sh5')
        il = StableswapImpLoss(lp, amt)
        self.assertIsInstance(il.apply(), float)


# ═══════════════════════════════════════════════════════════════════════════
# calc_iloss — math correctness via independent reference
# ═══════════════════════════════════════════════════════════════════════════

def _reference_il(A, alpha, max_iter = 50, tol = 1e-9,
                  epsilon_max = 0.95):
    """Independent reference implementation of the same closed form.

    Mirrors StableswapImpLoss internals in a separate code path so
    agreement between the two confirms the math landed correctly.
    Returns IL on reachable delta, None on unreachable.
    """
    delta = abs(1.0 - alpha)
    if delta == 0:
        return 0.0

    epsilon = delta * (A + 1) / (2 - delta)
    for _ in range(max_iter):
        if abs(epsilon) >= epsilon_max:
            return None
        alpha_A = A * (1 - epsilon**2)**2
        new_eps = delta * (alpha_A + 1) / (2 - delta)
        if abs(new_eps - epsilon) < tol:
            epsilon = new_eps
            break
        epsilon = new_eps
    if abs(epsilon) >= epsilon_max:
        return None

    u = epsilon**2 / ((4*A + 2) * (1 - epsilon**2))
    S_over_D = 1 + u
    v_lp = S_over_D * (1 - delta * (1 + epsilon) / 2)
    v_hold = 1 - delta / 2
    return (v_lp - v_hold) / v_hold


class TestStableswapImpLossCorrectness(unittest.TestCase):

    def test_alpha_one_gives_zero_il(self):
        lp, _, amt = _build_pool(ampl = 100, suffix = 'c1')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.calc_iloss(1.0), 0.0, places = 10)

    def test_delta_zero_gives_zero_il(self):
        lp, _, amt = _build_pool(ampl = 100, suffix = 'c2')
        il = StableswapImpLoss(lp, amt)
        # At low A, a small delta is reachable but should give a
        # small nonzero IL. At delta=0, IL=0 by short-circuit.
        # We can't call calc_iloss_at_delta(0) since 0 is outside
        # (0, 1); the behavior at exactly alpha=1 is tested above.
        self.assertAlmostEqual(il.calc_iloss(1.0), 0.0, places = 10)

    def test_matches_reference_at_low_A(self):
        # At A=10, δ=0.05 is reachable. Primitive and independent
        # reference should agree tightly.
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c3')
        il = StableswapImpLoss(lp, amt)
        result = il.calc_iloss(0.95)
        expected = _reference_il(A = 10, alpha = 0.95)
        self.assertIsNotNone(expected)
        self.assertAlmostEqual(result, expected, places = 8)

    def test_matches_reference_across_range_low_A(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c4')
        il = StableswapImpLoss(lp, amt)
        for alpha in [0.98, 0.95, 0.90, 1.02, 1.05, 1.10]:
            result = il.calc_iloss(alpha)
            expected = _reference_il(A = 10, alpha = alpha)
            self.assertIsNotNone(expected)
            self.assertAlmostEqual(
                result, expected, places = 8,
                msg = "alpha = {}".format(alpha),
            )

    def test_il_symmetric_around_peg(self):
        # IL(alpha) == IL(2 - alpha) to leading order.
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c5')
        il = StableswapImpLoss(lp, amt)
        for d in [0.02, 0.05, 0.08]:
            down = il.calc_iloss(1.0 - d)
            up = il.calc_iloss(1.0 + d)
            self.assertAlmostEqual(down, up, places = 8)

    def test_il_is_non_positive(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c6')
        il = StableswapImpLoss(lp, amt)
        for alpha in [0.98, 0.95, 0.90, 1.05, 1.10]:
            self.assertLessEqual(
                il.calc_iloss(alpha), 1e-12,
                msg = "alpha = {}".format(alpha),
            )

    def test_il_grows_with_deviation(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c7')
        il = StableswapImpLoss(lp, amt)
        il_small = abs(il.calc_iloss(0.98))
        il_large = abs(il.calc_iloss(0.90))
        self.assertGreater(il_large, il_small)

    def test_quadratic_scaling_near_peg(self):
        # For small δ, |IL| ∝ δ². Doubling δ → ~4× IL.
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c8')
        il = StableswapImpLoss(lp, amt)
        il_small = il.calc_iloss(1.0 - 0.01)
        il_large = il.calc_iloss(1.0 - 0.02)
        ratio = il_large / il_small
        # Leading-order gives exactly 4, higher-order terms perturb.
        self.assertAlmostEqual(ratio, 4.0, delta = 0.15)

    def test_higher_A_exceeds_lower_A_at_same_alpha(self):
        # The key stableswap-IL counterintuition: higher A means
        # MORE IL at the same alpha, not less. (Strong negative
        # convexity of the invariant.)
        #
        # Care required here: at HIGH A, small alphas are literally
        # UNREACHABLE — they'd require draining the pool past |ε|=0.95
        # to achieve the implied arbitrage equilibrium. The test needs
        # an (alpha, A_low, A_high) triple where both A values can
        # actually reach that alpha.
        #
        # At A=10, delta<0.17 is reachable; at A=5, delta<0.32.
        # alpha=0.90 (delta=0.10) is comfortably reachable at both.
        lp_low, _, amt_low = _build_pool(ampl = 5, suffix = 'c9a')
        lp_high, _, amt_high = _build_pool(ampl = 10, suffix = 'c9b')
        il_low = StableswapImpLoss(lp_low, amt_low)
        il_high = StableswapImpLoss(lp_high, amt_high)

        loss_low = il_low.calc_iloss(0.90)
        loss_high = il_high.calc_iloss(0.90)
        self.assertGreater(abs(loss_high), abs(loss_low))

    def test_calc_iloss_at_delta_matches_calc_iloss(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'c10')
        il = StableswapImpLoss(lp, amt)
        # calc_iloss_at_delta(0.05) should equal calc_iloss(0.95).
        via_delta = il.calc_iloss_at_delta(0.05)
        via_alpha = il.calc_iloss(0.95)
        self.assertAlmostEqual(via_delta, via_alpha, places = 10)


# ═══════════════════════════════════════════════════════════════════════════
# Reachability — DepegUnreachableError
# ═══════════════════════════════════════════════════════════════════════════

class TestStableswapImpLossReachability(unittest.TestCase):

    def test_high_A_small_depeg_raises(self):
        # At A=200, a tiny depeg (δ=0.02) requires ε≈2, which is
        # unreachable. Should raise DepegUnreachableError.
        lp, _, amt = _build_pool(ampl = 200, suffix = 'r1')
        il = StableswapImpLoss(lp, amt)
        with self.assertRaises(DepegUnreachableError):
            il.calc_iloss(0.98)

    def test_unreachable_error_carries_context(self):
        lp, _, amt = _build_pool(ampl = 200, suffix = 'r2')
        il = StableswapImpLoss(lp, amt)
        try:
            il.calc_iloss(0.98)
            self.fail("Expected DepegUnreachableError")
        except DepegUnreachableError as e:
            self.assertEqual(e.alpha, 0.98)
            self.assertEqual(e.A, 200)
            # max_reachable_delta should be populated.
            self.assertIsNotNone(e.max_reachable_delta)

    def test_unreachable_inherits_valueerror(self):
        # Callers that don't care about the distinction can catch
        # ValueError instead.
        lp, _, amt = _build_pool(ampl = 200, suffix = 'r3')
        il = StableswapImpLoss(lp, amt)
        with self.assertRaises(ValueError):
            il.calc_iloss(0.98)

    def test_reachable_on_low_A(self):
        # At A=10, δ=0.05 is well within reachable. No exception.
        lp, _, amt = _build_pool(ampl = 10, suffix = 'r4')
        il = StableswapImpLoss(lp, amt)
        result = il.calc_iloss(0.95)
        self.assertIsInstance(result, float)
        self.assertLess(result, 0)


# ═══════════════════════════════════════════════════════════════════════════
# apply — current pool state
# ═══════════════════════════════════════════════════════════════════════════

class TestStableswapImpLossApply(unittest.TestCase):

    def test_fresh_pool_near_zero_il(self):
        # Freshly joined pool is balanced — IL should be tiny.
        lp, _, amt = _build_pool(ampl = 10, suffix = 'a1')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.apply(), 0.0, places = 6)

    def test_swap_creates_il(self):
        # After a meaningful swap, dydx drifts from 1.0 → IL appears.
        lp, (usdc, dai), amt = _build_pool(ampl = 10, suffix = 'a2')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.apply(), 0.0, places = 6)
        # Drive a swap to push the pool off-balance.
        Swap().apply(lp, usdc, dai, USER, 2000)
        il_after = il.apply()
        self.assertLess(il_after, 0.0)


# ═══════════════════════════════════════════════════════════════════════════
# hold_value
# ═══════════════════════════════════════════════════════════════════════════

class TestStableswapImpLossHoldValue(unittest.TestCase):

    def test_fresh_pool_hold_is_sum_of_reserves(self):
        # Balanced 10000/10000 pool with 100% ownership → 20000 hold.
        lp, _, amt = _build_pool(ampl = 100, suffix = 'h1')
        il = StableswapImpLoss(lp, amt)
        self.assertAlmostEqual(il.hold_value(), 20000, delta = 50)

    def test_hold_value_scales_with_share(self):
        # hold_value should be lp_share_frac × sum_of_reserves.
        lp, _, amt = _build_pool(ampl = 100, suffix = 'h2')
        il_full = StableswapImpLoss(lp, amt)
        il_half = StableswapImpLoss(lp, amt / 2)
        self.assertAlmostEqual(
            il_half.hold_value(), il_full.hold_value() / 2,
            places = 4,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════════════════

class TestStableswapImpLossValidation(unittest.TestCase):

    def test_zero_lp_init_amt_raises(self):
        lp, _, _ = _build_pool(ampl = 100, suffix = 'v1')
        with self.assertRaises(ValueError) as ctx:
            StableswapImpLoss(lp, 0.0)
        self.assertIn("lp_init_amt", str(ctx.exception))

    def test_negative_lp_init_amt_raises(self):
        lp, _, _ = _build_pool(ampl = 100, suffix = 'v2')
        with self.assertRaises(ValueError):
            StableswapImpLoss(lp, -1.0)

    def test_calc_iloss_rejects_zero_alpha(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'v3')
        il = StableswapImpLoss(lp, amt)
        with self.assertRaises(ValueError):
            il.calc_iloss(0.0)

    def test_calc_iloss_rejects_negative_alpha(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'v4')
        il = StableswapImpLoss(lp, amt)
        with self.assertRaises(ValueError):
            il.calc_iloss(-0.5)

    def test_calc_iloss_at_delta_rejects_out_of_range(self):
        lp, _, amt = _build_pool(ampl = 10, suffix = 'v5')
        il = StableswapImpLoss(lp, amt)
        with self.assertRaises(ValueError):
            il.calc_iloss_at_delta(0.0)
        with self.assertRaises(ValueError):
            il.calc_iloss_at_delta(1.0)
        with self.assertRaises(ValueError):
            il.calc_iloss_at_delta(-0.1)

    def test_n3_pool_raises(self):
        lp, _, amt = _build_pool(ampl = 100, n_assets = 3, suffix = 'v6')
        with self.assertRaises(ValueError) as ctx:
            StableswapImpLoss(lp, amt)
        self.assertIn("2-asset", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
