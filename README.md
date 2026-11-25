# adoptionia
Projet final AI fullstack

---

## Jour 1 — Partie 4 : exploration Hacker News (Alexandre, tranche données)

Objectif : choisir les mots-clés pour récupérer, via l'API Algolia de Hacker News, des commentaires où une personne raconte son expérience de l'adoption de l'IA au travail. Ces commentaires seront ensuite classés selon ADKAR.

Détail complet, chiffres et extraits : [`notebooks/explore_hn.ipynb`](notebooks/explore_hn.ipynb).

### Décision

Endpoint `/search_by_date`, 6 mots-clés :

`"my job" AI` · `"my company" AI` · `"my team" AI` · `"my employer" AI` · `"my coworkers" AI` · `"my manager" AI`

La configuration à reprendre dans l'ETL (`MOTS_CLES`, `ENDPOINT`, `FILTRES`) se trouve dans la dernière cellule de code du notebook.

### Comment on a choisi

- 54 mots-clés testés et 4 269 commentaires lus et notés à la main, sans voir le mot-clé qui les avait ramenés (0 = hors sujet, 1 = partiel, 2 = témoignage riche).
- Ce qui fonctionne : une expression personnelle entre guillemets suivie de « AI ». Score moyen de 31/100, contre 8/100 pour les mots-clés sans guillemets.
- Les mots-clés pensés pour une étape ADKAR précise (« AI will replace my job », « don't know how to use AI »…) ne fonctionnent pas. Les étapes ADKAR apparaissent dans les témoignages ramenés par les 6 expressions.
- Chaque mot-clé retenu a été vérifié sur 70 commentaires (deux passes de lecture) : entre 39 et 60 % de commentaires pertinents. Les 6 mots-clés ne partagent que 3 % de doublons.

### Volume attendu

- Environ 5 400 commentaires bruts depuis 2023, dont environ 1 700 pertinents (estimation à ±25 %).
- Environ 25 nouveaux commentaires pertinents par semaine, donc les 2 000 seront atteints vers fin février 2027.
- Si on manque de données avant, 4 mots-clés de réserve sont prêts (deuxième passe de lecture à faire avant de les ajouter) : `"my org" AI`, `"my workplace" AI`, `"my boss" AI`, `"our company" AI`.

### Pour l'ETL

- Paramètres : `tags=comment` et `restrictSearchableAttributes=comment_text` (pour ne pas récupérer des commentaires où « AI » n'apparaît que dans le titre du fil).
- Découper la collecte par tranches de 6 mois : l'API ne renvoie jamais plus de 1 000 résultats par requête.
- Ne pas se fier à `nbHits` : c'est parfois une estimation fausse. Il faut compter les résultats réellement téléchargés.
- Une pause de 0,6 s entre deux appels, un timeout de 15 s et 3 essais en cas d'erreur.

### Pour le nettoyage

- Retirer le HTML (`<p>`, `<a>`, `<code>`) et décoder les entités (`&#x27;`, `&gt;`…) avec `html.unescape`. On en trouve dans 85 % des commentaires.
- Supprimer les citations d'autres commentaires, c'est-à-dire les lignes qui commencent par `>` (18 % des commentaires).
- Supprimer le champ `author` (pseudo).
- Dédoublonner sur `objectID`, puis sur le texte normalisé (le même texte est parfois publié sous deux identifiants).
- Écarter les textes de moins de 150 caractères et les fils « Who is hiring » / « Seeking work ».

### Pour la classification

- Environ la moitié des commentaires collectés sera hors sujet. Il faut d'abord trier « pertinent / pas pertinent », puis classer selon ADKAR.
- Les notes manuelles (environ 4 800 commentaires, fichier `data/notes_pertinence.json`) peuvent servir de jeu de test étiqueté. Elles ne sont pas sur Git : demander le fichier à Alexandre.

### Limites à assumer

- Population : surtout des développeurs anglophones de la tech, plutôt critiques envers l'IA.
- Les étapes Knowledge et Reinforcement sont peu représentées. Ability (la mise en pratique qui échoue) domine.
- Notation faite par une seule personne. Un deuxième annotateur sur une centaine de commentaires renforcerait le résultat.
- Les témoignages pertinents sont surtout récents (2025-2026). Avant 2025, seul un commentaire sur cinq est utile environ.
