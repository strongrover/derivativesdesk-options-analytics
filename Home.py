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
        <div class="project-title">QuantDesk - Options Pricing & Risk Analytics Platform</div>
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

    if st.button("Explore QuantDesk", use_container_width=True, type="primary"):
        st.switch_page("pages/QuantDesk.py")

    if st.button("Project Summary", use_container_width=True):
        st.info("Link to PDF or summary later")

    if st.button("Methodology", use_container_width=True):
        st.info("Explain Black-Scholes, Greeks, Monte Carlo")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-title">Project Library</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown("""
    <div class="project-card">
        <div class="project-title">Portfolio Risk Engine</div>
        <div class="project-text">
            Future module for portfolio VaR, CVaR, and allocation analytics.
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
            Future module for macro and equity market monitoring dashboards.
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
            Additional finance and analytics projects will be added over time.
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
