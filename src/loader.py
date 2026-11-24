# src/loader.py
"""Chargement du CSV SO 2025 en DataFrame pandas (dtype=str pour sécurité)."""
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/survey_results_public.csv")
SCHEMA = Path("data/reference/survey_results_schema.csv")

def load_survey(path: Path = RAW) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    return df

def load_schema(path: Path = SCHEMA) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")

def explode_multi(df: pd.DataFrame, col: str, sep: str = ";") -> pd.DataFrame:
    """Enregistre 1 ligne par item pour une colonne multi-choix ('a;b;c')."""
    return df.assign(**{col: df[col].str.split(sep)}).explode(col)