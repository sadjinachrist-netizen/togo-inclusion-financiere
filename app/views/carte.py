import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, CAT_COLORS, SEQ, SEQ_RED, fmt, header, insight, plotly, source

pref = D.prefectures()
reg = D.regions()
fin = D.points_fin()
mmp = D.points_mm()
cant = D.cantons()

header(
    "Carte des services financiers",
    "Choisissez une maille et un indicateur ; superposez les points de service. Survolez un territoire pour le détail.",
)

METRICS = {
    "Habitants par établissement financier": ("hab_par_etab_financier", SEQ_RED, "hab. / établissement", True),
    "Habitants par banque": ("hab_par_banque", SEQ_RED, "hab. / banque", True),
    "Agents mobile money pour 1 000 habitants": ("agents_mm_par_1000_hab", SEQ, "agents / 1 000 hab.", False),
    "Agents mobile money par guichet financier": ("agents_mm_par_guichet", SEQ_RED, "agents / guichet", True),
    "Part des cantons desservis uniquement par le mobile money": ("part_cantons_mm_uniquement", SEQ_RED, "% des cantons", True),
    "Population 2022": ("population", SEQ, "habitants", False),
    "Établissements financiers (nombre)": ("etab_financiers", SEQ, "établissements", False),
    "Agents mobile money (nombre)": ("agents_mm", SEQ, "agents", False),
}

f1, f2, f3 = st.columns([1, 1.6, 2])
maille = f1.radio("Maille", ["Préfectures", "Régions"], horizontal=True)
metric_lbl = f2.selectbox("Indicateur", list(METRICS))
layers = f3.multiselect("Points de service à superposer", ["Banques", "Micro-Finance", "Assurances", "Agents mobile money"],
                        default=["Banques"])
col, scale, unit, higher_is_worse = METRICS[metric_lbl]

# ------------------------------------------------------------------ données de la choroplèthe
if maille == "Préfectures":
    g = pref.groupby("map_key", as_index=False).agg(
        libelle=("prefecture", lambda s: " + ".join(s)), region=("region", "first"), population=("population", "sum"),
        etab_financiers=("etab_financiers", "sum"), banques=("banques", "sum"), microfinances=("microfinances", "sum"),
        guichets=("guichets", "sum"), agents_mm=("agents_mm", "sum"), cantons_total=("cantons_total", "sum"),
        cantons_mm_uniquement=("cantons_mm_uniquement", "sum"))
    g["hab_par_etab_financier"] = (g.population / g.etab_financiers.where(g.etab_financiers > 0)).round(0)
    g["hab_par_banque"] = (g.population / g.banques.where(g.banques > 0)).round(0)
    g["agents_mm_par_1000_hab"] = (g.agents_mm / g.population * 1000).round(2)
    g["agents_mm_par_guichet"] = (g.agents_mm / g.guichets.where(g.guichets > 0)).round(1)
    g["part_cantons_mm_uniquement"] = (g.cantons_mm_uniquement / g.cantons_total * 100).round(1)
    geo, loc, fid = D.geo_prefectures(), "map_key", "properties.map_key"
else:
    g = reg.copy()
    g["libelle"] = g["region"].astype(str)
    g["map_key"] = g["region"].astype(str)
    g["part_cantons_mm_uniquement"] = (g.cantons_mm_uniquement / g.cantons_total * 100).round(1)
    geo, loc, fid = D.geo_regions(), "map_key", "properties.region"

g["valeur"] = g[col]
g["_label"] = g["valeur"].apply(lambda v: fmt(v, 2 if col == "agents_mm_par_1000_hab" else 1 if col in ("agents_mm_par_guichet", "part_cantons_mm_uniquement") else 0))

fig = px.choropleth_map(
    g, geojson=geo, locations=loc, featureidkey=fid, color="valeur", color_continuous_scale=scale,
    map_style="carto-positron", center={"lat": 8.6, "lon": 1.05}, zoom=6.25, opacity=0.78,
    hover_name="libelle",
    hover_data={"valeur": False, "map_key": False, "_label": False},
    custom_data=["libelle", "_label", "population", "etab_financiers", "banques", "agents_mm", "cantons_mm_uniquement", "cantons_total"],
)
fig.update_traces(
    marker_line_color="white", marker_line_width=0.8,
    hovertemplate="<b>%{customdata[0]}</b><br>" + metric_lbl + " : <b>%{customdata[1]}</b> " + unit +
                  "<br>Population : %{customdata[2]:,.0f}<br>Établissements financiers : %{customdata[3]} (dont %{customdata[4]} banques)"
                  "<br>Agents mobile money : %{customdata[5]:,.0f}<br>Cantons MM uniquement : %{customdata[6]} / %{customdata[7]}<extra></extra>",
)
fig.update_layout(coloraxis_colorbar=dict(title=dict(text=unit, side="right"), orientation="h", thickness=10, len=0.55, y=0.99, x=0.72, yanchor="top", xanchor="center",
                                          bgcolor="rgba(255,255,255,.85)", tickfont_size=10), margin=dict(l=0, r=0, t=0, b=0))

