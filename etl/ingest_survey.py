"""Copie un fichier d'enquête tel quel dans S3, zone brute."""
import os, sys, boto3
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client("s3")
path = sys.argv[1]                                   # chemin du fichier local
key = f"raw/survey/{os.path.basename(path)}"         # même nom dans S3
s3.upload_file(path, os.environ["S3_BUCKET"], key)   # réécrire un fichier identique ne crée pas de doublon
print("Envoyé :", key)