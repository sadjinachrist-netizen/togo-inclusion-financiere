"""
Mobile money et inclusion financière au Togo — tableau de bord interactif
Data Challenge Économie Numérique · Défi 2 · Togo AI Lab / MESPTN
Auteur : SADJINA Christ

Lancer : streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="Inclusion financière numérique · Togo",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

from lib.ui import inject_css  # noqa: E402

inject_css()

pages = {
    "Diagnostic": [
        st.Page("views/overview.py", title="Vue d'ensemble", icon=":material/dashboard:", default=True),
        st.Page("views/internet.py", title="Internet et télécoms", icon=":material/wifi:"),
        st.Page("views/carte.py", title="Carte des services", icon=":material/map:"),
        st.Page("views/inclusion.py", title="Mobile money et inclusion", icon=":material/account_balance_wallet:"),
    ],
    "Pilotage": [
        st.Page("views/recommandations.py", title="Recommandations", icon=":material/lightbulb:"),
        st.Page("views/methodologie.py", title="Méthodologie et données", icon=":material/menu_book:"),
    ],
}

with st.sidebar:
    st.markdown(
        """
<div style="padding:.4rem 0 1rem 0">
  <div style="font-size:1.25rem;font-weight:800;color:#fff;line-height:1.15">Inclusion financière<br>numérique · Togo</div>
  <div style="font-size:.8rem;color:#9FB8AC;margin-top:.35rem">Data Challenge Économie Numérique · Défi 2</div>
</div>
""",
        unsafe_allow_html=True,
    )

nav = st.navigation(pages)

with st.sidebar:
    st.markdown(
        """
<div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,.12);font-size:.75rem;color:#9FB8AC;line-height:1.5">
<b style="color:#E6F0EA">Sources</b><br>
Géoportail Open Data du Togo · ARCEP · Banque mondiale · RGPH-5 2022 (INSEED) · geoBoundaries<br><br>
<b style="color:#E6F0EA">Auteur</b><br>SADJINA Christ · septembre 2026
</div>
""",
        unsafe_allow_html=True,
    )

nav.run()
