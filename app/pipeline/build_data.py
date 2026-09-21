"""
Pipeline de préparation des données — Défi 2 « Mobile money et inclusion financière »
Data Challenge Économie Numérique · Togo AI Lab

Entrées  : app/data/raw/*.csv  (exports du Géoportail Open Data + ARCEP + Banque mondiale)
           app/data/geo/togo_adm1.geojson, togo_adm2.geojson (geoBoundaries, OSM, 2017)
Sorties  : app/data/processed/*.csv, *.geojson

Lancer   : python pipeline/build_data.py   (depuis le dossier app/)
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
RAW, GEO, OUT = ROOT / "data" / "raw", ROOT / "data" / "geo", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

GRAND_LOME = {"GOLFE", "AGOE-NYIVE"}          # préfectures du District autonome du Grand Lomé
REGIONS_MM = {"SAVANES", "KARA", "CENTRALE", "PLATEAUX", "MARITIME"}


# ----------------------------------------------------------------------------- utilitaires
def norm(s: str) -> str:
    """Clé de jointure : majuscules, sans accents, espaces normalisés."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.upper().strip())


def parse_point(wkt: str) -> tuple[float, float]:
    """'POINT (lon lat)' -> (lon, lat)."""
    lon, lat = wkt.strip()[len("POINT ("):-1].split()
    return float(lon), float(lat)


def title_fr(s: str) -> str:
    """Libellé lisible depuis une clé normalisée (utilisé pour la population)."""
    return s.title().replace(" De ", " de ").replace("-De-", "-de-")


# ----------------------------------------------------------------------------- 1. mobile money
mm = pd.read_csv(RAW / "agents_mobile_money.csv")
for c in ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd", "operateur"]:
    mm[c] = mm[c].astype(str).str.strip()
mm[["lon", "lat"]] = mm["geometry"].apply(lambda w: pd.Series(parse_point(w)))
mm["moov"] = mm["operateur"].str.contains("Moov").astype(int)
mm["togocom"] = mm["operateur"].str.contains("Togocom").astype(int)
mm["operateur_label"] = pd.Series(
    ["Moov + Togocom" if a and b else "Moov seul" if a else "Togocom seul" if b else "Non renseigné"
     for a, b in zip(mm["moov"], mm["togocom"])]
)
mm["region_key"] = mm["region_nom_bdd"].map(norm)
mm["prefecture_key"] = mm["prefecture_nom_bdd"].map(norm)
mm["commune_key"] = mm["commune_nom_bdd"].map(norm)
mm["canton_key"] = mm["prefecture_key"] + " | " + mm["canton_nom_bdd"].map(norm)

# libellés officiels (accentués) pris dans le fichier mobile money — référence pour tout le projet
LIB_PREF = mm.drop_duplicates("prefecture_key").set_index("prefecture_key")["prefecture_nom_bdd"].to_dict()
LIB_COMM = mm.drop_duplicates("commune_key").set_index("commune_key")["commune_nom_bdd"].to_dict()
PREF_TO_REGION = mm.drop_duplicates("prefecture_key").set_index("prefecture_key")["region_nom_bdd"].to_dict()


def region6(pref_key: str) -> str:
    """6 régions : les 5 régions + le Grand Lomé (Golfe, Agoè-Nyivé), conformément au RGPH-5."""
    return "Grand Lomé" if pref_key in GRAND_LOME else PREF_TO_REGION[pref_key]


mm["region6"] = mm["prefecture_key"].map(region6)
mm_out = mm[["FID", "region6", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd",
             "prefecture_key", "commune_key", "canton_key", "operateur_label", "moov", "togocom", "lon", "lat"]]
mm_out = mm_out.rename(columns={"region6": "region", "prefecture_nom_bdd": "prefecture",
                                "commune_nom_bdd": "commune", "canton_nom_bdd": "canton"})
mm_out.to_csv(OUT / "points_mobile_money.csv", index=False)

# ----------------------------------------------------------------------------- 2. établissements financiers
fe = pd.read_csv(RAW / "etablissements_financiers.csv")
for c in ["region_nom_bdd", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd",
          "nom_localite", "etab_nom", "activite_statut", "activite_categorie"]:
    fe[c] = fe[c].astype(str).str.strip()
