"""Transform : une fonction par règle de nettoyage."""
import hashlib, html, os, re
import pandas as pd
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0                     # rend la détection de langue stable d'un lancement à l'autre
load_dotenv()

WORK_WORDS = ["company", "companies", "team", "manager", "job", "employer", "colleague",
              "boss", "workplace", "coworker", "management", "office", "work"]
# \b = début de mot : "teams" ou "workplace" comptent, mais plus "network" ni "steam" (revue de Florian, PR #35)
WORK_PATTERN = re.compile(r"\b(?:" + "|".join(WORK_WORDS) + ")")
# Fils d'offres d'emploi : pas des témoignages (décision du J1)
HIRING_THREADS = r"who is hiring|seeking work|who wants to be hired|freelancer\? seeking"

def remove_quotes(raw_html: str) -> str:
    """Retire les paragraphes qui citent un autre commentaire (ils commencent par '>').
    Sinon, la phrase d'une autre personne serait attribuée à l'auteur du commentaire."""
    paragraphs = re.split(r"<p>", raw_html or "")              # sur HN, chaque paragraphe commence par <p>
    kept = [p for p in paragraphs if not html.unescape(p).lstrip().startswith(">")]
    return "<p>".join(kept)

def strip_html(text: str) -> str:
    """'<p>It&#x27;s great</p>' devient "It's great"."""
    text = html.unescape(text or "")              # &#x27; devient '
    text = re.sub(r"<[^>]+>", " ", text)          # retire toutes les balises <...>
    return re.sub(r"\s+", " ", text).strip()      # plusieurs espaces deviennent un seul

def anonymize(text: str) -> str:
    """Masque ce qui peut identifier quelqu'un."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    text = re.sub(r"https?://\S+", "[URL]", text)
    text = re.sub(r"@\w+", "[USER]", text)
    return text

def hash_author(name) -> str:
    """'bob42' devient 'a91f3c2e' : même pseudo = même code.
    Le "sel" (HASH_SALT, secret dans le .env) empêche de retrouver le pseudo
    en hachant une liste de pseudos HN publics."""
    salt = os.environ.get("HASH_SALT", "")
    return hashlib.sha256((salt + str(name or "")).encode()).hexdigest()[:8]

def safe_lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:                              # texte trop court ou illisible
        return "unknown"

def is_about_work(text: str) -> bool:
    return bool(WORK_PATTERN.search(text.lower()))

def clean_hn(raw: pd.DataFrame) -> tuple:
    """Applique toutes les règles et compte combien de lignes chaque règle retire."""
    stats = {"entree": len(raw)}
    raw = raw.dropna(subset=["comment_text"]);          stats["apres_texte_present"] = len(raw)
    # Le titre du fil peut lui aussi contenir un e-mail ou un lien : on l'anonymise comme le texte
    context = raw["story_title"].fillna("").map(anonymize) if "story_title" in raw.columns else ""
    df = pd.DataFrame({
        "verbatim_id": "hn_" + raw["objectID"].astype(str),
        "source": "hn",
        "text": raw["comment_text"].map(remove_quotes).map(strip_html).map(anonymize),
        "context": context,
        "author_id": raw["author"].map(hash_author),   # le pseudo en clair ne sort jamais d'ici
        "created_on": pd.to_datetime(raw["created_at"], utc=True),
        "ingested_on": pd.to_datetime(raw["_ingested_at"], unit="s", utc=True),
    })
    df = df[~df["context"].str.contains(HIRING_THREADS, case=False, regex=True)]
    stats["apres_fils_emploi"] = len(df)
    df = df.drop_duplicates(subset="verbatim_id");      stats["apres_doublons_id"] = len(df)
    df = df.drop_duplicates(subset="text");             stats["apres_doublons_texte"] = len(df)
    df = df[df["text"].str.len().between(30, 3000)];    stats["apres_longueur"] = len(df)
    df = df[df["text"].map(is_about_work)];             stats["apres_filtre_travail"] = len(df)
    df["lang"] = df["text"].map(safe_lang)
    df = df[df["lang"].isin(["en", "fr"])];             stats["apres_langue"] = len(df)
    return df.reset_index(drop=True), stats
