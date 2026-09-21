# Mobile money et inclusion financière au Togo — tableau de bord

Data Challenge « Économie Numérique » · Défi 2 · Togo AI Lab / MESPTN
Auteur : **SADJINA Christ** · septembre 2026

Tableau de bord interactif (Python · Streamlit · Plotly) qui mesure l'adoption du numérique et le rôle du mobile money
dans l'inclusion financière, à partir des données ouvertes du Géoportail du Togo, de l'ARCEP, de la Banque mondiale et du RGPH-5 2022.

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Reconstruire les données préparées

```bash
python pipeline/build_data.py
```

Le pipeline lit `data/raw/` (exports bruts) et `data/geo/` (contours geoBoundaries) et écrit `data/processed/`.

## Structure

```
app.py                 point d'entrée et navigation
views/                 une page par vue (vue d'ensemble, internet, carte, inclusion, recommandations, méthodologie)
lib/data.py            chargement des données préparées (cache)
lib/ui.py              charte graphique, composants, thème Plotly
pipeline/build_data.py préparation des données (nettoyage, hiérarchie population, jointures, indicateurs)
data/raw/              6 jeux bruts + 2 dictionnaires de champs
data/geo/              contours ADM1 / ADM2 (geoBoundaries, licence ODbL / CC-BY-SA)
data/processed/        tables et GeoJSON prêts pour le dashboard
```

## Sources

- Géoportail Open Data de la République Togolaise : agents mobile money, établissements financiers
- INSEED, RGPH-5 2022 : population résidente par découpage administratif
- ARCEP Togo : abonnés Internet, marché de la téléphonie (2013-2019)
- Banque mondiale, WDI : individus utilisant Internet (% de la population)
- geoBoundaries (OpenStreetMap) : contours administratifs
