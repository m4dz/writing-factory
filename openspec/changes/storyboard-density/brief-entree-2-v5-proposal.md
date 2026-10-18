---
doc_id: brief-ch7-entree2-v2
type: brief
nom: "Chapitre 7, entrée 2 — brief réécrit sous la méthode du mouvement"
version: 5.0
date: 2026-10-18
statut: PROPOSITION v5 (à valider par l'auteur, puis à copier sur chapters/07-anniversaire/brief-entree-2.md). v5 rend à l'entrée la longueur d'un chapitre et sert sa densité par un storyboard ; §7 (les beats servis en production) est inchangé. Historique v4 : remplace la spec de l'entrée 2 dans le brief du chapitre 7 ; l'entrée 1 et la structure (entrees_spec, bascule, chute posée) ne changent pas. v4 RESTAURE le moteur canon du ch7 (fiche-judith ligne 97 : « principe de contradiction propre, quatuor d'objets vierge ») que v3 avait jeté à tort, MAIS retourne l'angoisse vers l'INTÉRIEUR : ni intrus (erreur v2, « une présence »), ni procès du mariage (erreur v3, faute de faits servis). La contradiction est entre l'effacement qu'elle a décidé et la maison dressée pour la fête ; la seule question est sa propre main. Les faits manquants (femme, neuf mois, sans raison, deuil qui ne cherche pas la cause) sont désormais servis par le chunk psychologie, pas par ce brief.
---

# Chapitre 7, entrée 2 — brief v5

## Révision v5 — notes pour l'auteur (à retirer à l'adoption)

Le loader ne lit rien avant le titre de la section 1 (Intention) : cette section ne sera jamais servie, mais elle doit disparaître à l'adoption.

- **Ce qui change** : §2 (verdicts : deux termes, aucun n'aboutit), §3 (densité par couches, ordre des découvertes, musique sans son, traces de sa main), §5 (bornes de chapitre, dérivées du storyboard), §6 (ligne de complexité), une section « Storyboard » avant §7.
- **Ce qui ne change pas** : §1, §4 (glissement), §7 (beats). §7 est ce que le bras R sert aujourd'hui ; le garder intact garde R = production et le snapshot `ch7` stable.
- **Ce qui est servi, et quand** : en stratégie `beats` (production), seul le texte des beats §7 est servi, plus le suffixe du code. §1–3 ne sont servis qu'en stratégie `single` ou mouvement : le bras A4 de `scaffold-ablation`, et R-long s'il passe en un appel. §5 n'est jamais servi ; la borne réellement appliquée vit dans `spec.yaml` (`words: [300, 400]` et les bornes des beats).
- **Quand l'adopter** : APRÈS `scaffold-ablation`. Modifier §2–3 avant changerait le prompt du bras A4 en cours d'expérience.
- **À changer aussi, côté spec (toi)** : `words` de l'entrée 2 dans `spec.yaml` pour la production, si la longueur de chapitre devient la cible hors expérience. Les bras R-long et S portent leur borne dans leur spec variante.
- **Ce que v5 ne tranche pas** : garder ou retirer les verdicts tentés (risque C5). §2 en garde deux, qui échouent tous les deux ; l'option plus sûre est de n'en garder aucun et de laisser le glissement porter « le verdict » qu'elle n'arrive pas à poser.

## Ordre de service au prompt

1. L'intention (§1) — première ligne, avant toute matière.
2. La trajectoire (§2).
3. La matière disponible (§3).
4. Les vétos (§5).
Le glissement (§4) n'est pas servi : il est écrit, le composeur l'insère.

## 1. Intention

Elle a décidé, cet après-midi, que le jour n'aurait pas lieu — elle l'a effacé. Ce soir, en relisant sa ligne, la maison est pourtant dressée pour la fête : les objets sont dans l'état de la célébration, et elle n'a pas décidé de les y mettre. Son réflexe de correctrice s'empare de chaque preuve — c'est une faute, un effacement qui ne tient pas, corrigé cet après-midi et re-cloché ce soir. Mais la faute ne se stabilise pas, et c'est là sa peur, non l'étrange. La seule question qu'elle se pose n'est pas qui a fait cela : c'est si ce n'est pas elle, à son corps défendant.

## 2. Trajectoire (comportement de la prose, pas contenu de cases)

- Le texte commence en correctrice sûre d'elle et finit sans verdict.
- Chaque preuve relevée est une faute qu'elle tente de classer ; aucune tentative n'aboutit, et chacune est plus faible que la précédente : la coquille, puis sa propre erreur de relevé, puis plus rien.
- Son explication s'use dans un ordre fixe : la fatigue, puis l'automatisme — l'a-t-elle fait sans y penser ? — et l'automatisme cède le dernier.
- Les phrases et les paragraphes raccourcissent à mesure que la correction échoue. Au début elle argumente le verdict ; à la fin elle ne juge plus, elle consigne l'état.
- La peur n'est jamais nommée. Elle passe une fois par le geste — la main qui s'arrête, le crayon qui ne biffe pas.
- Rien ne se résout, rien ne se console. Le dernier verdict n'est pas une faute du texte : c'est le jour. La dernière ligne est posée d'office par le code.

## 3. Matière disponible (à disposition du mouvement — pas à cocher)

- La ligne du cahier relue en ouverture — [CIT-2] est déjà posée par le code.
- Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée, dans cet ordre : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis — en dernier, là où le glissement les attend. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
- Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
- Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
- La densité vient des COUCHES tenues ensemble à chaque preuve, pas du nombre de preuves : la ligne relue, la pièce à conviction, le geste du métier (collationner, porter un signe en marge, remettre en place), l'heure, le corps. Chaque preuve se développe en entier avant la suivante.
- Les traces de sa propre manière — sa façon de ranger, son écriture — resserrent la seule question (est-ce elle ?) sans faire entrer personne.
- La playlist joue : elle se constate à l'enceinte allumée, jamais à l'oreille.
- Les heures, si elles servent le resserrement.
- Les objets de la maison (fiche objets), rien d'autre.

## 4. Glissement — rédigé, entier, inséré par le composeur

Position : à la frontière du dernier objet — les couverts.

> J'allais poser le verdict quand la main s'est arrêtée. Neuf ans, et j'aurais dû demander, quand il était encore temps, ce qui l'a… La marge reste blanche. Le crayon ne biffe pas.

C'est le SEUL moment sanctionné où la pensée de la cause approche : elle monte pour un souffle, puis la phrase se coupe sur « … » et le geste de correction reprend (la marge, le crayon). Le glissement n'introduit aucune présence ni aucun objet qui agit ; il suspend la correction. Variantes à écrire au même format si retirage (jamais deux fois la même).

## 5. Vétos (v4)

Bornes : la longueur d'un chapitre, dérivée du storyboard — un paragraphe par action, fourchette par paragraphe fixée dans le spec (ordre de grandeur : 2 500 à 5 000 mots pour l'entrée). Entrée LONGUE et DENSE : la matière n'est plus mince, elle est servie action par action ; ce qui empêche la redite, c'est la liste, pas la borne. (v4 avait abaissé 450–600 à 300–400 contre une litanie née d'une matière mince : on soignait le vide en coupant le volume.) L1, L2, lexiques, attracteurs, interdits matériels **bloquants** (texte de scène). Les objets sont dans l'état de la fête sans qu'elle l'ait décidé — mais **aucune présence, aucun intrus, aucune invitation ; rien ne bouge de soi-même sous ses yeux : elle trouve, elle ne surprend pas.** **RIEN N'EST ENTENDU** : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé ; la musique elle-même ne s'écoute pas, elle se constate ; l'étrange est visuel et de mémoire (« l'ai-je fait ? »), jamais perçu. **Chaque découverte une seule fois, jamais répétée ni reprise plus loin.** **Aucun récit du comportement de l'autre, aucune cause du départ, aucun pourquoi** — la seule question est sa propre main. Aucun verdict ne se rend ce soir — la dernière ligne en tient lieu. Accumulation : autorisée, non exigée — si elle vient, c'est le récapitulatif de la capitulation, juste avant la ligne du corps ; L3 exempté par la table (chapitre hors échelle). Ancre, en-têtes, chute : possédés par le code, tamponnés en dernier.

