"""Interface manager de l'Assistant ADKAR (Streamlit).
Lancer depuis la racine du projet, l'API tournant dans un autre terminal : streamlit run ui/app.py"""
import os
import pandas as pd
import requests
import streamlit as st

API = os.environ.get("API_URL", "http://localhost:8000")   # au J7, Docker changera cette adresse
STAGES = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]

# Chiffres affichés si l'API ne répond pas (pendant le développement, ou si elle tombe pendant la démo)
EXEMPLE_STATS = {"total_verbatims": 100, "total_frictions": 60,
                 "par_etape": {"Awareness": 10, "Desire": 12, "Knowledge": 23, "Ability": 10, "Reinforcement": 5},
                 "top_themes": {"manque de formation": 15, "peur pour son poste": 9},
                 "derniere_maj": "exemple"}


def call_api(method: str, route: str, timeout: int, **kwargs):
    """Appelle l'API. Renvoie (réponse, None) si tout va bien, ou (None, message d'erreur lisible)."""
    try:
        resp = requests.request(method, f"{API}{route}", timeout=timeout, **kwargs)
    except requests.exceptions.ConnectionError:
        return None, f"L'API ne répond pas ({API}). Est-elle lancée dans un autre terminal (uvicorn api.main:app) ?"
    except requests.exceptions.Timeout:
        return None, f"L'API n'a pas répondu en {timeout} s. Réessayez dans un instant."
    if not resp.ok:                                   # erreur 400, 422, 500... : on affiche la raison donnée par l'API
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        return None, f"Erreur {resp.status_code} de l'API : {detail}"
    return resp.json(), None


st.set_page_config(page_title="Assistant ADKAR", layout="wide")
page = st.sidebar.radio("Navigation", ["Tableau de bord", "Plan d'action", "Analyser un verbatim"])

if page == "Tableau de bord":
    st.title("Où l'adoption de l'IA bloque-t-elle ?")
    s, erreur = call_api("GET", "/stats", timeout=30)
    if erreur:
        st.warning(f"API indisponible : données d'exemple affichées. ({erreur})")
        s = EXEMPLE_STATS
    par_etape = pd.Series(s["par_etape"], dtype=float).reindex(STAGES).fillna(0)
    if par_etape.sum() > 0:
        principal = par_etape.idxmax()
        part = par_etape.max() / par_etape.sum()
        st.metric("Blocage principal", principal, f"{part:.0%} des frictions",
                  delta_color="off", delta_arrow="off")      # une part, pas une hausse : pas de flèche
    else:
        st.info("Aucune friction détectée pour l'instant.")
    c1, c2 = st.columns(2)
    c1.metric("Verbatims analysés", s["total_verbatims"])
    c2.metric("Frictions détectées", s["total_frictions"])
    st.subheader("Frictions par étape ADKAR")
    st.bar_chart(par_etape.rename("frictions"), sort=False,    # sort=False : ordre ADKAR, pas alphabétique
                 x_label="Étape ADKAR", y_label="Nombre de frictions")
    st.subheader("Thèmes les plus fréquents")
    st.table(pd.Series(s["top_themes"], name="nombre", dtype=int))
    st.caption(f"Dernière mise à jour des données : {s['derniere_maj']}")

elif page == "Plan d'action":
    st.title("Générer un plan d'action")
    stage = st.selectbox("Étape ADKAR à travailler", STAGES)
    question = st.text_input("Votre question (facultatif)", "Comment débloquer l'adoption ?")
    if st.button("Générer le plan"):
        with st.spinner("Analyse des verbatims et rédaction du plan (10 à 30 s)..."):
            r, erreur = call_api("POST", "/action-plan", timeout=120,
                                 json={"stage": stage, "question": question or "Comment débloquer l'adoption ?"})
        if erreur:
            st.error(erreur)
        else:
            st.markdown(r["plan"])
            if r.get("citations_inventees"):          # contrôle de rag/plan.py : doit rester vide
                st.warning("Identifiants cités absents des sources : " + ", ".join(r["citations_inventees"]))
            with st.expander(f"Voir les {len(r['sources'])} verbatims utilisés"):
                for meta, extrait in zip(r["sources"], r["extraits"]):
                    st.markdown(f"**[{meta['verbatim_id']}]** {extrait}")

else:
    st.title("Analyser un verbatim")
    text = st.text_area("Collez un retour d'employé (au moins 10 caractères)", max_chars=3000)
    if st.button("Analyser"):
        if len(text.strip()) < 10:
            st.warning("Le texte doit faire au moins 10 caractères.")
        else:
            with st.spinner("Classification en cours..."):
                r, erreur = call_api("POST", "/analyze", timeout=60, json={"text": text})
            if erreur:
                st.error(erreur)
            elif r.get("adkar_stage") == "error":
                st.error("Le LLM n'a pas pu classer ce texte. Réessayez.")
            else:
                st.metric("Étape ADKAR", r["adkar_stage"])
                c1, c2, c3 = st.columns(3)
                c1.metric("Friction", {True: "oui", False: "non"}.get(r.get("friction"), "?"))
                c2.metric("Sentiment", r.get("sentiment") or "?")
                c3.metric("Thème", r.get("theme") or "?")
                st.markdown(f"**Justification :** {r.get('justification') or '-'}")
                with st.expander("Réponse complète de l'API"):
                    st.write(r)
