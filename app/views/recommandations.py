import plotly.graph_objects as go
import streamlit as st

from lib import data as D
from lib.ui import C, REGION_COLORS, fmt, header, insight, plotly, reco, source

k = D.kpi()
pref = D.prefectures()
reg = D.regions()
cant = D.cantons()

header(
    "Six recommandations, chacune rattachée à un territoire et à un nombre d'habitants",
    "Priorisées par population concernée et par écart à la moyenne nationale. Les cibles sont calculées à partir du dashboard.",
)

sans_banque = pref[pref.sans_banque].sort_values("population", ascending=False)
mm_only = cant[cant.profil == "Mobile money uniquement"]
nat = k["hab_par_etab_financier"]
sousdot = pref[pref.hab_par_etab_financier > 2 * nat].sort_values("hab_par_etab_financier", ascending=False)
plateaux = reg[reg.region == "Plateaux"].iloc[0]
savanes = reg[reg.region == "Savanes"].iloc[0]
kpendjal = pref[pref.prefecture == "Kpendjal"].iloc[0]

# cible : ramener chaque préfecture sous-dotée à 2× la moyenne nationale
sousdot = sousdot.assign(cible_etab=(sousdot.population / (2 * nat)).round().astype(int) - sousdot.etab_financiers)
sousdot["cible_etab"] = sousdot["cible_etab"].clip(lower=1)

reco(1, "Faire des agents mobile money des guichets de services financiers complets",
     fmt(mm_only.agents_mm.sum()), f"agents dans {len(mm_only)} cantons sans aucun établissement financier",
     "Dans deux cantons sur trois, l'agent mobile money est le seul point d'accès financier. Élargir son rôle — ouverture de compte d'épargne, "
     "micro-crédit, micro-assurance, paiement de factures et de services publics — par des partenariats banques / microfinances / opérateurs, "
     "avec une formation certifiante des agents. Priorité aux Plateaux (74 cantons) et à la Kara (58 cantons).",
     "Priorité haute", "red", red=True)

reco(2, f"Ouvrir un guichet bancaire ou de microfinance dans les {len(sans_banque)} préfectures sans banque",
     fmt(sans_banque.population.sum()), "habitants sans aucune banque dans leur préfecture",
     "Par ordre de population : " + ", ".join(f"{r.prefecture} ({fmt(r.population)})" for r in sans_banque.itertuples()) + ". "
     f"Kpendjal n'a <b>aucun</b> établissement financier et 41 agents mobile money pour {fmt(kpendjal.population)} habitants : c'est le territoire prioritaire du pays. "
     "Cible : un guichet de microfinance par chef-lieu de préfecture en 24 mois, adossé à un agent mobile money « super-agent » pour la liquidité.",
     "Priorité haute", "red", red=True)

reco(3, f"Rattraper les {len(sousdot)} préfectures à plus de deux fois la moyenne nationale d'habitants par établissement",
     f"+{int(sousdot.cible_etab.sum())}", "établissements à créer pour ramener chacune sous 24 500 habitants par point de service",
     "Cibles par préfecture : " + ", ".join(f"{r.prefecture} +{r.cible_etab}" for r in sousdot.itertuples()) + ". "
     "Ces créations peuvent être des guichets légers (microfinance, mutuelle) plutôt que des agences bancaires classiques.",
     "Priorité haute", "red", red=True)

reco(4, "Rééquilibrer les Plateaux et les Savanes, les deux régions où l'offre décroche de la population",
     f"{fmt(plateaux.population + savanes.population)}", "habitants dans deux régions qui cumulent 34 % de la population et 23 % des établissements",
     f"Les Plateaux ont le plus faible taux d'agents mobile money du pays ({fmt(plateaux.agents_mm_par_1000_hab, 2)} pour 1 000 habitants contre "
     f"{fmt(k['agents_mm_par_1000_hab'], 2)} en moyenne) ; les Savanes le plus fort ratio d'agents par guichet ({fmt(savanes.agents_mm_par_guichet, 1)} contre "
     f"{fmt(k['agents_mm_par_guichet'], 1)}). Deux leviers différents : densifier le réseau d'agents dans les Plateaux, "
     "densifier les guichets dans les Savanes.",
     "Priorité moyenne", "gold")

