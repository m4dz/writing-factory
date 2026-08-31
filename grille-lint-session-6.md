# Grille de lint

Généré par `outillage/grille_session.py`. **Ne pas éditer les lignes AUTO** : elles se régénèrent. Remplir les lignes vides à la main, après lecture à voix haute.

**Règle de décision retenue** — celle du protocole d'origine (`_scene-test-style.md`), qui prime sur celle du paquet test-style : un item échoué sur **2 runs sur 3** désigne une section de la fiche à durcir. Un échec isolé sur un seul run est du bruit, on ne touche pas à la fiche.

**Tri des échecs**, structurant pour la suite : échec **mécanique** → durcir la fiche par l'exemple négatif. Échec **structurel** → c'est le prompt d'orchestration, donc LangGraph, PAS la fiche.

## Conditions des runs

| | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Température | 0.7 | 0.7 | 0.7 | 0.7 |
| Mots | 698 | 370 | 796 | 3525 |
| Durée (s) | 338 | 268 | 386 | 1401 |
| done_reason | stop | stop | stop | length |
| Entrées générées | 1 | 1 | 1 | 3 |
| Garde-fou 60 % déclenché | 0 | 0 | 0 | 2 |
| Temps par nœud (s) | {"write": 146.3, "accumulate": 47.9, "review": 80.4, "repair": 38.0, "coherence": 24.6} | {"write": 124.2, "accumulate": 23.4, "review": 66.5, "repair": 31.3, "coherence": 22.1} | {"write": 160.3, "accumulate": 29.1, "review": 115.3, "repair": 56.5, "coherence": 24.7} | {"plan": 87.7, "write": 590.1, "accumulate": 125.2, "review": 336.7, "repair": 223.5, "coherence": 36.9} |
| Cible 450-600 | ✗ hors cible | ✗ hors cible | ✗ hors cible | ✗ hors cible |

