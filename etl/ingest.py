"""Ingestion : récupère les commentaires Hacker News et les dépose bruts dans S3."""
import json, os, sys, time
import boto3, requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()                                   # lit le fichier .env
BUCKET = os.environ["S3_BUCKET"]                # nom du bucket, jamais écrit en dur dans le code
s3 = boto3.client("s3")                         # la "télécommande" pour parler à S3
API = "https://hn.algolia.com/api/v1/search_by_date"
# Mots-clés retenus au J1 (voir notebooks/explore_hn.ipynb et le README)
QUERIES = ['"my job" AI', '"my company" AI', '"my team" AI',
           '"my employer" AI', '"my coworkers" AI', '"my manager" AI']

def already_in_s3(key: str) -> bool:
    """Vrai si le fichier existe déjà dans S3 (c'est ce qui rend le script idempotent)."""
    try:
        s3.head_object(Bucket=BUCKET, Key=key)  # demande les infos du fichier
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":  # 404 = le fichier n'existe pas
            return False
        raise                                   # autre erreur (droits, réseau...) : on s'arrête

def fetch(query: str, since_ts: int) -> list:
    """Appelle l'API pour un mot-clé, uniquement les commentaires postérieurs à since_ts."""
    params = {"query": query, "tags": "comment",
              "restrictSearchableAttributes": "comment_text",  # cherche dans le commentaire, pas dans le titre du fil
              "hitsPerPage": 1000,                             # maximum de l'API
              "numericFilters": f"created_at_i>{since_ts}"}
    for essai in range(1, 4):                   # jusqu'à 3 essais si l'API ou le réseau a un raté
        try:
            r = requests.get(API, params=params, timeout=15)
            r.raise_for_status()                # erreur HTTP (500, 429...) -> on réessaie
            break
        except requests.RequestException as e:
            if essai == 3:
                raise                           # 3 échecs : on s'arrête proprement
            print(f"  essai {essai} raté ({e}), nouvel essai dans {5 * essai} s")
            time.sleep(5 * essai)
    hits = r.json()["hits"]
    if len(hits) >= params["hitsPerPage"]:      # l'API plafonne à 1000 : on prévient au lieu de perdre en silence
        print(f"  ATTENTION : '{query}' a atteint 1000 résultats, certains manquent. Réduire le nombre de jours.")
    return hits

def ingest(days: int) -> None:
    since_ts = int(time.time()) - days * 24 * 3600   # "maintenant moins N jours", en secondes
    new, skipped = 0, 0
    for q in QUERIES:
        for hit in fetch(q, since_ts):
            key = f"raw/hn/{hit['objectID']}.json"
            if already_in_s3(key):
                skipped += 1
                continue
            hit["_query"] = q                       # on note quel mot-clé l'a trouvé
            hit["_ingested_at"] = int(time.time())  # et quand (utile pour tracer l'origine)
            s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(hit))
            new += 1
        print(f"  mot-clé '{q}' traité")
        time.sleep(1)                               # politesse envers l'API
    print(f"Ingestion terminée : {new} nouveaux, {skipped} déjà présents")

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 2   # par défaut : 2 derniers jours
    ingest(days)
