# Journal de bord — adoptionia

## J0 — 24/11/2026
**Fait :** structure du projet (dossiers etl, rag, api, ui…), .gitignore, .env.example, requirements.txt, environnement Python 3.11, outil GitHub (gh), premier envoi sur GitHub (Marine)
**Choix + pourquoi :** Python 3.11 plutôt que 3.14, car plusieurs bibliothèques (pandas…) ne sont pas encore disponibles en 3.14 sur Mac Intel ; embeddings via l'API OpenAI plutôt que sentence-transformers, car PyTorch ne s'installe plus sur Mac Intel ; installation avec --prefer-binary pour éviter de compiler des bibliothèques
**Problème rencontré + solution :**
- Homebrew impossible à installer sur Mac Intel → gh installé depuis le .zip téléchargé (copie dans /usr/local/bin)
- Dossier créé à la main au lieu d'être cloné → git init + git remote add origin, puis fusion avec le .gitignore déjà présent sur GitHub (conflit résolu en gardant notre version)
- GitHub a bloqué le push : des clés AWS étaient dans .env.example → clés déplacées dans .env (ignoré par Git), commit refait avec git reset --soft
- pip : torch introuvable, pandas et cryptography impossibles à compiler → Python 3.11, suppression de sentence-transformers, --prefer-binary
**Preuve :** dépôt https://github.com/marinedfx05/adoptionia (commit « structure initiale »), capture du terminal « Environnement OK »