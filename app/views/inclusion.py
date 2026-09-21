import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, fmt, header, insight, kpi_row, plotly, source

k = D.kpi()
pref = D.prefectures()
comm = D.communes()
cant = D.cantons()
mmp = D.points_mm()
fin = D.points_fin()

header(
    "Mobile money et inclusion financière : là où l'agent est le seul guichet",
    "Rapport entre points d'accès et population, par préfecture et par commune. Identification des territoires desservis uniquement par le mobile money.",
)

# ------------------------------------------------------------------ filtres
regions = ["Toutes"] + [r for r in ["Grand Lomé", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]]
f1, f2 = st.columns([1, 2])
rsel = f1.selectbox("Région", regions)
p = pref if rsel == "Toutes" else pref[pref.region == rsel]
c = comm if rsel == "Toutes" else comm[comm.region == rsel]
ct = cant if rsel == "Toutes" else cant[cant.region == rsel]
mm_only = ct[ct.profil == "Mobile money uniquement"]

kpi_row([
    ("Population", fmt(p.population.sum()), f"{len(p)} préfecture(s) · {len(c)} communes", ""),
    ("Habitants par établissement", fmt(p.population.sum() / max(p.etab_financiers.sum(), 1)), f"{p.etab_financiers.sum()} établissements en activité", ""),
    ("Habitants par agent MM", fmt(p.population.sum() / max(p.agents_mm.sum(), 1)), f"{fmt(p.agents_mm.sum())} agents", ""),
    ("Cantons MM uniquement", f"{len(mm_only)} / {len(ct)}", f"{fmt(len(mm_only) / max(len(ct), 1) * 100, 0, ' %')} des cantons · {fmt(mm_only.agents_mm.sum())} agents", "red"),
    ("Préfectures sans banque", f"{int(p.sans_banque.sum())} / {len(p)}", fmt(p[p.sans_banque].population.sum()) + " habitants", "red"),
])

# ------------------------------------------------------------------ nuage préfectures
st.markdown("### Population et points de service : qui est sous-doté ?")
c1, c2 = st.columns([1.4, 1])
with c1:
    nat = k["hab_par_etab_financier"]
    pp = p.copy()
    pp["label"] = [n if (h > 2 * nat or pop_ > 280000 or e == 0) else "" for n, h, pop_, e in zip(pp.prefecture, pp.hab_par_etab_financier.fillna(1e9), pp.population, pp.etab_financiers)]
    fig = px.scatter(
        pp, x="population", y="etab_financiers", size="agents_mm", color="region", color_discrete_map=REGION_COLORS,
        hover_name="prefecture", size_max=42, text="label", log_x=True, log_y=True,
        labels={"population": "Population 2022", "etab_financiers": "Établissements financiers en activité", "region": "", "agents_mm": "Agents MM"},
        custom_data=["prefecture", "agents_mm", "hab_par_etab_financier", "banques"],
    )
    fig.update_traces(textposition="top center", textfont_size=10,
                      hovertemplate="<b>%{customdata[0]}</b><br>%{x:,.0f} habitants · %{y} établissements (%{customdata[3]} banques)<br>%{customdata[1]:,.0f} agents MM · %{customdata[2]:,.0f} hab./établissement<extra></extra>")
    xs = [p.population.min() * 0.9, p.population.max() * 1.1]
    fig.add_trace(go.Scatter(x=xs, y=[x / nat for x in xs], mode="lines", line=dict(color=C["muted"], dash="dot", width=1),
                             name=f"Moyenne nationale ({fmt(nat)} hab./étab.)", hoverinfo="skip"))
    fig.update_layout(legend_y=1.08, xaxis=dict(title="Population 2022 (échelle log)", tickvals=[50000, 100000, 200000, 500000, 1000000, 2000000], ticktext=["50 k", "100 k", "200 k", "500 k", "1 M", "2 M"]), yaxis=dict(title="Établissements financiers (échelle log)", tickvals=[1, 2, 5, 10, 20, 50, 100, 200]))
    plotly(fig, 430)
    source("Taille des bulles = nombre d'agents mobile money · sous la ligne pointillée : moins bien doté que la moyenne nationale")
with c2:
    st.markdown("**Habitants par établissement financier**")
    d = p.sort_values("hab_par_etab_financier", ascending=False).head(12)
    fig = go.Figure(go.Bar(
        x=d.hab_par_etab_financier, y=d.prefecture, orientation="h",
        marker_color=[REGION_COLORS[r] for r in d.region], text=[fmt(v) for v in d.hab_par_etab_financier],
        textposition="outside", cliponaxis=False,
        customdata=d[["etab_financiers", "region"]].values,
        hovertemplate="<b>%{y}</b> (%{customdata[1]})<br>%{x:,.0f} hab. / établissement · %{customdata[0]} établissements<extra></extra>",
    ))
    fig.add_vline(x=nat, line_dash="dot", line_color=C["muted"])
    fig.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis=dict(showticklabels=False, title=""), margin=dict(r=70, t=10))
    plotly(fig, 430)

insight("<b>La ligne pointillée est la moyenne nationale (12 266 habitants par établissement).</b> Toutes les préfectures situées en dessous sont "
        "sous-dotées. Akébou, Est-Mono et Kpendjal-Ouest comptent <b>entre 41 000 et 74 000 habitants par établissement</b> — de trois à six fois "
        "la moyenne — et aucune banque. Les grosses bulles basses (Tône, Haho, Ogou) sont des préfectures peuplées où le mobile money "
        "compense un réseau bancaire très mince.", "red")

