"""Captures pleine page de chaque vue du dashboard (QA visuelle + illustrations du rapport).
Usage : python tools/shoot.py [base_url] [largeur]
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
WIDTH = int(sys.argv[2]) if len(sys.argv) > 2 else 1440
OUT = Path(__file__).resolve().parents[1] / "qa"
OUT.mkdir(exist_ok=True)

PAGES = {
    "01_vue_ensemble": "/",
    "02_internet": "/internet",
    "03_carte": "/carte",
    "04_inclusion": "/inclusion",
    "05_recommandations": "/recommandations",
    "06_methodologie": "/methodologie",
}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": WIDTH, "height": 900}, device_scale_factor=1)
    for name, path in PAGES.items():
        pg.goto(BASE + path, wait_until="networkidle")
        time.sleep(4)
        # attendre que les graphiques plotly soient rendus
        try:
            pg.wait_for_selector(".js-plotly-plot .main-svg", timeout=15000)
        except Exception:
            pass
        time.sleep(2)
        # Streamlit défile dans un conteneur interne : on ajuste la hauteur du viewport au contenu
        h = pg.evaluate("document.querySelector('[data-testid=\"stMainBlockContainer\"]').scrollHeight + 80")
        pg.set_viewport_size({"width": WIDTH, "height": min(int(h), 6000)})
        time.sleep(2)
        pg.screenshot(path=str(OUT / f"{name}.png"), full_page=False)
        print(f"{name:22s} {WIDTH}x{h}")
    b.close()
