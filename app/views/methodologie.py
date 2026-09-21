from pathlib import Path

import pandas as pd
import streamlit as st

from lib import data as D
from lib.ui import header, insight, source

k = D.kpi()
header("Méthodologie, sources et limites", "Tout ce qui a été fait aux données avant d'être montré — et ce que ces données ne permettent pas de dire.")

st.markdown("### Sources")
src = pd.DataFrame([
    ["Agents mobile money", "Géoportail Open Data du Togo (MESPTN)", "19 788 points géolocalisés, région → canton, opérateur(s)", "Export CSV, décembre 2024"],
    ["Établissements financiers", "Géoportail Open Data du Togo", "738 points : banques, microfinances, assurances, mutuelles ; statut d'activité", "Export CSV, janvier 2025"],
    ["Population résidente 2022", "INSEED, RGPH-5 (via Géoportail, indicateurs)", "759 unités : pays, régions, préfectures, communes, cantons/quartiers", "Hiérarchie aplatie"],
    ["Usage d'Internet", "Banque mondiale, WDI (IT.NET.USER.ZS)", "% d'individus utilisant Internet, 1960-2022", "Annuel"],
    ["Abonnés Internet", "ARCEP Togo (via Géoportail)", "25 indicateurs : abonnés par technologie et opérateur, taux de pénétration", "2013-2019"],
    ["Marché de la téléphonie", "ARCEP Togo (via Géoportail)", "10 indicateurs : abonnés, télédensité, CA, investissements, ARPU, parts de marché", "2013-2019"],
    ["Contours administratifs", "geoBoundaries (OSM, Wambacher), gbOpen", "5 régions, 37 préfectures — découpage 2017", "Source externe, licence ODbL / CC-BY-SA"],
], columns=["Jeu de données", "Producteur", "Contenu", "Période / note"])
_md = "| " + " | ".join(src.columns) + " |
|" + "---|" * len(src.columns) + "
" + "
".join("| " + " | ".join(str(v) for v in row) + " |" for row in src.values)
st.markdown(_md)

st.markdown("### Traitements")
st.markdown("""
1. **Géométrie** : parsing du WKT `POINT (longitude latitude)` — longitude en premier — en colonnes `lon` / `lat`.
2. **Population** : la source liste 759 unités sans indiquer leur niveau. La hiérarchie a été reconstruite par la structure du fichier (région → préfecture → communes numérotées « Préfecture n » → cantons/quartiers) et validée par l'égalité *population de la préfecture = somme de ses communes*. Trois corrections documentées :
   - la préfecture d'**Avé** n'a pas de ligne : reconstruite = Avé 1 + Avé 2 (111 214) ;
   - deux libellés dupliqués (**Amou 2**, **Est-Mono 1**) : la seconde occurrence réaffectée à la commune manquante de la même préfecture (Amou 3, Est-Mono 3), ce qui rétablit l'égalité de contrôle ;
   - **Binah 2** absente : imputée par différence (84 199 − 44 039 = 40 160).
   Danyi 1 et Danyi 2 sont publiées agrégées : population non ventilée à la commune. Le niveau canton n'est pas exploité pour la population (le Grand Lomé est détaillé en quartiers, non en cantons).
3. **Six régions** : Golfe et Agoè-Nyivé (2 188 376 habitants) sont publiés hors de la région Maritime dans le RGPH-5, conformément au District autonome du Grand Lomé. Le dashboard suit ce découpage.
4. **Établissements financiers** : 14 valeurs de statut harmonisées ; seuls les établissements « Utilisé » (660 sur 738) entrent dans les ratios. Coquille `Micro-Finace` fusionnée.
5. **Agents mobile money** : champ opérateur multi-valué (« Moov, Togocom ») éclaté en indicateurs Moov / Togocom ; 6,8 % non renseignés conservés dans les comptages.
6. **Séries ARCEP** : opérateurs relabellisés (Togo Cellulaire → Togocom, Atlantique Telecom → Moov Africa). L'ARPU est publié dans une unité incohérente (10¹³ FCFA) et n'est pas affiché. La valeur 2018 des parts de marché apparaît inversée entre opérateurs dans la source.
7. **Cartographie** : les contours 2017 ne connaissent pas Agoè-Nyivé, Kpendjal-Ouest ni Oti-Sud ; ces préfectures sont cartographiées avec leur préfecture d'origine (Golfe, Kpendjal, Oti), les indicateurs étant recalculés sur l'ensemble fusionné. Les tableaux conservent les 39 préfectures actuelles.
""")

st.markdown("### Définitions")
st.markdown("""
- **Guichet financier** : banque ou institution de microfinance en activité (points où l'on peut ouvrir un compte, déposer et retirer).
- **Canton « mobile money uniquement »** : canton comptant au moins un agent mobile money et aucun établissement financier en activité.
- **Habitants par point de service** : population 2022 / nombre de points en activité, à la maille considérée.
- **Indice de priorité** (page Recommandations) : moyenne pondérée normalisée de trois écarts — 50 % habitants par établissement, 25 % agents pour 1 000 habitants (inversé), 25 % part des cantons mobile money uniquement.
""")

st.markdown("### Limites")
insight("""
<b>Ce que ces données ne disent pas.</b>
<ul style="margin:.4rem 0 0 1rem">
<li>Le nombre d'<b>agents</b> n'est pas le volume de <b>transactions</b> ni le nombre de comptes actifs : il mesure l'accès physique, pas l'usage.</li>
<li>Aucune donnée d'usage d'Internet n'existe à l'échelle infranationale : la fracture numérique territoriale n'est approchée que par les points de service financiers.</li>
<li>Les séries ARCEP s'arrêtent en 2019 ; l'évolution 2020-2022 repose sur la seule source Banque mondiale.</li>
<li>Les fichiers de points datent de décembre 2024 / janvier 2025, la population de 2022 : les ratios mélangent deux dates proches mais distinctes.</li>
<li>Les contours administratifs sont ceux de 2017 (source externe) ; le Géoportail ne publie pas de limites de préfecture.</li>
</ul>
""", "gold")

st.markdown("### Reproductibilité et données téléchargeables")
st.markdown("Le pipeline `pipeline/build_data.py` reconstruit toutes les tables à partir des fichiers bruts en une commande. "
            "Les tables préparées sont téléchargeables ci-dessous.")
P = Path(__file__).resolve().parents[1] / "data" / "processed"
cols = st.columns(4)
for i, (f, lbl) in enumerate([("prefectures.csv", "Préfectures (39)"), ("communes.csv", "Communes (117)"), ("cantons.csv", "Cantons (373)"),
                              ("regions.csv", "Régions (6)"), ("ts_usage_internet.csv", "Usage Internet"), ("ts_arcep.csv", "Séries ARCEP"),
                              ("points_etablissements_financiers.csv", "Établissements (points)"), ("points_mobile_money.csv", "Agents MM (points)")]):
    cols[i % 4].download_button(lbl, (P / f).read_bytes(), f, "text/csv", use_container_width=True)
source("Dashboard réalisé avec Python · Streamlit · Plotly. Auteur : SADJINA Christ, septembre 2026.")