# ------------------------------------------------------------------ couches de points
if "Agents mobile money" in layers:
    fig.add_trace(go.Scattermap(
        lat=mmp.lat, lon=mmp.lon, mode="markers", name="Agents mobile money",
        marker=dict(size=4, color=CAT_COLORS["Agents mobile money"], opacity=0.35),
        hoverinfo="skip",
    ))
for lay, cat in [("Banques", "Banque"), ("Micro-Finance", "Micro-Finance"), ("Assurances", "Assurance")]:
    if lay in layers:
        d = fin[(fin.categorie == cat) & fin.actif]
        fig.add_trace(go.Scattermap(
            lat=d.lat, lon=d.lon, mode="markers", name=f"{lay} ({len(d)})",
            marker=dict(size=7, color=CAT_COLORS[cat], opacity=0.9),
            customdata=d[["nom", "localite", "prefecture"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}<extra>" + lay + "</extra>",
        ))
fig.update_layout(legend=dict(orientation="v", y=0.99, x=0.01, yanchor="top", xanchor="left", bgcolor="rgba(255,255,255,.85)", font_size=11))

m1, m2 = st.columns([1.35, 1])
with m1:
    plotly(fig, 720)
    source("Contours : geoBoundaries (OSM, 2017) — Agoè-Nyivé, Kpendjal-Ouest et Oti-Sud sont représentés avec leur préfecture d'origine · Points : Géoportail Open Data")
with m2:
    st.markdown(f"### {metric_lbl}")
    st.markdown("<div class='kicker'>Les 8 valeurs les plus élevées</div>", unsafe_allow_html=True)
    order = g.sort_values("valeur", ascending=not higher_is_worse).dropna(subset=["valeur"])
    top = order.head(8)
    bar = go.Figure(go.Bar(
        x=top["valeur"], y=top["libelle"], orientation="h",
        marker_color=C["red"] if higher_is_worse else C["green"],
        text=top["_label"], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b> : %{text} " + unit + "<extra></extra>",
    ))
    bar.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis=dict(showticklabels=False, title=""), margin=dict(r=60, t=5, b=5))
    plotly(bar, 300)
    if maille == "Préfectures":
        sel = st.selectbox("Zoom sur une préfecture", ["—"] + sorted(pref.prefecture))
        if sel != "—":
            r = pref[pref.prefecture == sel].iloc[0]
            st.markdown(f"**{sel}** · {r.region} · {fmt(r.population)} habitants")
            st.markdown(f"- {r.etab_financiers} établissements financiers ({r.banques} banques, {r.microfinances} microfinances, {r.assurances} assurances)")
            st.markdown(f"- {fmt(r.agents_mm)} agents mobile money · {fmt(r.agents_mm_par_1000_hab, 2)} pour 1 000 hab.")
            st.markdown(f"- {fmt(r.hab_par_etab_financier)} habitants par établissement · {fmt(r.hab_par_banque) if r.banques else 'aucune banque'} par banque")
            st.markdown(f"- {r.cantons_mm_uniquement} cantons sur {r.cantons_total} desservis uniquement par le mobile money")
            cc = cant[(cant.prefecture == sel)].sort_values("agents_mm", ascending=False)
            st.dataframe(cc[["canton", "commune", "profil", "agents_mm", "etab_financiers", "banques"]].rename(columns={
                "canton": "Canton", "commune": "Commune", "profil": "Profil", "agents_mm": "Agents MM", "etab_financiers": "Étab. fin.", "banques": "Banques"}),
                hide_index=True, use_container_width=True, height=220)

insight("<b>Comment lire la carte.</b> Les teintes rouges signalent un déficit de service par habitant ; les points montrent où sont "
        "réellement les guichets. La superposition des agents mobile money (points rouges) sur les préfectures sans banque fait apparaître "
        "le phénomène central : <b>le réseau d'agents épouse la population là où le réseau bancaire s'arrête.</b>")

# ------------------------------------------------------------------ tableau
with st.expander("Tableau complet de la maille sélectionnée"):
    cols = ["libelle", "region", "population", "etab_financiers", "banques", "microfinances", "agents_mm",
            "hab_par_etab_financier", "hab_par_banque", "agents_mm_par_1000_hab", "agents_mm_par_guichet", "cantons_mm_uniquement", "cantons_total"]
    cols = [c for c in cols if c in g.columns]
    t = g[cols].rename(columns={"libelle": "Territoire", "region": "Région", "population": "Population", "etab_financiers": "Étab. financiers",
                                "banques": "Banques", "microfinances": "Microfinances", "agents_mm": "Agents MM", "hab_par_etab_financier": "Hab./étab.",
                                "hab_par_banque": "Hab./banque", "agents_mm_par_1000_hab": "Agents/1000 hab.", "agents_mm_par_guichet": "Agents/guichet",
                                "cantons_mm_uniquement": "Cantons MM seul", "cantons_total": "Cantons"})
    st.dataframe(t.sort_values("Population", ascending=False), hide_index=True, use_container_width=True)
    st.download_button("Télécharger (CSV)", t.to_csv(index=False).encode("utf-8-sig"), f"{maille.lower()}_indicateurs.csv", "text/csv")
