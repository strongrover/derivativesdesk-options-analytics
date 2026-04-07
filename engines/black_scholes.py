"""
engines/black_scholes.py
Black-Scholes-Merton pricing + full analytical Greeks engine.
No UI dependencies - pure math only.
"""

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


class BlackScholes:
    """Full Black-Scholes-Merton pricing and Greeks engine."""

    @staticmethod
    def d1d2(S, K, T, sigma, r, q=0.0):
        """Compute d1 and d2 for BSM formula."""
        if T <= 0 or sigma <= 0:
            return None, None
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2

    @classmethod
    def price(cls, S, K, T, sigma, r, option_type="call", q=0.0):
        """Price a European call or put option."""
        d1, d2 = cls.d1d2(S, K, T, sigma, r, q)
        if d1 is None:
            return max(S - K, 0) if option_type == "call" else max(K - S, 0)
        if option_type == "call":
            return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

    @classmethod
    def greeks(cls, S, K, T, sigma, r, option_type="call", q=0.0, theta_basis=252):
        """
        Compute full set of analytical Greeks including higher-order.
        Convention: vega is quoted per 1% vol move; volga is on the same basis.
        Theta is returned per day on the chosen day-count basis (default 252).
        Returns dict: delta, gamma, theta, vega, rho, vanna, charm, volga.
        """
        d1, d2 = cls.d1d2(S, K, T, sigma, r, q)
        if d1 is None:
            return {g: 0.0 for g in ["delta", "gamma", "theta", "vega", "rho", "vanna", "charm", "volga"]}

        phi = norm.pdf(d1)
        Nd1 = norm.cdf(d1)
        Nd2 = norm.cdf(d2)
        Nd1m = norm.cdf(-d1)
        Nd2m = norm.cdf(-d2)
        sqrtT = np.sqrt(T)

        delta = np.exp(-q * T) * (Nd1 if option_type == "call" else Nd1 - 1)
        gamma = np.exp(-q * T) * phi / (S * sigma * sqrtT)

        theta_call = (
            -np.exp(-q * T) * S * phi * sigma / (2 * sqrtT)
            - r * K * np.exp(-r * T) * Nd2
            + q * S * np.exp(-q * T) * Nd1
        ) / theta_basis
        theta_put = (
            -np.exp(-q * T) * S * phi * sigma / (2 * sqrtT)
            + r * K * np.exp(-r * T) * Nd2m
            - q * S * np.exp(-q * T) * Nd1m
        ) / theta_basis
        theta = theta_call if option_type == "call" else theta_put

        vega = S * np.exp(-q * T) * phi * sqrtT / 100
        rho_call = K * T * np.exp(-r * T) * Nd2 / 100
        rho_put = -K * T * np.exp(-r * T) * Nd2m / 100
        rho = rho_call if option_type == "call" else rho_put

        vanna = -np.exp(-q * T) * phi * d2 / sigma
        A = phi * (2 * (r - q) * T - d2 * sigma * sqrtT) / (2 * T * sigma * sqrtT)
        if option_type == "call":
            charm = -np.exp(-q * T) * (A - q * Nd1)
        else:
            charm = -np.exp(-q * T) * (A + q * Nd1m)
        volga = vega * d1 * d2 / sigma

        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega,
            "rho": rho,
            "vanna": vanna,
            "charm": charm,
            "volga": volga,
        }

    @classmethod
    def implied_vol(cls, market_price, S, K, T, r, option_type="call", q=0.0):
        """Solve for implied volatility via Brent's method."""
        if T <= 0:
            return np.nan
        try:
            intrinsic = max(S - K, 0) if option_type == "call" else max(K - S, 0)
            if market_price <= intrinsic:
                return np.nan
            f = lambda sigma: cls.price(S, K, T, sigma, r, option_type, q) - market_price
            return brentq(f, 1e-6, 10.0, xtol=1e-6, maxiter=500)
        except Exception:
            return np.nan

    @classmethod
    def put_call_parity(cls, S, K, T, sigma, r, q=0.0):
        """
        Verify put-call parity: C - P = S*e^(-qT) - K*e^(-rT)
        Returns (lhs, rhs, difference).
        """
        call_p = cls.price(S, K, T, sigma, r, "call", q)
        put_p = cls.price(S, K, T, sigma, r, "put", q)
        lhs = call_p - put_p
        rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
        return lhs, rhs, abs(lhs - rhs)
