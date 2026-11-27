"""Classe les verbatims propres qui ne le sont pas encore et sauvegarde clean/classified.parquet."""
import os, time
import pandas as pd
from dotenv import load_dotenv
from rag.classify import classify
from etl.load import save_parquet

load_dotenv()
B = os.environ["S3_BUCKET"]
LIMIT = int(os.environ.get("CLASSIFY_LIMIT", "200"))     # maximum par lancement
FIELDS = ["adkar_stage", "friction", "theme", "sentiment", "justification", "prompt_version"]

if __name__ == "__main__":
    clean = pd.read_parquet(f"s3://{B}/clean/verbatims.parquet")
    try:
        old = pd.read_parquet(f"s3://{B}/clean/classified.parquet")
    except Exception:                                    # premier lancement : rien de classé
        old = pd.DataFrame(columns=["verbatim_id"])
    todo = clean[~clean["verbatim_id"].isin(old["verbatim_id"])].head(LIMIT)
    print(f"{len(old)} déjà classés, {len(todo)} à classer maintenant")
    rows = []
    for i, row in enumerate(todo.to_dict("records"), 1):
        out = classify(row["text"])
        rows.append({**row, **{k: out.get(k) for k in FIELDS}})
        print(f"{i}/{len(todo)} -> {out['adkar_stage']}")
        time.sleep(1)
    result = pd.concat([old, pd.DataFrame(rows)], ignore_index=True)
    result["friction"] = result["friction"].astype("boolean")   # vrai/faux/inconnu
    save_parquet(result, "clean/classified.parquet")
    print(result["adkar_stage"].value_counts())