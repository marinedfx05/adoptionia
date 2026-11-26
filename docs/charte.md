# Charte — adoptionia

## L'utilisateur
Un manager (ou référent conduite du changement) qui déploie un outil d'IA dans son équipe.

## La décision qu'il prend
Quelles actions lancer cette semaine pour faire progresser l'adoption.

## Ce que ça coûte aujourd'hui
- Lire et trier 100 retours prend environ une journée.
- Les actions sont choisies « au feeling », sans savoir où l'équipe bloque.
- Les licences IA payées restent inutilisées.

## « Utile », c'est
- Au moins 70 % des verbatims classés dans la bonne étape ADKAR (sur un jeu annoté à la main).
- Un plan de 3 actions, chacune appuyée sur des verbatims cités.
- Une réponse en moins de 15 secondes.

## ML ou LLM ?
LLM + RAG : nos données sont du texte libre et notre sortie est un texte rédigé ;
le RAG oblige le modèle à s'appuyer sur nos données réelles plutôt que d'inventer.

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=
S3_BUCKET=
LLM_API_KEY=
LLM_MODEL=
DISCORD_WEBHOOK=
HASH_SALT=
EMBEDDING_MODEL=

## Données
- Source principale : commentaires Hacker News
    Quoi : commentaires publics du forum Hacker News, récupérés via l'API Algolia (https://hn.algolia.com/api/v1/), gratuite et sans clé.
    Pourquoi : ce sont des témoignages réels et spontanés, à la première personne, sur l'IA au travail : imposition par la direction, refus, formation, échecs, abandon. Ils sont renouvelés chaque jour, ce qui garantit la fraîcheur des données. Ils sont aussi « sales » (HTML, entités comme &#x27;, citations, doublons, hors-sujet), ce qui justifie un vrai pipeline ETL.
    Mots-clés retenus : 6 expressions personnelles entre guillemets suivies de « AI » : "my job", "my company", "my team", "my employer", "my coworkers", "my manager". Elles ont été choisies parmi 54 mots-clés testés, après la lecture et la notation manuelle de 4 269 commentaires (voir notebooks/explore_hn.ipynb).
    Volume : environ 5 400 commentaires bruts depuis 2023, dont environ 1 700 pertinents, plus environ 25 nouveaux commentaires pertinents par semaine.
    Couverture ADKAR : les 5 étapes sont présentes. Ability (la mise en pratique qui échoue) domine, Knowledge et Reinforcement sont plus rares.
    Licence et éthique : contenus publics. Les pseudos (author) sont supprimés à la transformation, et la source est citée.
    Limites : public surtout composé de développeurs anglophones de la tech, plutôt critiques envers l'IA. Environ la moitié des commentaires collectés est hors sujet, donc la classification doit d'abord trier la pertinence. Les témoignages utiles sont surtout récents (2025-2026).
- Source secondaire : Anthropic Interviewer (https://huggingface.co/datasets/Anthropic/AnthropicInterviewer), licence CC-BY. 1 250 entretiens de professionnels sur l'IA au travail, consentement public des participants. Format dialogue : on ne garde que les réponses des participants.
- Source tertiaire : 

## Hors périmètre
Pas de données nominatives, pas d'évaluation individuelle des salariés.