fe["categorie"] = fe["activite_categorie"].replace({"Micro-Finace": "Micro-Finance"})
STATUT_ACTIF = {"Utilisé", "Utilise"}
fe["actif"] = fe["activite_statut"].isin(STATUT_ACTIF)
fe["statut"] = fe["activite_statut"].map(lambda s: "En activité" if s in STATUT_ACTIF else
                                        "Fermé / abandonné" if s in {"Fermé", "Abandonné"} else
                                        "En construction / inachevé" if s in {"En construction", "Inacheve", "En réfection"} else
                                        "Non renseigné")
fe[["lon", "lat"]] = fe["geometry"].apply(lambda w: pd.Series(parse_point(w)))
fe["prefecture_key"] = fe["prefecture_nom_bdd"].map(norm)
fe["commune_key"] = fe["commune_nom_bdd"].map(norm)
fe["canton_key"] = fe["prefecture_key"] + " | " + fe["canton_nom_bdd"].map(norm)
fe["region"] = fe["prefecture_key"].map(region6)
fe_out = fe[["FID", "region", "prefecture_nom_bdd", "commune_nom_bdd", "canton_nom_bdd", "nom_localite",
             "etab_nom", "categorie", "statut", "actif", "prefecture_key", "commune_key", "canton_key", "lon", "lat"]]
fe_out = fe_out.rename(columns={"prefecture_nom_bdd": "prefecture", "commune_nom_bdd": "commune",
                                "canton_nom_bdd": "canton", "nom_localite": "localite", "etab_nom": "nom"})
fe_out.to_csv(OUT / "points_etablissements_financiers.csv", index=False)

# ----------------------------------------------------------------------------- 3. population RGPH-5 (hiérarchie aplatie)
pop_raw = pd.read_csv(RAW / "population_rgph5_2022.csv")
pop_raw["key"] = pop_raw["découpage-administratif"].map(norm)
pop_raw["value"] = pop_raw["Value"].astype(int)

PREFS = set(LIB_PREF)
rows, reg, pref, com = [], None, None, None
for key, val in zip(pop_raw["key"], pop_raw["value"]):
    if key == "TOGO":
        lvl = "pays"
    elif key in REGIONS_MM:
        lvl, reg, pref, com = "region", key, None, None
    elif pref and re.fullmatch(re.escape(pref) + r" \d+", key):
        lvl, com = "commune", key
    elif key in PREFS and key != pref:          # (un canton homonyme de sa propre préfecture reste "infra")
        lvl, pref, com = "prefecture", key, None
    else:
        lvl = "infra"          # canton, quartier ou village : niveau non fiable, non utilisé
    rows.append((lvl, reg, pref, com, key, val))
pop = pd.DataFrame(rows, columns=["niveau", "region_key", "prefecture_key", "commune_key", "key", "population"])

# Préfecture d'Avé absente du fichier : reconstruite à partir de ses deux communes
if "AVE" not in set(pop.loc[pop.niveau == "prefecture", "key"]):
    ave = pop[pop.key.str.fullmatch(r"AVE \d+")]
    pop = pd.concat([pop, pd.DataFrame([{"niveau": "prefecture", "region_key": "MARITIME", "prefecture_key": "AVE",
                                         "commune_key": None, "key": "AVE", "population": int(ave.population.sum())}])])
    pop.loc[pop.key.str.startswith("AVE "), "prefecture_key"] = "AVE"
    pop.loc[pop.key.str.startswith("AVE "), "niveau"] = "commune"

# Libellés de commune dupliqués dans la source (AMOU 2 ×2, EST-MONO 1 ×2) : la 2e occurrence correspond à la
# commune manquante de la même préfecture (AMOU 3, EST-MONO 3). Réaffectation validée par l'égalité
# « population de la préfecture = somme de ses communes » (contrôlée plus bas).
pop = pop.reset_index(drop=True)
_c = pop[pop.niveau == "commune"]
for k, grp in _c.groupby("key"):
    if len(grp) > 1:
        pk = grp.prefecture_key.iloc[0]
        have = set(_c[_c.prefecture_key == pk].key)
        missing = sorted(set(c for c in LIB_COMM if c.startswith(pk + " ")) - have)
        for i, miss in zip(grp.index[1:], missing):
            print(f"  réaffectation : ligne {i} '{k}' -> '{miss}'")
            pop.loc[i, "key"] = miss
