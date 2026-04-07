import os
import sys

import numpy as np
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines import BlackScholes
from pages.tabs import tab_exotics, tab_payoff_vol, tab_pricer, tab_risk
from utils import build_ticker_table, inject_styles


st.set_page_config(
    page_title="QuantDesk - Options Analytics",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

CAC40_TICKERS = build_ticker_table()

with st.sidebar:
    st.markdown("<div class='sidebar-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-kicker'>Derivatives Pricer - Parameters</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section'>01 - Underlying</div>", unsafe_allow_html=True)

    selected_ticker = st.selectbox(
        "CAC 40 Underlying",
        list(CAC40_TICKERS.keys()),
        label_visibility="collapsed",
    )
    ticker_data = CAC40_TICKERS[selected_ticker]

    is_live = ticker_data.get("source") == "live"
    change_pct = ticker_data.get("change_pct", 0.0)
    last_updated = ticker_data.get("last_updated", "-")
    change_color = "#22c55e" if change_pct >= 0 else "#ef4444"
    source_label = "LIVE - Yahoo Finance" if is_live else "OFFLINE - Cached"
    dot_color = "#22c55e" if is_live else "#6b7280"

    st.markdown(
        f"""
    <div class='sidebar-status'>
      <div class='sidebar-status-top'>
        <span style='display:inline-block;width:6px;height:6px;border-radius:50%;
                     background:{dot_color};margin-right:6px;vertical-align:middle'></span>
        {source_label}
      </div>
      <div class='sidebar-status-mid' style='color:{change_color}'>Day Delta: {change_pct:+.2f}%</div>
      <div class='sidebar-status-bot'>{last_updated}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    S = st.number_input("Spot Price (S)", value=float(ticker_data["S"]), step=0.5, format="%.2f")
    K = st.number_input("Strike Price (K)", value=float(round(ticker_data["S"] * 1.02, 0)), step=0.5, format="%.2f")

    st.markdown("<div class='sidebar-section'>02 - Option</div>", unsafe_allow_html=True)

    T_days = st.slider("Days to Expiry", 1, 730, 90)
    T = T_days / 365.0
    sigma = st.slider("Implied Vol (%)", 5.0, 100.0, float(ticker_data["sigma"] * 100), step=0.5) / 100.0
    r = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 3.5, step=0.05) / 100.0
    q = st.slider("Dividend Yield (%)", 0.0, 8.0, 1.5, step=0.1) / 100.0
    option_type = st.radio("Type", ["call", "put"], horizontal=True)

    st.markdown("<div class='sidebar-section'>03 - Position & Exotics</div>", unsafe_allow_html=True)

    quantity = st.number_input("Contracts (x100)", value=10, min_value=1, step=1)
    entry_price = st.number_input(
        "Entry Price (paid)",
        value=0.0,
        step=0.1,
        format="%.3f",
        help="Leave 0 to use the current theoretical price",
    )

    with st.expander("Phoenix Parameters", expanded=False):
        coupon_rate = st.slider("Annual Coupon (%)", 2.0, 20.0, 8.0, step=0.5) / 100.0
        call_barrier_pct = st.slider("Call Barrier (%)", 90, 110, 100, step=1)
        put_barrier_pct = st.slider("Put Barrier (%)", 50, 90, 70, step=1)
        n_mc = st.select_slider("MC Paths", [5000, 10000, 20000, 50000], value=20000)

    st.markdown("<div class='qd-divider'></div>", unsafe_allow_html=True)
    if st.button("Refresh Market Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

bs_price = BlackScholes.price(S, K, T, sigma, r, option_type, q)
greeks = BlackScholes.greeks(S, K, T, sigma, r, option_type, q)
vol_spread = (sigma - ticker_data["sigma"]) * 100
ep = entry_price if entry_price > 0 else bs_price

intrinsic = max(S - K, 0) if option_type == "call" else max(K - S, 0)
time_value = bs_price - intrinsic
moneyness_ratio = S / K

if 0.99 <= moneyness_ratio <= 1.01:
    moneyness_label = "ATM"
    moneyness_color = "amber"
elif (moneyness_ratio > 1 and option_type == "call") or (moneyness_ratio < 1 and option_type == "put"):
    moneyness_label = "ITM"
    moneyness_color = "pos"
else:
    moneyness_label = "OTM"
    moneyness_color = "neg"

breakeven = K + bs_price if option_type == "call" else K - bs_price
move_req = abs(breakeven - S) / S * 100
move_1sd = sigma * 100 * np.sqrt(T)
realistic = "within" if move_req < move_1sd else "outside"

st.markdown(
    f"""
<div class='header-strip'>
  <div class='header-hero'>Derivatives Pricer</div>
  <div class='header-summary'>
    <div class='header-name'>
      {selected_ticker.split("(")[0].strip()} | {option_type.upper()}
    </div>
    <div class='header-right'>
      Spot: <span class='header-spot-value'>EUR {S:,.2f}</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

col_price, col_greeks = st.columns([1.05, 2.95], gap="large")

with col_price:
    st.markdown(
        f"""
    <div class='price-panel'>
      <div class='qd-label'>Fair Value</div>
      <div style='height:8px'></div>
      <div class='price-main'><span class='price-currency'>EUR</span>{bs_price:.4f}</div>
      <div class='price-subline'>
        <div class='price-subitem'>
          <span class='price-subitem-label'>Intrinsic Price</span>
          <span class='price-subitem-value'>EUR {intrinsic:.4f}</span>
        </div>
        <div class='price-subitem'>
          <span class='price-subitem-label'>Time Value</span>
          <span class='price-subitem-value'>EUR {time_value:.4f}</span>
        </div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col_greeks:
    st.markdown(
        f"""
    <div class='stat-row'>
      <div class='stat-item'>
        <span class='stat-label'>Delta</span>
        <span class='stat-value amber'>{greeks['delta']:+.4f}</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Gamma</span>
        <span class='stat-value'>{greeks['gamma']:.5f}</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Theta / day (252)</span>
        <span class='stat-value neg'>{greeks['theta']:.4f}</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Vega / 1%</span>
        <span class='stat-value'>{greeks['vega']:.4f}</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Rho / 1%</span>
        <span class='stat-value'>{greeks['rho']:.4f}</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Vol Spread</span>
        <span class='stat-value {'pos' if vol_spread > 0 else 'neg'}'>{vol_spread:+.1f}%</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Realised Vol</span>
        <span class='stat-value'>{ticker_data['sigma']*100:.1f}%</span>
      </div>
      <div class='stat-item'>
        <span class='stat-label'>Moneyness</span>
        <span class='stat-value {moneyness_color}'>{moneyness_label} ({moneyness_ratio:.2f}x)</span>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
<div class='insight-box'>
  Break-even at <strong>EUR {breakeven:,.2f}</strong> -
  requires a <strong>{move_req:.1f}% move</strong> in {T_days} days.
  At {sigma*100:.1f}% vol a 1 std-dev move is <strong>{move_1sd:.1f}%</strong> -
  break-even is <strong>{realistic} one standard deviation</strong>.
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height: 4px'></div>", unsafe_allow_html=True)

section_labels = [
    "01 - Pricer & Greeks",
    "02 - Payoff & Vol",
    "03 - Risk & Scenarios",
    "04 - Exotics",
]
active_section = st.radio(
    "Section",
    section_labels,
    horizontal=True,
    label_visibility="collapsed",
)

if active_section == "01 - Pricer & Greeks":
    tab_pricer.render(S, K, T, T_days, sigma, r, q, option_type)
elif active_section == "02 - Payoff & Vol":
    tab_payoff_vol.render(
        S, K, T, T_days, sigma, r, q, option_type, ep, quantity,
    )
elif active_section == "03 - Risk & Scenarios":
    tab_risk.render(S, K, T, T_days, sigma, r, q, option_type, ep, quantity)
else:
    tab_exotics.render(
        S, K, T, sigma, r, q, option_type,
        coupon_rate, call_barrier_pct, put_barrier_pct, n_mc
    )

st.markdown("<hr style='margin:30px 0 10px'>", unsafe_allow_html=True)
st.markdown(
    """
<div class='qd-footer'>
  QUANTDESK - OPTIONS ANALYTICS - BLACK-SCHOLES - MONTE CARLO - CAC 40 - FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY
</div>
""",
    unsafe_allow_html=True,
)
