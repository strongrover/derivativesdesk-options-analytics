"""
utils/styles.py
Single source of truth for all custom CSS.
Call inject_styles() once at the top of any page.
"""

import streamlit as st

_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {
    --bg: #121212;
    --bg-elev: #171717;
    --bg-card: #1b1b1b;
    --bg-card-2: #202020;
    --border: #2a2a2a;
    --border-soft: #232323;

    --text-1: #f5f7fa;
    --text-2: #d6d9de;
    --text-3: #9aa3ad;
    --text-4: #6b7280;

    --amber: #f4c542;
    --gold: #ffd966;
    --coral: #ff7f50;
    --green: #22c55e;
    --red: #ef4444;
    --blue: #60a5fa;

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;

    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;
    --space-7: 40px;
    --space-8: 56px;

    --shadow-soft: 0 0 0 1px rgba(255,255,255,0.02), 0 10px 30px rgba(0,0,0,0.18);
  }

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: var(--text-2);
  }

  .stApp, .main {
    background: var(--bg);
  }

  .block-container {
    max-width: 1460px;
    padding-top: 28px;
    padding-bottom: 36px;
    padding-left: 2.2rem;
    padding-right: 2.2rem;
  }

  /* ─────────────────────────────────────────────────────────────
     Typography
  ───────────────────────────────────────────────────────────── */
  h1, h2, h3, h4, h5, h6 {
    color: var(--text-1) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin-bottom: 0.35rem;
  }

  h1 { font-size: 30px !important; }
  h2 { font-size: 24px !important; }
  h3 { font-size: 20px !important; }

  p, li, label, .stMarkdown, .stText {
    color: var(--text-2) !important;
    line-height: 1.6;
  }

  .mono {
    font-family: 'JetBrains Mono', monospace !important;
  }

  .muted {
    color: var(--text-3) !important;
  }

  .subtle {
    color: var(--text-4) !important;
  }

  /* ─────────────────────────────────────────────────────────────
     Sidebar
  ───────────────────────────────────────────────────────────── */
  section[data-testid="stSidebar"] {
    background: #181818;
    border-right: 1px solid var(--border);
  }

  section[data-testid="stSidebar"] * {
    color: var(--text-2) !important;
  }

  .sidebar-shell {
    padding-top: 4px;
  }

  .sidebar-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--blue);
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 18px;
  }

  .sidebar-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--blue);
    padding: 12px 0 8px 0;
    border-bottom: 1px solid var(--border-soft);
    margin-bottom: 12px;
    margin-top: 10px;
  }

  .sidebar-status {
    background: #141414;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 12px 13px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-soft);
  }

  .sidebar-status-top {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    color: var(--blue);
  }

  .sidebar-status-mid {
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
  }

  .sidebar-status-bot {
    margin-top: 4px;
    font-size: 11px;
    color: var(--text-4);
  }

  /* ─────────────────────────────────────────────────────────────
     Tabs
  ───────────────────────────────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid var(--border);
    gap: 8px;
    margin-bottom: 8px;
  }

  .stTabs [data-baseweb="tab"] {
    color: var(--text-3) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    padding: 12px 16px 10px 16px;
    border-radius: 0;
    background: transparent;
  }

  .stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
    background: transparent !important;
  }

  /* ─────────────────────────────────────────────────────────────
     Inputs
  ───────────────────────────────────────────────────────────── */
  label, .stMarkdown p, p {
    color: var(--text-2) !important;
  }

  .stSelectbox > div > div,
  .stNumberInput > div > div > input,
  .stTextInput > div > div > input,
  .stDateInput input,
  .stTextArea textarea {
    background: #161616 !important;
    border: 1px solid var(--border) !important;
    color: var(--text-1) !important;
    border-radius: 10px !important;
  }

  .stRadio > div {
    flex-direction: row;
    gap: 16px;
  }

  /* Section nav: style horizontal radio like the old tab strip */
  div[role="radiogroup"] {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
    padding-bottom: 0;
  }

  div[role="radiogroup"] > label {
    margin: 0 !important;
    padding: 12px 16px 10px 16px !important;
    border-radius: 0 !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    min-height: auto !important;
    display: inline-flex !important;
    align-items: center;
  }

  div[role="radiogroup"] > label p {
    margin: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    color: var(--text-3) !important;
  }

  div[role="radiogroup"] > label[data-checked="true"] {
    border-bottom: 2px solid var(--amber) !important;
  }

  div[role="radiogroup"] > label[data-checked="true"] p {
    color: var(--amber) !important;
  }

  div[role="radiogroup"] input[type="radio"] {
    display: none !important;
  }

  /* ── Global slider styling fix ───────────────────────────── */
  .stSlider label,
  .stSlider span,
  .stSlider div {
    color: #f3f4f6 !important;
    font-size: 14px !important;
  }

  /* Slider track */
  .stSlider [data-baseweb="slider"] > div > div {
    background: linear-gradient(to right, #ff4c4c, #f4c542) !important;
    height: 4px !important;
  }

  /* Slider handle */
  .stSlider [role="slider"] {
    background: #f4c542 !important;
    border: 2px solid #ffffff !important;
    box-shadow: 0 0 0 2px rgba(0,0,0,0.35) !important;
  }

  /* Min / max endpoint labels and inline slider numbers */
  .stSlider [data-baseweb="slider"] span {
    color: #111111 !important;
    font-weight: 700 !important;
    background: #f4c542 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
  }

  /* Extra safety for any slider text wrappers */
  .stSlider * {
    text-shadow: none !important;
  }

  /* Prevent invisible text in dark theme containers */
  section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] span,
  section[data-testid="stSidebar"] .stSlider [role="slider"],
  .main .stSlider [data-baseweb="slider"] span,
  .main .stSlider [role="slider"] {
    opacity: 1 !important;
  }

  .stButton > button {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    background: #1c1c1c !important;
    color: var(--text-1) !important;
    font-weight: 500 !important;
    min-height: 42px;
  }

  .stButton > button:hover {
    border-color: #3a3a3a !important;
    background: #222 !important;
  }

  /* ─────────────────────────────────────────────────────────────
     Reusable layout primitives
  ───────────────────────────────────────────────────────────── */
  .qd-stack-xs > * + * { margin-top: 6px; }
  .qd-stack-sm > * + * { margin-top: 12px; }
  .qd-stack-md > * + * { margin-top: 18px; }
  .qd-stack-lg > * + * { margin-top: 28px; }

  .qd-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: var(--shadow-soft);
  }

  .qd-card-tight {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    box-shadow: var(--shadow-soft);
  }

  .qd-card-muted {
    background: #151515;
    border: 1px solid var(--border-soft);
    border-radius: var(--radius-md);
    padding: 16px 18px;
  }

  .qd-meta-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 10px;
  }

  .qd-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-4);
  }

  .qd-value {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-1);
  }

  .qd-divider {
    border-top: 1px solid var(--border);
    margin: 18px 0;
  }

  /* ─────────────────────────────────────────────────────────────
     Page header
  ───────────────────────────────────────────────────────────── */
  .header-strip {
    padding: 3em 0 22px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 22px;
  }

  .stApp .header-strip .header-hero {
    display: block;
    font-family: 'Inter', sans-serif !important;
    font-size: 55px !important;
    font-weight: 800 !important;
    color: var(--text-1) !important;
    letter-spacing: -0.05em !important;
    line-height: 0.95 !important;
    margin-bottom: 16px !important;
  }

  .header-summary {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
  }

  .header-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-1);
    letter-spacing: 0.08em;
    line-height: 1.2;
    text-transform: uppercase;
  }

  .header-meta {
    display: none;
  }

  .header-right {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--text-1);
    text-align: right;
    line-height: 1.2;
    min-width: 180px;
  }

  .header-spot-value {
    color: var(--text-1);
    font-weight: 600;
  }

  .data-source-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
  }

  /* ─────────────────────────────────────────────────────────────
     Section heading
  ───────────────────────────────────────────────────────────── */
  .section-label {
    font-family: 'Inter', sans-serif;
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.01em;
    text-transform: none;
    color: var(--text-1);
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
    margin-top: 6px;
  }

  /* ─────────────────────────────────────────────────────────────
     Price + stat system
  ───────────────────────────────────────────────────────────── */
  .price-panel {
    padding: 2px 0 18px 0;
  }

  .price-main {
    font-family: 'JetBrains Mono', monospace;
    font-size: 42px;
    font-weight: 500;
    color: var(--text-1);
    letter-spacing: -0.04em;
    line-height: 1;
  }

  .price-currency {
    font-size: 20px;
    color: var(--text-4);
    margin-right: 5px;
  }

  .price-subline {
    margin-top: 12px;
    display: flex;
    gap: 28px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-3);
    line-height: 1.4;
    flex-wrap: wrap;
  }

  .price-subitem {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 120px;
  }

  .price-subitem-label {
    color: var(--text-3);
  }

  .price-subitem-value {
    color: var(--text-1);
  }

  .stat-row {
    display: flex;
    gap: 24px;
    row-gap: 16px;
    margin: 8px 0 0 0;
    flex-wrap: wrap;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 104px;
  }

  .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-4);
  }

  .stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    color: var(--text-1);
    line-height: 1.2;
  }

  .stat-value.pos   { color: var(--green); }
  .stat-value.neg   { color: var(--red); }
  .stat-value.amber { color: var(--amber); }

  /* ─────────────────────────────────────────────────────────────
     Info surfaces
  ───────────────────────────────────────────────────────────── */
  .insight-box {
    background: #171717;
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 14px 16px;
    margin: 12px 0 10px 0;
    font-size: 14px;
    color: var(--text-2);
    line-height: 1.65;
  }

  .insight-box strong {
    color: var(--text-1);
    font-weight: 600;
  }

  .card-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-soft);
  }

  /* ─────────────────────────────────────────────────────────────
     Tables / alerts
  ───────────────────────────────────────────────────────────── */
  .stDataFrame {
    background: transparent !important;
  }

  div[data-testid="stMetricContainer"],
  div[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 16px;
  }

  div[data-testid="metric-container"] label {
    color: var(--text-3) !important;
    font-size: 11px !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: var(--text-1) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 24px !important;
  }

  .stInfo {
    background: rgba(244,197,66,0.06) !important;
    border-left-color: var(--amber) !important;
    color: var(--text-2) !important;
    border-radius: 10px !important;
  }

  hr {
    border-color: var(--border) !important;
  }

  /* ─────────────────────────────────────────────────────────────
     Footer
  ───────────────────────────────────────────────────────────── */
  .qd-footer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-4);
    text-align: center;
    letter-spacing: 0.12em;
    padding-top: 4px;
  }

  /* ─────────────────────────────────────────────────────────────
     Responsive
  ───────────────────────────────────────────────────────────── */
  @media (max-width: 1100px) {
    .header-summary {
      flex-direction: column;
      align-items: flex-start;
    }

    .header-right {
      text-align: left;
      min-width: auto;
    }

    .price-main {
      font-size: 34px;
    }

    .stat-item {
      min-width: 92px;
    }
  }
</style>
"""

def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

