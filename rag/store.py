"""Accès à la base vectorielle ChromaDB (un simple dossier : data/chroma)."""
import chromadb

CHROMA_PATH = "data/chroma"

def get_collection(name: str):
    """Ouvre une collection (la crée si elle n'existe pas). Deux collections : 'verbatims' et 'adkar_knowledge'."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name)

def reset_collection(name: str) -> None:
    """Supprime une collection (pour tout reconstruire)."""
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(name)
    except Exception:
        pass                    # elle n'existait pas : rien à faire