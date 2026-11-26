"""Point d'entrée unique vers le LLM (OpenAI)."""
import json, os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    # Accepte les deux noms de clé, comme rag/embedder.py : LLM_API_KEY (clé OpenAI) ou JEDHA_AI_API_KEY
    api_key=os.environ.get("LLM_API_KEY") or os.environ["JEDHA_AI_API_KEY"],
    base_url=os.environ.get("JEDHA_AI_BASE_URL")
)

MODEL = os.environ.get("LLM_MODEL", "openai/gpt-4.1-mini")

def ask(prompt: str, temperature: float = 0.0, as_json: bool = False):
    """Envoie un prompt au LLM. Renvoie le texte, ou un dictionnaire Python si as_json=True."""
    extra = {"response_format": {"type": "json_object"}} if as_json else {}
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
        **extra,
    )
    text = resp.choices[0].message.content
    return json.loads(text) if as_json else text

if __name__ == "__main__":
    print(ask("Dis bonjour en une phrase, en français."))