# ------------------------------------------------------------------ MM uniquement
st.markdown("### Les territoires desservis uniquement par le mobile money")
c3, c4 = st.columns([1, 1.3])
with c3:
    prof = ct.groupby("profil").agg(cantons=("canton_key", "count"), agents=("agents_mm", "sum")).reset_index()
    order = ["Mobile money uniquement", "Mobile money + établissements", "Établissements sans agent MM", "Aucun service"]
    prof["profil"] = pd.Categorical(prof.profil, order, ordered=True)
    prof = prof.sort_values("profil")
    fig = go.Figure(go.Pie(labels=prof.profil.astype(str), values=prof.cantons, hole=0.58, sort=False,
                           marker_colors=[C["red"], C["green"], C["gold"], "#B8C4BE"][: len(prof)],
                           textinfo="value+percent", hovertemplate="<b>%{label}</b><br>%{value} cantons<extra></extra>"))
    fig.update_layout(title="Profil des cantons", legend=dict(orientation="v", y=0.5, x=1.0), margin=dict(t=40),
                      annotations=[dict(text=f"{len(ct)}<br>cantons", x=0.5, y=0.5, showarrow=False, font_size=16, font_color=C["green_dark"])])
    plotly(fig, 340)
with c4:
    d = p.sort_values("cantons_mm_uniquement", ascending=False).head(12)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d.prefecture, y=d.cantons_mm_uniquement, name="Cantons MM uniquement", marker_color=C["red"],
                         hovertemplate="<b>%{x}</b><br>%{y} cantons desservis uniquement par le mobile money<extra></extra>"))
    fig.add_trace(go.Bar(x=d.prefecture, y=d.cantons_total - d.cantons_mm_uniquement, name="Autres cantons", marker_color="#D5E0DA",
                         hovertemplate="<b>%{x}</b><br>%{y} autres cantons<extra></extra>"))
    fig.update_layout(barmode="stack", title="Préfectures comptant le plus de cantons « mobile money uniquement »", xaxis_title="", yaxis_title="Cantons", legend=dict(orientation="h", y=-0.35))
    plotly(fig, 340)
source("Un canton est « mobile money uniquement » s'il compte au moins un agent et aucun établissement financier en activité")

insight(f"<b>{k['cantons_mm_uniquement']} cantons sur {k['cantons_total']} — {fmt(k['cantons_mm_uniquement'] / k['cantons_total'] * 100, 0)} % — n'ont pour seul service financier que leurs agents mobile money.</b> "
        f"Ils hébergent {fmt(k['agents_mm_en_zone_mm_uniquement'])} agents. Dans les Plateaux, ce sont 74 cantons sur 110 ; dans la Kara, 58 sur 72. "
        f"À l'échelle des communes, {k['communes_mm_uniquement']} communes sur 117 sont dans ce cas. "
        "Ces territoires ne sont pas des zones blanches : le service existe, mais il est réduit au dépôt, au retrait et au transfert.", "red")

# ------------------------------------------------------------------ opérateurs et tableau
c5, c6 = st.columns([1, 1.6])
with c5:
    st.markdown("### Qui opère les agents ?")
    mmr = mmp if rsel == "Toutes" else mmp[mmp.region == rsel]
    op = mmr.operateur_label.value_counts().reindex(["Moov + Togocom", "Togocom seul", "Moov seul", "Non renseigné"]).fillna(0)
    fig = go.Figure(go.Bar(x=op.values, y=op.index, orientation="h",
                           marker_color=[C["green_dark"], C["green"], C["gold"], "#B8C4BE"],
                           text=[f"{fmt(v)} ({fmt(v / op.sum() * 100, 1)} %)" for v in op.values], textposition="outside", cliponaxis=False,
                           hovertemplate="<b>%{y}</b> : %{x:,.0f} agents<extra></extra>"))
    fig.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis=dict(showticklabels=False), margin=dict(r=110, t=10))
    plotly(fig, 260)
    insight(f"Deux agents sur trois servent <b>les deux opérateurs</b> : le réseau est largement interopérable au niveau du point de vente. "
            f"{fmt(k['agents_mm_non_renseigne_pct'], 1)} % des agents n'ont pas d'opérateur renseigné.")
with c6:
    st.markdown("### Communes : le détail")
    t = c[["commune", "prefecture", "region", "population", "etab_financiers", "banques", "agents_mm", "hab_par_etab_financier", "agents_mm_par_1000_hab", "mm_uniquement"]].copy()
    t = t.rename(columns={"commune": "Commune", "prefecture": "Préfecture", "region": "Région", "population": "Population", "etab_financiers": "Étab. fin.",
                          "banques": "Banques", "agents_mm": "Agents MM", "hab_par_etab_financier": "Hab./étab.", "agents_mm_par_1000_hab": "Agents/1000 hab.",
                          "mm_uniquement": "MM uniquement"})
    only = st.checkbox("Afficher uniquement les communes desservies par le seul mobile money", value=False)
    if only:
        t = t[t["MM uniquement"]]
    st.dataframe(t.sort_values("Hab./étab.", ascending=False), hide_index=True, use_container_width=True, height=330,
                 column_config={"Population": st.column_config.NumberColumn(format="localized"), "Hab./étab.": st.column_config.NumberColumn(format="localized"),
                                "Agents/1000 hab.": st.column_config.NumberColumn(format="%.2f"), "MM uniquement": st.column_config.CheckboxColumn()})
    st.download_button("Télécharger les communes (CSV)", t.to_csv(index=False).encode("utf-8-sig"), "communes_inclusion.csv", "text/csv")
source("Population communale : RGPH-5 2022 ; Danyi 1 et Danyi 2 sont publiées agrégées dans la source (population non ventilée)")