pop_pref = pop[pop.niveau == "prefecture"][["key", "population"]].rename(columns={"key": "prefecture_key"})
pop_comm = pop[pop.niveau == "commune"][["key", "prefecture_key", "population"]].rename(columns={"key": "commune_key"})
pop_comm = pop_comm[pop_comm.commune_key.isin(set(LIB_COMM))]          # exclut les quartiers "ATIEGOU 2", etc.
# Commune absente de la source alors que la préfecture est complète (BINAH 2) : imputée par différence
for pk, ptot in pop_pref.set_index("prefecture_key").population.items():
    have = pop_comm[pop_comm.prefecture_key == pk]
    missing = sorted(set(c for c in LIB_COMM if c.startswith(pk + " ")) - set(have.commune_key))
    if len(missing) == 1 and ptot - have.population.sum() > 0:
        print(f"  imputation : '{missing[0]}' = {ptot:,} - {have.population.sum():,} = {ptot - have.population.sum():,}")
        pop_comm = pd.concat([pop_comm, pd.DataFrame([{"commune_key": missing[0], "prefecture_key": pk,
                                                       "population": int(ptot - have.population.sum())}])], ignore_index=True)
pop_total = int(pop.loc[pop.niveau == "pays", "population"].iloc[0])
assert len(pop_pref) == 39, f"{len(pop_pref)} préfectures avec population (39 attendues)"
_chk = pop_comm.groupby("prefecture_key").population.sum().rename("somme_communes").to_frame().join(pop_pref.set_index("prefecture_key"))
_bad = _chk[(_chk.somme_communes - _chk.population).abs() > 0]
if len(_bad):
    print("⚠ préfectures dont la somme des communes ≠ valeur :")
    print(_bad)
assert abs(pop_pref.population.sum() - pop_total) < 1000, "somme des préfectures ≠ total Togo"

# ----------------------------------------------------------------------------- 4. table PRÉFECTURES (39)
def agg_points(df: pd.DataFrame, key: str) -> pd.DataFrame:
    g = df.groupby(key)
    out = pd.DataFrame({
        "agents_mm": mm.groupby(key).size() if df is mm else g.size(),
    })
    return out


fe_act = fe[fe.actif]
pref = pd.DataFrame({"prefecture_key": sorted(PREFS)})
pref["prefecture"] = pref.prefecture_key.map(LIB_PREF)
pref["region"] = pref.prefecture_key.map(region6)
pref = pref.merge(pop_pref, on="prefecture_key", how="left")
pref["agents_mm"] = pref.prefecture_key.map(mm.groupby("prefecture_key").size()).fillna(0).astype(int)
for cat, col in [("Banque", "banques"), ("Micro-Finance", "microfinances"), ("Assurance", "assurances"), ("Mutuelle", "mutuelles")]:
    pref[col] = pref.prefecture_key.map(fe_act[fe_act.categorie == cat].groupby("prefecture_key").size()).fillna(0).astype(int)
pref["etab_financiers"] = pref[["banques", "microfinances", "assurances", "mutuelles"]].sum(axis=1)
pref["guichets"] = pref["banques"] + pref["microfinances"]              # points où l'on peut ouvrir un compte / déposer
pref["hab_par_etab_financier"] = (pref.population / pref.etab_financiers.where(pref.etab_financiers > 0)).round(0)
pref["hab_par_banque"] = (pref.population / pref.banques.where(pref.banques > 0)).round(0)
pref["hab_par_agent_mm"] = (pref.population / pref.agents_mm.where(pref.agents_mm > 0)).round(0)
pref["agents_mm_par_1000_hab"] = (pref.agents_mm / pref.population * 1000).round(2)
pref["agents_mm_par_guichet"] = (pref.agents_mm / pref.guichets.where(pref.guichets > 0)).round(1)
pref["part_population"] = (pref.population / pop_total * 100).round(2)
pref["part_agents_mm"] = (pref.agents_mm / len(mm) * 100).round(2)
pref["part_etab_financiers"] = (pref.etab_financiers / len(fe_act) * 100).round(2)
pref["sans_banque"] = pref.banques == 0
pref["sans_etab_financier"] = pref.etab_financiers == 0

