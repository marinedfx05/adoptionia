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
- Tests : 10 tests sur le nettoyage (`pytest -v` : 10 passed).
- Morceaux indexés : 862 dans `verbatims`, 5 dans `adkar_knowledge` (une section par étape ADKAR).
- Recherche par le sens : 7/15 résultats pertinents sur 3 questions en anglais : « nobody trained us on the tool » (1/5), « afraid AI will replace my job » (4/5), « management forces us to use AI » (2/5). En français : 3/10 sur 2 questions (« on ne sait pas à quoi ça sert » 0/5, « mon manager nous oblige à utiliser l'IA » 3/5).
- Lecture : la recherche marche bien quand les verbatims parlent directement du sujet (peur pour l'emploi), mal quand le sujet est rare dans les données (formation) ou formulé de façon abstraite. Le multilingue fonctionne mais avec des distances plus grandes (1,05-1,5 contre 0,7-0,9 en anglais).

**Problème rencontré + solution :**
- `ConnectError` sur les embeddings : le client utilisait l'adresse `JEDHA_AI_BASE_URL`, injoignable → client OpenAI direct, sans `base_url`.
- Revue de Florian sur la PR #35 : le filtre par sous-chaîne gardait des textes hors sujet → filtre par mot entier.
- Contrôle qualité : il reste 1 `@` dans un verbatim → [vérifié : pas une donnée personnelle / règle d'anonymisation corrigée].
- Annotation du J5 réorganisée : Alexandre étant pris, Marine et Florian annoteront 45 verbatims chacun·e.

**Rétrospective Sprint 1 :**
- Ce qui a bien marché : [ex. un fichier par personne, travail en parallèle sans s'attendre, revues de PR utiles (#35)].
- Ce qu'on change pour le Sprint 2 : [ex. ouvrir la PR dès que la branche est poussée, faire `git log` avant d'ouvrir une PR, noter les chiffres réels au fil de la journée].

**Preuve :** capture du notebook d'embeddings, capture du test de recherche, PR #35 


## J5 — 26/11/2026

**Fait :**
- Marine + Florian : jeu de test de 90 verbatims tirés au hasard (`eval/test_set.csv`, PR #48). Pré-annoté avec Claude, puis relu et corrigé par Marine (35 textes hors sujet passés en `none`) ; lignes 67 à 91 à relire par Florian.
- Sasha : connexion au LLM (`rag/llm.py`, fonction unique `ask`) et classification ADKAR (`rag/classify.py`) : prompt enrichi par RAG avec les 2 sections du guide les plus proches, température 0, réponse en JSON strict, 2 essais si la réponse est invalide.
- Florian : mesure de la classification (`eval/evaluate.py`), exactitude, rapport par étape et matrice de confusion, historique dans MLflow (PR #49) ; Docker et docker-compose (PR #51).
- Marine : prompt v2 (étape 6), puis classification de tous les verbatims (`etl/run_classify.py`) et ajout de l'étape ADKAR dans ChromaDB (`rag/index.py`) (PR #50) ; génération des 10 plans, grille de notation (Google Sheets) et organisation de la notation.
- Alexandre : plans d'action RAG (`rag/plan.py`) avec vérification des sources citées, et tests (`tests/test_plan.py`).

**Choix + pourquoi :**
- Une seule fonction `ask` pour appeler le LLM : changer de fournisseur ne modifie qu'un fichier.
- Température 0 pour classer (réponse stable d'un lancement à l'autre), 0,4 pour rédiger les plans (un peu de variété).
- JSON strict : le programme lit la réponse sans ambiguïté ; une réponse invalide est retentée puis marquée `error`, jamais inventée.
- Plans « fondés » : le LLM ne doit utiliser que les verbatims fournis et citer leurs identifiants ; `plan.py` vérifie que chaque identifiant cité existe dans les sources.
- Classification calculée une fois et stockée (`clean/classified.parquet`), sans redemander au LLM à chaque affichage ; script idempotent, qui ne reclasse jamais un verbatim déjà classé.
- On s'arrête à une seule amélioration du prompt (v2) : le reste de la chaîne passe avant (conseil de Jedha).

**Chiffres :**
- Exactitude v1 : 49 % (44/90). Confusion principale : textes hors sujet (`none`) auxquels le LLM donne une étape, soit 34 des 46 erreurs (surtout Ability, Awareness, Desire).
- Prompt v2 : ajout de deux consignes (« réponds none si le texte ne décrit pas une difficulté concrète d'adoption dans une équipe : publicité, opinion générale, marché de l'emploi, témoignage positif » et « en cas de doute, choisis none »).
- Exactitude v2 : **54 % (49/90)**, +5 points. Le LLM répond désormais `none` sur 36 des 53 textes hors sujet. Confusions restantes : `none` → Ability (8) et Awareness (5), Desire dispersé (Awareness 3, Reinforcement 3).
- Objectif de la charte (70 %) non atteint : à retravailler au Sprint 3 (exemples dans le prompt, définitions plus nettes entre Desire et Reinforcement).
- Verbatims classés : 447/447 avec le prompt v2. Répartition : [none …, Ability …, Desire …, Awareness …, Reinforcement …, Knowledge …].
- Base ChromaDB : [~860] morceaux de verbatims avec leur étape ADKAR, 5 sections du guide.
- Score rubric des 10 plans : [X,X]/5 (pertinent [..], actionnable [..], fondé [..]), notés par Florian, Alexandre et Sasha.

**Problème rencontré + solution :**
- `KeyError: 'JEDHA_AI_BASE_URL'` : `rag/llm.py` exigeait l'adresse Jedha → rendue optionnelle (`os.environ.get`).
- Clé API refusée (`401`) : `sk-` écrit deux fois, puis clé Jedha envoyée à OpenAI → configuration Jedha complète dans le `.env` (adresse + préfixe `openai/` des modèles).
- Classification interrompue avant la fin : le script n'enregistre qu'à la fin d'un lancement → relance par paquets de 50 (`for i in …; do CLASSIFY_LIMIT=50 …`), chaque paquet est sauvegardé.
- Plans sans filtre par étape tant que `classified.parquet` n'existait pas → réindexation après la classification, puis filtre `where` remis par Alexandre.
- Jeu de test d'abord poussé sur la mauvaise branche (`charte-gitignore`) → fichier recopié sur `jeu-de-test`, branche inutile supprimée.
- Limite à assumer : le jeu de test a été pré-annoté par un LLM puis corrigé à la main ; l'accord entre deux humains (étape 2.4) n'a pas été mesuré.

**Preuve :** `docs/img/j5_mlflow.png`, `docs/img/j5_mlflow_v1_v2.png` (branche `23-evaluation`), `eval/results_v1.csv`, `eval/results_v2.csv`, `eval/plans_a_noter.md`, `eval/rubric.csv`, PR #48, #49, #50, #51



## J6 — 27/11/2026

**Fait :**
- Sasha : API FastAPI à 4 routes (`api/main.py`, PR #56) : `/health` (l'application répond), `/analyze` (classe un nouveau verbatim), `/stats` (frictions par étape et par thème pour le tableau de bord), `/action-plan` (plan d'action RAG). Documentation automatique sur `/docs`.
- Alexandre : interface Streamlit à 3 pages pour le manager (`ui/app.py`, PR #57) : tableau de bord, plan d'action avec les verbatims utilisés, analyse d'un verbatim. Correction du graphique (ordre ADKAR, axes nommés) et captures des 3 pages (PR #58).
- Florian : Dockerfile, `.dockerignore` et `docker-compose.yml` (PR #51, à terminer au J7) ; test Docker au tour 4 de l'étape 7.
- Marine : fichiers Terraform de production (`infra/main.tf`, `infra/variables.tf`, PR #54) vérifiés avec `terraform plan`, sans `apply` ; envoi des 10 plans et de la grille de notation (PR #55) ; relecture et merge des PR #56 et #57, relecture de la PR #51.
- Les quatre : test de bout en bout à distance, en relais sur Discord (Alexandre : collecte, nettoyage, classification → S3 ; Sasha puis Marine : indexation, API, interface sur leur propre Mac), vidéo de secours de la démo. Résultat : 460 verbatims propres et classés dans S3 (447 avant la nouvelle collecte).

**Choix + pourquoi :**
- Une API entre l'IA et l'interface : l'interface ne connaît que 4 adresses, on peut changer le LLM ou la base sans la toucher, et on pourra brancher d'autres outils plus tard.
- Pydantic vérifie les entrées de l'API (texte de 10 à 3 000 caractères, étape ADKAR connue) : une mauvaise demande reçoit une erreur claire (400/422) au lieu de faire planter l'application.
- L'interface affiche des données d'exemple et un avertissement si l'API ne répond pas : la démo ne s'arrête pas net.
- Docker : la même application tourne à l'identique sur nos 4 Mac et sur le serveur. Les secrets restent dans `.env`, lu au lancement, jamais copié dans l'image. L'API n'est joignable que depuis la machine (`127.0.0.1:8000`), seule l'interface est publique (8501).
- Terraform écrit aujourd'hui, appliqué demain : on vérifie à tête reposée la liste de ce qui sera créé (`plan`), et le serveur payant n'est allumé qu'au moment de s'en servir.
- Sécurité de l'infrastructure : bucket S3 privé (accès public bloqué), serveur avec un rôle IAM limité à ce seul bucket (aucune clé AWS sur le serveur), SSH ouvert seulement depuis notre IP.
- Test de bout en bout en relais : chacun·e lance sa partie sur son propre Mac, les données passent par le bucket S3 commun. Ça prouve aussi que l'application marche sur plusieurs machines.

**Chiffres :**
- Test de bout en bout : 460 verbatims propres et classés dans S3 après la nouvelle collecte (+13).
- `/stats` (capture avant la nouvelle collecte) : 447 verbatims analysés, 226 frictions ; blocage principal **Ability** (89 frictions, 39 %), puis Desire 51, Awareness 47, Reinforcement 21, Knowledge 18.
- Thèmes les plus fréquents : qualité du code produit par l'IA (7), peur de perdre son emploi (4), qualité et usage de l'IA (3), perte de plaisir au travail (3).
- Plan d'action : 8 verbatims sources par plan 
- `terraform plan` : 8 ressources à créer, 0 à modifier, 0 à supprimer.
- Tests automatiques : 19 tests pytest OK.

**Problème rencontré + solution :**
- `terraform plan` refusé (`not a valid CIDR block`) : l'adresse IP collée était en IPv6, avec un `%` ajouté par le terminal → IPv4 récupérée directement dans la commande : `-var="my_ip=$(curl -4 -s https://checkip.amazonaws.com)"`.
- Commandes git tapées sur une seule ligne, séparées par des virgules → une commande par ligne.
- Nom de branche `<num>-terraform` refusé par le terminal : `<num>` était à remplacer par le numéro de l'issue (29).
- PR #53 en double : son contenu était déjà sur `main` via la PR #50 (fichiers identiques) → fermée sans merge.
- L'interface ne pouvait pas démarrer tant que `ui/app.py` n'était pas sur `main` → merge de la PR #57 avant le test de bout en bout.
- Graphique du tableau de bord dans l'ordre alphabétique → remis dans l'ordre ADKAR (PR #58).
- `data/` n'était plus ignoré par git depuis la PR #46 (seul `data/raw/` l'était) : la base ChromaDB locale risquait d'être poussée sur GitHub → `data/` remis dans le `.gitignore` (PR #..).

**Preuve :** `docs/img/j6_api_docs.png`, `docs/img/j6_stats_before.png`, `docs/img/j6_stats_after.png`, `docs/img/j6_terraform_plan.png`, `docs/img/j6_dashboard.png`, `docs/img/j6_plan.png`, `docs/img/j6_analyse.png`, `docs/img/j6_demo.mov` (ou lien Google Drive), PR #51, #54, #55, #56, #57, #58