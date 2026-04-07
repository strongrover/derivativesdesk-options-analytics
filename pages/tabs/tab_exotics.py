"""
pages/tabs/tab_exotics.py
Tab 04 - Exotic Products
  Left:  Phoenix Autocall (Monte Carlo) with coupon sensitivity chart
  Right: Digital (Cash-or-Nothing) with strike range chart + vanilla comparison

Performance fixes:
  - Phoenix main price cached via st.cache_data (keyed on all params)
  - Coupon sweep cached separately — 20x MC calls no longer re-run on every render
  - Digital/vanilla curves vectorized with scipy.stats.norm directly (no Python loop)
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import norm

from engines import BlackScholes, DigitalOption, PhoenixOption
from utils import C, apply_layout


# ── Cached pricers ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _cached_phoenix_price(S, K, T, sigma, r, q, coupon_rate, call_barrier, put_barrier, n_paths):
    return PhoenixOption.price(
        S=S, K=K, T=T, sigma=sigma, r=r, q=q,
        coupon_rate=coupon_rate,
        call_barrier=call_barrier,
        put_barrier=put_barrier,
        n_paths=n_paths,
    )


@st.cache_data(ttl=300, show_spinner=False)
def _cached_coupon_sweep(S, K, T, sigma, r, q, call_barrier, put_barrier):
    """Run the 20-point coupon sensitivity sweep once and cache it."""
    coupons = np.linspace(0.02, 0.20, 20)
    prices = [
        PhoenixOption.price(
            S, K, T, sigma, r, q, c,
            call_barrier, put_barrier,
            n_paths=5_000,
        )[0]
        for c in coupons
    ]
    return coupons, np.array(prices)


# ── Vectorized digital curves (no Python loop) ────────────────────────────────

def _digital_vs_strike(S, sigma, T, r, q, n=100):
    """Return (k_range, dig_call_arr, dig_put_arr) — fully vectorized."""
    k_range = np.linspace(S * 0.70, S * 1.30, n)
    d2 = (np.log(S / k_range) + (r - q - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    disc = np.exp(-r * T)
    dig_c = disc * norm.cdf(d2)
    dig_p = disc * norm.cdf(-d2)
    return k_range, dig_c, dig_p


def _vanilla_vs_digital_spot(K, sigma, T, r, q, S_center, n=100):
    """Return (s_rng, vanilla_call, digital_call_x_K) — fully vectorized."""
    s_rng = np.linspace(S_center * 0.70, S_center * 1.30, n)
    # Vectorized BSM call
    with np.errstate(divide="ignore", invalid="ignore"):
        sqrtT = np.sqrt(T)
        d1 = (np.log(s_rng / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * sqrtT)
        d2 = d1 - sigma * sqrtT
        vanilla = s_rng * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        d2_dig = (np.log(s_rng / K) + (r - q - 0.5 * sigma ** 2) * T) / (sigma * sqrtT)
        digital_xK = np.exp(-r * T) * norm.cdf(d2_dig) * K
    return s_rng, vanilla, digital_xK


# ── Main render ───────────────────────────────────────────────────────────────

def render(S, K, T, sigma, r, q, option_type, coupon_rate, call_barrier_pct, put_barrier_pct, n_mc):
    col1, col2 = st.columns(2)

    # ── LEFT: Phoenix ─────────────────────────────────────────────────────────
    with col1:
        st.markdown("<div class='section-label'>Phoenix Autocall Note - Monte Carlo</div>", unsafe_allow_html=True)

        with st.spinner("Pricing Phoenix..."):
            ph_price, ph_stderr = _cached_phoenix_price(
                S, K, T, sigma, r, q,
                coupon_rate,
                call_barrier_pct / 100,
                put_barrier_pct / 100,
                n_mc,
            )

        ci_lo = ph_price - 1.96 * ph_stderr
        ci_hi = ph_price + 1.96 * ph_stderr

        st.markdown(
            f"""
        <div class='card-box'>
          <div style='font-family:JetBrains Mono,monospace;font-size:9px;color:#4a6a8a;
                      letter-spacing:2px;text-transform:uppercase;margin-bottom:10px'>
            Phoenix Autocall
          </div>
          <div class='price-main'><span class='price-currency'>EUR</span>{ph_price:.4f}</div>
          <div style='font-family:JetBrains Mono,monospace;font-size:10px;color:#444;margin-top:8px'>
            95% CI: [EUR {ci_lo:.4f}, EUR {ci_hi:.4f}] - SE = {ph_stderr:.4f}
          </div>
          <div style='margin-top:14px;display:grid;grid-template-columns:1fr 1fr;
                      gap:10px;font-family:JetBrains Mono,monospace;font-size:11px'>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>Coupon p.a.</div>
              <div style='color:#ddd'>{coupon_rate*100:.1f}%</div>
            </div>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>MC Paths</div>
              <div style='color:#ddd'>{n_mc:,}</div>
            </div>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>Call Barrier</div>
              <div style='color:#7ec8a0'>{call_barrier_pct}% of K</div>
            </div>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>Put Barrier</div>
              <div style='color:#c87e7e'>{put_barrier_pct}% of K</div>
            </div>
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Coupon sweep — cached, runs once per unique param combination
        with st.spinner("Building coupon sensitivity..."):
            coupons, ph_sweep = _cached_coupon_sweep(
                S, K, T, sigma, r, q,
                call_barrier_pct / 100,
                put_barrier_pct / 100,
            )

        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(
            x=coupons * 100,
            y=ph_sweep,
            mode="lines+markers",
            line=dict(color=C["coral"], width=2.5),
            marker=dict(color=C["coral"], size=4),
            hovertemplate="Coupon=%{x:.1f}%<br>Price=EUR %{y:.4f}<extra></extra>",
        ))
        fig_ph.add_vline(
            x=coupon_rate * 100,
            line_dash="dash",
            line_color=C["gold"],
            annotation_text="Current",
        )
        apply_layout(fig_ph, "Phoenix Price vs Coupon Rate", xaxis_title="Coupon Rate (%)", yaxis_title="Price (EUR)")
        st.plotly_chart(fig_ph, use_container_width=True)

    # ── RIGHT: Digital ────────────────────────────────────────────────────────
    with col2:
        st.markdown("<div class='section-label'>Digital Option - Cash-or-Nothing</div>", unsafe_allow_html=True)

        dig_call = DigitalOption.price(S, K, T, sigma, r, "call", q)
        dig_put  = DigitalOption.price(S, K, T, sigma, r, "put",  q)
        disc     = np.exp(-r * T)

        st.markdown(
            f"""
        <div class='card-box'>
          <div style='font-family:JetBrains Mono,monospace;font-size:9px;color:#4a6a8a;
                      letter-spacing:2px;text-transform:uppercase;margin-bottom:10px'>
            Digital Option
          </div>
          <div style='display:grid;grid-template-columns:1fr 1fr;gap:16px;
                      font-family:JetBrains Mono,monospace'>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>
                Call - prob S&gt;K
              </div>
              <div style='font-size:28px;color:#7ec8a0;margin:4px 0'>{dig_call:.4f}</div>
              <div style='color:#555;font-size:10px'>~ {dig_call*100:.1f}%</div>
            </div>
            <div>
              <div style='color:#444;font-size:9px;letter-spacing:1px;text-transform:uppercase'>
                Put - prob S&lt;K
              </div>
              <div style='font-size:28px;color:#c87e7e;margin:4px 0'>{dig_put:.4f}</div>
              <div style='color:#555;font-size:10px'>~ {dig_put*100:.1f}%</div>
            </div>
          </div>
          <div style='margin-top:10px;font-size:10px;color:#444;font-family:JetBrains Mono,monospace'>
            C + P = {dig_call+dig_put:.6f} - should ~ exp(-rT) = {disc:.6f}
          </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Vectorized — no Python loop
        k_range, dig_c, dig_p = _digital_vs_strike(S, sigma, T, r, q)

        fig_dig = go.Figure()
        fig_dig.add_trace(go.Scatter(x=k_range, y=dig_c, name="Digital Call", line=dict(color=C["green"], width=2)))
        fig_dig.add_trace(go.Scatter(x=k_range, y=dig_p, name="Digital Put",  line=dict(color=C["red"],   width=2)))
        fig_dig.add_vline(x=S, line_dash="dash", line_color=C["amber"], annotation_text="Spot",   annotation_position="bottom left")
        fig_dig.add_vline(x=K, line_dash="dash", line_color=C["gold"],  annotation_text="Strike", annotation_position="top right")
        apply_layout(fig_dig, "Digital Option Price vs Strike", xaxis_title="Strike (EUR)", yaxis_title="Price (risk-neutral prob x disc)")
        st.plotly_chart(fig_dig, use_container_width=True)

        st.markdown("<div class='section-label'>Vanilla vs Digital Call</div>", unsafe_allow_html=True)

        # Vectorized — no Python loop
        s_rng, van, dig_xK = _vanilla_vs_digital_spot(K, sigma, T, r, q, S)

        fig_vd = go.Figure()
        fig_vd.add_trace(go.Scatter(x=s_rng, y=van,    name="Vanilla Call", line=dict(color=C["amber"], width=2)))
        fig_vd.add_trace(go.Scatter(x=s_rng, y=dig_xK, name="Digital x K",  line=dict(color=C["gold"],  width=2, dash="dot")))
        apply_layout(fig_vd, "Vanilla vs Digital Call (EUR)", xaxis_title="Spot (EUR)", yaxis_title="Value (EUR)")
        st.plotly_chart(fig_vd, use_container_width=True)
