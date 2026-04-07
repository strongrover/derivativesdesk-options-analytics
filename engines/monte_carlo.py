"""
engines/monte_carlo.py
Monte Carlo pricing engine.
Currently implements: PhoenixOption (autocall), DigitalOption (cash-or-nothing).
Barrier options and TARF to be added in Phase 2.
"""

import numpy as np
from scipy.stats import norm


class PhoenixOption:
    """
    Autocall Phoenix Note - Monte Carlo pricing.

    Structure:
    - Quarterly (or configurable) observation dates.
    - If spot >= call_barrier * K on an observation date: note is autocalled,
      investor receives capital + accrued coupon.
    - If spot >= put_barrier * K (but below call barrier): investor receives
      periodic coupon only.
    - At maturity if not called:
        - spot >= put_barrier * K -> full capital returned
        - spot < put_barrier * K -> capital at risk (receives spot value)
    """

    @staticmethod
    def price(S, K, T, sigma, r, q=0.0, coupon_rate=0.08, call_barrier=1.0, put_barrier=0.7, obs_freq=4, n_paths=20_000, seed=42):
        """
        Price the Phoenix via GBM Monte Carlo.

        Returns
        -------
        (price, std_error) : tuple[float, float]
        """
        if T <= 0:
            return 0.0, 0.0

        np.random.seed(seed)
        steps = max(int(np.ceil(obs_freq * T)), 1)
        dt = T / steps
        t_obs = np.linspace(dt, T, steps)

        Z = np.random.standard_normal((n_paths, steps))
        log_returns = (r - q - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
        S_paths = S * np.exp(np.cumsum(log_returns, axis=1))

        payoffs = np.zeros(n_paths)
        alive = np.ones(n_paths, dtype=bool)
        coupon_per_period = coupon_rate * K / obs_freq
        missed_coupons = np.zeros(n_paths)

        for i, t in enumerate(t_obs):
            n_periods = i + 1
            spot = S_paths[:, i]

            called = alive & (spot >= call_barrier * K)
            # Accrued autocall coupon is based on completed coupon periods, not raw elapsed years.
            payoffs[called] += (K + coupon_rate * K * n_periods / obs_freq) * np.exp(-r * t)
            missed_coupons[called] = 0.0
            alive[called] = False

            # Current coupon payment for alive paths at/above coupon barrier, with memory settlement
            coupon_paid = alive & (spot >= put_barrier * K)
            coupons_due = 1.0 + missed_coupons[coupon_paid]
            payoffs[coupon_paid] += coupons_due * coupon_per_period * np.exp(-r * t)
            missed_coupons[coupon_paid] = 0.0

            # Missed coupon accumulation for alive paths below coupon barrier
            missed_now = alive & (spot < put_barrier * K)
            missed_coupons[missed_now] += 1.0

        final = S_paths[:, -1]
        above = alive & (final >= put_barrier * K)
        below = alive & (final < put_barrier * K)
        # Maturity memory convention: if above barrier and still alive, settle outstanding coupons + capital
        payoffs[above] += (K + missed_coupons[above] * coupon_per_period) * np.exp(-r * T)
        payoffs[below] += final[below] * np.exp(-r * T)

        return float(np.mean(payoffs)), float(np.std(payoffs) / np.sqrt(n_paths))


class DigitalOption:
    """
    Cash-or-nothing digital option (analytical BSM).

    Pays 1 unit at expiry if:
    - Call: S_T > K
    - Put:  S_T < K
    The price is therefore the risk-neutral probability of finishing ITM,
    discounted at the risk-free rate.
    """

    @staticmethod
    def price(S, K, T, sigma, r, option_type="call", q=0.0):
        """
        Price a cash-or-nothing digital.

        Returns probability x discount factor (i.e. the option's fair value
        for a 1-unit payout).
        """
        if T <= 0 or sigma <= 0:
            return 0.0
        d2 = (np.log(S / K) + (r - q - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == "call":
            return float(np.exp(-r * T) * norm.cdf(d2))
        return float(np.exp(-r * T) * norm.cdf(-d2))
