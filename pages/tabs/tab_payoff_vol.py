"""
pages/tabs/tab_payoff_vol.py
Tab 02 - Payoff & Vol Surface
  Row 1: P&L payoff profiles (today / halfway / expiry) + greek vs time to expiry
  Row 2: Price vs volatility curve
  Row 3: Interactive vol surface (3D or heatmap) + vol smile slice
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from engines import BlackScholes
from utils import C, PLOTLY_LAYOUT, PLOTLY_SCENE, apply_layout


def render(S, K, T, T_days, sigma, r, q, option_type, ep, quantity):
    col1, col2 = st.columns(2)
    spot_range = np.linspace(S * 0.60, S * 1.40, 200)

    with col1:
        st.markdown("<div class='section-label'>P&L Payoff Profiles</div>", unsafe_allow_html=True)

        def pnl_at_T(t_val):
            return np.array([
                BlackScholes.price(s, K, t_val, sigma, r, option_type, q) - ep
                for s in spot_range
            ]) * quantity * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spot_range, y=pnl_at_T(T), name="Today", line=dict(color=C["amber"], width=2)))
        fig.add_trace(go.Scatter(x=spot_range, y=pnl_at_T(T / 2), name="Halfway", line=dict(color=C["gold"], width=1.5, dash="dot")))
        fig.add_trace(go.Scatter(x=spot_range, y=pnl_at_T(0.0001), name="Expiry", line=dict(color=C["coral"], width=2.5)))
        fig.add_hline(y=0, line_color="rgba(255,255,255,0.15)", line_dash="dash")
        fig.add_vline(x=K, line_color=C["gold"], line_dash="dash", annotation_text="Strike", annotation_position="top right")
        fig.add_vline(x=S, line_color=C["green"], line_dash="dash", annotation_text="Spot", annotation_position="bottom left")
        apply_layout(fig, "P&L by Spot (EUR)", yaxis_title="P&L (EUR)", xaxis_title="Spot Price (EUR)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-label'>Greek vs Time to Expiry</div>", unsafe_allow_html=True)

        greek_time = st.selectbox("Greek", ["delta", "gamma", "theta", "vega"], key="tab2_greek")
        T_range = np.linspace(1 / 365, max(T, 30 / 365), 120)
        vals_t = [BlackScholes.greeks(S, K, t, sigma, r, option_type, q)[greek_time] for t in T_range]

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=T_range * 365,
            y=vals_t,
            mode="lines",
            line=dict(color=C["coral"], width=2),
            fill="tozeroy",
            fillcolor="rgba(255,127,80,0.08)",
        ))
        fig2.add_vline(x=T_days, line_dash="dash", line_color=C["amber"], annotation_text="Now")
        apply_layout(fig2, f"{greek_time.capitalize()} vs Days to Expiry", xaxis_title="Days to Expiry")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-label'>Option Price vs Volatility</div>", unsafe_allow_html=True)

    vol_range = np.linspace(0.05, 1.0, 150)
    prices_vol = [BlackScholes.price(S, K, T, v, r, option_type, q) for v in vol_range]

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=vol_range * 100,
        y=prices_vol,
        mode="lines",
        line=dict(color=C["green"], width=2),
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.08)",
        hovertemplate="Vol=%{x:.1f}%<br>Price=EUR %{y:.4f}<extra></extra>",
    ))
    fig3.add_vline(x=sigma * 100, line_dash="dash", line_color=C["gold"], annotation_text=f"Current {sigma*100:.1f}%")
    apply_layout(fig3, "Option Price vs Implied Volatility", xaxis_title="Implied Vol (%)", yaxis_title="Price (EUR)")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div class='section-label'>Implied Volatility Surface</div>", unsafe_allow_html=True)

    c_ctrl, c_chart = st.columns([1, 3])
    with c_ctrl:
        smile_type = st.selectbox("Surface model", ["Parametric Smile", "Skew Only", "Flat"])
        show_2d = st.checkbox("2D heatmap", value=False)

    strikes_pct = np.linspace(0.70, 1.30, 25)
    expiries_d = np.array([7, 14, 30, 60, 90, 120, 180, 270, 365])
    IV_surface = np.zeros((len(expiries_d), len(strikes_pct)))

    for j, t_d in enumerate(expiries_d):
        t_yr = t_d / 365
        for i, k_pct in enumerate(strikes_pct):
            m = k_pct - 1
            skew = -0.04 * m / max(np.sqrt(t_yr), 0.05)
            smile = 0.03 * m ** 2
            term = 0.01 * np.sqrt(t_yr)
            noise = np.random.default_rng(hash((j, i)) % (2 ** 32)).normal(0, 0.003)

            if smile_type == "Flat":
                IV_surface[j, i] = sigma
            elif smile_type == "Skew Only":
                IV_surface[j, i] = max(0.01, sigma + skew + term + noise)
            else:
                IV_surface[j, i] = max(0.01, sigma + skew + smile + term + noise)

    with c_chart:
        if show_2d:
            fig_vol = go.Figure(data=go.Heatmap(
                z=IV_surface * 100,
                x=[f"{k:.0f}%" for k in strikes_pct * 100],
                y=[f"{d}d" for d in expiries_d],
                colorscale=[[0.0, "#1f1f1f"], [0.35, C["blue"]], [0.65, C["amber"]], [0.85, C["gold"]], [1.0, C["red"]]],
                hovertemplate="Strike=%{x}<br>Expiry=%{y}<br>IV=%{z:.1f}%<extra></extra>",
                colorbar=dict(title="IV (%)", tickfont=dict(color=C["white"])),
            ))
            apply_layout(fig_vol, "Implied Volatility Surface (Heatmap)", xaxis_title="Strike (%)", yaxis_title="Expiry")
        else:
            fig_vol = go.Figure(data=go.Surface(
                z=IV_surface * 100,
                x=strikes_pct * 100,
                y=expiries_d,
                colorscale=[[0.0, "#1f1f1f"], [0.25, C["blue"]], [0.5, C["amber"]], [0.75, C["gold"]], [1.0, C["red"]]],
                hovertemplate="Strike=%{x:.0f}%<br>T=%{y}d<br>IV=%{z:.1f}%<extra></extra>",
                contours_z=dict(show=True, usecolormap=True, highlightcolor=C["amber"], project_z=True),
                opacity=0.88,
            ))
            fig_vol.update_layout(**PLOTLY_LAYOUT, scene=PLOTLY_SCENE, height=520)

        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("<div class='section-label'>Vol Smile - Current Expiry</div>", unsafe_allow_html=True)
    idx = np.argmin(np.abs(expiries_d - T_days))
    smile_vols = IV_surface[idx, :]

    fig_smile = go.Figure()
    fig_smile.add_trace(go.Scatter(
        x=strikes_pct * 100,
        y=smile_vols * 100,
        mode="lines+markers",
        line=dict(color=C["coral"], width=2.5),
        marker=dict(color=C["coral"], size=5),
        hovertemplate="Strike=%{x:.0f}%<br>IV=%{y:.2f}%<extra></extra>",
    ))
    fig_smile.add_vline(x=100, line_dash="dash", line_color=C["amber"], annotation_text="ATM")
    apply_layout(fig_smile, f"Vol Smile - {expiries_d[idx]}d Expiry", xaxis_title="Strike (% of Spot)", yaxis_title="Implied Vol (%)")
    st.plotly_chart(fig_smile, use_container_width=True)
