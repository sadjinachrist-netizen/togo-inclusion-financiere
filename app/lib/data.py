"""Chargement des données préparées (cache Streamlit)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"

REGION_ORDER = ["Grand Lomé", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"]


@st.cache_data(show_spinner=False)
def kpi() -> dict:
    return json.load(open(P / "kpi_national.json", encoding="utf-8"))


@st.cache_data(show_spinner=False)
def regions() -> pd.DataFrame:
    d = pd.read_csv(P / "regions.csv")
    d["region"] = pd.Categorical(d["region"], REGION_ORDER, ordered=True)
    return d.sort_values("region").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def prefectures() -> pd.DataFrame:
    return pd.read_csv(P / "prefectures.csv")


@st.cache_data(show_spinner=False)
def communes() -> pd.DataFrame:
    return pd.read_csv(P / "communes.csv")


@st.cache_data(show_spinner=False)
def cantons() -> pd.DataFrame:
    return pd.read_csv(P / "cantons.csv")


@st.cache_data(show_spinner=False)
def points_fin() -> pd.DataFrame:
    return pd.read_csv(P / "points_etablissements_financiers.csv")


@st.cache_data(show_spinner=False)
def points_mm() -> pd.DataFrame:
    return pd.read_csv(P / "points_mobile_money.csv")


@st.cache_data(show_spinner=False)
def ts_internet() -> pd.DataFrame:
    return pd.read_csv(P / "ts_usage_internet.csv")


@st.cache_data(show_spinner=False)
def ts_arcep() -> pd.DataFrame:
    return pd.read_csv(P / "ts_arcep.csv")


@st.cache_data(show_spinner=False)
def geo_prefectures() -> dict:
    return json.load(open(P / "prefectures.geojson", encoding="utf-8"))


@st.cache_data(show_spinner=False)
def geo_regions() -> dict:
    return json.load(open(P / "regions.geojson", encoding="utf-8"))


def arcep_series(name_contains: str, famille: str | None = None, operateur: str | None = None) -> pd.DataFrame:
    d = ts_arcep()
    m = d["indicateur"].str.contains(name_contains, case=False, regex=False)
    if famille:
        m &= d["famille"] == famille
    if operateur is not None:
        m &= d["operateur"] == operateur
    return d[m].sort_values("annee")
