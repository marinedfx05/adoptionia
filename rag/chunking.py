"""Découpage des textes en morceaux (chunks) avant le calcul des embeddings."""

def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list:
    """Texte court (<= 800 caractères) : un seul morceau.
    Texte long : morceaux de 500 caractères qui se chevauchent de 50
    (le chevauchement évite de couper une idée en deux)."""
    if len(text) <= 800:
        return [text]
    chunks, start = [], 0
    while True:
        chunks.append(text[start:start + size])
        if start + size >= len(text):       # ce morceau atteint la fin : on s'arrête
            break                           # (sinon il resterait un minuscule morceau déjà contenu dans le précédent)
        start += size - overlap
    return chunks

def chunk_guide(md: str) -> list:
    """Guide ADKAR : un morceau par étape (titre '## ...'), avec son nom en tête."""
    parts = md.split("\n## ")[1:]           # [1:] : on saute le titre principal
    return ["## " + p.strip() for p in parts if p.strip()]
