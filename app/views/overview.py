import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, fmt, header, insight, kpi_row, plotly, source

k = D.kpi()
reg = D.regions()
pref = D.prefectures()
wb = D.ts_internet()

header(
    "Le mobile money est devenu la première porte d'entrée vers les services financiers",
    "Diagnostic national à partir des données ouvertes : usage d'Internet, marché télécom, établissements financiers, "
    "agents mobile money et population 2022 (RGPH-5).",
)

# ------------------------------------------------------------------ KPI
kpi_row([
    ("Population 2022", fmt(k["population_2022"]), "RGPH-5 · 6 régions · 39 préfectures", ""),
    ("Usage d'Internet", fmt(k["pct_internet_2022"], 1, " %"), "des individus en 2022 (Banque mondiale)", "gold"),
    ("Agents mobile money", fmt(k["agents_mm"]), f"{fmt(k['agents_mm_par_1000_hab'], 2)} pour 1 000 habitants", ""),
    ("Établissements financiers", fmt(k["etab_financiers_actifs"]), f"{k['banques']} banques · {k['microfinances']} microfinances · {k['assurances']} assurances", ""),
    ("Habitants par banque", fmt(k["hab_par_banque"]), f"{fmt(k['hab_par_etab_financier'])} par établissement financier", ""),
])
st.markdown("")
kpi_row([
    ("Cantons « mobile money uniquement »", f"{k['cantons_mm_uniquement']} / {k['cantons_total']}",
     f"{fmt(k['cantons_mm_uniquement'] / k['cantons_total'] * 100, 0, ' %')} des cantons n'ont aucun établissement financier", "red"),
    ("Agents MM en zone sans établissement", fmt(k["agents_mm_en_zone_mm_uniquement"]),
     f"{fmt(k['agents_mm_en_zone_mm_uniquement'] / k['agents_mm'] * 100, 1, ' %')} des agents sont le seul service financier de leur canton", "red"),
    ("Préfectures sans banque", f"{k['prefectures_sans_banque']} / 39", "dont Kpendjal sans aucun établissement financier", "red"),
    ("Agents MM par guichet", fmt(k["agents_mm_par_guichet"], 1), "agents mobile money pour un guichet de banque ou de microfinance", "gold"),
    ("Habitants par agent MM", fmt(k["hab_par_agent_mm"]), "contre 12 266 par établissement financier", ""),
])

insight(
    "<b>Lecture.</b> Un Togolais sur trois utilise Internet, mais il y a <b>30 fois plus</b> d'agents mobile money que de "
    "guichets bancaires ou de microfinance. Dans <b>deux cantons sur trois</b>, l'agent mobile money est le seul point d'accès "
    "à un service financier. La question n'est plus <i>si</i> le mobile money porte l'inclusion financière, mais <i>où</i> il la porte seul."
)

# ------------------------------------------------------------------ concentration régionale
c1, c2 = st.columns([1.15, 1])
with c1:
    st.markdown("### Où sont les habitants, où sont les services ?")
    long = reg.melt(id_vars="region", value_vars=["part_population", "part_etab_financiers", "part_agents_mm"],
                    var_name="indicateur", value_name="part")
    long["indicateur"] = long["indicateur"].map({"part_population": "Population", "part_etab_financiers": "Établissements financiers",
                                                 "part_agents_mm": "Agents mobile money"})
    fig = px.bar(long, x="region", y="part", color="indicateur", barmode="group", text="part",
                 color_discrete_map={"Population": "#9FB8AC", "Établissements financiers": C["green_dark"], "Agents mobile money": C["red"]},
                 labels={"part": "Part nationale (%)", "region": "", "indicateur": ""})
    fig.update_traces(texttemplate="%{text:.0f} %", textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_title="Part nationale (%)", legend_y=1.08)
    plotly(fig, 360)
    source("Géoportail Open Data (établissements financiers, agents mobile money) · RGPH-5 2022")
with c2:
    st.markdown("### Habitants par établissement financier")
    d = reg.sort_values("hab_par_etab_financier", ascending=True)
    fig = go.Figure(go.Bar(
        x=d["hab_par_etab_financier"], y=d["region"].astype(str), orientation="h",
        marker_color=[REGION_COLORS[r] for r in d["region"].astype(str)],
        text=[fmt(v) for v in d["hab_par_etab_financier"]], textposition="outside", cliponaxis=False,
        customdata=d[["etab_financiers", "population"]].values,
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} habitants par établissement<br>%{customdata[0]} établissements · %{customdata[1]:,.0f} habitants<extra></extra>",
    ))
    fig.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(showticklabels=False), margin=dict(r=70))
    plotly(fig, 360)
    source("Établissements financiers en activité (660) · RGPH-5 2022")

