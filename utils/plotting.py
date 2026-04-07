"""
utils/plotting.py
Shared Plotly layout helpers.
Import apply_layout and PLOTLY_LAYOUT into any page that creates charts.
"""

import plotly.graph_objects as go

# ── Base Plotly theme ─────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#171717",
    plot_bgcolor="#1f1f1f",
    font=dict(family="Inter, sans-serif", color="#e5e7eb", size=13),
    xaxis=dict(gridcolor="#3a3a3a", linecolor="#666", zerolinecolor="#666"),
    yaxis=dict(gridcolor="#3a3a3a", linecolor="#666", zerolinecolor="#666"),
    margin=dict(l=45, r=20, t=35, b=45),
    hovermode="x unified",
)

# 3-D scene for vol surface
PLOTLY_SCENE = dict(
    xaxis=dict(
        title="Strike (%)",
        backgroundcolor="#1f1f1f",
        gridcolor="#3a3a3a",
        color="#e5e7eb"
    ),
    yaxis=dict(
        title="Days to Expiry",
        backgroundcolor="#1f1f1f",
        gridcolor="#3a3a3a",
        color="#e5e7eb"
    ),
    zaxis=dict(
        title="Implied Vol (%)",
        backgroundcolor="#1f1f1f",
        gridcolor="#3a3a3a",
        color="#e5e7eb"
    ),
    bgcolor="#171717",
)

# ── Color palette ─────────────────────────────────────────────────────────────
C = {
    "amber":  "#f4c542",   # yellow
    "gold":   "#ffd966",
    "coral":  "#ff7f50",
    "green":  "#22FF00",
    "red":    "#FF0000",
    "blue":   "#0051FF",
    "white":  "#f8fafc",
    "dim":    "#9ca3af",
}


def apply_layout(fig: go.Figure, title: str = "", **kwargs) -> go.Figure:
    """Apply the standard dark theme to any Plotly figure."""
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text=title, font=dict(color=C["blue"], size=12), x=0),
        **kwargs,
    )
    return fig
