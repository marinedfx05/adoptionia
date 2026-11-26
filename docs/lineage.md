# Dictionnaire de données et lignée — adoptionia

Ce fichier répond à la question « d'où vient ce champ, et qu'est-ce qu'on lui a fait ? » pour chaque donnée du projet.

## Vue d'ensemble

```
API Algolia Hacker News
   │  etl/ingest.py  (6 mots-clés du J1, /search_by_date, idempotent)
   ▼
S3 raw/hn/<objectID>.json      ← copie exacte de la réponse de l'API (+ _query, _ingested_at)
   │  python -m etl.run_clean  (extract.py → transform.py → load.py)
   ▼
S3 clean/verbatims.parquet     ← verbatims propres et anonymisés
   │  python -m rag.index
   ▼
ChromaDB data/chroma           ← collections « verbatims » et « adkar_knowledge »
```

`python -m etl.rebuild` refait les deux dernières flèches depuis la zone brute.

## Zone brute : S3 raw/hn/

Un fichier JSON par commentaire, nommé par son `objectID` : relancer l'ingestion ne crée aucun doublon.

| Champ | Origine | Remarque |
| --- | --- | --- |
| objectID, comment_text, author, created_at, created_at_i, story_title, story_id, parent_id, story_url, updated_at, _tags, _highlightResult | réponse de l'API Algolia HN, sans modification | contient encore le pseudo (`author`) et le HTML : la zone brute n'est jamais exposée |
| _query | ajouté par etl/ingest.py | le premier mot-clé qui a trouvé le commentaire |
| _ingested_at | ajouté par etl/ingest.py | horodatage Unix de l'ingestion |

## Fichier propre : clean/verbatims.parquet

| Champ | Type | Origine | Transformation |
| --- | --- | --- | --- |
| verbatim_id | texte | objectID de l'API HN | préfixe "hn_" ; unique |
| source | texte | ajouté | "hn" (la valeur "survey" est prévue pour l'enquête) |
| text | texte | comment_text de l'API HN | citations d'autres commentaires (`>`) retirées ; HTML retiré et entités décodées ; e-mails → [EMAIL], URLs → [URL], mentions @ → [USER] |
| context | texte | story_title de l'API HN | anonymisé comme `text` ; vide si absent |
| author_id | texte | author de l'API HN | empreinte SHA-256 du pseudo mélangé à un sel secret (HASH_SALT, dans le .env), 8 caractères ; le pseudo n'est jamais conservé |
| created_on | date (UTC) | created_at de l'API HN | converti en date UTC |
| ingested_on | date (UTC) | _ingested_at, ajouté à l'ingestion | converti en date UTC |
| lang | texte | calculé | détection automatique (langdetect, résultat stable) ; on garde en et fr |

## Règles de filtrage (dans l'ordre d'etl/transform.py)

| # | Règle | Pourquoi | Lignes restantes (25/11/2026) |
| --- | --- | --- | --- |
| 0 | Entrée : fichiers de raw/hn/ | | 471 |
| 1 | Texte présent (comment_text non vide) | un commentaire supprimé n'a pas de texte | 471 |
| 2 | Exclure les fils « Who is hiring / Seeking work » | ce sont des offres d'emploi, pas des témoignages | 458 |
| 3 | Doublons d'identifiant | sécurité, en plus de l'ingestion idempotente | 458 |
| 4 | Doublons de texte | même texte publié sous deux identifiants | 458 |
| 5 | Longueur entre 30 et 3 000 caractères | trop court = pas de témoignage ; trop long = rare et dilue le sens | 452 |
| 6 | Parle du travail : un mot de WORK_WORDS (etl/transform.py) en début de mot | « network » ne compte pas, « teams » oui | 447 |
| 7 | Langue en ou fr | le modèle et le guide sont en anglais/français | 447 |

Tests : `pytest -v` (tests/test_transform.py, 10 tests) vérifie chaque règle.

## Base vectorielle : ChromaDB (dossier data/chroma, non versionné)

| Collection | Contenu | Identifiant | Origine |
| --- | --- | --- | --- |
| verbatims | morceaux de `text` (texte entier si ≤ 800 caractères, sinon morceaux de 500 avec 50 de chevauchement) + embedding text-embedding-3-small (1 536 nombres) | `<verbatim_id>_<n° du morceau>` | clean/verbatims.parquet |
| adkar_knowledge | une section par étape ADKAR (titre `## …`) + embedding | `kb_<n°>` | knowledge/adkar_guide.md (rédigé par l'équipe) |

Métadonnées de chaque morceau de verbatim : verbatim_id, source, lang, created_on.
L'indexation utilise un `upsert` : relancer `python -m rag.index` ne crée aucun doublon.

## Données personnelles

- Pseudos : jamais en clair après la zone brute (empreinte salée).
- E-mails, URLs, mentions : masqués dans `text` et `context`.
- Limite connue : les noms propres écrits dans un texte ne sont pas masqués (il faudrait un outil de reconnaissance des noms, piste J9).
- Seuls des textes déjà anonymisés sont envoyés à l'API d'embeddings.
