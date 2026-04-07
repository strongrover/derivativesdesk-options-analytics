"""
pages/tabs/tab_risk.py
Tab 03 - Risk & Scenarios
  Section A: Spot x Vol shock P&L heatmap + named stress tests
  Section B: GBM backtest with delta-hedge option, VaR/CVaR stats, P&L histogram

Performance fix:
  The original code had a triple nested Python loop:
    for path in paths:           # n_sims iterations
      for t in range(steps):     # T_days iterations
        BlackScholes.greeks(...)  # scalar BSM call

  At 1000 paths x 90 days = 90,000 individual BSM calls per render.
  This is replaced with fully vectorized numpy BSM applied to the entire
  (n_sims, steps) matrix in one shot — ~100-200x faster.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import norm

from engines import BlackScholes
from utils import C, apply_layout


# ── Vectorized BSM across a 2-D spot matrix ───────────────────────────────────

def _matrix_bsm_call_delta(spots, T_remaining, K, sigma, r, q):
    """
    Compute BSM delta for every (path, timestep) simultaneously.
    spots       : (n_paths, n_steps)  float array
    T_remaining : (n_steps,)          float array — time left at each step
    Returns delta matrix (n_paths, n_steps).
    """
    T_rem = np.maximum(T_remaining, 1e-6)           # (n_steps,)
    sqrtT = np.sqrt(T_rem)
    # broadcast: spots is (n, t), T_rem is (t,)
    d1 = (np.log(spots / K) + (r - q + 0.5 * sigma**2) * T_rem) / (sigma * sqrtT)
    return np.exp(-q * T_rem) * norm.cdf(d1)        # (n_paths, n_steps)


def _matrix_bsm_put_delta(spots, T_remaining, K, sigma, r, q):
    T_rem = np.maximum(T_remaining, 1e-6)
    sqrtT = np.sqrt(T_rem)
    d1 = (np.log(spots / K) + (r - q + 0.5 * sigma**2) * T_rem) / (sigma * sqrtT)
    return np.exp(-q * T_rem) * (norm.cdf(d1) - 1)


def _matrix_bsm_price(spots, T_remaining, K, sigma, r, q, option_type):
    """
    Price BSM for every (path, timestep) simultaneously.
    Returns price matrix (n_paths, n_steps+1).
    """
    T_rem = np.maximum(T_remaining, 1e-6)
    sqrtT = np.sqrt(T_rem)
    d1 = (np.log(spots / K) + (r - q + 0.5 * sigma**2) * T_rem) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT
    if option_type == "call":
        return spots * np.exp(-q * T_rem) * norm.cdf(d1) - K * np.exp(-r * T_rem) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T_rem) * norm.cdf(-d2) - spots * np.exp(-q * T_rem) * norm.cdf(-d1)


@st.cache_data(show_spinner=False)
def _run_backtest(S, K, T_days, sigma, r, q, option_type, ep, quantity, n_sims, bt_seed, hedge):
    """
    Fully vectorized GBM backtest. Cached per unique parameter set.
    Returns (pnl_matrix, final_pnls) where pnl_matrix is (n_sims, T_days+1).
    """
    np.random.seed(int(bt_seed))
    steps = T_days
    dt = 1 / 252
    mu = r - q

    # Generate all paths at once: (n_sims, steps)
    Z = np.random.standard_normal((n_sims, steps))
    log_ret = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
    paths = np.hstack([
        np.full((n_sims, 1), S),
        S * np.exp(np.cumsum(log_ret, axis=1))
    ])  # (n_sims, steps+1)

    # Time-to-expiry at each column: shape (steps+1,)
    T_remaining_vals = np.array([max((T_days - t) / 365, 1e-4) for t in range(steps + 1)])

    # Option value at every path x timestep: (n_sims, steps+1)
    values = _matrix_bsm_price(paths, T_remaining_vals, K, sigma, r, q, option_type)

    if hedge:
        # Delta at hedge points (all steps except final): (n_sims, steps)
        T_rem_hedge = T_remaining_vals[:-1]           # (steps,)
        spots_hedge = paths[:, :-1]                   # (n_sims, steps)

        if option_type == "call":
            deltas = _matrix_bsm_call_delta(spots_hedge, T_rem_hedge, K, sigma, r, q)
        else:
            deltas = _matrix_bsm_put_delta(spots_hedge, T_rem_hedge, K, sigma, r, q)

        # Spot moves: (n_sims, steps)
        dS = np.diff(paths, axis=1)

        # Hedge P&L per step: trading P&L from spot move plus financing cost on inventory
        financing_increments = deltas * spots_hedge * r * dt  # (n_sims, steps)
        hedge_pnl_increments = -deltas * dS - financing_increments  # (n_sims, steps)
        hedge_pnl = np.hstack([
            np.zeros((n_sims, 1)),
            np.cumsum(hedge_pnl_increments, axis=1)
        ])  # (n_sims, steps+1)
    else:
        hedge_pnl = np.zeros_like(values)

    pnl_matrix = (values - ep + hedge_pnl) * quantity * 100
    final_pnls = pnl_matrix[:, -1]

    return pnl_matrix, final_pnls


# ── Main render ───────────────────────────────────────────────────────────────

def render(S, K, T, T_days, sigma, r, q, option_type, ep, quantity):

    # ── Section A: Scenario heatmap ───────────────────────────────────────────
    st.markdown("<div class='section-label'>Scenario Analysis - Spot & Vol Shock Grid</div>", unsafe_allow_html=True)

    col_ctrl, col_heat = st.columns([1, 3])

    with col_ctrl:
        spot_shocks = st.multiselect(
            "Spot shocks (%)", [-30, -20, -15, -10, -5, 0, 5, 10, 15, 20, 30],
            default=[-20, -10, -5, 0, 5, 10, 20],
        )
        vol_shocks = st.multiselect(
            "Vol shocks (%pt)", [-10, -5, -3, 0, 3, 5, 10],
            default=[-5, 0, 5],
        )
        days_fwd = st.slider("Days forward", 0, T_days, 0)

    T_rem = max((T_days - days_fwd) / 365, 0.001)

    with col_heat:
        rows = []
        for vs in vol_shocks:
            row = {"dVol": f"{vs:+d}%pt"}
            for ss in spot_shocks:
                s2 = S * (1 + ss / 100)
                v2 = max(sigma + vs / 100, 0.01)
                p2 = BlackScholes.price(s2, K, T_rem, v2, r, option_type, q)
                pnl = (p2 - ep) * quantity * 100
                row[f"S{ss:+d}%"] = pnl
            rows.append(row)

        df_scen = pd.DataFrame(rows).set_index("dVol")
        colorscale = [
            [0.0, "#8B0000"],
            [0.25, "#FF4C4C"],
            [0.5, "#f4c542"],
            [0.75, "#7CFC00"],
            [1.0, "#00FF00"],
        ]

        fig_heat = go.Figure(data=go.Heatmap(
            z=df_scen.values,
            x=df_scen.columns.tolist(),
            y=df_scen.index.tolist(),
            colorscale=colorscale,
            zmid=0,
            text=[[f"EUR {v:,.0f}" for v in row] for row in df_scen.values],
            texttemplate="%{text}",
            hovertemplate="Spot=%{x}<br>dVol=%{y}<br>P&L=%{text}<extra></extra>",
            colorbar=dict(title="P&L (EUR)", tickfont=dict(color=C["white"])),
        ))
        apply_layout(fig_heat, "P&L Scenario Grid (EUR)", xaxis_title="Spot Shock", yaxis_title="Vol Shock")
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Section A2: Named stress tests ────────────────────────────────────────
    st.markdown("<div class='section-label'>Named Stress Tests</div>", unsafe_allow_html=True)

    stress_scenarios = {
        "Black Monday (-20% spot, +15% vol)": (S * 0.80, sigma + 0.15, r),
        "Tech Crash (-35% spot, +25% vol)":   (S * 0.65, sigma + 0.25, r),
        "Melt-Up Rally (+20% spot, -10% vol)":(S * 1.20, sigma - 0.10, r),
        "Flash Crash (-15% spot, +30% vol)":  (S * 0.85, sigma + 0.30, r),
        "Vol Spike Only (+20% vol)":           (S,        sigma + 0.20, r),
        "Rate Shock (+200bp)":                 (S,        sigma,        r + 0.02),
        "Spot +10% only":                      (S * 1.10, sigma,        r),
        "Spot -10% only":                      (S * 0.90, sigma,        r),
    }

    stress_rows = []
    for label, (s2, v2, r2) in stress_scenarios.items():
        v2 = max(v2, 0.01)
        p2 = BlackScholes.price(s2, K, T, v2, r2, option_type, q)
        pnl = (p2 - ep) * quantity * 100
        g2 = BlackScholes.greeks(s2, K, T, v2, r2, option_type, q)
        stress_rows.append({
            "Scenario": label,
            "Price":    f"EUR {p2:.4f}",
            "P&L":      f"EUR {pnl:+,.0f}",
            "Delta":    f"{g2['delta']:+.4f}",
            "Vega":     f"{g2['vega']:.4f}",
        })

    df_stress = pd.DataFrame(stress_rows).set_index("Scenario")
    st.dataframe(df_stress, use_container_width=True)

    # ── Section B: GBM backtest ───────────────────────────────────────────────
    st.markdown(
        "<div class='section-label' style='margin-top:28px'>GBM Backtest - Simulated Paths</div>",
        unsafe_allow_html=True,
    )

    col_bt_ctrl, col_bt_chart = st.columns([1, 3])

    with col_bt_ctrl:
        n_sims    = st.slider("Simulated paths", 100, 5000, 1000, step=100)
        hedge     = st.checkbox("Approx. daily delta hedge", value=True)
        bt_seed   = st.number_input("Random seed", 42, 9999, 42)
        show_hist = st.checkbox("Show P&L distribution", value=True)
        run_bt    = st.button("▶ Run Simulation", use_container_width=True)

    # Track whether a simulation result exists in session state
    if run_bt:
        with st.spinner("Running backtest..."):
            pnl_matrix, final_pnls = _run_backtest(
                S, K, T_days, sigma, r, q, option_type, ep, quantity,
                n_sims, int(bt_seed), hedge,
            )
        st.session_state["bt_pnl_matrix"]  = pnl_matrix
        st.session_state["bt_final_pnls"]  = final_pnls
        st.session_state["bt_n_sims"]      = n_sims
        st.session_state["bt_hedge"]       = hedge

    # Show results if we have them (from this run or a prior run)
    if "bt_pnl_matrix" not in st.session_state:
        with col_bt_chart:
            st.info("Configure parameters and click **▶ Run Simulation** to start.")
        return

    pnl_matrix  = st.session_state["bt_pnl_matrix"]
    final_pnls  = st.session_state["bt_final_pnls"]
    n_sims      = st.session_state["bt_n_sims"]
    hedge       = st.session_state["bt_hedge"]

    t_axis = np.arange(T_days + 1)
    n_show = min(n_sims, 30)

    with col_bt_chart:
        fig_bt = go.Figure()
        for i in range(n_show):
            pnl_path = pnl_matrix[i]
            color = "rgba(34,197,94,0.10)" if pnl_path[-1] >= 0 else "rgba(239,68,68,0.10)"
            fig_bt.add_trace(go.Scatter(
                x=t_axis, y=pnl_path,
                mode="lines",
                line=dict(width=0.8, color=color),
                showlegend=False,
            ))

        mean_pnl = pnl_matrix.mean(axis=0)
        fig_bt.add_trace(go.Scatter(
            x=t_axis, y=mean_pnl,
            mode="lines",
            line=dict(width=2.5, color=C["gold"]),
            name="Mean path",
        ))
        fig_bt.add_hline(y=0, line_color="rgba(255,255,255,0.15)")
        apply_layout(
            fig_bt,
            f"P&L Evolution - {n_sims} Paths ({'Delta-Hedged' if hedge else 'Unhedged'})",
            xaxis_title="Days",
            yaxis_title="P&L (EUR)",
        )
        st.plotly_chart(fig_bt, use_container_width=True)

    if show_hist:
        pnl_arr = final_pnls
        var_95  = np.percentile(pnl_arr, 5)
        var_99  = np.percentile(pnl_arr, 1)
        cvar_95 = pnl_arr[pnl_arr <= var_95].mean()
        win_rate= (pnl_arr > 0).mean() * 100

        col_stats, col_hist = st.columns([1, 2])

        with col_stats:
            st.markdown(
                f"""
            <div class='card-box' style='font-family:JetBrains Mono,monospace;font-size:12px'>
              <div style='color:#4a6a8a;font-size:9px;letter-spacing:2px;
                          text-transform:uppercase;margin-bottom:12px'>Backtest Statistics</div>
              <div style='display:grid;gap:10px'>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Mean P&L</div>
                     <div style='color:#ddd'>EUR {pnl_arr.mean():+,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Median P&L</div>
                     <div style='color:#ddd'>EUR {float(np.median(pnl_arr)):+,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Std Dev</div>
                     <div style='color:#ddd'>EUR {pnl_arr.std():,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>VaR 95%</div>
                     <div style='color:#c87e7e'>EUR {var_95:,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>VaR 99%</div>
                     <div style='color:#c87e7e'>EUR {var_99:,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>CVaR 95%</div>
                     <div style='color:#c87e7e'>EUR {cvar_95:,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Win Rate</div>
                     <div style='color:#7ec8a0'>{win_rate:.1f}%</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Max Loss</div>
                     <div style='color:#c87e7e'>EUR {pnl_arr.min():,.0f}</div></div>
                <div><div style='color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px'>Max Gain</div>
                     <div style='color:#7ec8a0'>EUR {pnl_arr.max():,.0f}</div></div>
              </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col_hist:
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=pnl_arr, nbinsx=60,
                marker_color=C["amber"], opacity=0.75,
                hovertemplate="P&L=EUR %{x:,.0f}<br>Count=%{y}<extra></extra>",
            ))
            fig_hist.add_vline(x=0, line_color="rgba(255,255,255,0.4)", line_dash="dash")
            fig_hist.add_vline(x=var_95, line_color=C["red"], line_dash="dot",
                               annotation_text="VaR 95%", annotation_font_color=C["red"])
            fig_hist.add_vline(x=var_99, line_color=C["red"], line_dash="dash",
                               annotation_text="VaR 99%", annotation_font_color=C["red"])
            apply_layout(fig_hist, "P&L Distribution", xaxis_title="Final P&L (EUR)", yaxis_title="Frequency")
            st.plotly_chart(fig_hist, use_container_width=True)
