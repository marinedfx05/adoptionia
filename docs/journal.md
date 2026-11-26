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


## J2 — 24/11/2026

**Fait :**
- Marine : création du bucket S3 `adoptionia-dev-md` et partage des accès aux trois autres (utilisateur IAM `adoptionia-dev`, jamais de clés root).
- Alexandre : script `etl/ingest.py` qui récupère les commentaires Hacker News via l'API Algolia (30 derniers jours) et les dépose dans `raw/hn/` ; explication du principe aux trois autres avant de coder.
- Florian : [ingestion de la source enquête / ou : source enquête non retenue] ; premier conteneur Docker (« Bonjour depuis Docker »).
- Marine : guide ADKAR (5 étapes, branche `8-guide-adkar`).
- Alexandra : relecture de la Pull Request du guide ADKAR.
**Choix + pourquoi :**
- Région `eu-north-1` (Stockholm) : imposée par la nouvelle console « projets » d'AWS (non modifiable) ; données en Union européenne, donc conformes au RGPD.
- Ingestion idempotente (`already_in_s3`) : relancer le script ne crée pas de doublons, ce qui est indispensable pour le CRON nocturne du J7.
- On garde les données brutes telles quelles dans `raw/` : le nettoyage se fait au J3 dans `clean/`, et on peut toujours revenir à la source.
**Chiffres :**
- 470 fichiers dans raw/hn/ après le 1er lancement (objectif ≥ 300).
- 2e lancement : 496 « déjà présent », 0 nouveaux (preuve : pas de doublons).
- Durée d'un lancement : moins d'1 min (relance chronométrée : 36 s).

