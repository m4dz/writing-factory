# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 | 0.7 |
| Mots | 375 | 1691 | 566 | 230 |
| Durée (s) | 273 | 874 | 365 | 202 |
| done_reason | stop | stop | stop | stop |
| Entrées générées | 1 | 3 | 1 | 1 |
| Garde-fou 60 % déclenché | 0 | 0 | 0 | 0 |
| Temps par nœud (s) | {"write": 127.1, "accumulate": 19.9, "glisse": 7.1, "review": 61.3, "repair": 33.2, "coherence": 23.4} | {"plan": 103.2, "write": 265.2, "accumulate": 141.5, "glisse": 44.8, "review": 200.6, "repair": 92.2, "coherence": 25.7} | {"write": 139.5, "accumulate": 59.0, "glisse": 17.7, "review": 83.0, "repair": 41.1, "coherence": 24.2} | {"write": 79.4, "accumulate": 28.0, "glisse": 6.7, "review": 39.6, "repair": 25.7, "coherence": 21.4} |
| Cible 450-600 | ✗ hors cible | ✗ hors cible | ✓ | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✓ | ✓ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✗ | ✓ | ✓ | ✓ |
| Élision manquante (« je te appelle ») | ✗ | ✓ | ✓ | ✓ |
| Passé simple *(candidats, à confirmer)* | ⚠ mis | ⚠ mis | ✓ | ✓ |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✓ (1) | ✗ (3) | ✓ (1) | ✓ (1) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (1) | ✓ (3) | ✓ (2) | ✗ (0) |
| Heure ou quantité exacte | ✗ (0) | ✓ (4) | ✗ (0) | ✗ (0) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Entrées de journal détectées | 1 | 3 | 1 | 1 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (1) | ✓ (3) | ✓ (1) | ✓ (1) |
| Dates consécutives, sans répétition | ✓ : [12] | ✓ : [12, 13, 14] | ✓ : [12] | ✓ : [12] |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) | ✗ (1) | ✓ (0) | ✓ (0) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✓ (1) | ✓ (1/1/1) | ✓ (1) | ✓ (1) |
| L4 · Points de suspension = glissement seul | ✓ (0) — mais aucun glissement, échec M1 | ✓ (1) | ✓ (0) — mais aucun glissement, échec M1 | ✓ (0) — mais aucun glissement, échec M1 |

## Chapitre 2 — interdits scopés (AUTO)

Verdict imposé : **erreur de relevé** · objets actifs : cahier, assiette, égouttoir

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | ✗ | ✗ | ✓ | ✓ |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Quatuor réservé ch. 7 absent | ✓ (0) | ✓ (0) | ✗ (1) | ✓ (0) |

## Session 5 — voix et formulaire (AUTO)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Attracteurs (« Demain est un autre jour », bouée, océan) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Méta-termes en sortie (couperet, squelette, beat…) | ✓ (0) | ✓ (0) | ✗ (1) | ✗ (1) |
| Formulaire par paraphrase (« … est le suivant : ») | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| ⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)* | — (0) | — (0/0/0) | ⚑ (2) | — (0) |
| ⚑ Couple décision-exécution *(candidat, M3 tranche)* | — (0) | — (0) | — (0) | — (0) |
| En-têtes cohérents (jour de semaine ↔ date) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run C1 | Run CC | Run C2 | Run C3 |
|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |

## Preuves des croix automatiques

- **Run C1**
  - **incise** : `… tard, j'étais fatiguée, peut-être avais-je agi mécaniquement sans y prêter attention. J'ai essayé de…`
  - **élision** : `…tard, j'étais fatiguée, peut-être avais-je agi mécaniquement sans y prêter attention. …`
  - **accumulation** : `Je suis rentrée tard, j'ai rangé mes affaires, je me suis préparé un thé, je me suis installée dans le salon, j'ai allumé la télévision, j'ai regardé …`
  - **L3 entrée 1** : `Je suis rentrée tard, j'ai rangé mes affaires, je me suis préparé un thé, je me suis installée dans le salon, j'ai allumé la télévision, j'ai regardé …`
- **Run CC**
  - **accumulation** : `Hier soir, je suis rentrée chez moi, j'ai posé mon sac à main sur la table de l'entrée, je me suis dirigée vers la cuisine, j'ai sorti une barquette d…`
  - **accumulation** : `Le carnet est ouvert sur la table, une page blanche attendant d'être remplie

Je suis rentrée à 20h30, j'ai enlevé mes chaussures, j'ai allumé la lumi…`
  - **accumulation** : `Je suis rentrée chez moi à 21h30, j'ai enlevé mes chaussures, j'ai allumé la télévision, je me suis préparé un thé, j'ai mangé une pomme, j'ai sorti d…`
  - **L2 fuite** : `fantômes — …ettes sont toujours sur la table, comme deux fantômes dans la pièce d'à côté. Je me tourne et me r…`
  - **L3 entrée 1** : `Hier soir, je suis rentrée chez moi, j'ai posé mon sac à main sur la table de l'entrée, je me suis dirigée vers la cuisine, j'ai sorti une barquette d…`
  - **L3 entrée 2** : `Le carnet est ouvert sur la table, une page blanche attendant d'être remplie

Je suis rentrée à 20h30, j'ai enlevé mes chaussures, j'ai allumé la lumi…`
  - **L3 entrée 3** : `Je suis rentrée chez moi à 21h30, j'ai enlevé mes chaussures, j'ai allumé la télévision, je me suis préparé un thé, j'ai mangé une pomme, j'ai sorti d…`
- **Run C2**
  - **méta-terme** : `…ir plus que ce qu'il y a. Pas ce soir.  Couperet : je me relève, je note cette résolutio…`
  - **accumulation** : `Rentrée tard, deux assiettes mises sur la table, sans y penser, laissé la vaisselle sale jusqu'au matin, relu l'entrée de la veille, marquée par le pa…`
  - **L3 entrée 1** : `Rentrée tard, deux assiettes mises sur la table, sans y penser, laissé la vaisselle sale jusqu'au matin, relu l'entrée de la veille, marquée par le pa…`
- **Run C3**
  - **méta-terme** : `…s mains sont glacées en écrivant cela.  Couperet.…`
  - **accumulation** : `Je suis revenue du travail, j'ai rangé mes affaires, je me suis changée, j'ai préparé le dîner pour deux, j'ai mangé seule, j'ai laissé une assiette s…`
  - **L3 entrée 1** : `Je suis revenue du travail, j'ai rangé mes affaires, je me suis changée, j'ai préparé le dîner pour deux, j'ai mangé seule, j'ai laissé une assiette s…`

## Lecture du run de contrôle

Le contrôle (brief sans les 5 lignes « Régime : … ») ne se score pas comme les autres. Trois lectures possibles, à cocher :

- [ ] **Bascules tenues sans les lignes régime** → le style ET la dramaturgie vivent dans la fiche. Meilleur cas.
- [ ] **Voix tenue mais registre monotone** → la fiche porte la voix, le plan de scènes devra porter la dramaturgie. `plan_node` devra émettre une directive de régime par beat.
- [ ] **Voix perdue** → la fiche ne tient pas sans béquille. Retravailler les chunks *voix* et *interdits* avant tout câblage.

## Verdict

- [ ] Fiche validée en l'état (≥ 80 % de la grille sur les 3 runs)
- [ ] Chunks à durcir : ______________________
- [ ] Relève du pipeline, pas de la fiche : ______________________
- [ ] Température à revoir : ______________________

Notes :

