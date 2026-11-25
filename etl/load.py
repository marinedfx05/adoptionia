"""Load : écrit un tableau en Parquet dans S3."""
import io, os
import boto3, pandas as pd
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client("s3")

def save_parquet(df: pd.DataFrame, key: str) -> None:
    """Parquet = format compact qui garde les types (une date reste une date, pas un texte)."""
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3.put_object(Bucket=os.environ["S3_BUCKET"], Key=key, Body=buffer.getvalue())
    print(f"Écrit : s3://{os.environ['S3_BUCKET']}/{key} ({len(df)} lignes)")