reco(5, "Accélérer l'usage d'Internet : passer de 37,6 % à 50 % d'individus connectés",
     fmt(k["population_2022"] * (0.50 - k["pct_internet_2022"] / 100)), "personnes supplémentaires à connecter pour atteindre 50 %",
     "La télédensité mobile plafonne à 82 % depuis 2017 : la croissance viendra de l'usage, non de nouvelles SIM. Trois leviers : "
     "couverture 4G hors du Grand Lomé (174 000 clients 4G en 2019, 6 900 abonnés fibre), tarification des forfaits data d'entrée de gamme, "
     "et services publics numériques qui créent la raison de se connecter — l'année 2020 (+8,3 points) a montré que l'usage suit l'utilité.",
     "Priorité moyenne", "gold")

reco(6, "Mettre à jour et compléter l'open data",
     "2019", "dernière année publiée pour le marché télécom (ARCEP)",
     f"Les séries ARCEP s'arrêtent en 2019 ; les trois années les plus dynamiques ne sont documentées que par la Banque mondiale. "
     f"{fmt(k['agents_mm_non_renseigne_pct'], 1)} % des agents mobile money n'ont pas d'opérateur renseigné ; le fichier population publie la hiérarchie "
     "administrative sans colonne de niveau, avec deux libellés dupliqués et une préfecture absente ; les contours administratifs récents "
     "(Agoè-Nyivé, Kpendjal-Ouest, Oti-Sud) ne sont pas disponibles en open data. Publier ces éléments rendrait le suivi de l'inclusion financière reproductible chaque année.",
     "Données", "green")

# ------------------------------------------------------------------ carte de priorité
st.markdown("### Indice de priorité par préfecture")
st.markdown("<div class='kicker'>Combinaison de trois écarts à la moyenne nationale : habitants par établissement, agents mobile money pour 1 000 habitants "
            "(inversé) et part des cantons desservis uniquement par le mobile money. 0 = aucun déficit, 100 = déficit maximal observé.</div>", unsafe_allow_html=True)


def score(s, invert=False):
    s = s.fillna(s.max())
    r = (s - s.min()) / (s.max() - s.min())
    return 1 - r if invert else r


p = pref.copy()
p["score"] = (100 * (0.5 * score(p.hab_par_etab_financier) + 0.25 * score(p.agents_mm_par_1000_hab, invert=True) + 0.25 * score(p.part_cantons_mm_uniquement))).round(0)
p = p.sort_values("score", ascending=False)
fig = go.Figure()
for r_ in ["Grand Lomé", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]:
    d = p[p.region == r_]
    fig.add_trace(go.Bar(
        x=d.prefecture, y=d.score, name=r_, marker_color=REGION_COLORS[r_],
        customdata=d[["region", "population", "hab_par_etab_financier", "agents_mm_par_1000_hab", "part_cantons_mm_uniquement"]].values,
        hovertemplate="<b>%{x}</b> (%{customdata[0]}) · indice %{y}<br>%{customdata[1]:,.0f} habitants<br>%{customdata[2]:,.0f} hab./établissement · "
                      "%{customdata[3]:.2f} agents/1000 hab. · %{customdata[4]:.0f} % de cantons MM seul<extra></extra>",
    ))
fig.update_layout(xaxis=dict(categoryorder="array", categoryarray=list(p.prefecture)), barmode="stack", bargap=0.15, legend_y=1.08)
fig.update_layout(xaxis_title="", yaxis_title="Indice de priorité (0-100)", xaxis_tickangle=-45)
plotly(fig, 380)
source("Calcul : 50 % habitants par établissement · 25 % agents MM pour 1 000 hab. (inversé) · 25 % part des cantons MM uniquement — normalisation min-max")
top5 = p.head(5)
_ps = int(top5.region.isin(["Plateaux", "Savanes"]).sum())
insight("<b>Cinq préfectures prioritaires : " + ", ".join(top5.prefecture) + ".</b> Elles totalisent "
        f"{fmt(top5.population.sum())} habitants. Aucune n'est dans le Grand Lomé ; {_ps} sur 5 sont dans les Plateaux ou les Savanes.", "red")
