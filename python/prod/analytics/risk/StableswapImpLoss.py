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

import math


# Fixed-point iteration parameters for inverting ε given δ.
_FIXED_POINT_TOL = 1e-9
_FIXED_POINT_MAX_ITER = 50

# Reachability bound on |ε|. At |ε| = 1 the pool is fully drained; near 1
# the leading-order expansion breaks down numerically. 0.95 gives a
# comfortable safety margin while still covering realistic depeg
# scenarios (on a test pool at A=200, 0.95 corresponds to roughly 30%
# reachable depeg).
_EPSILON_MAX = 0.95


class DepegUnreachableError(ValueError):
    """Raised when the requested alpha (or equivalently, depeg magnitude)
    cannot be reached by the pool — i.e. the arbitrage required to push
    the internal price to the target would need to drain the pool beyond
    the safe |ε| < 0.95 bound.

    Inherits from ValueError so callers who don't care about the
    distinction can catch ValueError and move on.

    Attributes
    ----------
    alpha : float
        The requested price ratio that couldn't be reached.
    A : float
        The amplification coefficient at which the request was made
        (higher A → less reachable at the same alpha).
    max_reachable_delta : float, optional
        If computable, the largest |1 - alpha| magnitude this pool
        can actually reach. None when not computable cheaply.
    """

    def __init__(self, alpha, A, max_reachable_delta = None):
        self.alpha = alpha
        self.A = A
        self.max_reachable_delta = max_reachable_delta
        msg = (
            "StableswapImpLoss: alpha={:.6f} is unreachable at A={}. "
            "The pool's arbitrage-equilibrium price cannot reach this "
            "value without draining the pool past |ε|=0.95."
        ).format(alpha, A)
        if max_reachable_delta is not None:
            msg += " Max reachable |1-alpha| ≈ {:.4f}.".format(
                max_reachable_delta
            )
        super().__init__(msg)


