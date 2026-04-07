"""
pages/tabs/tab_pricer.py
Tab 01 - Pricer & Greeks
  Left:  call/put comparison table, put-call parity
  Right: Greek sensitivity vs spot ladder
  Below: full Greeks ladder across all CAC 40 tickers
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engines import BlackScholes
from utils import apply_layout, build_ticker_table, C


def render(S, K, T, T_days, sigma, r, q, option_type):

    col_left, col_right = st.columns([1, 1])

    # LEFT: Comparison table + parity check
    with col_left:
        st.markdown("<div class='section-label'>Call vs Put Comparison</div>", unsafe_allow_html=True)

        call_p = BlackScholes.price(S, K, T, sigma, r, "call", q)
        put_p = BlackScholes.price(S, K, T, sigma, r, "put", q)
        call_g = BlackScholes.greeks(S, K, T, sigma, r, "call", q)
        put_g = BlackScholes.greeks(S, K, T, sigma, r, "put", q)

        df_compare = pd.DataFrame({
            "Metric": ["Price", "Delta", "Gamma", "Theta / day (252)", "Vega", "Rho", "Vanna", "Volga"],
            "Call": [
                f"EUR {call_p:.4f}", f"{call_g['delta']:+.4f}", f"{call_g['gamma']:.5f}",
                f"{call_g['theta']:.4f}", f"{call_g['vega']:.4f}", f"{call_g['rho']:.4f}",
                f"{call_g['vanna']:.4f}", f"{call_g['volga']:.4f}",
            ],
            "Put": [
                f"EUR {put_p:.4f}", f"{put_g['delta']:+.4f}", f"{put_g['gamma']:.5f}",
                f"{put_g['theta']:.4f}", f"{put_g['vega']:.4f}", f"{put_g['rho']:.4f}",
                f"{put_g['vanna']:.4f}", f"{put_g['volga']:.4f}",
            ],
        }).set_index("Metric")
        st.dataframe(df_compare, use_container_width=True)

        lhs, rhs, diff = BlackScholes.put_call_parity(S, K, T, sigma, r, q)
        st.info(
            f"**Put-Call Parity** - C - P = {lhs:.4f} - "
            f"S*e^(-qT) - K*e^(-rT) = {rhs:.4f} - Diff = {diff:.6f}"
        )

    # RIGHT: Greek vs spot ladder
    with col_right:
        st.markdown("<div class='section-label'>Greek Sensitivity - Spot Ladder</div>", unsafe_allow_html=True)

        greek_sel = st.selectbox("Select Greek", ["delta", "gamma", "theta", "vega", "rho"], key="pricer_greek")
        spot_range = np.linspace(S * 0.70, S * 1.30, 120)
        vals = [BlackScholes.greeks(s, K, T, sigma, r, option_type, q)[greek_sel] for s in spot_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=spot_range,
            y=vals,
            mode="lines",
            line=dict(color=C["amber"], width=2),
            fill="tozeroy",
            fillcolor="rgba(244,197,66,0.08)",
            name=greek_sel.capitalize(),
            hovertemplate=f"S=EUR %{{x:.2f}}<br>{greek_sel}=%{{y:.5f}}<extra></extra>",
        ))
        fig.add_vline(
            x=S,
            line_dash="dash",
            line_color=C["green"],
            annotation_text="Spot",
            annotation_font_color="#7ec8a0",
            annotation_position="bottom left",
        )
        fig.add_vline(
            x=K,
            line_dash="dash",
            line_color=C["gold"],
            annotation_text="Strike",
            annotation_font_color="#d4c27a",
            annotation_position="top right",
        )
        apply_layout(fig, title=f"{greek_sel.capitalize()} vs Spot")
        st.plotly_chart(fig, use_container_width=True)

    # BELOW: Full Greeks ladder across all CAC 40 tickers
    st.markdown(
        "<div class='section-label' style='margin-top:20px'>Greeks Ladder - All CAC 40 Underlyings</div>",
        unsafe_allow_html=True,
    )

    CAC40_TICKERS = build_ticker_table()
    rows = []
    for name, data in CAC40_TICKERS.items():
        s_ = data["S"]
        k_ = round(s_ * 1.02, 1)
        p_ = BlackScholes.price(s_, k_, T, data["sigma"], r, option_type, q)
        g_ = BlackScholes.greeks(s_, k_, T, data["sigma"], r, option_type, q)
        rows.append({
            "Ticker": name.split("(")[0].strip(),
            "Spot": f"EUR {s_:,.2f}",
            "Strike": f"EUR {k_:,.1f}",
            "Vol": f"{data['sigma'] * 100:.1f}%",
            "Price": f"EUR {p_:.4f}",
            "Delta": f"{g_['delta']:+.4f}",
            "Gamma": f"{g_['gamma']:.5f}",
            "Theta / day (252)": f"{g_['theta']:.4f}",
            "Vega": f"{g_['vega']:.4f}",
            "Rho": f"{g_['rho']:.4f}",
            "Vanna": f"{g_['vanna']:.4f}",
            "Volga": f"{g_['volga']:.4f}",
        })

    df_all = pd.DataFrame(rows).set_index("Ticker")
    st.dataframe(df_all, use_container_width=True, height=380)

