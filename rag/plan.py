"""Génération d'un plan d'action pour un manager, appuyé sur les verbatims (RAG).
Prérequis : verbatims classés (etl/run_classify.py) puis base réindexée (python -m rag.index).
Lancer depuis la racine du projet : python -m rag.plan"""
import re
import time
from rag.embedder import embed
from rag.store import get_collection
from rag.llm import ask

STAGES = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]
N_VERBATIMS = 8                          # nombre de verbatims donnés au LLM
ID_PATTERN = re.compile(r"\b[a-z]+_\d+\b")   # forme d'un identifiant de verbatim, ex. hn_49855161

PLAN_PROMPT = """Tu conseilles un manager qui déploie un outil d'IA dans son équipe.
Étape ADKAR principalement bloquée : {stage}
Question du manager : {question}

Bonnes pratiques de notre guide :
{guide}

Verbatims d'employés (avec identifiant entre crochets) :
{verbatims}

Rédige en français :
1. Un diagnostic en 2 phrases.
2. Exactement 3 actions. Pour chacune : quoi, qui, quand, indicateur de réussite,
   et les identifiants des verbatims qui la justifient entre crochets, par exemple [hn_412].
Utilise UNIQUEMENT les verbatims fournis. S'ils ne suffisent pas, dis-le.
Ne cite jamais une phrase sans son identifiant, et n'invente aucune citation."""


def find_verbatims(q_vec: list, stage: str) -> tuple:
    """Retrieval : les N_VERBATIMS verbatims les plus proches, classés dans cette étape.
    On demande plus de morceaux que nécessaire, car un long verbatim est découpé
    en plusieurs morceaux et apparaîtrait sinon plusieurs fois."""
    res = get_collection("verbatims").query(query_embeddings=q_vec, n_results=N_VERBATIMS * 3,
                                            where={"adkar_stage": stage})   # seulement cette étape
    sources, extraits = [], []
    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
        if meta["verbatim_id"] not in {s["verbatim_id"] for s in sources}:   # un verbatim = une source
            sources.append(meta)
            extraits.append(doc)
        if len(sources) == N_VERBATIMS:
            break
    return sources, extraits


def ask_with_retry(prompt: str, temperature: float, tries: int = 3) -> str:
    """Appel au LLM avec nouvel essai en cas de coupure passagère (ex. erreur 429)."""
    for attempt in range(1, tries + 1):
        try:
            return ask(prompt, temperature=temperature) or ""     # "" si le LLM renvoie une réponse vide
        except Exception as e:
            if attempt == tries:
                raise
            print(f"Erreur du LLM ({e.__class__.__name__}), nouvel essai dans {5 * attempt} s")
            time.sleep(5 * attempt)


def make_plan(stage: str, question: str = "Comment débloquer l'adoption ?") -> dict:
    if stage not in STAGES:
        raise ValueError(f"Étape inconnue : {stage!r}. Choisir parmi {STAGES}.")
    q_vec = embed([f"{stage} : {question}"])

    sources, extraits = find_verbatims(q_vec, stage)
    if not sources:
        raise RuntimeError(f"Aucun verbatim classé {stage} dans ChromaDB. Vérifier : (1) lancement depuis "
                           "la racine du projet ; (2) python -m rag.index relancé après la classification.")
    guide = get_collection("adkar_knowledge").query(query_embeddings=q_vec, n_results=2)

    # Augmented : verbatims et guide ajoutés au prompt. Generation : le LLM rédige.
    verbatims_txt = "\n".join(f"[{m['verbatim_id']}] {d[:400]}" for d, m in zip(extraits, sources))
    prompt = PLAN_PROMPT.format(stage=stage, question=question,
                                guide="\n---\n".join(guide["documents"][0]),
                                verbatims=verbatims_txt)
    plan = ask_with_retry(prompt, temperature=0.4)    # 0,4 : un peu de variété pour rédiger

    # Contrôle « Fondé » : tout identifiant cité doit figurer dans les sources fournies
    fournis = {s["verbatim_id"] for s in sources}
    return {"plan": plan,
            "sources": sources,
            "extraits": extraits,
            "citations_inventees": sorted(set(ID_PATTERN.findall(plan)) - fournis)}   # doit rester vide


if __name__ == "__main__":
    r = make_plan("Knowledge")
    print(r["plan"])
    print("\nSources :", [s["verbatim_id"] for s in r["sources"]])
    print("Citations inventées :", r["citations_inventees"] or "aucune")
