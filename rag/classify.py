"""Classification d'un verbatim selon ADKAR, avec repères issus du guide (RAG)."""
from rag.embedder import embed
from rag.store import get_collection
from rag.llm import ask

PROMPT_VERSION = "v2"
STAGES = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement", "none"]

PROMPT = """Tu es expert en conduite du changement et tu utilises le modèle ADKAR.
Repères issus de notre guide :
{context}

Verbatim d'un employé :
\"\"\"{text}\"\"\"

Consignes :
- Choisis la PREMIÈRE étape ADKAR qui bloque cette personne.
- Si le verbatim ne parle pas d'une difficulté d'adoption de l'IA au travail, réponds "none".
- Réponds "none" si le texte ne décrit pas une difficulté CONCRÈTE d'adoption de l'IA dans une équipe : publicité ou présentation d'un produit, opinion générale sur l'IA, marché de l'emploi ou peur du chômage, témoignage positif sans frein.
- En cas de doute entre une étape et "none", choisis "none".
Réponds uniquement avec ce JSON :
{{"adkar_stage": "Awareness|Desire|Knowledge|Ability|Reinforcement|none",
  "friction": true ou false,
  "theme": "3 à 5 mots",
  "sentiment": "negatif|neutre|positif",
  "justification": "une phrase"}}"""

def adkar_context(text: str, k: int = 2) -> str:
    """RAG : les k sections du guide ADKAR les plus proches du verbatim."""
    res = get_collection("adkar_knowledge").query(query_embeddings=embed([text]), n_results=k)
    return "\n---\n".join(res["documents"][0])

def classify(text: str) -> dict:
    prompt = PROMPT.format(context=adkar_context(text), text=text)
    for _ in range(2):                                    # 2 essais si la réponse est invalide
        try:
            out = ask(prompt, temperature=0, as_json=True)
            if out.get("adkar_stage") in STAGES:
                out["prompt_version"] = PROMPT_VERSION
                return out
        except Exception as e:
            print("Réponse invalide, nouvel essai :", e)
    return {"adkar_stage": "error", "friction": None, "theme": None,
            "sentiment": None, "justification": None, "prompt_version": PROMPT_VERSION}