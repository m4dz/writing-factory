# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 |
| Mots | 490 | 638 | 552 |
| Durée (s) | 297 | 358 | 374 |
| done_reason | stop | stop | stop |
| Entrées générées | 1 | 1 | 1 |
| Garde-fou 60 % déclenché | 0 | 0 | 0 |
| Temps par nœud (s) | {"write": 137.4, "accumulate": 23.3, "review": 76.3, "repair": 36.3, "coherence": 22.7} | {"write": 160.3, "accumulate": 26.3, "review": 95.9, "repair": 56.2, "coherence": 25.5} | {"write": 387.5, "accumulate": 76.9, "review": 100.6, "repair": 521.0, "coherence": 24.3} |
| Cible 450-600 | ✓ | ✗ hors cible | ✓ |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✗ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✓ | ✓ |
| Élision manquante (« je te appelle ») | ✓ | ✗ | ✓ |
| Passé simple *(candidats, à confirmer)* | ✓ | ⚠ mis | ✓ |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Exactement une phrase d'accumulation | ✓ (1) | ✗ (2) | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (2) | ✓ (4) | ✓ (9) |
| Heure ou quantité exacte | ✓ (8) | ✓ (7) | ✓ (2) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Entrées de journal détectées | 1 | 1 | 1 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (1) | ✓ (1) | ✓ (1) |
| Dates consécutives, sans répétition | ✓ : [12] | ✓ : [12] | ✓ : [12] |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2 · Fuite lexicale — champ de la mort | ✗ (1) | ✓ (0) | ✓ (0) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✓ (1) | ✓ (1) | ✗ (0) |
| L4 · Points de suspension = glissement seul | ✓ (1) | ✓ (1) | ✓ (1) |

## Chapitre 2 — interdits scopés (AUTO)

Verdict imposé : **erreur de relevé** · objets actifs : cahier, assiette, égouttoir

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | ✓ | ✓ | ✗ |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) | ✓ (0) | ✓ (0) |
| Quatuor réservé ch. 7 absent | ✓ (0) | ✓ (0) | ✓ (0) |
| ⚑ Interdits matériels *(drapeau — décor hors du monde)* | — (0) | — (0) | ⚑ (télévision) |

## Sessions 5-6 — voix, formulaire et décor (AUTO)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Attracteurs *(familles : folie, demain qui résout, bouée/océan)* | ✗ (1) | ✗ (1) | ✓ (0) |
| Méta-termes en sortie (couperet, squelette, beat…) | ✓ (0) | ✓ (0) | ✓ (0) |
| Formulaire par paraphrase (« … est le suivant : ») | ✓ (0) | ✓ (0) | ✓ (0) |
| État mental nommé en apposition *(perplexe, songeuse, incrédule…)* | ✓ (0) | ✓ (0) | ✓ (0) |
| ⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)* | ⚑ (3) | — (0) | — (0) |
| ⚑ Couple décision-exécution *(candidat, M3 tranche)* | — (0) | — (0) | — (0) |
| En-têtes cohérents (jour de semaine ↔ date) | ✓ (0) | ✓ (0) | ✓ (0) |
| Accumulation d'étapes, non de beats *(≤ 20 % d'items abstraits)* | ✓ (3%) | ✓ (0%) | — (aucune accumulation) |
| Aucun paragraphe redit *(similarité ≥ 50 %, hors artefacts du code)* | ✓ (0) | ✓ (0) | ✓ (0) |
| Aucune phrase reprise d'un paragraphe à l'autre | ✓ (0) | ✗ (4) | ✗ (3) |
| M1 · composition du glissement *(présence, unicité, conformité L4)* | ✓ (1 posé(s), un par entrée, conformes) | ✓ (1 posé(s), un par entrée, conformes) | ✓ (1 posé(s), un par entrée, conformes) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run S7-1 | Run S7-2 | Run S7-3 |
|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |

## Preuves des croix automatiques

- **Run S7-1**
  - **attracteur** : `… cette question de côté pour le moment. Demain est un autre jour, et j'aurai besoin de toutes mes forces…`
  - **accumulation** : `18h30, la table du séjour, le cahier refermé, le carnet ouvert, 19h00, la cuisine, l'égouttoir en vue, hier la vaisselle, aujourd'hui le compte, 19h15…`
  - **L2 fuite** : `fantôme — …e à ne plus penser à cette deuxième assiette fantôme. Demain est un autre jour, et j'ai un manusc…`
  - **L3 entrée 1** : `18h30, la table du séjour, le cahier refermé, le carnet ouvert, 19h00, la cuisine, l'égouttoir en vue, hier la vaisselle, aujourd'hui le compte, 19h15…`
- **Run S7-2**
  - **tic d'IA** : `…u cahier du soir est là, devant moi, et je ne peux m'empêcher de la relire, encore et encore. Hier soir,…`
  - **élision** : `…idée. Demain sera un autre jour, me dis-je en fermant les yeux. Demain, je noterai to…`
  - **attracteur** : `…à ce point. Je me sens fatiguée, vidée. Demain sera un autre jour, me dis-je en fermant les yeux. Demain,…`
  - **accumulation** : `Je suis revenue à 19h30, j'ai posé le cahier sur la table du séjour, je me suis dirigée vers la cuisine, j'ai ouvert le robinet, j'ai laissé l'eau cou…`
  - **accumulation** : `Je l'ai laissée sur la table jusqu'au matin", j'ai compris que j'avais écrit cela hier soir en pensant avoir mis deux assiettes, j'ai refermé le cahie…`
  - **L3 entrée 1** : `Je suis revenue à 19h30, j'ai posé le cahier sur la table du séjour, je me suis dirigée vers la cuisine, j'ai ouvert le robinet, j'ai laissé l'eau cou…`
- **Run S7-3** — aucune croix automatique.

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

