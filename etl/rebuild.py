"""Reconstruit tout depuis la zone brute : nettoyage, fichier propre, base vectorielle."""
import os
from dotenv import load_dotenv

def main() -> None:
    # Comme run_clean : on vérifie le .env avant d'importer ce qui se connecte à S3
    load_dotenv()
    for variable in ("S3_BUCKET", "HASH_SALT"):
        if not os.environ.get(variable):
            raise SystemExit(f"{variable} manque dans le .env.")
    # Sans clé API, l'indexation échouerait APRÈS avoir vidé la base : on vérifie avant
    if not (os.environ.get("LLM_API_KEY") or os.environ.get("JEDHA_AI_API_KEY")):
        raise SystemExit("Clé API manquante dans le .env (LLM_API_KEY ou JEDHA_AI_API_KEY) : rien n'a été modifié.")
    from etl.extract import load_raw_hn
    from etl.transform import clean_hn
    from etl.load import save_parquet
    from rag.index import index_verbatims, index_knowledge
    from rag.store import reset_collection

    clean, stats = clean_hn(load_raw_hn())     # rejoue le nettoyage depuis le brut
    save_parquet(clean, "clean/verbatims.parquet")
    reset_collection("verbatims")              # on repart de zéro (après le nettoyage : si celui-ci échoue, l'ancienne base reste)
    reset_collection("adkar_knowledge")
    print("Verbatims indexés :", index_verbatims(clean))
    print("Sections ADKAR indexées :", index_knowledge())
    print("Reconstruction terminée :", stats)

if __name__ == "__main__":
    main()
