"""Les embeddings, calculés par l'API OpenAI (aucun modèle à installer sur le Mac ou le serveur)."""
import os
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
MODEL_NAME = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")

@lru_cache                       # crée la connexion une seule fois
def get_client() -> OpenAI:
    return OpenAI(api_key=os.environ["LLM_API_KEY"])

def embed(texts: list) -> list:
    """Transforme une liste de textes en liste d'embeddings (listes de 1 536 nombres)."""
    vectors = []
    for i in range(0, len(texts), 100):          # on envoie 100 textes par appel
        response = get_client().embeddings.create(model=MODEL_NAME, input=texts[i:i + 100])
        vectors.extend(d.embedding for d in response.data)
    return vectors