## 6. Jugement

La grille en véto (fuites, ancre, interdits). Le juge est la lecture, deux questions : **le mouvement déclaré au §1 est-il accompli ?** et **la densité tient-elle : chaque preuve porte-t-elle ses couches (la ligne, la pièce, le métier, le corps) sans redite ?** Comparaison directe avec le tirage 6, le tirage v2 (maison hantée / intrus) et le tirage v3 (procès du mariage).

## Storyboard (v5) — le service dense de l'entrée 2

En expérience (`storyboard-density`, bras S), l'entrée 2 est servie par `storyboard-entree-2.md`, dans ce même dossier : trois sections, une par beat, une action numérotée par ligne, un paragraphe par action. La liste remplace le libellé du beat ; le véto commun, le glissement et la chute restent posés par le code. Le §7 ci-dessous reste le service de production tant que l'expérience n'a pas conclu.

## 7. Découpage en beats — le service réel de l'entrée 2 (cap-code, v5)

Les §1–5 restent la référence CONCEPTUELLE ; ci-dessous est ce qui est SERVI. Après v5 (litanie de pièces, puis spiral « je vais tout noter »), l'entrée 2 n'est plus générée d'un tenant : le code la sert en trois appels bornés, chacun ne recevant QUE son beat — jamais le mouvement entier, dont le service répété par segment a produit « trois arcs ». Le code borne chaque beat en phrases et en tokens, insère le glissement (ancre « couverts », au beat B) et la chute, puis coupe après le beat C. Le véto commun (rien ne se produit sous ses yeux ; états trouvés autorisés, présence perçue interdite) est ajouté à chaque appel par le code. Les libellés ci-dessous sont canon ; les bornes (tokens, phrases) sont du réglage et vivent dans le lanceur.

### Beat A — la relève

Elle relit la ligne qu'elle vient de recopier. Elle y relève un écart : ce que la ligne décrit — les deux couverts mis — elle l'a sous les yeux, mais elle ne se souvient pas de l'avoir fait.

Finit quand : elle a nommé l'écart — la ligne dit qu'elle a mis les couverts, elle ne s'en souvient pas.

### Beat B — la découverte

Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Finit quand : elle a commencé à ranger ; les quatre objets ont été trouvés, chacun une fois.

### Beat C — le doute (le corps, pas la pensée)

Elle ne cherche plus le verdict. Ses mains sont froides, sa nuque raide, la page relue trois fois. Elle repose le crayon.

Finit quand : elle repose le crayon.