## Mécanique — échec si présent (AUTO)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Lexique pastiche (indicible, ténèbres, effroi…) | ✓ | ✓ | ✓ | ✓ |
| Tic d'IA (« une part de moi », « un mélange de »…) | ✓ | ✓ | ✗ | ✗ |
| Point d'exclamation hors dialogue | ✓ | ✓ | ✓ | ✓ |
| Incise adverbiale ou prépositionnelle (« d'un ton surpris ») | ✓ | ✓ | ✗ | ✓ |
| Élision manquante (« je te appelle ») | ✓ | ✓ | ✓ | ✓ |
| Passé simple *(candidats, à confirmer)* | ✓ | ✓ | ✓ | ⚠ parcourent |

## Mécanique — échec si présent (MANUEL)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Deux adjectifs ou plus coordonnés sur un même nom |   |   |   |   |
| Émotion annoncée avant d'être montrée |   |   |   |   |
| Météo ou obscurité corrélée à la tension |   |   |   |   |
| Information hors du champ perceptif du narrateur |   |   |   |   |
| Doute résolu, dans un sens ou dans l'autre |   |   |   |   |

## Structure — échec si absent (AUTO)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Exactement une phrase d'accumulation | ✓ (1) | ✗ (0) | ✓ (1) | ✗ (3) |
| ≥ 1 phrase-couperet (3-6 mots) en fin de paragraphe | ✓ (1) | ✓ (1) | ✓ (1) | ✓ (4) |
| Heure ou quantité exacte | ✓ (2) | ✓ (3) | ✓ (2) | ✓ (13) |

## Structure — échec si absent (MANUEL)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Une vérification matérielle de l'anomalie (le geste, décrit) |   |   |   |   |
| Le décalage dans le dialogue (la sœur répond à côté) |   |   |   |   |
| Les cinq beats présents, dans l'ordre |   |   |   |   |

## Protocole ch. 2 — contrôles L1-L4 (AUTO)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Entrées de journal détectées | 1 | 1 | 1 | 3 |
| En-têtes au format normalisé (« Jour N. Météo. ») | ✓ (1) | ✓ (1) | ✓ (1) | ✓ (3) |
| Dates consécutives, sans répétition | ✓ : [12] | ✓ : [12] | ✓ : [12] | ✓ : [12, 13, 14] |
| L1 · Noms propres (zéro toléré) | ✓ (0) | ✓ (0) | ✓ (0) | ✗ (1) |
| L2 · Fuite lexicale — champ de la mort | ✓ (0) | ✓ (0) | ✓ (0) | ✗ (1) |
| L2b · Fuite ambiguë (« disparue ») — signalée, non bloquante | — (0) | — (0) | — (0) | — (0) |
| L3 · Accumulation par entrée (≥60 mots, ≥6 virg.) | ✓ (1) | ✗ (0) | ✓ (1) | ✓ (1/1/1) |
| L4 · Points de suspension = glissement seul | ✓ (1) | ✓ (1) | ✓ (1) | ✓ (3) |

## Chapitre 2 — interdits scopés (AUTO)

Verdict imposé : **erreur de relevé** · objets actifs : cahier, assiette, égouttoir

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Verdict du chapitre présent (lint EN PRÉSENCE) | ✗ | ✗ | ✓ | ✓ |
| Termes réservés absents (la tierce, l'errata, le bon à tirer) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Quatuor réservé ch. 7 absent | ✓ (0) | ✓ (0) | ✓ (0) | ✗ (2) |
| ⚑ Interdits matériels *(drapeau — décor hors du monde)* | ⚑ (travail hors du domicile) | ⚑ (travail hors du domicile) | ⚑ (lave-vaisselle, travail hors du domicile) | ⚑ (lave-vaisselle, sac à main, travail hors du domicile, télévision) |

## Sessions 5-6 — voix, formulaire et décor (AUTO)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Attracteurs *(familles : folie, demain qui résout, bouée/océan)* | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Méta-termes en sortie (couperet, squelette, beat…) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Formulaire par paraphrase (« … est le suivant : ») | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| État mental nommé en apposition *(perplexe, songeuse, incrédule…)* | ✗ (1) | ✗ (1) | ✗ (1) | ✗ (1) |
| ⚑ « je décide de » ≤ 1/entrée *(drapeau, non bloquant)* | ⚑ (7) | — (1) | ⚑ (6) | ⚑ (0/0/4) |
| ⚑ Couple décision-exécution *(candidat, M3 tranche)* | — (0) | ⚑ (1) | ⚑ (1) | ⚑ (2) |
| En-têtes cohérents (jour de semaine ↔ date) | ✓ (0) | ✓ (0) | ✓ (0) | ✓ (0) |
| Accumulation d'étapes, non de beats *(≤ 20 % d'items abstraits)* | ✓ (0%) | — (aucune accumulation) | ✓ (0%) | ✓ (0%/0%/17%) |
| M1 · composition du glissement *(présence, unicité, conformité L4)* | ✓ (1 posé(s), un par entrée, conformes) | ✓ (1 posé(s), un par entrée, conformes) | ✓ (1 posé(s), un par entrée, conformes) | ✓ (3 posé(s), un par entrée, conformes) |

## Protocole ch. 2 — contrôles M1-M4 (MANUEL)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| M1 · Le glissement — la phrase s'interrompt au bord du où/pourquoi, puis retour immédiat à un fait matériel |   |   |   |   |
| M2 · Le « tu » — adressé à celle qui est partie, toléré avec réticence (échec si complice ou neutre) |   |   |   |   |
| M3 · Décision sans geste — toute décision est notée, aucune exécution racontée en scène |   |   |   |   |
| M4 · L'entrée répond à côté — la relecture ne confirme jamais la mémoire de la narratrice |   |   |   |   |

## Oral — jugement à la lecture (MANUEL, debout, chronométré)

| Contrôle attendu | Run S6-1 | Run S6-2 | Run S6-3 | Run S6-C |
|---|---|---|---|---|
| Tenu en moins de 2 minutes à voix haute |   |   |   |   |
| Aucune phrase reprise deux fois pour la comprendre |   |   |   |   |
| Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix |   |   |   |   |

## Preuves des croix automatiques

- **Run S6-1**
  - **accumulation** : `Je suis revenue de mon travail, j'ai déposé mes affaires dans l'entrée, je suis allée directement dans la cuisine pour préparer mon dîner, j'ai sorti …`
  - **L3 entrée 1** : `Je suis revenue de mon travail, j'ai déposé mes affaires dans l'entrée, je suis allée directement dans la cuisine pour préparer mon dîner, j'ai sorti …`
- **Run S6-2**
  - **⚑ couple décision-exécution** : `[geste narré] « Je décide de rétablir ma soirée, de la commencer depuis le début, de n… » puis « Peut-être que cela m'aidera à comprendre où j'ai pu me tromper.… » (me)`
- **Run S6-3**
  - **tic d'IA** : `…iettes tourner dans le cycle de lavage. Je ne peux m'empêcher de ressentir une certaine frustration face…`
  - **incise** : `…urnée de travail intensive. Peut-être ai-je simplement oublié de ranger une deuxième assiette …`
  - **⚑ couple décision-exécution** : `[geste narré] « Je décide de reconstruire ma soirée étape par étape, en commençant par… » puis « J'ai dû retirer mes chaussures dans l'entrée, poser mes affaires sur l… » (mes)`
  - **accumulation** : `Je rentre chez moi, je retire mes chaussures dans l'entrée, je pose mes affaires sur la console, je me rends dans la cuisine, je sors une assiette du …`
  - **L3 entrée 1** : `Je rentre chez moi, je retire mes chaussures dans l'entrée, je pose mes affaires sur la console, je me rends dans la cuisine, je sors une assiette du …`
- **Run S6-C**
  - **tic d'IA** : `…veille. Mais mon esprit était ailleurs. Je ne pouvais pas m'empêcher de penser à Romane et à la façon dont notr…`
  - **⚑ couple décision-exécution** : `[geste narré] « J'ai décidé de me lever pour aller vérifier si tout était en ordre dan… » puis « Je me suis dirigée vers la porte de la cuisine pour l'ouvrir.… » (dirigée)`
  - **⚑ couple décision-exécution** : `[geste narré] « Je décide de refaire le fil de ma soirée d'hier, étape par étape, pour… » puis « J'ai accroché mon manteau dans l'entrée et j'ai posé mon sac à main su… » (accroché, posé)`
  - **accumulation** : `Je suis revenue dans la cuisine pour vérifier le nombre d'assiettes sur l'égouttoir, il y en avait deux, j'ai réalisé que j'avais sorti une deuxième a…`
  - **accumulation** : `Je suis rentrée chez moi à 18h30, j'ai accroché mon manteau à la patère de l'entrée, j'ai posé mon sac à main sur la console, je suis allée dans la cu…`
  - **accumulation** : `Je referme le cahier et le pose sur la table de la cuisine, à côté de mon carnet, je me tiens debout, les mains sur le bord de l'évier, fixant les deu…`
  - **L1 nom propre** : `Romane — …r sorti une deuxième assiette pour Romane, par habitude. J'ai réalisé que je…`
  - **L2 fuite** : `fantôme — …Alors, pourquoi est-elle encore là, comme un fantôme du passé ?  Je décide de vérifier une derniè…`
  - **L3 entrée 1** : `Je suis revenue dans la cuisine pour vérifier le nombre d'assiettes sur l'égouttoir, il y en avait deux, j'ai réalisé que j'avais sorti une deuxième a…`
  - **L3 entrée 2** : `Je suis rentrée chez moi à 18h30, j'ai accroché mon manteau à la patère de l'entrée, j'ai posé mon sac à main sur la console, je suis allée dans la cu…`
  - **L3 entrée 3** : `Je referme le cahier et le pose sur la table de la cuisine, à côté de mon carnet, je me tiens debout, les mains sur le bord de l'évier, fixant les deu…`

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

