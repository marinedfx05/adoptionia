"""API de l'Assistant ADKAR : 4 routes."""
import os
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from rag.classify import classify
from rag.plan import make_plan

load_dotenv()
app = FastAPI(title="Assistant ADKAR", version="1.0")
STAGES = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]

# --- Les "formulaires" acceptés par l'API (Pydantic vérifie leur format tout seul) ---
class VerbatimIn(BaseModel):
    text: str = Field(min_length=10, max_length=3000)

class PlanIn(BaseModel):
    stage: str
    question: str = "Comment débloquer l'adoption ?"

def load_classified() -> pd.DataFrame:
    return pd.read_parquet(f"s3://{os.environ['S3_BUCKET']}/clean/classified.parquet")

# --- Les routes ---
@app.get("/health")
def health():
    """L'app est-elle vivante ? (utilisé par la surveillance au J8)"""
    return {"status": "ok"}

@app.post("/analyze")
def analyze(v: VerbatimIn):
    """Classe un nouveau verbatim selon ADKAR."""
    return classify(v.text)

@app.get("/stats")
def stats():
    """Répartition des frictions par étape et par thème, pour le tableau de bord."""
    df = load_classified()
    frictions = df[
    (df["friction"].fillna(False).astype(bool))
    & (df["adkar_stage"] != "none")
]
    return {
        "total_verbatims": int(len(df)),
        "total_frictions": int(len(frictions)),
        "par_etape": {k: int(v) for k, v in frictions["adkar_stage"].value_counts().items()},
        "top_themes": {k: int(v) for k, v in frictions["theme"].value_counts().head(5).items()},
        "derniere_maj": str(df["ingested_on"].max()),
    }

@app.post("/action-plan")
def action_plan(p: PlanIn):
    """Génère un plan d'action (RAG) pour une étape ADKAR."""
    if p.stage not in STAGES:
        raise HTTPException(status_code=400, detail=f"stage doit être parmi {STAGES}")
    return make_plan(p.stage, p.question)