class StableswapImpLoss:

    """ Impermanent loss for a 2-asset Curve-style stableswap pool.

        Mirrors the shape of uniswappy.analytics.risk.UniswapImpLoss and
        balancerpy.analytics.risk.BalancerImpLoss: construct with
        (lp, lp_init_amt), then call .apply() for live pool state or
        .calc_iloss(alpha) for what-if scenarios.

        Math
        ----
        For a 2-asset stableswap with invariant
        4A(x + y) + D = 4AD + D³/(4xy), parameterize by
        ε = (x - y)/(x + y) and S = x + y. Substituting into the
        invariant and solving to leading order in ε yields:

            u = S/D - 1 = ε² / [(4A + 2)(1 - ε²)]

        The internal dydx (ratio of output to input from infinitesimal
        swap) expands to:

            δ = 1 - dydx ≈ 2ε / (α_A + 1 + ε)
            where α_A = A · (1 - ε²)²

        Inverting for ε given δ:

            ε = δ(α_A + 1) / (2 - δ)

        This is a fixed-point equation because α_A depends on ε via
        (1 - ε²)². Converges in 3-10 iterations for practical (δ, A).

        Once ε is known, IL follows from the LP/hold value difference:

            v_LP   = S · (1 - δ(1 + ε) / 2)
            v_hold = D · (1 - δ / 2)
            IL     = (v_LP - v_hold) / v_hold

        The alpha / delta convention
        ----------------------------
        `alpha` is the standard IL-world convention — ratio of
        current-to-entry price of one asset. For stableswap, the two
        assets are nominally pegged (entry price ≈ 1), so `alpha`
        directly represents where the depegged asset sits relative
        to peg. `delta = 1 - alpha` is the depeg magnitude; the
        stableswap derivation is most naturally expressed in δ, but
        the public API takes alpha for symmetry with the other IL
        classes.

        Stableswap IL is symmetric around the peg: IL(alpha) ==
        IL(2 - alpha) to leading order, because the derivation uses
        |δ| = |1 - alpha| throughout. alpha > 1 (asset above peg)
        and alpha < 1 (asset below peg) produce the same magnitude
        of IL.

        The "strong negative convexity" property
        ----------------------------------------
        A surprising consequence of this math, emphasized in
        Cintra & Holloway (2023) "Detecting Depegs": at high A,
        stableswap pools exhibit LARGER absolute IL than a V2
        constant-product pool at the same alpha, not smaller. The
        flat curve forces arbitrageurs to drain substantial balance
        to move dydx even a little; once they do, the LP holds a
        skewed composition. The marketing line "stableswap protects
        LPs from IL" is true per unit of trading volume (small dydx
        change per dollar traded) but misleading per unit of price
        deviation. This class reports the per-alpha IL — the
        quantity that matters in a depeg event.

        Reachability
        ------------
        At A=200, an alpha very close to peg (say 0.98) would require
        ε ≈ 2, which is physically impossible (|ε| must be < 1 for
        y > 0). Real pools absorb arbitrage up to |ε| near 1 before
        fully draining. The class raises DepegUnreachableError when
        |ε| ≥ 0.95. Callers who want to tolerate unreachability
        can catch ValueError (which DepegUnreachableError inherits
        from).

        Scope limits
        ------------
        - 2-asset pools only in v1. Balancer-style N-asset
          generalization is a natural next iteration; the invariant
          generalizes but the leading-order inversion does not.
        - Leading-order expansion. Accuracy is best for moderate
          ε (say |ε| < 0.8); for near-drained pools higher-order
          terms start to matter. Covers most realistic depeg
          scenarios.
        - Fee exclusion. IL is computed from price divergence
          alone — accumulated fees are not netted in. Matches the
          UniswapImpLoss / BalancerImpLoss convention.
    """

    def __init__(self, lp, lp_init_amt):

        """ __init__

            Parameters
            ----------
            lp : StableswapExchange
                The pool. Must have been joined (math_pool initialized).
                Must be 2-asset; N>2 raises ValueError.
            lp_init_amt : float
                LP tokens held by this position, in human units.
                Must be > 0.

            Raises
            ------
            ValueError
                If lp_init_amt <= 0, the pool is not joined, or N != 2.
        """

        if lp_init_amt <= 0:
            raise ValueError(
                "StableswapImpLoss: lp_init_amt must be > 0; "
                "got {}".format(lp_init_amt)
            )

        if lp.math_pool is None:
            raise ValueError(
                "StableswapImpLoss: pool has not been joined "
                "(math_pool is None)."
            )

        n_assets = lp.math_pool.n
        if n_assets != 2:
            raise ValueError(
                "StableswapImpLoss: only 2-asset pools supported "
                "in v1; got N={}. N>2 extension is a future "
                "iteration.".format(n_assets)
            )

        self.lp = lp
        self.lp_init = lp_init_amt
        self.A = lp.math_pool.A
        self.n_assets = n_assets

        # Pool invariant D in human units, via balanced-pool
        # approximation D ≈ x + y at entry. Matches AssessDepegRisk.
        tkn_names = list(lp.tkn_reserves.keys())
        self.token_names = tkn_names
        decimal_balances = lp.math_pool.balances
        token_decimals = lp.tkn_decimals
        entry_balances_human = [
            lp.dec2amt(decimal_balances[i], token_decimals[tkn_names[i]])
            for i in range(n_assets)
        ]
        self.D = sum(entry_balances_human)

        # LP's fractional share of the total pool supply.
        lp_amt_dec = lp.amt2dec(lp_init_amt, 18)
        total_supply_dec = lp.math_pool.tokens
        self.lp_share_frac = (
            lp_amt_dec / total_supply_dec
            if total_supply_dec > 0 else 0.0
        )

        # Per-token entry amounts at the LP's share — "hold"
        # counterfactual amounts.
        self.entry_balances = entry_balances_human
        self.per_token_init = [
            b * self.lp_share_frac for b in entry_balances_human
        ]

    def calc_iloss(self, alpha):

        """ calc_iloss

            Closed-form stableswap IL at price ratio alpha.

            Parameters
            ----------
            alpha : float
                Price ratio of the depegged asset vs its peg. Must be
                > 0. IL is symmetric around alpha=1; alpha=0.95 and
                alpha=1.05 produce the same magnitude.

            Returns
            -------
            float
                IL as a fraction: 0.0 at alpha=1, negative otherwise.

            Raises
            ------
            ValueError
                If alpha <= 0.
            DepegUnreachableError
                If the pool cannot reach the arbitrage equilibrium
                implied by alpha without draining past |ε| = 0.95.
        """

        if alpha <= 0:
            raise ValueError(
                "StableswapImpLoss.calc_iloss: alpha must be > 0; "
                "got {}".format(alpha)
            )

        delta = abs(1.0 - alpha)

        # Exact peg case — no iteration needed.
        if delta == 0.0:
            return 0.0

        # Invert ε from δ via fixed-point iteration.
        epsilon = self._solve_epsilon(delta)
        if epsilon is None:
            raise DepegUnreachableError(
                alpha = alpha, A = self.A,
                max_reachable_delta = self._max_reachable_delta(),
            )

        # IL closed form.
        u = epsilon**2 / ((4 * self.A + 2) * (1 - epsilon**2))
        S_over_D = 1 + u
        v_lp_per_unit_D = S_over_D * (1 - delta * (1 + epsilon) / 2)
        v_hold_per_unit_D = 1 - delta / 2

        if v_hold_per_unit_D <= 0:
            # Would only trigger for delta >= 2, i.e. alpha <= -1, which
            # is already ruled out by the alpha > 0 check above.
            return 0.0

        return (v_lp_per_unit_D - v_hold_per_unit_D) / v_hold_per_unit_D

    def calc_iloss_at_delta(self, delta):

        """ calc_iloss_at_delta

            Convenience wrapper: compute IL at depeg magnitude δ rather
            than at a price ratio alpha. Internally translates to
            calc_iloss(1 - delta).

            Parameters
            ----------
            delta : float
                Depeg magnitude. Must be in (0, 1). Use this when
                the natural framing is "how much did it move off
                peg" rather than "where is the price now."

            Returns
            -------
            float
                IL as a fraction.

            Raises
            ------
            ValueError
                If delta outside (0, 1).
            DepegUnreachableError
                If the resulting alpha is unreachable.
        """

        if not (0 < delta < 1):
            raise ValueError(
                "StableswapImpLoss.calc_iloss_at_delta: delta must "
                "be in (0, 1); got {}".format(delta)
            )
        return self.calc_iloss(1.0 - delta)

    def apply(self):

        """ apply

            Compute IL at the pool's current state.

            Reads dydx from the math pool to derive the implied
            price ratio, then returns IL at that alpha. Useful for
            "what's my IL right now" calls after the pool has seen
            trading activity.

            Returns
            -------
            float
                IL as a fraction. 0.0 at a perfectly-balanced pool.

            Raises
            ------
            DepegUnreachableError
                If the pool's current state implies an alpha past
                the reachability bound. Shouldn't occur for
                self-consistent math_pool states but is theoretically
                possible and caught cleanly.
        """

        # dydx (without fee) gives the marginal ratio at index 0
        # per unit of index 1. For a balanced pool this ~ 1.0; for
        # a depegged pool it drifts from 1.0 by δ.
        dydx = self.lp.math_pool.dydx(0, 1, use_fee = False)
        if dydx <= 0:
            return 0.0

        # In the derivation, δ = 1 - dydx (signed); by symmetry we
        # can take the absolute value to get magnitude.
        delta = abs(1.0 - dydx)
        if delta == 0.0:
            return 0.0

        return self.calc_iloss(1.0 - delta)

    def hold_value(self):

        """ hold_value

            Counterfactual: value if the caller had held their entry
            tokens instead of LPing. Denominated at peg (1:1 across
            assets), so this equals the sum of per-token entry amounts.

            Returns
            -------
            float
                Hold value in peg-numeraire units (== sum of
                per_token_init).
        """

        return sum(self.per_token_init)

    # ─── Internal helpers ──────────────────────────────────────────────

    def _solve_epsilon(self, delta):

        """Fixed-point iteration on ε given δ and self.A.

        Returns ε on convergence, or None if |ε| grew past the
        reachability bound (indicating the caller's δ is too close
        to peg for this high-A pool to accommodate).

        Parameters
        ----------
        delta : float
            Depeg magnitude (positive).

        Returns
        -------
        float or None
            Converged ε, or None if unreachable.
        """

        # Seed with leading-order value.
        epsilon = delta * (self.A + 1) / (2 - delta)

        for _ in range(_FIXED_POINT_MAX_ITER):
            if abs(epsilon) >= _EPSILON_MAX:
                return None
            alpha_A = self.A * (1 - epsilon ** 2) ** 2
            epsilon_new = delta * (alpha_A + 1) / (2 - delta)
            if abs(epsilon_new - epsilon) < _FIXED_POINT_TOL:
                epsilon = epsilon_new
                break
            epsilon = epsilon_new

        # Recheck post-iteration — solution may have grown past the
        # bound in the later iterations.
        if abs(epsilon) >= _EPSILON_MAX:
            return None
        return epsilon

    def _max_reachable_delta(self):

        """Coarse estimate of the largest δ this pool can reach.

        Uses |ε| = 0.94 (just inside the reachability bound) and the
        leading-order relation δ ≈ 2ε / (α_A + 1 + ε) to back out
        the corresponding δ. Only used for error-message enrichment
        on DepegUnreachableError, so approximate is fine.
        """

        eps = 0.94
        alpha_A = self.A * (1 - eps ** 2) ** 2
        # Rearranging δ = 2ε / (α_A + 1 + ε):
        return 2 * eps / (alpha_A + 1 + eps)
