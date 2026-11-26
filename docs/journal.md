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


## J1 — 24/11/2026
**Fait :** board + 13 issues (Marine), charte et schéma v1 (Marine), exploration HN (Alexandre), choix de la source enquête (Alexandre)
**Choix + pourquoi :** 
- LLM + RAG car texte libre ; HN car réel, renouvelé, sale ; mots-clés retenus : ChatGPT at work, AI mandate
- Anthropic Interviewer, sur Hugging Face. : seul jeu qui coche les 4 critères. 1 250 entretiens de vrais professionnels sur l'IA au travail, en texte libre, licence CC-BY (usage autorisé en citant la source), et les participants ont consenti à la publication.
- Écartés : WORKBank (aucune licence déclarée), ECHO/Reddit (licence floue), et deux jeux Kaggle/Mendeley qui sont synthétiques.
**Chiffres :** 
- Mots-clés retenus : 6 expressions personnelles entre guillemets suivies de « AI » : "my job", "my company", "my team", "my employer", "my coworkers", "my manager". Elles ont été choisies parmi 54 mots-clés testés, après la lecture et la notation manuelle de 4 269 commentaires (voir notebooks/explore_hn.ipynb).
**Problème rencontré + solution :** 
- push refusé (clés AWS dans .env.example) → clés retirées, .env.example vidé
**Preuve :** docs/img/j1_board.png, PR #5, PR #6


## J2 — 25/11/2026
**Fait :** bucket S3 adoptionia-dev-md (Marine), script d'ingestion HN vers raw/hn/ (Alexandre), ingestion de la source enquête (Florian), premier conteneur Docker (Florian), guide ADKAR commencé avec les signaux classés par étape (Marine)
**Choix + pourquoi :**
- Un fichier JSON par commentaire, nommé par son identifiant : si le fichier existe déjà, on ne le réécrit pas → script idempotent, relançable sans doublons
- Région eu-north-1 (Stockholm) : imposée par le nouveau plan gratuit AWS (organisé en projets, sans sélecteur de région) ; .env, Terraform et guide mis à jour en conséquence
- Guide ADKAR : signaux = extraits courts de vrais commentaires HN ; définitions et actions manager rédigées avec nos mots (pas de copie de sources protégées)
**Chiffres :** 31 signaux ADKAR (Awareness 6, Desire 7, Knowledge 6, Ability 7, Reinforcement 5) tirés de 18 commentaires
**Problème rencontré + solution :**
- Pas de sélecteur de région dans la console AWS → région trouvée dans settings.aws.com (Project → Region), guide adapté à eu-north-1
- Charte « disparue » de VS Code → elle était sur la branche 1-charte, pas encore fusionnée dans main
- Schéma d'architecture non suivi par Git (U) → ajouté à la branche 1-charte et poussé
- Notebook d'Alexandre absent de main → sa Pull Request n'avait pas été créée ; créée depuis GitHub (New pull request, compare 2-exploration-hn) puis fusionnée
**Preuve :** capture du 2e lancement de l'ingestion, PR #.. (ingestion HN), PR #.. (guide ADKAR), PR #.. (exploration HN)

## J3 - 25/11/2026
**Fait :**
Essai Terraform
terraform init        # télécharge le "plugin" AWS (une fois par dossier)
terraform plan        # montre ce qui VA être créé, sans rien faire
terraform apply       # crée réellement : tapez yes puis Entrée
terraform destroy     # supprimer le bucket S3

**Chiffres :**
1240 fichiers bruts lus
Écrit : s3://adoptionia-dev-md/clean/verbatims.parquet (598 lignes)
Lignes restantes après chaque étape :
  entree                    1240
  apres_doublons_id         1102
  apres_doublons_texte      1085
  apres_longueur             960
  apres_filtre_travail       612
  apres_langue               598