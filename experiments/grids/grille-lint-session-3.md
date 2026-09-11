# Grille de lint — session 1

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 | 0.7 | 0.5 | 0.9 |
| Mots | 492 | 492 | 439 | 446 | 338 | 583 |
| Durée (s) | 111 | 67 | 61 | 60 | 49 | 83 |
| done_reason | stop | stop | stop | stop | stop | stop |
| Cible 450-600 | ✓ | ✓ | ✗ hors cible | ✗ hors cible | ✗ hors cible | ✓ |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Élision manquante (« je te appelle ») | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Passé simple *(candidats, à confirmer)* | ⚠ mis | ✓ | ⚠ mis | ✓ | ⚠ mis | ⚠ pris |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (1) | ✓ (1) | ✓ (4) | ✓ (1) | ✓ (5) | ✓ (4) |
| Heure ou quantité exacte | ✓ (1) | ✗ (0) | ✗ (0) | ✗ (0) | ✓ (2) | ✓ (1) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Entrées de journal détectées | 1 | 1 | 1 | 1 | 1 | 1 |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) | ✓ (0) | ✗ (1) | ✓ (0) | ✓ (0) | ✓ (0) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) | ✗ (0) |
| L4 · Points de suspension = glissement seul | ✓ (0) — mais aucun glissement, échec M1 | ✗ (2) >1/entrée, 2 hors champ | ✗ (4) >1/entrée, 2 hors champ | ✗ (2) >1/entrée | ✗ (1) 1 hors champ | ✗ (4) >1/entrée, 3 hors champ |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle | X1 | X2 |
|---|---|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |   |   |

## Preuves des croix automatiques

- **Run 1** — aucune croix automatique.
- **Run 2**
  - **L4 entrée 1, hors champ du départ** : `…ire me joue des tours à cause de la fatigue ? Je ne sais pas... Et je ne veux pas savoir.  Ce qui compte, c'est que je vais…`
  - **L4 entrée 1, hors champ du départ** : `…our, une nouvelle journée à remplir de routine et d'oubli.  ...…`
- **Run 3**
  - **L2 fuite** : `tombe — …é, comme pour éviter qu'elle ne glisse et ne tombe par terre. Le reste de nourriture avait séch…`
  - **L4 entrée 1, hors champ du départ** : `…lle laissée dans l'évier, la douche avant d'aller me coucher... Et puis j'ai réalisé quelque chose.  Je me suis levée et je…`
  - **L4 entrée 1, hors champ du départ** : `…stoire d'assiette sale. Mais je ne peux m'empêcher de penser... où donc est passée l'autre assiette ?…`
- **Contrôle** — aucune croix automatique.
- **X1**
  - **L4 entrée 1, hors champ du départ** : `… l'avenir pour éviter ce genre de confusion.  [Le glissement...]  Pourquoi est-ce que je ne me souviens pas de ça ? Où ai-j…`
- **X2**
  - **exclamation** : `…moi hier soir. Mais cela n'a aucun sens ! Je suis seule dans cette maison depuis……`
  - **incise** : `…-vaisselle. Comment est-ce possible ? Ai-je simplement mal compté ? ai-je mal vu ?  Je décide …`
  - **L4 entrée 1, hors champ du départ** : `…e : 450–600 mots.  Je note ce jour, comme chaque jour depuis… depuis que tout a commencé. Le rituel est toujours le même …`
  - **L4 entrée 1, hors champ du départ** : `… lave-vaisselle et je compte les assiettes. Une, deux, trois… Trois assiettes sales, comme si quelqu'un avait mangé avec …`
  - **L4 entrée 1, hors champ du départ** : `…cela n'a aucun sens ! Je suis seule dans cette maison depuis…  Non, je refuse de penser à ça. Je vais trouver une explica…`

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

