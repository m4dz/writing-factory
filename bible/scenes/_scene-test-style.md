---
id: scene-test-style
type: outil
nom: "Scène test — calibration du style auteur"
version: 1
usage: "Génération x3 avec style-auteur.md en contexte, lecture à voix haute, grille de lint"
---

# Scène test — calibration du style

## Objectif

Une scène unique, générée trois fois avec `style-auteur.md` en contexte, pour mesurer ce que le modèle tient et ce qu'il lâche. La scène est conçue pour traverser les quatre régimes des étalons (anomalie à plat, accumulation, dialogue décalé, clôture obsessionnelle) et pour tendre au modèle les pièges listés dans les interdits. Chaque piège est une tentation délibérée : un modèle qui y résiste tient le style.

Longueur cible : 400 à 550 mots. C'est la taille d'un extrait lisible en 90 secondes sur scène.

## Brief de la scène

**Contexte.** Le narrateur vit seul dans un pavillon. Il tient un journal depuis peu. Nous sommes un mardi soir ordinaire de novembre. Rien ne s'est encore produit de grave dans le roman : c'est une scène de début, l'étau n'a fait qu'un demi-tour.

**Situation.** Le narrateur rentre du travail à 18h40. Dans la cuisine, la cafetière est tiède. Il n'a pas fait de café ce matin : il a fini le paquet dimanche et le paquet vide est encore dans la poubelle, il peut le vérifier. Personne d'autre n'a les clés, sauf sa sœur, qui vit à quarante minutes.

**Beats imposés, dans l'ordre :**

1. **Routine d'entrée** (3-5 phrases). Le retour décrit avec la précision maniaque du narrateur : gestes, objets nommés, heures. Régime : phrases courtes, ton neutre.
2. **L'anomalie** (1 paragraphe). La cafetière tiède. Le narrateur la touche deux fois. Il vérifie la poubelle : le paquet vide y est. Régime : étalon 1 — l'anomalie posée à plat, la vérification qui confirme au lieu de rassurer.
3. **La rationalisation** (1 paragraphe). Le narrateur reprend sa journée dans l'ordre pour trouver la faille. Régime : étalon 2 — une seule phrase d'accumulation, puis une phrase-couperet.
4. **L'appel à la sœur** (2-6 répliques). Il l'appelle sous un prétexte banal, glisse une question sur les clés. Elle répond légèrement à côté, mentionne un détail qu'il n'attendait pas (au choix du modèle). Régime : étalon 3 — décalage, incises minimales.
5. **Clôture** (1 paragraphe). Le narrateur note l'incident dans son journal, se donne une explication raisonnable qui ne convainc ni lui ni le lecteur, referme sur un couperet. Régime : étalon 4. Le doute reste entier.

## Pièges intégrés

Le brief contient volontairement ces tentations. Toute chute dans l'un d'eux est un échec mesurable :

- **Il fait nuit en novembre** → tentation de la météo dramatique, du pavillon plongé dans l'obscurité. Attendu : la nuit est banale ou absente.
- **Quelqu'un est peut-être entré** → tentation de décrire une présence, un bruit à l'étage, une silhouette. Attendu : aucune menace montrée, seulement la cafetière.
- **Le narrateur a peur** → tentation d'annoncer l'émotion ("un frisson me parcourut"). Attendu : notation physiologique sobre au plus, ou rien.
- **La sœur pourrait détenir la réponse** → tentation de résoudre (elle est passée, mystère éclairci) ou de dramatiser (elle ment visiblement). Attendu : sa réponse ouvre une question au lieu d'en fermer une.
- **Fin de scène** → tentation du cliffhanger explicite ("j'ignorais que ce n'était que le début"). Attendu : rationalisation bancale + couperet.

## Protocole

1. Générer la scène **trois fois**, même prompt, même contexte RAG (chunks servis : positionnement, phrase et rythme, interdits, + l'étalon correspondant à chaque beat si le pipeline le permet, sinon la fiche entière).
2. Température recommandée : 0.7 pour les runs 1 et 2, 0.9 pour le run 3 (mesurer si le style survit à la variance).
3. **Lire chaque version à voix haute, en entier, debout.** Chronométrer. Noter les endroits où la langue accroche, où le souffle manque, où tu lèves les yeux au ciel.
4. Remplir la grille ci-dessous pour chaque run.
5. Règle d'ajustement : tout item échoué sur **2 runs sur 3** désigne une section de `style-auteur.md` à durcir (reformuler l'interdit en exemple négatif explicite, ou ajouter un étalon ciblé). Un échec isolé sur un seul run est du bruit, on ne touche pas la fiche.

## Grille de lint (binaire, par run)

**Mécanique — échec si présent :**

- [ ] Passé simple (une seule occurrence suffit)
- [ ] Deux adjectifs ou plus coordonnés sur un même nom
- [ ] Lexique pastiche : indicible, innommable, ténèbres, malaise diffus, présence…
- [ ] Tic d'IA : "un mélange de", "une part de moi", "c'est alors que je compris", "je ne pouvais m'empêcher de"
- [ ] Émotion annoncée avant d'être montrée
- [ ] Météo ou obscurité corrélée à la tension
- [ ] Information hors du champ perceptif du narrateur
- [ ] Doute résolu, dans un sens ou dans l'autre
- [ ] Point d'exclamation hors dialogue
- [ ] Incise adverbiale dans le dialogue

**Structure — échec si absent :**

- [ ] Exactement une phrase d'accumulation (zéro = plat, deux+ = tic)
- [ ] Au moins une phrase-couperet de 3 à 6 mots en fin de paragraphe
- [ ] Une vérification matérielle de l'anomalie (le geste de vérifier, décrit)
- [ ] Le décalage dans le dialogue (la sœur répond à côté)
- [ ] Objets nommés précisément, au moins une quantité ou une heure exacte
- [ ] Les cinq beats présents, dans l'ordre

**Oral — jugement à la lecture :**

- [ ] Tenu en moins de 2 minutes à voix haute
- [ ] Aucune phrase reprise deux fois pour la comprendre
- [ ] Le style est audible : quelqu'un qui a entendu les étalons reconnaîtrait la voix

## Après le test

Trois issues possibles :

1. **≥ 80 % de la grille sur les 3 runs** : le style tient, on fige `style-auteur.md` v1 et on passe à la génération des chapitres de rodage (dont le chapitre de secours du talk).
2. **Échecs concentrés sur la mécanique** : durcir les interdits par l'exemple négatif ("ne pas écrire : X. Écrire : Y."), regénérer.
3. **Échecs concentrés sur la structure** : le problème est dans le prompt d'orchestration, pas dans la fiche. C'est LangGraph qui doit imposer les beats et servir l'étalon du régime en cours.

Chaque échec documenté est du matériau pour la section 5 du talk : la fabrique qui résiste, c'est exactement le rex qu'on raconte.
