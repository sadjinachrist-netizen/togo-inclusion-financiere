"""Charte graphique, composants et thème Plotly."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------- palette (vert Togo, or, rouge d'alerte)
C = {
    "green": "#0F6E4E", "green_dark": "#0B3D2E", "green_light": "#DCEFE6", "lime": "#4ADE80",
    "gold": "#D9A521", "red": "#C8453B", "red_light": "#FBE9E7", "ink": "#14201A", "muted": "#5F6B66",
    "bg": "#F6F8F7", "card": "#FFFFFF", "line": "#E3E8E5",
}
REGION_COLORS = {"Grand Lomé": "#0B3D2E", "Maritime": "#0F6E4E", "Plateaux": "#3A9A6E",
                 "Centrale": "#D9A521", "Kara": "#B8742A", "Savanes": "#C8453B"}
CAT_COLORS = {"Banque": "#0B3D2E", "Micro-Finance": "#3A9A6E", "Assurance": "#D9A521", "Mutuelle": "#8FBFA3",
              "Agents mobile money": "#C8453B"}
SEQ = ["#E8F3EE", "#BFE0D0", "#8CC7AC", "#57A986", "#2E8A66", "#0F6E4E", "#0B3D2E"]
SEQ_RED = ["#FDF3F2", "#F8D5D1", "#F0ADA6", "#E5827A", "#D65C52", "#C8453B", "#8E2C25"]

FONT = "Inter, 'Segoe UI', Helvetica, Arial, sans-serif"

# ---------------------------------------------------------------- thème Plotly
_tpl = go.layout.Template()
_tpl.layout = go.Layout(
    font=dict(family=FONT, size=13, color=C["ink"]),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=[C["green"], C["gold"], C["red"], "#3A9A6E", "#B8742A", "#8FBFA3"],
    xaxis=dict(showgrid=False, zeroline=False, linecolor=C["line"], title_font_size=12),
    yaxis=dict(showgrid=True, gridcolor=C["line"], zeroline=False, title_font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title=None, font_size=12),
    title=dict(font=dict(size=15, color=C["green_dark"]), x=0, xanchor="left"),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family=FONT),
)
pio.templates["togo"] = _tpl
pio.templates.default = "togo"


# ---------------------------------------------------------------- formats
def fmt(n, dec: int = 0, suffix: str = "") -> str:
    """Nombre au format français : 19 788 · 37,6 %."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    s = f"{n:,.{dec}f}".replace(",", " ").replace(".", ",")
    return s + suffix


# ---------------------------------------------------------------- CSS global
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: {FONT}; }}
.block-container {{ padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1240px; }}
section[data-testid="stSidebar"] {{ background: {C['green_dark']}; }}
section[data-testid="stSidebar"] * {{ color: #E6F0EA; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{ border-radius: 8px; margin: 2px 0; }}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,255,255,.08); }}
section[data-testid="stSidebar"] a[aria-current="page"] {{ background: rgba(74,222,128,.18); }}
section[data-testid="stSidebar"] a[aria-current="page"] span {{ color: {C['lime']}; font-weight: 600; }}
section[data-testid="stSidebar"] [data-testid="stSidebarNavSectionHeader"] {{ color: {C['lime']}; letter-spacing: .08em; font-size: .72rem; }}
h1 {{ font-weight: 800; letter-spacing: -.02em; color: {C['green_dark']}; }}
h2, h3 {{ font-weight: 700; color: {C['green_dark']}; }}
.kicker {{ color: {C['muted']}; font-size: 1.02rem; margin: -.4rem 0 1.1rem 0; }}
.kpi {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 12px; padding: .9rem 1rem .8rem; height: 100%; }}
.kpi .lbl {{ color: {C['muted']}; font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; font-weight: 600; }}
.kpi .val {{ font-size: 1.9rem; font-weight: 800; color: {C['green_dark']}; line-height: 1.15; margin: .15rem 0; }}
.kpi .val.red {{ color: {C['red']}; }}
.kpi .val.gold {{ color: {C['gold']}; }}
.kpi .sub {{ color: {C['muted']}; font-size: .8rem; }}
.insight {{ background: {C['green_light']}; border-left: 4px solid {C['green']}; border-radius: 8px; padding: .8rem 1rem; margin: .4rem 0 1rem; }}
.insight.red {{ background: {C['red_light']}; border-left-color: {C['red']}; }}
.insight.gold {{ background: #FBF3DD; border-left-color: {C['gold']}; }}
.insight b {{ color: {C['green_dark']}; }}
.reco {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 12px; padding: 1rem 1.1rem; margin-bottom: .8rem; }}
.reco .n {{ display:inline-block; width: 30px; height: 30px; border-radius: 50%; background: {C['green']}; color: white; text-align: center; line-height: 30px; font-weight: 700; margin-right: .6rem; }}
.reco .n.red {{ background: {C['red']}; }}
.reco .t {{ font-weight: 700; font-size: 1.05rem; color: {C['green_dark']}; }}
.reco .impact {{ font-size: 1.5rem; font-weight: 800; color: {C['red']}; }}
.reco .impact small {{ font-size: .8rem; color: {C['muted']}; font-weight: 500; }}
.reco p {{ margin: .4rem 0 0; color: {C['ink']}; }}
.badge {{ display:inline-block; padding: .15rem .55rem; border-radius: 999px; font-size: .72rem; font-weight: 700; letter-spacing:.04em; }}
.badge.red {{ background: {C['red_light']}; color: {C['red']}; }}
.badge.green {{ background: {C['green_light']}; color: {C['green']}; }}
.badge.gold {{ background: #FBF3DD; color: #8A6510; }}
.src {{ color: {C['muted']}; font-size: .78rem; margin-top: -.4rem; }}
div[data-testid="stMetric"] {{ background: {C['card']}; border: 1px solid {C['line']}; border-radius: 12px; padding: .6rem .9rem; }}
footer {{ visibility: hidden; }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, kicker: str) -> None:
    st.markdown(f"# {title}")
    st.markdown(f"<div class='kicker'>{kicker}</div>", unsafe_allow_html=True)


def kpi_row(items: list[tuple[str, str, str, str]]) -> None:
    """items = [(label, value, sub, color)] avec color in {'', 'red', 'gold'}."""
    cols = st.columns(len(items))
    for col, (lbl, val, sub, color) in zip(cols, items):
        col.markdown(
            f"<div class='kpi'><div class='lbl'>{lbl}</div><div class='val {color}'>{val}</div><div class='sub'>{sub}</div></div>",
            unsafe_allow_html=True,
        )


def insight(text: str, kind: str = "") -> None:
    st.markdown(f"<div class='insight {kind}'>{text}</div>", unsafe_allow_html=True)


def reco(n: int, title: str, impact: str, impact_label: str, body: str, tag: str, tag_kind: str, red: bool = False) -> None:
    st.markdown(
        f"""<div class='reco'>
<span class='n {'red' if red else ''}'>{n}</span><span class='t'>{title}</span>
<span class='badge {tag_kind}' style='float:right;margin-top:.35rem'>{tag}</span>
<div style='margin-top:.5rem'><span class='impact'>{impact} <small>{impact_label}</small></span></div>
<p>{body}</p></div>""",
        unsafe_allow_html=True,
    )


def source(text: str) -> None:
    st.markdown(f"<div class='src'>Source : {text}</div>", unsafe_allow_html=True)


def plotly(fig: go.Figure, height: int = 380, key: str | None = None) -> None:
    fig.update_layout(height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "locale": "fr",
                                                            "modeBarButtonsToRemove": ["lasso2d", "select2d"]}, key=key)
