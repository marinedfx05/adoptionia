"""Extract : lit tous les fichiers bruts de S3 et les rassemble dans un tableau."""
import json, os
import boto3, pandas as pd
from dotenv import load_dotenv

load_dotenv()
s3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]

def list_keys(prefix: str) -> list:
    """Liste tous les fichiers sous un préfixe (S3 répond par pages de 1000 : on les parcourt toutes)."""
    keys = []
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=prefix):
        keys += [obj["Key"] for obj in page.get("Contents", [])]
    return keys

def load_raw_hn() -> pd.DataFrame:
    """Télécharge chaque JSON brut de raw/hn/ et les met dans un DataFrame."""
    rows = []
    for key in list_keys("raw/hn/"):
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        rows.append(json.loads(body))
    print(f"{len(rows)} fichiers bruts lus")
    return pd.DataFrame(rows)