Le 1er lancement couvrait 60 jours au lieu de 30 : sur 30 jours, nos 6 mots-clés ne ramenaient qu'environ 250 commentaires, sous l'objectif de 300.
« 496 déjà présents » est plus grand que 470 parce que 26 commentaires contiennent deux de nos mots-clés : le script les voit deux fois, mais ne les écrit qu'une fois.
Aujourd'hui, raw/hn/ contient 471 fichiers : 1 nouveau commentaire publié entre deux lancements.
Preuve en image : docs/img/j2_idempotence.png (PR #34). 

**Problème rencontré + solution :**
- `.env` encore réglé sur `eu-west-3` (Paris), d'où des erreurs d'accès au bucket → remplacé par `AWS_REGION=eu-north-1` et l'équipe prévenue.
- `git checkout` refusé à cause de modifications locales du notebook → `git restore` sur le notebook, puis commit du reste.
- Fichiers « disparus » (journal, charte, guide) : ils étaient sur d'autres branches → retrouvés avec `git log --all -- <fichier>` et `git branch -a --contains <commit>`.
**Preuve :** capture console S3 (`raw/hn/`), capture du 2e lancement, PR #[..] (ingestion, Closes #6), PR #[..] (Florian, Closes #7), PR #[..] (guide ADKAR), PR #[..] (journal J2).



## J3 — 25/11/2026

**Fait :**
- Alexandra : atelier « bases de pandas » (20 min, chacun·e dans son notebook) puis validation du schéma cible ; renommage des colonnes `author_id`, `created_on`, `ingested_on` pour un schéma plus lisible.
- Alexandre : ETL en 4 fichiers (`extract.py`, `transform.py`, `load.py`, `run_clean.py`), lancé → `clean/verbatims.parquet` sur S3 ; notebook `check_clean.ipynb` pour relire le résultat.
- Florian : tests `pytest` écrits le matin sans attendre l'ETL (`[N] passed`) ; il a mené la vérification de la qualité à l'œil.
- Marine : premier essai de Terraform (`init`, `plan`, `apply`, `destroy` sur un bucket de test) ; guide ADKAR enrichi avec 25 verbatims réels (5 par étape) tirés de `clean/verbatims.parquet`.

**Choix + pourquoi :**
- Une fonction par règle de nettoyage : chaque règle est testable seule et on sait combien de lignes elle retire.
- Pseudo de l'auteur remplacé par un code (hash SHA-256) ; emails, URL et @mentions masqués : aucune donnée personnelle dans `clean/` (RGPD).
- Texte de 30 à 3 000 caractères : en dessous, pas de sens exploitable ; au-dessus, ce sont des essais, pas des verbatims.
- Filtre « travail » (company, team, manager…) : on ne garde que ce qui parle d'adoption de l'IA *en entreprise*.
- Langues `en` et `fr` uniquement : ce sont les deux langues que l'équipe sait relire et annoter.
- Les données brutes `raw/` restent intactes : le nettoyage est rejouable à tout moment.

**Chiffres (tableau de comptage) :**
- le script prend les 471 commentaires bruts du J2, les nettoie, et range 447 commentaires propres dans S3 (clean/verbatims.parquet).

| Étape | Lignes restantes |
|---|---|
| Entrée (fichiers bruts) | [471] |
| Après nettoyage | [447] |

Signaux ADKAR repérés par mots-clés : 163 verbatims candidats (Awareness 65, Desire 25, Knowledge 28, Ability 71, Reinforcement 3). Ensuite, 25 ont été choisis à la main.

**Exemples avant/après nettoyage :**
1. `<p>It&#x27;s great</p>` → `It's great` (HTML retiré)
2. `contact me at bob@mail.com` → `contact me at [EMAIL]` (anonymisation)
3. auteur `bob42` → `a91f3c2e` (pseudo haché)

**Problème rencontré + solution :**
- Florian : apprentissage d'utilisation de GitHub
- Alexandre: paramètrage compte AWS


## J4 — 26/11/2026

**Fait :**
- Les quatre : essai des embeddings dans un notebook (similarité « formation » EN/FR vs « pizza »).
- Sasha : fichiers outils `rag/embedder.py` (embeddings OpenAI `text-embedding-3-small`, 1 536 nombres par texte, envoi par paquets de 100) et `rag/store.py` (ChromaDB dans `data/chroma`, collections `verbatims` et `adkar_knowledge`).
- Alexandre : découpage des textes (`rag/chunking.py`) [à confirmer], remplissage de ChromaDB avec Sasha (`rag/index.py`) [à confirmer], `etl/rebuild.py` [à confirmer], dictionnaire de données `docs/lineage.md` [à confirmer] ; corrections du nettoyage après la revue de Florian (PR #35) ; tests et notebook de contrôle qualité (PR #40).
- Florian : revue de la PR #35 (filtre « travail » trop large) ; test de la recherche par le sens sur 3 questions.
- Marine : relecture du guide ADKAR (enrichi au J3 avec 25 verbatims réels) ; relecture des PR #35 et #36 ; création des issues du Sprint 2.

**Choix + pourquoi :**
- Embeddings par l'API OpenAI plutôt qu'un modèle local : rien à installer sur Mac Intel ni sur le serveur, et le même modèle comprend l'anglais et le français.
- ChromaDB en simple dossier local : aucune base de données à administrer ; on peut le reconstruire à tout moment depuis S3 (`rebuild.py`), donc il n'est pas sauvegardé sur GitHub.
- Deux collections séparées : `verbatims` (ce que disent les salariés) et `adkar_knowledge` (notre guide), pour que le RAG cherche au bon endroit.
- Filtre « travail » par mot entier (`\b`) : « network » ou « steam » ne comptent plus comme parlant de travail (revue de Florian).
- Le titre du fil de discussion est anonymisé comme le texte, et un tableau vide ne peut jamais écraser le fichier propre.

**Chiffres :**
- Fichier propre : 447 verbatims, 100 % en anglais, de 49 à 2 812 caractères, du 26/09 au 25/11/2026 ; 24 liens masqués, 0 e-mail.
- Tests : 10 tests sur le nettoyage (`pytest -v` : [N] passed).
- Morceaux indexés : [N] dans `verbatims`, [N] dans `adkar_knowledge`.
- Recherche par le sens : [N]/15 résultats pertinents sur 3 questions : « [question 1] », « [question 2] », « [question 3] ».

**Problème rencontré + solution :**
- `ConnectError` sur les embeddings : le client utilisait l'adresse `JEDHA_AI_BASE_URL`, injoignable → client OpenAI direct, sans `base_url`.
- Revue de Florian sur la PR #35 : le filtre par sous-chaîne gardait des textes hors sujet → filtre par mot entier.
- Contrôle qualité : il reste 1 `@` dans un verbatim → [vérifié : pas une donnée personnelle / règle d'anonymisation corrigée].
- Annotation du J5 réorganisée : Alexandre étant pris, Marine et Florian annoteront 45 verbatims chacun·e.

**Rétrospective Sprint 1 :**
- Ce qui a bien marché : [ex. un fichier par personne, travail en parallèle sans s'attendre, revues de PR utiles (#35)].
- Ce qu'on change pour le Sprint 2 : [ex. ouvrir la PR dès que la branche est poussée, faire `git log` avant d'ouvrir une PR, noter les chiffres réels au fil de la journée].

**Preuve :** capture du notebook d'embeddings, capture du test de recherche, PR #35 