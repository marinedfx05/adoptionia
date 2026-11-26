"""Lance le nettoyage complet : brut S3 -> propre S3."""
import os
from dotenv import load_dotenv

def main() -> None:
    # On vérifie le .env AVANT d'importer extract/load, qui se connectent à S3 dès leur import
    load_dotenv()
    for variable in ("S3_BUCKET", "HASH_SALT"):
        if not os.environ.get(variable):
            raise SystemExit(f"{variable} manque dans le .env (HASH_SALT : sans lui, les pseudos hachés seraient retrouvables).")
    from etl.extract import load_raw_hn
    from etl.transform import clean_hn
    from etl.load import save_parquet

    raw = load_raw_hn()
    clean, stats = clean_hn(raw)
    save_parquet(clean, "clean/verbatims.parquet")
    print("\nLignes restantes après chaque étape :")
    for etape, n in stats.items():
        print(f"  {etape:25s} {n}")

if __name__ == "__main__":
    main()
