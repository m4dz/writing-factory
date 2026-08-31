# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 | 0.7 |
| Mots | 286 | 193 | 260 | 821 |
| Durée (s) | 400 | 339 | 552 | 713 |
| done_reason | stop | stop | stop | stop |
| Entrées générées | 1 | 1 | 1 | 3 |
| Garde-fou 60 % déclenché | 0 | 0 | 0 | 1 |
| Temps par nœud (s) | {"plan": 191.8, "write": 66.6, "review": 90.4, "repair": 38.4, "coherence": 9.7} | {"plan": 139.1, "write": 71.2, "review": 82.6, "repair": 34.7, "coherence": 9.3} | {"plan": 222.1, "write": 115.8, "review": 156.5, "repair": 38.4, "coherence": 9.8} | {"plan": 229.6, "write": 289.3, "review": 108.0, "repair": 67.1, "coherence": 16.3} |
| Cible 450-600 | ✗ hors cible | ✗ hors cible | ✗ hors cible | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✓ | ✓ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✓ | ✓ | ✓ |
| Élision manquante (« je te appelle ») | ✓ | ✓ | ✓ | ✓ |
| Passé simple *(candidats, à confirmer)* | ✓ | ✓ | ⚠ mis | ✓ |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✗ (0) | ✓ (1) | ✗ (0) | ✓ (3) |
| Heure ou quantité exacte | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Entrées de journal détectées | 1 | 1 | 1 | 8 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (1) | ✓ (1) | ✓ (1) | ✓ (8) |
| Dates consécutives, sans répétition | ✓ : [12] | ✓ : [12] | ✓ : [12] | ✗ 4 doublon(s) : [8, 7, 7, 7, 7, 9, 10, 7] |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) | ✗ (1) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0/0/0/0/0/0/0/0) |
| L4 · Points de suspension = glissement seul | ✓ (0) — mais aucun glissement, échec M1 | ✓ (0) — mais aucun glissement, échec M1 | ✗ (1) 1 hors champ | ✓ (0) — mais aucun glissement, échec M1 |

## Chapitre 2 — interdits scopés (AUTO)

Verdict imposé : **erreur de relevé** · objets actifs : cahier, assiette, égouttoir

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | ✗ | ✓ | ✗ | ✗ |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Quatuor réservé ch. 7 absent | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run B1 | Run B2 | Run B3 | Run BC |
|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |

## Preuves des croix automatiques

- **Run B1** — aucune croix automatique.
- **Run B2** — aucune croix automatique.
- **Run B3**
  - **L4 entrée 1, hors champ du départ** : `…ase me saute aux yeux : "deux assiettes mises, sans y penser..." Mais je suis sûre de ne pas avoir mis deux assiettes hier …`
- **Run BC**
  - **L1 nom propre** : `Judith — …, exactement. "La maison est vide, Judith. Tu es seule." C'est ce que dit le…`

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

