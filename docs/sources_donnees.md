# Sources de données — adoptionia

Ce document explique **quelles données** le projet utilise, **pourquoi** nous les avons choisies, et **lesquelles nous avons écartées**. Il complète la section « Données » de `docs/charte.md`.

---

## 1. Source principale : commentaires Hacker News

- **Quoi :** commentaires publics du forum Hacker News, récupérés via l'API Algolia (`https://hn.algolia.com/api/v1/`), gratuite et sans clé.
- **Pourquoi :** témoignages réels, renouvelés chaque jour, et « sales » (HTML, entités comme `&#x27;`, pseudos, doublons, hors-sujet) : de quoi justifier un vrai ETL.
- **Mots-clés retenus :** voir `notebooks/explore_hn.ipynb` (cellule finale `MOTS_CLES`).
- **Limite :** public surtout composé de développeurs anglophones, plutôt critiques envers l'IA.

---

## 2. Source secondaire (« enquête ») : Anthropic Interviewer ✅

| | |
| --- | --- |
| **Lien** | https://huggingface.co/datasets/Anthropic/AnthropicInterviewer |
| **Contenu** | Transcriptions d'entretiens avec 1 250 professionnels sur leur usage de l'IA au travail : 1 000 « population active générale » (`workforce`), 125 créatifs (`creatives`), 125 scientifiques (`scientists`) |
| **Format** | CSV, 2 colonnes : `transcript_id`, `text` (dialogue « Assistant: … / User: … », environ 5 000 à 27 000 caractères par entretien) |
| **Taille** | 1 250 lignes, environ 11 Mo |
| **Langue** | Anglais |
| **Licence** | Données sous **CC-BY** (code sous MIT) : réutilisation autorisée, **à condition de citer la source** |
| **Consentement** | Les participants ont accepté la publication de leurs transcriptions brutes |

### Grille de sélection (étape 5 du J1)

| Critère exigé | Résultat |
| --- | --- |
| Au moins une colonne de texte rédigé | ✅ Entretiens complets en texte libre |
| Sujet : l'IA au travail | ✅ C'est le thème même de l'étude (intégration de l'IA au travail, rôle des collègues et de la culture d'entreprise, frustrations, avenir) |
| Licence compatible avec un usage pédagogique | ✅ CC-BY |
| Au moins quelques centaines de lignes | ✅ 1 250 entretiens |

### Pourquoi c'est le meilleur choix

1. **Seul candidat qui coche les 4 critères à la fois.**
2. **Complémentaire de Hacker News :** HN = réactions spontanées, surtout de développeurs ; Interviewer = entretiens guidés auprès d'un public plus large (population active générale, créatifs, scientifiques).
3. **Très adapté à ADKAR :** les questions abordent la compréhension, l'envie, les compétences, les difficultés concrètes et la place de l'IA dans l'équipe.
4. **Un second format pour l'ETL :** dialogue à découper (on ne garde que les réponses « User »), alors que HN fournit du HTML en JSON. Cela démontre que notre pipeline gère deux formats.

### Limites assumées

- **Biais possible :** enquête menée par un éditeur d'IA, les participants sont peut-être plus favorables à l'IA que la moyenne. Hacker News, plus critique, équilibre ce biais.
- **Source figée :** pas de nouvelles données dans le temps (la fraîcheur est assurée par Hacker News).
- **Traitement nécessaire :** retirer les questions de l'intervieweur, découper les réponses en verbatims.

### Citation à reprendre (obligatoire avec CC-BY)

> Handa K., Stern M., Huang S. et al. (2025). *Introducing Anthropic Interviewer: What 1,250 professionals told us about working with AI.* Anthropic. https://anthropic.com/research/anthropic-interviewer — Données : https://huggingface.co/datasets/Anthropic/AnthropicInterviewer (CC-BY).

---

## 3. Alternatives étudiées et écartées

| Jeu de données | Lien | Pourquoi écarté |
| --- | --- | --- |
| **WORKBank** (Stanford) | https://huggingface.co/datasets/SALT-NLP/WORKBank | Données réelles (1 500 travailleurs, 104 métiers), mais le sujet est « quelles tâches automatiser », pas le vécu d'un déploiement ; réponses libres courtes ; **aucune licence déclarée** sur la fiche. |
| **ECHO** (Princeton, Reddit) | https://echo.cs.princeton.edu | Très riche (millions de posts de travailleurs), mais base de recherche **sans licence de réutilisation claire**, soumise aux conditions de Reddit ; doublon d'usage avec HN (forum). |
| **Global AI Adoption & Workforce Impact Survey 24-26** (Kaggle) | https://www.kaggle.com/datasets/meruvakodandasuraj/global-ai-adoption-and-workforce-impact-survey-24-26 | Pas de texte libre, aucune source vérifiable, **deux licences contradictoires** affichées : très probablement un jeu fabriqué. |
| **Workplace AI Usage & Security Pulse Survey** (Mendeley) | https://data.mendeley.com/datasets/khx7dkyhm7/1 | **Données synthétiques** : réponses ouvertes générées par un modèle de langage, donc pas de vrais verbatims. |
| **Stack Overflow Developer Survey 2025** | https://survey.stackoverflow.co/2025/ai | Questions surtout à choix multiples, pas de réponses rédigées sur le vécu de l'IA au travail. |

---

## 4. Règles communes aux deux sources

- **Anonymisation :** les pseudos (`author` côté HN) sont supprimés ou hachés dans `etl/transform.py` ; aucune donnée nominative dans `clean/`.
- **Pas d'évaluation individuelle** des personnes (voir « Hors périmètre » de la charte).
- **Citation des sources** dans le README et dans l'interface finale.