# cantons desservis uniquement par le mobile money, par préfecture
cant = pd.DataFrame({"canton_key": sorted(set(mm.canton_key) | set(fe_act.canton_key))})
cant["prefecture_key"] = cant.canton_key.str.split(" \\| ").str[0]
cant["prefecture"] = cant.prefecture_key.map(LIB_PREF)
cant["region"] = cant.prefecture_key.map(region6)
cant["canton"] = cant.canton_key.map(mm.drop_duplicates("canton_key").set_index("canton_key")["canton_nom_bdd"].to_dict())
cant["canton"] = cant["canton"].fillna(cant.canton_key.map(fe.drop_duplicates("canton_key").set_index("canton_key")["canton_nom_bdd"].to_dict()))
cant["commune"] = cant.canton_key.map(mm.drop_duplicates("canton_key").set_index("canton_key")["commune_nom_bdd"].to_dict())
cant["agents_mm"] = cant.canton_key.map(mm.groupby("canton_key").size()).fillna(0).astype(int)
cant["etab_financiers"] = cant.canton_key.map(fe_act.groupby("canton_key").size()).fillna(0).astype(int)
cant["banques"] = cant.canton_key.map(fe_act[fe_act.categorie == "Banque"].groupby("canton_key").size()).fillna(0).astype(int)
cant["lat"] = cant.canton_key.map(mm.groupby("canton_key")["lat"].mean())
cant["lon"] = cant.canton_key.map(mm.groupby("canton_key")["lon"].mean())
cant["profil"] = pd.Series(
    ["Mobile money uniquement" if a > 0 and e == 0 else
     "Mobile money + établissements" if a > 0 and e > 0 else
     "Établissements sans agent MM" if a == 0 and e > 0 else "Aucun service"
     for a, e in zip(cant.agents_mm, cant.etab_financiers)]
)
cant.to_csv(OUT / "cantons.csv", index=False)

mm_only = cant[cant.profil == "Mobile money uniquement"]
pref["cantons_total"] = pref.prefecture_key.map(cant.groupby("prefecture_key").size()).fillna(0).astype(int)
pref["cantons_mm_uniquement"] = pref.prefecture_key.map(mm_only.groupby("prefecture_key").size()).fillna(0).astype(int)
pref["agents_mm_en_zone_mm_uniquement"] = pref.prefecture_key.map(mm_only.groupby("prefecture_key")["agents_mm"].sum()).fillna(0).astype(int)
pref["part_cantons_mm_uniquement"] = (pref.cantons_mm_uniquement / pref.cantons_total * 100).round(1)

# clé cartographique (contours geoBoundaries 2017 : 3 préfectures récentes fusionnées avec leur préfecture d'origine)
MAP_MERGE = {"AGOE-NYIVE": "GOLFE", "KPENDJAL-OUEST": "KPENDJAL", "OTI-SUD": "OTI"}
pref["map_key"] = pref.prefecture_key.map(lambda k: MAP_MERGE.get(k, k))
pref = pref.sort_values(["region", "prefecture"]).reset_index(drop=True)
pref.to_csv(OUT / "prefectures.csv", index=False)