insight(
    f"<b>Le Grand Lomé concentre {fmt(reg.loc[reg.region == 'Grand Lomé', 'part_etab_financiers'].iloc[0], 0)} % des établissements financiers "
    f"pour {fmt(reg.loc[reg.region == 'Grand Lomé', 'part_population'].iloc[0], 0)} % de la population.</b> "
    f"Dans les Savanes, un établissement financier dessert {fmt(reg.loc[reg.region == 'Savanes', 'hab_par_etab_financier'].iloc[0])} habitants, "
    f"soit <b>{fmt(reg.loc[reg.region == 'Savanes', 'hab_par_etab_financier'].iloc[0] / reg.loc[reg.region == 'Grand Lomé', 'hab_par_etab_financier'].iloc[0], 1)} fois plus</b> qu'à Lomé. "
    "Les Plateaux, deuxième région la plus peuplée, ne reçoivent que 15 % des établissements et 16 % des agents.",
    "gold",
)

# ------------------------------------------------------------------ mobile money vs guichets + internet
c3, c4 = st.columns([1, 1])
with c3:
    st.markdown("### Agents mobile money pour un guichet financier")
    d = reg.sort_values("agents_mm_par_guichet", ascending=False)
    fig = go.Figure(go.Bar(
        x=d["region"].astype(str), y=d["agents_mm_par_guichet"],
        marker_color=[C["red"] if v >= 40 else C["green"] for v in d["agents_mm_par_guichet"]],
        text=[fmt(v, 1) for v in d["agents_mm_par_guichet"]], textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>%{y:.1f} agents mobile money par guichet<extra></extra>",
    ))
    fig.add_hline(y=k["agents_mm_par_guichet"], line_dash="dot", line_color=C["muted"],
                  annotation_text=f"National : {fmt(k['agents_mm_par_guichet'], 1)}", annotation_position="bottom right")
    fig.update_traces(textposition="inside", insidetextanchor="end", textfont_color="white")
    fig.update_layout(xaxis_title="", yaxis_title="Agents MM par guichet (banque + microfinance)")
    plotly(fig, 340)
    source("Guichets = banques + institutions de microfinance en activité")
with c4:
    st.markdown("### Usage d'Internet : 0,8 % en 2000, 37,6 % en 2022")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wb["annee"], y=wb["pct_individus_internet"], mode="lines+markers", line=dict(color=C["green"], width=3),
                             marker=dict(size=6), fill="tozeroy", fillcolor="rgba(15,110,78,.08)",
                             hovertemplate="%{x} : %{y:.1f} % des individus<extra></extra>", name="Individus utilisant Internet"))
    for y, txt in [(2016, "3G/4G, +4 pts"), (2020, "+8,3 pts (2020)")]:
        v = wb.loc[wb.annee == y, "pct_individus_internet"].iloc[0]
        fig.add_annotation(x=y, y=v, text=txt, showarrow=True, arrowhead=0, ax=-40, ay=-35, font_size=11, font_color=C["muted"])
    fig.update_layout(yaxis_title="% des individus", xaxis_title="", showlegend=False)
    plotly(fig, 340)
    source("Banque mondiale, WDI (IT.NET.USER.ZS) · détail dans la page « Internet et télécoms »")

insight(
    "<b>Dans les Savanes, un guichet financier « couvre » 50 agents mobile money ; à Lomé, 31.</b> Plus on s'éloigne de la capitale, "
    "plus le mobile money supplée l'absence de banque. C'est une force — l'accès existe — et une fragilité : dépôt, retrait et "
    "transfert sont possibles, mais pas l'épargne rémunérée, le crédit ni l'assurance.",
    "red",
)

st.markdown("### Les cinq préfectures les moins bien dotées")
worst = pref.sort_values("hab_par_etab_financier", ascending=False).head(5)
kpi_row([(r.prefecture, fmt(r.hab_par_etab_financier), f"hab. / établissement · {r.etab_financiers} étab. · {r.agents_mm} agents MM · {r.region}", "red")
         for r in worst.itertuples()])
st.markdown("")
insight("<b>Kpendjal</b> (88 365 habitants) n'a aucun établissement financier en activité et seulement 41 agents mobile money — "
        "0,46 pour 1 000 habitants, cinq fois moins que la moyenne nationale. C'est la préfecture la plus à l'écart du pays, "
        "sur les deux dimensions à la fois.", "red")
