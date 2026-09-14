# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 | 0.7 |
| Mots | 185 | 201 | 366 | 1260 |
| Durée (s) | 226 | 236 | 319 | 837 |
| done_reason | stop | stop | stop | stop |
| Entrées générées | 1 | 1 | 1 | 3 |
| Garde-fou 60 % déclenché | 1 | 0 | 0 | 0 |
| Temps par nœud (s) | {"write": 142.2, "review": 34.7, "repair": 28.7, "coherence": 19.1} | {"write": 124.5, "review": 56.8, "repair": 32.2, "coherence": 19.6} | {"write": 160.7, "review": 91.6, "repair": 45.3, "coherence": 20.7} | {"plan": 141.3, "write": 347.5, "review": 234.7, "repair": 92.4, "coherence": 18.8} |
| Cible 450-600 | ✗ hors cible | ✗ hors cible | ✗ hors cible | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✓ | ✓ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✗ | ✓ | ✗ |
| Élision manquante (« je te appelle ») | ✓ | ✓ | ✓ | ✗ |
| Passé simple *(candidats, à confirmer)* | ✓ | ✓ | ⚠ parcourent | ⚠ pris |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (2) | ✗ (0) | ✓ (3) | ✓ (7) |
| Heure ou quantité exacte | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Entrées de journal détectées | 1 | 1 | 1 | 1 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (1) | ✓ (1) | ✓ (1) | ✗ (0) |
| Dates consécutives, sans répétition | ✓ : [12] | ✓ : [12] | ✓ : [12] | — |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) | ✓ (0) | ✓ (0) | ✗ (1) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| L4 · Points de suspension = glissement seul | ✓ (0) — mais aucun glissement, échec M1 | ✓ (0) — mais aucun glissement, échec M1 | ✓ (0) — mais aucun glissement, échec M1 | ✓ (0) — mais aucun glissement, échec M1 |

## Chapitre 2 — interdits scopés (AUTO)

Verdict imposé : **erreur de relevé** · objets actifs : cahier, assiette, égouttoir

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | ✗ | ✗ | ✗ | ✗ |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Quatuor réservé ch. 7 absent | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run Bp1 | Run Bp2 | Run Bp3 | Run BpC |
|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |

## Preuves des croix automatiques

- **Run Bp1** — aucune croix automatique.
- **Run Bp2**
  - **incise** : `…ude sans m'en rendre compte ? Ou bien ai-je simplement mal compté hier soir, dans la pénombre …`
- **Run Bp3** — aucune croix automatique.
- **Run BpC**
  - **incise** : `…e narratrice qui semble perdre pied. Est-elle vraiment folle, ou est-ce simplement une impress…`
  - **élision** : `…sir le lien qui les unit. Peut-être est-ce intentionnel de l'auteur, mais cela me frustre un pe…`
  - **élision** : `…e quoi que ce soit dans la nuit. Serais-je en train de perdre la tête ?  Assise à la …`
  - **L2 fuite** : `mortes — … dans la forêt. Le texte dit : "Les feuilles mortes craquaient sous ses pas, alors qu'elle avanç…`

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

