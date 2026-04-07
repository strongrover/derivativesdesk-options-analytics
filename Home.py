import streamlit as st

st.set_page_config(
    page_title="Finance Projects",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #cfcfcf;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Lora', serif !important;
        color: #ffffff !important;
        letter-spacing: -0.3px;
    }

    p, .stMarkdown, .stText,
    div, span, label, button {
        font-family: 'Inter', sans-serif !important;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    button[kind="header"] {
        display: none !important;
    }

    .stApp {
        background-color: #161616;
    }

    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1100px;
    }

    .hero-box {
        background: #1f1f1f;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 2.2rem;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.6rem;
        font-family: 'Lora', serif !important;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #bdbdbd;
        line-height: 1.7;
        max-width: 720px;
    }

    .section-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: #8f8f8f;
        margin-bottom: 0.7rem;
        font-weight: 600;
    }

    .project-card {
        background: #1f1f1f;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.4rem;
        min-height: 220px;
    }

    .project-title {
        font-size: 1.2rem;
        font-weight: 650;
        color: #ffffff;
        margin-bottom: 0.5rem;
        font-family: 'Lora', serif !important;
    }

    .project-text {
        font-size: 0.96rem;
        color: #c7c7c7;
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    .tag {
        display: inline-block;
        padding: 0.25rem 0.55rem;
        margin: 0 0.35rem 0.35rem 0;
        border-radius: 999px;
        background: #252525;
        border: 1px solid #333333;
        color: #d2d2d2;
        font-size: 0.78rem;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        height: 2.7rem;
        font-family: 'Inter', sans-serif !important;
    }

    .footer-note {
        color: #8c8c8c;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">Finance & Markets Lab</div>
    <div class="hero-subtitle">
        Building tools for derivatives pricing, risk analysis, and market decision-making.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Featured Project</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2.2, 1], gap="large")

with col1:
    st.markdown("""
    <div class="project-card">
        <div class="project-title">DerivDesk - Options Pricing & Risk Analytics Platform</div>
        <div class="project-text">
            End-to-end derivatives analytics platform covering pricing, volatility modeling,
            risk simulation, scenario analysis, and structured products on CAC 40 equities.
        </div>
        <div>
            <span class="tag">Black-Scholes</span>
            <span class="tag">Greeks</span>
            <span class="tag">Monte Carlo</span>
            <span class="tag">Volatility Surface</span>
            <span class="tag">Stress Testing</span>
            <span class="tag">Exotics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.write("")
    st.write("")

    if "show_project_summary" not in st.session_state:
        st.session_state.show_project_summary = False
    if "show_methodology" not in st.session_state:
        st.session_state.show_methodology = False

    if st.button("Explore DerivDesk", use_container_width=True, type="primary"):
        st.switch_page("pages/DerivDesk.py")

    if st.button("Project Summary", use_container_width=True):
        st.session_state.show_project_summary = not st.session_state.show_project_summary
    if st.session_state.show_project_summary:
        st.markdown("""
    ### QuantDesk — Project Summary

    QuantDesk is an end-to-end derivatives analytics platform designed to replicate how a trading desk approaches option pricing, volatility, and risk.

    The platform integrates analytical pricing models with simulation-based methods to provide a unified view of valuation and risk exposure.

    **Key Capabilities**
    - Black-Scholes pricing with full Greeks (Delta, Gamma, Theta, Vega, Rho)
    - Higher-order sensitivities (Vanna, Charm, Volga)
    - Implied volatility surface modelling (skew & smile)
    - Scenario analysis across spot and volatility shocks
    - Monte Carlo simulation for structured products (Phoenix autocall)
    - Digital option pricing with probability interpretation

    **Objective**
    To bridge the gap between theoretical derivatives models and practical, desk-oriented risk analysis tools.

    **Scope**
    Focused on CAC 40 equities with live market data integration and fallback robustness.
    """)

    if st.button("Methodology", use_container_width=True):
        st.session_state.show_methodology = not st.session_state.show_methodology
    if st.session_state.show_methodology:
        st.markdown("""
    ### Methodology

    **Vanilla Options (Closed-Form)**  
    For European options where the payoff depends solely on \( S_T \), pricing is based on the analytical Black–Scholes–Merton framework:

    $$
    C(S,t) = S e^{-qT} N(d_1) - K e^{-rT} N(d_2)
    $$

    where:

    $$
    d_1 = \\frac{\\ln(S/K) + (r - q + 0.5\\sigma^2)T}{\\sigma \\sqrt{T}}, \\quad
    d_2 = d_1 - \\sigma \\sqrt{T}
    $$

    ---

    **Greeks Computation**  
    Sensitivities are derived analytically to measure exposure to the main option risk factors:

    $$
    \\Delta = e^{-qT} N(d_1), \\quad
    \\Gamma = \\frac{e^{-qT} \\phi(d_1)}{S \\sigma \\sqrt{T}}, \\quad
    \\Vega = S e^{-qT} \\phi(d_1) \\sqrt{T}
    $$

    $$
    \\Theta = -\\frac{S e^{-qT} \\phi(d_1) \\sigma}{2\\sqrt{T}}
    - rK e^{-rT} N(d_2) + qS e^{-qT} N(d_1)
    $$

    ---

    **Monte Carlo Simulation (GBM)**  
    For path-dependent and exotic structures, the underlying is simulated using Geometric Brownian Motion:

    $$
    dS_t = (r - q) S_t dt + \\sigma S_t dW_t
    $$

    Discretized form:

    $$
    S_{t+\\Delta t} = S_t \\exp\\left((r - q - 0.5\\sigma^2)\\Delta t + \\sigma \\sqrt{\\Delta t} Z\\right)
    $$

    where \( Z \\sim \\mathcal{N}(0,1) \).
    """)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Project Library</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown("""
    <div class="project-card">
        <div class="project-title">Portfolio Risk Engine</div>
        <div class="project-text">
            Upcoming project focused on portfolio VaR, CVaR, and allocation analytics.
        </div>
        <div>
            <span class="tag">VaR</span>
            <span class="tag">Risk</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="project-card">
        <div class="project-title">Market Dashboard</div>
        <div class="project-text">
            Upcoming project focused on macro and equity market monitoring dashboards.
        </div>
        <div>
            <span class="tag">Markets</span>
            <span class="tag">Macro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="project-card">
        <div class="project-title">More Projects Coming</div>
        <div class="project-text">
            A growing pipeline of finance and analytics projects currently in development.
        </div>
        <div>
            <span class="tag">Python</span>
            <span class="tag">Finance</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer-note">
Built to showcase finance projects across pricing, risk, and market analytics.
</div>
""", unsafe_allow_html=True)
