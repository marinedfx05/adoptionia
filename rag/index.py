"""Indexation : calcule les embeddings et remplit les deux collections ChromaDB."""
import os
import pandas as pd
from dotenv import load_dotenv
from rag.chunking import chunk_text, chunk_guide
from rag.embedder import embed
from rag.store import get_collection

load_dotenv()

def index_verbatims(df: pd.DataFrame) -> int:
    col = get_collection("verbatims")
    ids, docs, metas = [], [], []
    for _, row in df.iterrows():
        for i, chunk in enumerate(chunk_text(row["text"])):
            ids.append(f"{row['verbatim_id']}_{i}")              # identifiant unique de chaque morceau
            docs.append(chunk)
            metas.append({"verbatim_id": row["verbatim_id"],     # pour retrouver le verbatim d'origine
                        "source": row["source"],
                          "lang": row["lang"],
                          "adkar_stage": str(row.get("adkar_stage", "unknown")),
                          "created_on": str(row["created_on"].date())})
    for start in range(0, len(ids), 500):                       # par paquets de 500
        end = start + 500
        col.upsert(ids=ids[start:end], documents=docs[start:end],
                   embeddings=embed(docs[start:end]), metadatas=metas[start:end])
    return len(ids)

def index_knowledge(path: str = "knowledge/adkar_guide.md") -> int:
    col = get_collection("adkar_knowledge")
    with open(path, encoding="utf-8") as f:
        sections = chunk_guide(f.read())
    col.upsert(ids=[f"kb_{i}" for i in range(len(sections))],
               documents=sections, embeddings=embed(sections))
    return len(sections)

if __name__ == "__main__":
    try:
        df = pd.read_parquet(f"s3://{os.environ['S3_BUCKET']}/clean/classified.parquet")
    except Exception:
        df = pd.read_parquet(f"s3://{os.environ['S3_BUCKET']}/clean/verbatims.parquet")
    print("Morceaux de verbatims indexés :", index_verbatims(df))
    print("Sections ADKAR indexées :", index_knowledge())
