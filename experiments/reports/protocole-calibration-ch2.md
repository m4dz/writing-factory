# Protocole de calibration — Chapitre 2 (session 2)

Objet : calibrer conjointement la génération du chapitre 2 (« Première fuite ») et la fiche `style-auteur.md` (v2 → v3). Frappe directe sur Ollama, sans RAG : toute divergence observée est imputable au couple fiche + brief, jamais au retrieval. Même modèle et même température de référence que la session 1, pour comparabilité.

## 1. Brief machine — chapitre 2

> **Chapitre 2.** Journal intime, première personne, **une seule entrée datée**, un soir. Cible : 450–600 mots.
>
> **Beats, dans l'ordre :**
> 1. **Le rituel.** Elle date, elle note sa journée — banale, en phrases courtes. Sa méthode est posée : dater, noter, relire.
> 2. **La relecture.** Elle relit l'entrée de la veille, comme chaque soir. L'entrée mentionne une seconde assiette, mise à table, laissée là jusqu'au matin.
> 3. **La vérification.** Sa mémoire est nette : elle a dîné seule, une assiette. Elle va à la cuisine, elle vérifie — le geste décrit, pas résumé. La vérification confirme l'entrée, pas sa mémoire.
> 4. **La rationalisation.** Explication raisonnable, argumentée : fatigue, automatisme. C'est ici que vit la phrase d'accumulation : reprendre la soirée dans l'ordre, étape par étape, et une étape cloche.
> 5. **La clôture.** Une mesure de méthode (elle notera plus précisément, désormais), une notation physiologique, une phrase-couperet.
>
> **Matériau imposé :** le cahier, la cuisine, l'assiette. Rien d'autre n'est requis.
> **Une occurrence du glissement** (voir §3, D4) : la pensée approche le départ — pourquoi, où — et la phrase s'interrompt.
>
> **Interdits :** aucun nom propre. Aucun dialogue, aucun personnage en présence. Aucune explication autre que rationnelle, aucune entité, aucune hypothèse surnaturelle formulée. Le registre de l'absence est celui du départ, exclusivement. La narratrice constate ; aucune décision n'est exécutée en scène.

## 2. Protocole de runs

| Run | Conditions | Rôle |
|---|---|---|
| 1–3 | T = 0.7, brief complet | Runs de score, règle 2/3 |
| C | T = 0.7, brief sans les lignes de beats | Run de contrôle : la voix vit-elle dans la fiche seule ? |
| X1, X2 (optionnels) | T = 0.5 / 0.9, brief complet | Exploration de la plage de température, hors score |

Règle de décision inchangée (protocole session 1) : un item échoué sur 2 runs sur 3 désigne une section à durcir ; un échec isolé est du bruit. Tri inchangé : échec **mécanique** → durcir la fiche par l'exemple négatif ; échec **structurel** → prompt d'orchestration (LangGraph), pas la fiche. Précision nouvelle : en frappe directe sans RAG, une fuite lexicale (§3, L2) est un échec **fiche/interdits** — elle ne pourra être imputée au contexte qu'une fois le retrieval branché.

**Archivage try-and-fail :** chaque run raté est conservé tel quel, horodaté, avec sa ligne de grille en en-tête — c'est le matériau du journal des murs (placeholders sections 5–6 de la keynote). Rien ne se jette.

## 3. Extensions de grille (s'ajoutent à `grille-lint-session-2.md`)

**Auto :**

| ID | Contrôle | Règle |
|---|---|---|
| L1 | Noms propres | Échec si toute majuscule hors début de phrase résolue en nom propre. Zéro toléré. |
| L2 | Lint de fuite lexicale | Échec si tout match de la liste champ de la mort (`brief-chapitre-7.md` §2). |
| L3 | Accumulation **par entrée** | Exactement une par entrée de journal (re-scope de « par scène ») : ≥ 60 mots, ≥ 6 virgules, aucun point interne. |
| L4 | Points de suspension | N'existent que comme marque du glissement (D4) : échec si occurrence hors proximité du lexique du départ, ou si > 1 par entrée. |

**Manuel :**

| ID | Contrôle | Règle |
|---|---|---|
| M1 | Le glissement | ≥ 1, lisible : la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel. |
| M2 | Le « tu » | Conforme §6 vérité de surface : adressé à la partie, toléré avec réticence. Échec si « tu » complice ou neutre. |
| M3 | Décision sans geste | Toute décision est notée comme prise ; aucune exécution racontée en scène. |
| M4 | L'entrée répond à côté | La relecture ne confirme jamais la mémoire de la narratrice : l'entrée répond toujours à une question voisine de celle qu'elle se posait. |

## 4. Delta proposé — fiche style v2 → v3 (à valider conjointement)

- **D1 — Unité de compte.** « Scène » → « entrée de journal » partout où la fiche compte (accumulation, physiologie, couperet). Le chapitre 7 à deux entrées reçoit ainsi deux accumulations naturelles : la liste d'effacement, la spirale de capitulation.
- **D2 — Section Dialogue → section Adresse.** Ce roman est sans dialogue : la section actuelle est lettre morte, et son étalon enseigne le contraire du huis clos. Mais son principe directeur survit, transposé : **l'interlocuteur qui répond à côté, c'est le journal.** « Une réponse franche est un échec » devient « une entrée qui confirme la mémoire de la narratrice est un échec » — l'entrée relue répond toujours à une question voisine, et laisse la narratrice avec plus de questions qu'avant la relecture. La section traite aussi le « tu » (adresse à la partie, réticence) qui n'existe pas dans la v2.
- **D3 — Étalons sans noms propres.** « Malet » et « Anna » sortent des étalons (interdit global des noms avant le chapitre 8 — et « Anna » entre en collision avec l'historique du projet). L'étalon 3 (dialogue en présence) est remplacé par un étalon d'adresse/relecture conforme à D2. Les étalons 1, 2, 4 sont conservés : leur contenu (les clés, la coupelle) est assez distant de l'intrigue pour servir de cible de rythme sans contaminer la matière.
- **D4 — Le glissement, avec convention typographique.** Nouvelle entrée de la section Narration : quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt — points de suspension, puis retour immédiat au fait matériel. Les « … » sont interdits partout ailleurs dans le texte : le marqueur devient univoque, donc comptable (L4). Exemple positif et contre-exemple à rédiger dans la fiche.
- **D5 — Interdits augmentés.** S'ajoutent à la liste : tout nom propre ; tout vocabulaire pour l'absence hors du champ du départ ; toute tentative de contact (appel, lettre, recherche).
- **D6 — Décision sans geste.** Nouvelle règle de Narration : la narratrice note ses décisions, jamais leurs exécutions. « J'ai décidé de ranger le cahier ailleurs » existe ; la scène du rangement n'existe pas.
- **D7 — Horizon, hors calibration : profils de quota par régime.** La rigidité formelle de la fiche est la méthode de Judith ; son érosion peut se scénariser. Régimes 1–2 : quotas stricts. Régime 3 : dérèglement délibéré (accumulation qui déborde, couperet qui manque). À instruire plus tard comme directive de `plan_node`, pas maintenant.

## 5. Sortie attendue de la session

1. Grille session 2 remplie, verdict coché.
2. Fiche v3 amendée sur les deltas validés + défauts constatés 2/3.
3. Un chapitre 2 candidat (le meilleur run, éventuellement retouché à la main — la retouche est notée, c'est une donnée de calibration).
4. Le lot de runs ratés horodatés pour le journal des murs.
