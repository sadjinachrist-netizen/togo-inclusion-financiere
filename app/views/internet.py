import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, fmt, header, insight, kpi_row, plotly, source

wb = D.ts_internet()
ar = D.ts_arcep()

header(
    "Internet : une décennie d'accélération, portée par le mobile",
    "Évolution de l'usage d'Internet (2000-2022), abonnements par technologie et dynamique du marché des télécommunications (2013-2019).",
)

# ------------------------------------------------------------------ périodes
wb["periode"] = pd.cut(wb["variation_pts"], [-1, 0.5, 2, 100], labels=["Stagnation (< 0,5 pt/an)", "Croissance (0,5-2 pts/an)", "Accélération (> 2 pts/an)"])
v2013, v2022 = wb.loc[wb.annee == 2013, "pct_individus_internet"].iloc[0], wb.loc[wb.annee == 2022, "pct_individus_internet"].iloc[0]
kpi_row([
    ("Usage d'Internet 2022", fmt(v2022, 1, " %"), "des individus (Banque mondiale)", "gold"),
    ("2000 → 2013", f"{fmt(wb.loc[wb.annee == 2000, 'pct_individus_internet'].iloc[0], 1)} → {fmt(v2013, 1)} %", "13 ans de quasi-stagnation : +0,3 pt par an", "red"),
    ("2013 → 2022", f"×{fmt(v2022 / v2013, 1)}", f"+{fmt(v2022 - v2013, 1)} points en 9 ans : +3,7 pts par an", ""),
    ("Meilleure année", "2020", "+8,3 points en un an (confinements, télétravail, e-services)", ""),
    ("Taux de pénétration 2019", fmt(ar.loc[ar.indicateur_clean.str.startswith('Taux de pénétration Internet (Toutes'), 'value'].iloc[-1], 1, " %"), "abonnements / population (ARCEP) — ≠ individus", ""),
])

c1, c2 = st.columns([1.35, 1])
with c1:
    st.markdown("### Usage d'Internet : trois phases")
    colors = {"Stagnation (< 0,5 pt/an)": "#B8C4BE", "Croissance (0,5-2 pts/an)": C["gold"], "Accélération (> 2 pts/an)": C["green"]}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wb.annee, y=wb.pct_individus_internet, mode="lines", line=dict(color=C["green_dark"], width=2), name="% individus", hoverinfo="skip"))
    for per, g in wb.dropna(subset=["periode"]).groupby("periode", observed=True):
        fig.add_trace(go.Bar(x=g.annee, y=g.variation_pts, name=per, marker_color=colors[per], yaxis="y2",
                             hovertemplate="%{x} : %{y:+.1f} pt<extra>" + per + "</extra>"))
    fig.update_layout(
        yaxis=dict(title="% des individus utilisant Internet"),
        yaxis2=dict(title="Variation annuelle (points)", overlaying="y", side="right", showgrid=False, range=[0, 10], dtick=2),
        barmode="overlay", legend_y=1.1, xaxis=dict(dtick=2),
    )
    plotly(fig, 400)
    source("Banque mondiale, WDI — Individuals using the Internet (% of population), Togo")
with c2:
    st.markdown("### Ce que disent les trois phases")
    insight("<b>2000-2013 · stagnation.</b> De 0,8 % à 4,5 % en treize ans. Internet reste un service fixe, urbain et cher : "
            "le pays compte alors moins de 65 000 abonnés fixes.", "red")
    insight("<b>2014-2019 · décollage mobile.</b> +16 points en six ans. La 3G se généralise (130 000 clients en 2013, 1,9 million en 2018), "
            "la 4G est lancée en 2018. Le taux de pénétration ARCEP passe de 5 % à 50 %.", "gold")
    insight("<b>2020-2022 · accélération.</b> +17 points en trois ans, dont +8,3 en 2020. La crise sanitaire fait basculer les usages "
            "(paiement, administration, éducation à distance). 37,6 % des Togolais utilisent Internet en 2022.")

# ------------------------------------------------------------------ deux sources
st.markdown("### Abonnements ou individus ? Deux mesures, deux lectures")
pen = ar[ar.indicateur_clean.str.startswith("Taux de pénétration Internet (Toutes")]
penhd = ar[ar.indicateur_clean.str.startswith("Taux de pénétration Internet haut")]
fig = go.Figure()
fig.add_trace(go.Scatter(x=pen.annee, y=pen.value, name="Taux de pénétration — abonnements (ARCEP)", line=dict(color=C["gold"], width=3), mode="lines+markers"))
fig.add_trace(go.Scatter(x=penhd.annee, y=penhd.value, name="Pénétration haut débit (ARCEP)", line=dict(color=C["gold"], width=2, dash="dot"), mode="lines+markers"))
w = wb[(wb.annee >= 2013) & (wb.annee <= 2022)]
fig.add_trace(go.Scatter(x=w.annee, y=w.pct_individus_internet, name="Individus utilisant Internet (Banque mondiale)", line=dict(color=C["green"], width=3), mode="lines+markers"))
fig.update_layout(yaxis_title="% de la population", xaxis=dict(dtick=1), hovermode="x unified")
plotly(fig, 340)
source("ARCEP Togo (2013-2019) · Banque mondiale (2013-2022)")
insight("En 2019, l'ARCEP compte <b>44,8 abonnements Internet pour 100 habitants</b>, la Banque mondiale <b>20,7 % d'individus</b> utilisateurs. "
        "L'écart n'est pas une erreur : une personne cumule souvent plusieurs cartes SIM, et un abonnement n'est pas toujours un usage. "
        "Le second chiffre mesure l'inclusion réelle ; le premier, la capacité du réseau. <b>Les séries ARCEP s'arrêtent en 2019</b> : "
        "les trois années les plus dynamiques ne sont documentées que par la source internationale.", "gold")

