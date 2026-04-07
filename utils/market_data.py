"""
utils/market_data.py
Live market data fetching from Yahoo Finance with graceful fallback.
All Streamlit caching lives here so pages stay clean.
"""

import numpy as np
import streamlit as st
import yfinance as yf


CAC40_META = {
    "LVMH (MC.PA)": {"ticker": "MC.PA", "sector": "Luxury", "fallback_S": 658.2, "fallback_sigma": 0.238},
    "TotalEnergies (TTE.PA)": {"ticker": "TTE.PA", "sector": "Energy", "fallback_S": 61.4, "fallback_sigma": 0.213},
    "Hermes (RMS.PA)": {"ticker": "RMS.PA", "sector": "Luxury", "fallback_S": 2105.0, "fallback_sigma": 0.255},
    "Sanofi (SAN.PA)": {"ticker": "SAN.PA", "sector": "Healthcare", "fallback_S": 91.3, "fallback_sigma": 0.198},
    "Airbus (AIR.PA)": {"ticker": "AIR.PA", "sector": "Aerospace", "fallback_S": 166.5, "fallback_sigma": 0.268},
    "Schneider Electric (SU.PA)": {"ticker": "SU.PA", "sector": "Industrials", "fallback_S": 233.8, "fallback_sigma": 0.224},
    "L'Oreal (OR.PA)": {"ticker": "OR.PA", "sector": "Consumer", "fallback_S": 375.5, "fallback_sigma": 0.207},
    "BNP Paribas (BNP.PA)": {"ticker": "BNP.PA", "sector": "Banking", "fallback_S": 68.2, "fallback_sigma": 0.279},
    "Stellantis (STLAM.PA)": {"ticker": "STLAM.PA", "sector": "Automotive", "fallback_S": 14.1, "fallback_sigma": 0.312},
    "Safran (SAF.PA)": {"ticker": "SAF.PA", "sector": "Aerospace", "fallback_S": 242.6, "fallback_sigma": 0.231},
}


@st.cache_data(ttl=300)
def fetch_live_data(ticker_symbol: str) -> dict | None:
    """
    Fetch live spot, daily change, and 30-day realised vol from Yahoo Finance.
    Cached for 5 minutes. Returns None on any failure.
    """
    try:
        tkr = yf.Ticker(ticker_symbol)
        hist = tkr.history(period="60d", interval="1d", auto_adjust=True)
        if hist.empty or len(hist) < 5:
            return None

        spot = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        change_pct = (spot - prev) / prev * 100

        log_rets = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
        sigma = float(log_rets.tail(30).std() * np.sqrt(252))

        info = tkr.fast_info
        currency = getattr(info, "currency", "EUR")
        last_updated = hist.index[-1].strftime("%Y-%m-%d %H:%M UTC")

        return {
            "S": spot,
            "sigma": max(sigma, 0.05),
            "change_pct": change_pct,
            "currency": currency,
            "last_updated": last_updated,
            "source": "live",
        }
    except Exception:
        return None


def get_ticker_data(name: str) -> dict:
    """Return live data for a ticker, falling back to hardcoded values."""
    meta = CAC40_META[name]
    live = fetch_live_data(meta["ticker"])
    if live:
        live["sector"] = meta["sector"]
        return live
    return {
        "S": meta["fallback_S"],
        "sigma": meta["fallback_sigma"],
        "sector": meta["sector"],
        "change_pct": 0.0,
        "currency": "EUR",
        "last_updated": "offline (cached)",
        "source": "fallback",
    }


@st.cache_data(ttl=300)
def build_ticker_table() -> dict:
    """Build the full CAC 40 ticker table. Cached for 5 minutes."""
    return {name: get_ticker_data(name) for name in CAC40_META}