# ----------------------------------------------------------------------------- 5. table COMMUNES (117)
comm = pd.DataFrame({"commune_key": sorted(set(LIB_COMM))})
comm["commune"] = comm.commune_key.map(LIB_COMM)
comm["prefecture_key"] = comm.commune_key.map(mm.drop_duplicates("commune_key").set_index("commune_key")["prefecture_key"].to_dict())
comm["prefecture"] = comm.prefecture_key.map(LIB_PREF)
comm["region"] = comm.prefecture_key.map(region6)
comm = comm.merge(pop_comm[["commune_key", "population"]], on="commune_key", how="left")
comm["agents_mm"] = comm.commune_key.map(mm.groupby("commune_key").size()).fillna(0).astype(int)
comm["etab_financiers"] = comm.commune_key.map(fe_act.groupby("commune_key").size()).fillna(0).astype(int)
comm["banques"] = comm.commune_key.map(fe_act[fe_act.categorie == "Banque"].groupby("commune_key").size()).fillna(0).astype(int)
comm["microfinances"] = comm.commune_key.map(fe_act[fe_act.categorie == "Micro-Finance"].groupby("commune_key").size()).fillna(0).astype(int)
comm["hab_par_etab_financier"] = (comm.population / comm.etab_financiers.where(comm.etab_financiers > 0)).round(0)
comm["hab_par_agent_mm"] = (comm.population / comm.agents_mm.where(comm.agents_mm > 0)).round(0)
comm["agents_mm_par_1000_hab"] = (comm.agents_mm / comm.population * 1000).round(2)
comm["mm_uniquement"] = (comm.agents_mm > 0) & (comm.etab_financiers == 0)
comm["lat"] = comm.commune_key.map(mm.groupby("commune_key")["lat"].mean())
comm["lon"] = comm.commune_key.map(mm.groupby("commune_key")["lon"].mean())
comm = comm.sort_values(["region", "prefecture", "commune"]).reset_index(drop=True)
comm.to_csv(OUT / "communes.csv", index=False)

# ----------------------------------------------------------------------------- 6. table RÉGIONS (6)
reg = pref.groupby("region", as_index=False).agg(
    population=("population", "sum"), agents_mm=("agents_mm", "sum"), banques=("banques", "sum"),
    microfinances=("microfinances", "sum"), assurances=("assurances", "sum"), mutuelles=("mutuelles", "sum"),
    etab_financiers=("etab_financiers", "sum"), guichets=("guichets", "sum"), prefectures=("prefecture", "count"),
    cantons_total=("cantons_total", "sum"), cantons_mm_uniquement=("cantons_mm_uniquement", "sum"),
)
reg["hab_par_etab_financier"] = (reg.population / reg.etab_financiers).round(0)
reg["hab_par_banque"] = (reg.population / reg.banques).round(0)
reg["hab_par_agent_mm"] = (reg.population / reg.agents_mm).round(0)
reg["agents_mm_par_1000_hab"] = (reg.agents_mm / reg.population * 1000).round(2)
reg["agents_mm_par_guichet"] = (reg.agents_mm / reg.guichets).round(1)
reg["part_population"] = (reg.population / pop_total * 100).round(1)
reg["part_agents_mm"] = (reg.agents_mm / len(mm) * 100).round(1)
reg["part_etab_financiers"] = (reg.etab_financiers / len(fe_act) * 100).round(1)
reg.to_csv(OUT / "regions.csv", index=False)

# ----------------------------------------------------------------------------- 7. séries temporelles
wb = pd.read_csv(RAW / "usage_internet_banque_mondiale.csv")
wb = wb[["date", "value"]].rename(columns={"date": "annee", "value": "pct_individus_internet"}).dropna()
wb = wb[wb.annee >= 2000].sort_values("annee")
wb["variation_pts"] = wb.pct_individus_internet.diff().round(2)
wb.to_csv(OUT / "ts_usage_internet.csv", index=False)

OPERATEUR = {"Togo Cellulaire": "Togocom", "Togo Telecom": "Togocom", "Atlantique Telecom": "Moov Africa",
             "Atlantique Telecom Togo": "Moov Africa"}


