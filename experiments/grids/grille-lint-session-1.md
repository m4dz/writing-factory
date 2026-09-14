# Grille de lint — session 1

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.9 | 0.7 | 0.7 | 0.7 |
| Mots | 384 | 310 | 356 | 452 | 425 | 673 |
| Durée (s) | 53 | 46 | 48 | 66 | 96 | 88 |
| done_reason | stop | stop | stop | stop | stop | stop |
| Cible 400-550 | ✗ hors cible | ✗ hors cible | ✗ hors cible | ✓ | ✓ | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| Élision manquante (« je te appelle ») | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| Passé simple *(candidats, à confirmer)* | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (7) | ✓ (3) | ✗ (0) | ✓ (2) | ✗ (0) | ✓ (1) |
| Heure ou quantité exacte | ✓ (1) | ✓ (1) | ✓ (4) | ✓ (2) | ✓ (1) | ✓ (2) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | Contrôle-2 | Contrôle-3 |
|---|---|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |   |   |

## Preuves des croix automatiques

- **Run 1** — aucune croix automatique.
- **Run 2**
  - **tic d'IA** : `…ant, alors que je me préparais à dîner, je ne pouvais m'empêcher de penser à cette cafetière tiède. Quelque…`
- **Run 3**
  - **incise** : `…uisine ? — Le paquet de café ? a-t-elle répété d'un ton surpris. Non, je ne prends jamais tes affaires …`
- **Contrôle**
  - **exclamation** : `…lie de verrouiller la porte demain soir !…`
  - **incise** : `… caféine matinale." "Oui, peut-être", ai-je répondu distraitement avant de raccrocher.  Je suis resté pla…`
  - **incise** : `…lut frérot ! Comment vas-tu ?" a-t-elle dit d'une voix enjouée. "Bien, merci. Ecoute, je te appelle pa…`
  - **élision** : `… voix enjouée. "Bien, merci. Ecoute, je te appelle parce que... j'ai un petit problème ave…`
- **Contrôle-2**
  - **exclamation** : `…hé d'une voix enjouée :  "Salut frangin ! Quoi de neuf ? J'ai remercié ma sœur et…`
- **Contrôle-3** — aucune croix automatique.

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

