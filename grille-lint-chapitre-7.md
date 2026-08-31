# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run CH7 |
|---|---|
| Température | 0.7 |
| Mots | 361 |
| Durée (s) | 297 |
| done_reason | stop |
| Entrées générées | 2 |
| Garde-fou 60 % déclenché | 0 |
| Temps par nœud (s) | {"write": 156.2, "accumulate": 14.0, "review": 69.0, "repair": 32.0, "coherence": 24.2} |
| Cible 450-600 | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run CH7 |
|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ |
| Point d'exclamation hors dialogue | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ |
| Élision manquante (« je te appelle ») | ✓ |
| Passé simple *(candidats, à confirmer)* | ✓ |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run CH7 |
|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |
| Émotion annoncée avant d'être montrée |   |
| Météo ou obscurité corrélée à la tension |   |
| Information hors du champ perceptif du narrateur |   |
| Doute résolu, dans un sens ou dans l'autre |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run CH7 |
|---|---|
| Exactement une phrase d'accumulation | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (7) |
| Heure ou quantité exacte | ✓ (4) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run CH7 |
|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |
| Les cinq beats présents, dans l'ordre |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run CH7 |
|---|---|
| Entrées de journal détectées | 2 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (2) |
| Dates consécutives, sans répétition | ✓ : [14, 14] (1 même jour — structure imposée) |
| L1 · Noms propres (zéro toléré) | ✗ (1) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✗ (0/0) |
| L4 · Points de suspension = glissement seul | ✓ (1) |

## Chapitre 7 — interdits scopés (AUTO)

Verdict imposé : **hors échelle — brief dédié** · objets actifs : quatuor réservé, activé

| Contrôle attendu | Run CH7 |
|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | — |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) |
| Quatuor réservé ch. 7 absent — N/A ici | — |
| ⚑ Interdits matériels *(drapeau — décor hors du monde)* | — (0) |

## Sessions 5-6 — voix, formulaire et décor (AUTO)

| Contrôle attendu | Run CH7 |
|---|---|
| Attracteurs *(familles : folie, demain qui résout, bouée/océan)* | ✓ (0) |
| Méta-termes en sortie (couperet, squelette, beat…) | ✓ (0) |
| Formulaire par paraphrase (« … est le suivant : ») | ✓ (0) |
| État mental nommé en apposition *(perplexe, songeuse, incrédule…)* | ✓ (0) |
| ⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)* | — (0/0) |
| ⚑ Couple décision-exécution *(candidat, M3 tranche)* | — (0) |
| En-têtes cohérents (jour de semaine ↔ date) | ✓ (0) |
| Accumulation d'étapes, non de beats *(≤ 20 % d'items abstraits)* | — (aucune accumulation) |
| Aucun paragraphe redit *(similarité ≥ 50 %, hors artefacts du code)* | ✓ (0) |
| Accumulation à la première personne | ✓ (0) |
| ⚑ Citation hors ancre *(drapeau — le cahier est fourni, pas fabriqué)* | — (0) |
| Aucune phrase reprise d'un paragraphe à l'autre | ✓ (0) |
| M1 · composition du glissement *(présence, unicité, conformité L4)* | ✓ (1 posé(s), un par entrée, conformes) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run CH7 |
|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run CH7 |
|---|---|
| Tenu en moins de 2 minutes à voix haute |   |
| Aucune phrase reprise deux fois pour la comprendre |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |

## Preuves des croix automatiques

- **Run CH7**
  - **L1 nom propre** : `Bluetooth — …mer. 20 h 00. Le salon. L'enceinte Bluetooth allumée, la musique qui s'échappe …`

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