LABELS = {
    "T Togo Cellulaire": ("Abonnés Internet mobile", "Togocom"),
    "T Atlantique Telecom": ("Abonnés Internet mobile", "Moov Africa"),
    "T Abonnés Internet Togo Telecom": ("Abonnés Internet fixe (Togo Telecom)", "Togocom"),
    "Part de marché Togo Cellulaire (en abonnées) en %": ("Part de marché mobile (%)", "Togocom"),
    "Part de marché Atlantique Telecom Togo (en abonnées)": ("Part de marché mobile (%)", "Moov Africa"),
    "Abonnés GPRS /EDGE Togo Cellulaire": ("Abonnés GPRS/EDGE (2G)", "Togocom"),
    "Abonnés GPRS/EDGE Atlantique Telecom": ("Abonnés GPRS/EDGE (2G)", "Moov Africa"),
    "Nombre de clients 3G Togo Cellulaire": ("Clients 3G", "Togocom"),
    "Nombre de clients 3G Atlantique Telecom": ("Clients 3G", "Moov Africa"),
    "Nombre de clients 4G Togo Cellulaire": ("Clients 4G", "Togocom"),
    "Nombre de clients 4G Atlantique Telecom": ("Clients 4G", "Moov Africa"),
    "T abonnés Internet Fixe et Mobile (Toutes technologies)": ("Abonnés Internet (toutes technologies)", ""),
    "T abonnés Internet haut débit Fixe et Mobile": ("Abonnés Internet haut débit", ""),
    "T abonnés Internet mobiles (Toutes technologies)": ("Abonnés Internet mobile (toutes technologies)", ""),
    "T abonnés Internet mobiles (Haut débit)": ("Abonnés Internet mobile haut débit", ""),
    "Le nombre total d'abonnés fixe et mobile": ("Abonnés téléphonie (fixe + mobile)", ""),
    "Le nombre total d'abonnées mobiles GSM": ("Abonnés mobile GSM", ""),
    "Le nombre total d'abonnés fixe": ("Abonnés téléphonie fixe", ""),
    "Chiffres d'Affaires": ("Chiffre d'affaires du secteur (FCFA)", ""),
    "Investissement": ("Investissements du secteur (FCFA)", ""),
    "ARPU segment mobile GSM": ("ARPU mobile (indice, unité source incohérente)", ""),
}


def clean_ind(label: str) -> tuple[str, str]:
    """(indicateur lisible, opérateur)"""
    if label.strip() in LABELS:
        return LABELS[label.strip()]
    op = ""
    for k, v in OPERATEUR.items():
        if k in label:
            op = v
    lab = label
    for k in OPERATEUR:
        lab = lab.replace(k, "").strip()
    lab = re.sub(r"^T\s+", "", lab).strip(" -")
    return lab, op


def load_arcep(fname: str, famille: str) -> pd.DataFrame:
    d = pd.read_csv(RAW / fname)
    d.columns = [c.strip().lower() for c in d.columns]
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d["annee"] = d["date"].astype(int)
    d[["indicateur_clean", "operateur"]] = d["indicateur"].apply(lambda s: pd.Series(clean_ind(s)))
    d["famille"] = famille
    return d[["famille", "indicateur", "indicateur_clean", "operateur", "unit", "annee", "value"]]


arcep = pd.concat([load_arcep("abonnes_internet_arcep.csv", "Internet"),
                   load_arcep("marche_telephonie_arcep.csv", "Téléphonie")], ignore_index=True)
arcep.to_csv(OUT / "ts_arcep.csv", index=False)

# ----------------------------------------------------------------------------- 8. contours cartographiques
adm2 = json.load(open(GEO / "togo_adm2.geojson", encoding="utf-8"))
RENAME_GEO = {"AVE": "AVE", "KERAN": "KERAN", "TANDJOUARE": "TANDJOARE", "TONE": "TONE", "PLAINE DE MO": "MO",
              "LOME COMMUNE": "GOLFE"}
feats = {}
for f in adm2["features"]:
    k = norm(f["properties"]["shapeName"])
    k = RENAME_GEO.get(k, k)
    feats.setdefault(k, []).append(shape(f["geometry"]))
geo_pref = {"type": "FeatureCollection", "features": []}
for k, geoms in feats.items():
    g = unary_union(geoms).simplify(0.002, preserve_topology=True)
    libel = LIB_PREF.get(k, k.title())
    if k == "GOLFE":
        libel = "Golfe + Agoè-Nyivé (Grand Lomé)"
    elif k == "KPENDJAL":
        libel = "Kpendjal + Kpendjal-Ouest"
    elif k == "OTI":
        libel = "Oti + Oti-Sud"
    geo_pref["features"].append({"type": "Feature", "id": k, "properties": {"map_key": k, "libelle": libel}, "geometry": mapping(g)})