# ------------------------------------------------------------------ technologies
c3, c4 = st.columns(2)
with c3:
    st.markdown("### Le passage 2G → 3G → 4G")
    tech = ar[ar.indicateur_clean.isin(["Abonnés GPRS/EDGE (2G)", "Clients 3G", "Clients 4G"])]
    tech = tech.groupby(["annee", "indicateur_clean"], as_index=False).value.sum()
    fig = px.area(tech, x="annee", y="value", color="indicateur_clean",
                  color_discrete_map={"Abonnés GPRS/EDGE (2G)": "#B8C4BE", "Clients 3G": C["green"], "Clients 4G": C["green_dark"]},
                  labels={"value": "Abonnés (les deux opérateurs)", "annee": "", "indicateur_clean": ""})
    fig.update_layout(xaxis=dict(dtick=1, range=[2012.8, 2019.2]), legend_y=1.08)
    fig.update_traces(hovertemplate="%{x} : %{y:,.0f}<extra>%{fullData.name}</extra>")
    plotly(fig, 340)
    source("ARCEP — abonnés par technologie, Togocom + Moov Africa")
with c4:
    st.markdown("### Fixe : marginal, mais la fibre décolle")
    fixe = ar[ar.indicateur_clean.isin(["ADSL", "FTTH", "Wimax", "Abonnés Internet fixe (Togo Telecom)"])]
    fig = px.line(fixe, x="annee", y="value", color="indicateur_clean", markers=True,
                  labels={"value": "Abonnés", "annee": "", "indicateur_clean": ""})
    fig.update_layout(xaxis=dict(dtick=1, range=[2012.8, 2019.2]), legend_y=1.08)
    plotly(fig, 340)
    source("ARCEP — ADSL, FTTH (fibre), Wimax, Internet fixe Togo Telecom")

insight("<b>Le mobile fait tout le travail.</b> En 2019, les abonnés Internet mobile représentent 99 % des abonnements Internet. "
        "La 4G, lancée en 2018, compte 174 000 clients en 2019 ; la fibre (FTTH) passe de 0 à 6 900 abonnés en trois ans — un début, "
        "concentré dans le Grand Lomé. Note : la baisse de 2019 (3G, total Internet) survient alors que l'usage mesuré par la Banque mondiale continue de croître ; "
        "elle traduit vraisemblablement un changement de méthode de comptage des abonnés actifs plutôt qu'une perte d'usagers — point à confirmer auprès de l'ARCEP.")

# ------------------------------------------------------------------ marché
st.markdown("### Le marché : un duopole, des revenus stables, un pic d'investissement en 2018")
c5, c6, c7 = st.columns(3)
with c5:
    pm = ar[ar.indicateur_clean == "Part de marché mobile (%)"]
    fig = px.line(pm, x="annee", y="value", color="operateur", markers=True,
                  color_discrete_map={"Togocom": C["green_dark"], "Moov Africa": C["gold"]},
                  labels={"value": "Part de marché (%)", "annee": "", "operateur": ""})
    fig.update_layout(title="Parts de marché mobile (%)", yaxis_range=[40, 60], xaxis=dict(dtick=1, range=[2012.8, 2019.2]), legend=dict(orientation="h", y=-0.22))
    plotly(fig, 320)
with c6:
    ca = ar[ar.indicateur_clean.str.startswith("Chiffre d'affaires")]
    inv = ar[ar.indicateur_clean.str.startswith("Investissements")]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ca.annee, y=ca.value / 1e9, name="Chiffre d'affaires", marker_color=C["green"], hovertemplate="%{x} : %{y:,.1f} Md FCFA<extra>CA</extra>"))
    fig.add_trace(go.Bar(x=inv.annee, y=inv.value / 1e9, name="Investissements", marker_color=C["gold"], hovertemplate="%{x} : %{y:,.1f} Md FCFA<extra>Invest.</extra>"))
    fig.update_layout(title="CA et investissements (Md FCFA)", barmode="group", xaxis=dict(dtick=1), legend=dict(orientation="h", y=-0.22))
    plotly(fig, 320)
with c7:
    td = ar[ar.indicateur_clean == "Télédensité mobile GSM"]
    fig = px.area(td, x="annee", y="value", labels={"value": "Abonnés mobile / 100 hab.", "annee": ""})
    fig.update_traces(line_color=C["green"], fillcolor="rgba(15,110,78,.12)", hovertemplate="%{x} : %{y:.1f} %<extra></extra>")
    fig.update_layout(title="Télédensité mobile (%)", xaxis=dict(dtick=1, range=[2012.8, 2019.2]))
    plotly(fig, 320)
source("ARCEP Togo, observatoire du marché 2013-2019 · Togo Cellulaire = Togocom, Atlantique Telecom = Moov Africa")
insight("Le chiffre d'affaires du secteur est <b>stable autour de 180 milliards FCFA</b> pendant que le nombre d'abonnés Internet est multiplié par dix : "
        "le prix moyen de l'accès s'effondre, ce qui explique une partie de la démocratisation. Les investissements bondissent à "
        "<b>68,5 milliards en 2018</b>, l'année du lancement de la 4G, puis reculent. La télédensité mobile plafonne à 82 % depuis 2017 : "
        "<b>la croissance future viendra de l'usage, pas de nouvelles cartes SIM.</b> Le duopole reste équilibré (51 / 49 en 2019) ; "
        "la valeur 2018 des parts de marché apparaît inversée dans la source.", "gold")
