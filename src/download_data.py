# src/download_data.py
"""Télécharge les données sources de la SO 2025 (voir data/reference pour le questionnaire)."""
import kagglehub

path = kagglehub.dataset_download("aliaslam25/stack-overflow-developer-survey-2025")
print("Dataset téléchargé dans :", path)