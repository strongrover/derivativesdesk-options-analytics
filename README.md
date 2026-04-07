# QuantDesk - Options Analytics Engine

> **Live derivatives pricing dashboard** built with Python, Streamlit, Plotly, and SciPy.
> CAC 40 Top 10 underlyings - Black-Scholes - Greeks - Implied Vol Surface - Monte Carlo - Exotics

---

## Features

| Module | Details |
|--------|---------|
| **Black-Scholes Pricer** | Call and Put pricing with full put-call parity verification |
| **Greeks Engine** | Delta, Gamma, Theta, Vega, Rho plus higher-order Vanna, Charm, and Volga |
| **Implied Vol Surface** | 3D interactive surface (9 expiries x 25 strikes) with skew and smile models |
| **P&L Scenario Grid** | Spot x Vol shock heatmap plus 8 named stress tests |
| **Monte Carlo Backtest** | GBM path simulation, delta-hedging, VaR/CVaR, win rate, and P&L distribution |
| **Phoenix Autocall** | Monte Carlo exotic with coupon, call barrier, and put barrier |
| **Digital Options** | Cash-or-nothing call and put with implied probability display |
| **Greeks Ladder** | Full table across all CAC 40 tickers plus strike x vol heatmap |

## CAC 40 Underlyings

LVMH - TotalEnergies - Hermes - Sanofi - Airbus - Schneider Electric - L'Oreal - BNP Paribas - Stellantis - Safran

---

## Deploy to Streamlit Community Cloud

### Step 1 - Push to GitHub

```bash
# Create a new repo on github.com, then:
git init
git add .
git commit -m "Initial commit - QuantDesk options engine"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/quantdesk.git
git push -u origin main
```

### Step 2 - Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Connect your GitHub account
4. Select your repo -> branch: `main` -> Main file: `app.py`
5. Click **"Deploy!"**

Your public URL will be:

```
https://YOUR_USERNAME-quantdesk-app-XXXXX.streamlit.app
```

## Local Development

```bash
pip install -r requirements.txt
streamlit run Home.py
```

Open http://localhost:8501

---

## Tech Stack

- **Python 3.11+**
- **Streamlit** - UI framework
- **Plotly** - Interactive 3D/2D charts
- **SciPy** - Numerical optimization for the implied vol solver
- **NumPy** - Vectorized pricing and simulation

## License

MIT - free to use, modify, and showcase on your CV.
