"""Lance le nettoyage complet : brut S3 -> propre S3."""
import os
from etl.extract import load_raw_hn
from etl.transform import clean_hn
from etl.load import save_parquet

if __name__ == "__main__":
    if not os.environ.get("HASH_SALT"):
        raise SystemExit("HASH_SALT manque dans le .env : sans lui, les pseudos hachés seraient retrouvables.")
    raw = load_raw_hn()
    clean, stats = clean_hn(raw)
    save_parquet(clean, "clean/verbatims.parquet")
    print("\nLignes restantes après chaque étape :")
    for etape, n in stats.items():
        print(f"  {etape:25s} {n}")