json.dump(geo_pref, open(OUT / "prefectures.geojson", "w", encoding="utf-8"))
missing = set(pref.map_key) - set(feats)
assert not missing, f"préfectures sans contour : {missing}"

adm1 = json.load(open(GEO / "togo_adm1.geojson", encoding="utf-8"))
reg_geoms = {norm(f["properties"]["shapeName"]).replace(" REGION", ""): shape(f["geometry"]) for f in adm1["features"]}
grand_lome = unary_union(feats["GOLFE"])
reg_geoms["MARITIME"] = reg_geoms["MARITIME"].difference(grand_lome)
reg_geoms["GRAND LOME"] = grand_lome
LIB_REG = {"SAVANES": "Savanes", "KARA": "Kara", "CENTRALE": "Centrale", "PLATEAUX": "Plateaux", "MARITIME": "Maritime", "GRAND LOME": "Grand Lomé"}
geo_reg = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "id": LIB_REG[k], "properties": {"region": LIB_REG[k]}, "geometry": mapping(g.simplify(0.002, preserve_topology=True))}
    for k, g in reg_geoms.items()]}
json.dump(geo_reg, open(OUT / "regions.geojson", "w", encoding="utf-8"))

# ----------------------------------------------------------------------------- 9. indicateurs nationaux
kpi = {
    "population_2022": pop_total,
    "agents_mm": int(len(mm)),
    "etab_financiers_actifs": int(len(fe_act)),
    "etab_financiers_total": int(len(fe)),
    "banques": int((fe_act.categorie == "Banque").sum()),
    "microfinances": int((fe_act.categorie == "Micro-Finance").sum()),
    "assurances": int((fe_act.categorie == "Assurance").sum()),
    "mutuelles": int((fe_act.categorie == "Mutuelle").sum()),
    "hab_par_etab_financier": round(pop_total / len(fe_act)),
    "hab_par_banque": round(pop_total / (fe_act.categorie == "Banque").sum()),
    "hab_par_agent_mm": round(pop_total / len(mm)),
    "agents_mm_par_1000_hab": round(len(mm) / pop_total * 1000, 2),
    "agents_mm_par_guichet": round(len(mm) / fe_act.categorie.isin(["Banque", "Micro-Finance"]).sum(), 1),
    "cantons_total": int(len(cant)),
    "cantons_mm_uniquement": int(len(mm_only)),
    "agents_mm_en_zone_mm_uniquement": int(mm_only.agents_mm.sum()),
    "prefectures_sans_banque": int(pref.sans_banque.sum()),
    "prefectures_sans_etab_financier": int(pref.sans_etab_financier.sum()),
    "communes_mm_uniquement": int(comm.mm_uniquement.sum()),
    "pct_internet_2022": float(wb[wb.annee == 2022].pct_individus_internet.iloc[0]),
    "agents_mm_non_renseigne_pct": round(float((mm.operateur_label == "Non renseigné").mean() * 100), 1),
}
json.dump(kpi, open(OUT / "kpi_national.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ----------------------------------------------------------------------------- rapport
print("=== Pipeline OK ===")
print(f"population Togo 2022           : {pop_total:,}")
print(f"préfectures                    : {len(pref)}  (population : {pref.population.notna().sum()})")
print(f"communes                       : {len(comm)}  (population : {comm.population.notna().sum()})")
print(f"cantons                        : {len(cant)}  dont MM uniquement : {len(mm_only)}  ({mm_only.agents_mm.sum():,} agents)")
print(f"établissements financiers      : {len(fe)} dont actifs {len(fe_act)}")
print(f"régions (6)                    : {', '.join(reg.region)}")
print(f"préfectures sans banque        : {', '.join(pref[pref.sans_banque].prefecture)}")
print(f"séries ARCEP                   : {arcep.indicateur.nunique()} indicateurs, {arcep.annee.min()}-{arcep.annee.max()}")
print(f"contours                       : {len(geo_pref['features'])} préfectures cartographiques, {len(geo_reg['features'])} régions")
print(json.dumps(kpi, indent=2, ensure_ascii=False))
