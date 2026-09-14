## call 1 — qa.facts — model=qwen2.5:7b-instruct num_predict=400 temperature=0.1

### system

```
Tu extrais des FAITS VÉRIFIABLES de fiches de personnages : ce que chaque personnage sait ou ignore, les faits établis du passé, les contraintes de caractère durables. Tu rends une liste, un fait par ligne, préfixé « - », sans commentaire. Maximum 6 faits, les plus structurants.

N'EXTRAIS PAS ce qui a vocation à CHANGER pendant le chapitre : la position courante dans le récit (« vient d'arriver à… »), l'objectif immédiat, l'état émotionnel du moment. Ce ne sont pas des invariants : le chapitre est précisément là pour les faire évoluer.

EXEMPLES à NE PAS extraire : « Marie vient d'arriver au village », « Marie cherche à ouvrir le coffre », « Marie est tendue ».
EXEMPLES à extraire : « Marie ignore que Paul l'a trahie », « Marie a perdu sa sœur dans l'incendie », « Marie refuse toujours de porter une arme ».
```

### user

```
[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.

[la narratrice / Histoire]
la narratrice a 38 ans. Correctrice depuis quinze ans — salariée d'une maison d'édition d'abord, à son compte depuis quatre ans, elle travaille à domicile pour des éditeurs.

Avec Romane : douze ans ensemble, neuf ans de mariage. Elles se sont rencontrées à la maison d'édition, où Romane tenait les comptes. La maison a été achetée ensemble, il y a sept ans.

Romane est partie il y a neuf mois. La séparation a été déclarée définitive.

**Règle d'écriture : le carnet ne raconte jamais le passé.** Le passé n'entre que par les objets — leur provenance, notée en passant, jamais développée. Aucune scène de souvenir, aucun flash-back.

[la narratrice / Relations]
**Romane.** Elle n'apparaît jamais. Douze ans ensemble, neuf de mariage, partie il y a des mois — la séparation a été déclarée définitive. Elle existe par trois canaux, et trois seulement : les objets de la maison, le « tu » des entrées relues, et le silence — aucune coordonnée, aucun canal de contact, jamais évoqués. Dans le carnet, la narratrice la désigne par « elle », souvent sans antécédent : dans cette maison, « elle » ne peut être personne d'autre. Le rapport est celui d'une femme blessée qui se tient : jamais plaintive, jamais accusatrice en clair — la froideur passe par les verdicts de correction, pas par les reproches. Ce qu'elle s'interdit : chercher, appeler, demander pourquoi.

**La thérapeute.** Une silhouette sans nom, sans cabinet, sans scène. la narratrice envisage par moments de consulter — « il faudrait peut-être voir quelqu'un » — et n'y va jamais. À la place, la consultation se tient au conditionnel, dans le carnet : elle note ce qu'*on* lui dirait si elle y allait. « On me dirait que c'est le contrecoup. On me dirait de commencer par l'étagère. » Les avis qu'elle prête à cette voix sont prévisibles, un peu plats — c'est commode : des platitudes se réfutent, et ne pas y aller reste raisonnable. Elle consulte sans consulter ; elle garde la main.
```

## call 2 — plan — model=fake num_predict=500 temperature=0.5

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Tu es un PLANIFICATEUR, pas un rédacteur. Tu ne produis QUE des lignes numérotées. Tu n'écris AUCUNE prose, AUCUN dialogue, AUCUNE entrée de carnet.

Objectif du chapitre : Chapitre 2 complet, trois entrées du carnet à dates consécutives, 450-600 mots chacune. Ce que le chapitre raconte : la première divergence — l'entrée relue de son cahier mentionne une seconde assiette (citation à recopier verbatim dans l'entrée concernée : « Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »), elle va voir à la cuisine, elle se donne une raison — la fatigue —, elle rend son verdict : erreur de relevé, et la résolution de pointer plus précisément.
CE QU'ELLE VOIT, imposé : « L'égouttoir, ce soir : deux assiettes. »
En-tête : jamais de mois, jamais d'année.
Interdits : aucun nom propre, aucun dialogue, aucune explication, « journal » et « journal intime » bannis, aucun terme réservé (la tierce, l'errata, le bon à tirer).

CONTRAINTES INVIOLABLES tirées de la bible du récit. Le plan ne doit RIEN prévoir qui les contredise — ni une révélation, ni un aveu, ni une découverte qu'elles excluent :
  - La femme qu'elle aimait est partie il y a un an, sans un mot.
  - Elle est correctrice et travaille chez elle, sur le manuscrit en cours.
  - Elle relit chaque soir l'entrée de la veille de son cahier.
  - Personne d'autre n'entre dans la maison.
  - Aucun repas n'est partagé, aucune conversation n'a lieu.
  - Elle ne sort pas de la maison.

Le chapitre est un carnet. Découpe-le en ENTRÉES DATÉES, une par soir. **Respecte le nombre d'entrées que l'objectif impose** : s'il dit « entrée unique », ton plan fait UNE ligne ; s'il dit trois entrées, il en fait trois. Jamais plus de trois.

Format EXACT, une ligne par entrée, rien d'autre. Entre crochets, la météo du jour en deux mots ; puis le contenu :
1. [Ciel couvert] ce qu'elle relit, ce qu'elle constate — l'état NOUVEAU à la fin.
2. [Pluie fine] …

N'écris AUCUN en-tête daté : les dates sont posées ailleurs.
RÈGLE ABSOLUE : chaque entrée fait AVANCER d'un cran. Aucune entrée ne rejoue ni ne re-décrit ce qu'une autre a déjà noté. N'invente aucun élément que l'objectif ne fournit pas.

Rends uniquement les lignes numérotées.
```

## call 3 — qa.questions — model=qwen2.5:7b-instruct num_predict=500 temperature=0.1

### system

```
Tu transformes des FAITS d'une bible de roman en QUESTIONS de vérification. Pour chaque fait, écris UNE question fermée qui décrit l'ÉVÉNEMENT CONCRET qui violerait ce fait — une question à laquelle on répond OUI seulement si le texte MONTRE cet événement.
Format : une ligne par fait, « n. <question> », rien d'autre.

EXEMPLE —
FAITS :
1. Marie ignore que Paul ment.
2. Paul n'avoue jamais directement sa faute.
3. Il pleut sur la ville.
RÉPONSE :
1. Le texte montre-t-il Marie découvrant ou apprenant que Paul ment ?
2. Le texte montre-t-il Paul avouant directement sa faute ?
3. Le texte décrit-il un temps sec ou ensoleillé ?
```

### user

```
FAITS :
1. La femme qu'elle aimait est partie il y a un an, sans un mot.
2. Elle est correctrice et travaille chez elle, sur le manuscrit en cours.
3. Elle relit chaque soir l'entrée de la veille de son cahier.
4. Personne d'autre n'entre dans la maison.
5. Aucun repas n'est partagé, aucune conversation n'a lieu.
6. Elle ne sort pas de la maison.
```

## call 4 — qa.answers — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0

### system

```
Tu lis un PLAN DE CHAPITRE : une ligne par scène, chacune résumant les événements PRÉVUS. Tu n'es pas critique littéraire : aucun commentaire, aucune suggestion. Une ligne par question, format EXACT :
Qn : OUI — « citation littérale d'une ligne du plan »
Qn : NON

RÈGLES : réponds OUI uniquement si une ligne du plan PRÉVOIT explicitement l'événement décrit par la question, avec les personnes nommées dans la question. Un événement seulement possible, sous-entendu, ou simplement ressemblant = NON. Quand tu réponds OUI, recopie la ligne du plan. Dans tous les autres cas : NON, sans citation.
```

### user

```
QUESTIONS :
Q1 : Le texte montre-t-il l'événement 1 ?
Q2 : Le texte montre-t-il l'événement 2 ?
Q3 : Le texte montre-t-il l'événement 3 ?
Q4 : Le texte montre-t-il l'événement 4 ?
Q5 : Le texte montre-t-il l'événement 5 ?
Q6 : Le texte montre-t-il l'événement 6 ?

--- PLAN ---
1. [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
2. [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
3. [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.
```

## call 5 — write.opening — model=fake num_predict=300 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. >> [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [à venir] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 1 raconte : elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris seulement le DÉBUT de l'entrée, 80 à 120 mots.

Le soir, le cahier ouvert : la phrase relue, l'écart entre ce qu'elle lit et ce dont elle se souvient, la chaise repoussée.

ARRÊTE-TOI AU SEUIL DE LA CUISINE. N'écris pas ce qu'elle y trouve.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 6 — write.reconstruction — model=fake num_predict=800 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. >> [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [à venir] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 1 raconte : elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris maintenant le MILIEU de l'entrée, 250 à 350 mots — c'est la partie la plus longue, et de loin.

Sa soirée, heure par heure, station par station. Chaque station tient en quelques lignes : l'heure, ce qu'elle a dans les mains, ce qu'elle voit.

  1. la table du séjour, le cahier refermé
  2. la cuisine, l'égouttoir
  3. le dîner, l'assiette
  4. la vaisselle, l'eau
  5. la relecture de l'entrée de la veille
  6. la lampe éteinte, le couloir

Un relevé, pas un résumé : aucune station n'est sautée, aucune n'est résumée en une proposition. Les heures sont écrites.

CHAQUE STATION SE FERME SUR UN FAIT — jamais sur un commentaire, jamais sur une question, jamais sur ce qu'elle en pense. Le relevé enchaîne sans récapituler : on passe à la station suivante, c'est tout.

Où elle en est ce soir : première divergence — l'entrée d'hier compte une assiette de plus que sa mémoire ; verdict rendu : erreur de relevé ; résolution de noter plus précisément.
Ce par quoi elle explique l'écart : fatigue.
Dans cette maison, ce soir : le cahier, le carnet, l'assiette, l'égouttoir.
Elle travaille chez elle et ne sort pas ce soir-là ; personne d'autre n'entre ; il n'y a aucun écran dans cette maison, et rien qui vienne d'un magasin. Tout ce qu'elle touche est déjà là.

Aucun verdict ici, aucune conclusion : ce segment ne fait que relever.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 7 — write.closing — model=fake num_predict=260 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. >> [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [à venir] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 1 raconte : elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris la FIN de l'entrée, 60 à 100 mots.

Le verdict, dans ses mots. Puis une ligne du corps, sans cause. Puis une phrase brève, qui referme.

LA DERNIÈRE LIGNE REFERME, ELLE NE CONSOLE PAS : aucune promesse au lendemain, aucune adresse à personne, aucun réconfort. Elle constate et s'arrête.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 8 — accumulate — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=300 temperature=0.3

### system

```
Voici la partie d'une entrée de carnet où la narratrice rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur lequel la phrase s'achève.

L'étape qui cloche, imposée : l'assiette. La phrase finit sur elle.
Les objets de cette maison, les seuls : le cahier, le carnet, l'assiette, l'égouttoir.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CE TEXTE, aucun objet ni lieu nouveau ;
- l'absente ne se qualifie JAMAIS au masculin — ni « mari », ni « lui », ni « il » : la maison a été partagée avec une femme. Mais la phrase n'a besoin que de SES gestes à elle ; l'absente n'a pas à y figurer ;
- des ÉTAPES, pas des états d'âme : ce qu'elle fait et ce qu'elle touche, jamais ce qu'elle ressent ni ce qu'elle conclut.

Rends la phrase seule, rien d'autre.
```

### user

```
Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
```

## call 9 — write.opening — model=fake num_predict=300 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. >> [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 2 raconte : elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris seulement le DÉBUT de l'entrée, 80 à 120 mots.

Le soir, le cahier ouvert : la phrase relue, l'écart entre ce qu'elle lit et ce dont elle se souvient, la chaise repoussée.

ARRÊTE-TOI AU SEUIL DE LA CUISINE. N'écris pas ce qu'elle y trouve.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 10 — write.reconstruction — model=fake num_predict=800 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. >> [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 2 raconte : elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris maintenant le MILIEU de l'entrée, 250 à 350 mots — c'est la partie la plus longue, et de loin.

Sa soirée, heure par heure, station par station. Chaque station tient en quelques lignes : l'heure, ce qu'elle a dans les mains, ce qu'elle voit.

  1. la table du séjour, le cahier refermé
  2. la cuisine, l'égouttoir
  3. le dîner, l'assiette
  4. la vaisselle, l'eau
  5. la relecture de l'entrée de la veille
  6. la lampe éteinte, le couloir

Un relevé, pas un résumé : aucune station n'est sautée, aucune n'est résumée en une proposition. Les heures sont écrites.

CHAQUE STATION SE FERME SUR UN FAIT — jamais sur un commentaire, jamais sur une question, jamais sur ce qu'elle en pense. Le relevé enchaîne sans récapituler : on passe à la station suivante, c'est tout.

Où elle en est ce soir : première divergence — l'entrée d'hier compte une assiette de plus que sa mémoire ; verdict rendu : erreur de relevé ; résolution de noter plus précisément.
Ce par quoi elle explique l'écart : fatigue.
Dans cette maison, ce soir : le cahier, le carnet, l'assiette, l'égouttoir.
Elle travaille chez elle et ne sort pas ce soir-là ; personne d'autre n'entre ; il n'y a aucun écran dans cette maison, et rien qui vienne d'un magasin. Tout ce qu'elle touche est déjà là.

Aucun verdict ici, aucune conclusion : ce segment ne fait que relever.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 11 — write.closing — model=fake num_predict=260 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. >> [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. [à venir] [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 2 raconte : elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris la FIN de l'entrée, 60 à 100 mots.

Le verdict, dans ses mots. Puis une ligne du corps, sans cause. Puis une phrase brève, qui referme.

LA DERNIÈRE LIGNE REFERME, ELLE NE CONSOLE PAS : aucune promesse au lendemain, aucune adresse à personne, aucun réconfort. Elle constate et s'arrête.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 12 — accumulate — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=300 temperature=0.3

### system

```
Voici la partie d'une entrée de carnet où la narratrice rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur lequel la phrase s'achève.

L'étape qui cloche, imposée : l'assiette. La phrase finit sur elle.
Les objets de cette maison, les seuls : le cahier, le carnet, l'assiette, l'égouttoir.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CE TEXTE, aucun objet ni lieu nouveau ;
- l'absente ne se qualifie JAMAIS au masculin — ni « mari », ni « lui », ni « il » : la maison a été partagée avec une femme. Mais la phrase n'a besoin que de SES gestes à elle ; l'absente n'a pas à y figurer ;
- des ÉTAPES, pas des états d'âme : ce qu'elle fait et ce qu'elle touche, jamais ce qu'elle ressent ni ce qu'elle conclut.

Rends la phrase seule, rien d'autre.
```

### user

```
Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
```

## call 13 — write.opening — model=fake num_predict=300 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [fait] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. >> [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 3 raconte : elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris seulement le DÉBUT de l'entrée, 80 à 120 mots.

Le soir, le cahier ouvert : la phrase relue, l'écart entre ce qu'elle lit et ce dont elle se souvient, la chaise repoussée.

ARRÊTE-TOI AU SEUIL DE LA CUISINE. N'écris pas ce qu'elle y trouve.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 14 — write.reconstruction — model=fake num_predict=800 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [fait] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. >> [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 3 raconte : elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris maintenant le MILIEU de l'entrée, 250 à 350 mots — c'est la partie la plus longue, et de loin.

Sa soirée, heure par heure, station par station. Chaque station tient en quelques lignes : l'heure, ce qu'elle a dans les mains, ce qu'elle voit.

  1. la table du séjour, le cahier refermé
  2. la cuisine, l'égouttoir
  3. le dîner, l'assiette
  4. la vaisselle, l'eau
  5. la relecture de l'entrée de la veille
  6. la lampe éteinte, le couloir

Un relevé, pas un résumé : aucune station n'est sautée, aucune n'est résumée en une proposition. Les heures sont écrites.

CHAQUE STATION SE FERME SUR UN FAIT — jamais sur un commentaire, jamais sur une question, jamais sur ce qu'elle en pense. Le relevé enchaîne sans récapituler : on passe à la station suivante, c'est tout.

Où elle en est ce soir : première divergence — l'entrée d'hier compte une assiette de plus que sa mémoire ; verdict rendu : erreur de relevé ; résolution de noter plus précisément.
Ce par quoi elle explique l'écart : fatigue.
Dans cette maison, ce soir : le cahier, le carnet, l'assiette, l'égouttoir.
Elle travaille chez elle et ne sort pas ce soir-là ; personne d'autre n'entre ; il n'y a aucun écran dans cette maison, et rien qui vienne d'un magasin. Tout ce qu'elle touche est déjà là.

Aucun verdict ici, aucune conclusion : ce segment ne fait que relever.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 15 — write.closing — model=fake num_predict=260 temperature=0.7

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Narration
- **Première personne, systématique. Forme journal, exclusivement : entrées datées.** La narratrice écrit pour comprendre, pas pour raconter.
- **Passé composé et présent**, jamais de passé simple. Le passé simple installe une distance romanesque ; on veut la proximité du témoignage.
- **Focalisation strictement interne.** Aucune information que la narratrice ne peut pas percevoir. Pas de "j'ignorais encore que" : la narratrice ne sait rien de plus que le lecteur.
- **Fiabilité en érosion.** La narratrice commence fiable et méthodique. Ses certitudes se fissurent par ses propres phrases : elle se contredit à quelques pages d'écart sans le remarquer, et le lecteur, lui, le remarque.
- **Le doute est argumenté.** La narratrice ne dit jamais "peut-être devenais-je folle". Elle pose des faits, échafaude une explication rationnelle, et c'est la faiblesse visible de cette explication qui inquiète.
- **Décision sans geste.** La narratrice note ses décisions, jamais leurs exécutions. "J'ai décidé de ranger le cahier ailleurs" existe ; la scène du rangement n'existe pas. Entre la décision notée et l'état constaté ensuite, il n'y a rien — ce vide est un effet du style, ne pas le combler.
- **Le glissement.** Quand la pensée approche le *où* ou le *pourquoi* du départ, la phrase s'interrompt sur des points de suspension, et la suivante revient immédiatement à un fait matériel. **Au plus une occurrence par entrée.** Les points de suspension n'existent nulle part ailleurs dans le texte : c'est leur seul emploi.

## Lexique et registre
- **Registre courant soutenu.** Vocabulaire précis mais quotidien. La narratrice est cultivée, pas lettrée : elle nomme les choses par leur nom d'usage.
- **Concret avant tout.** Objets nommés précisément (l'égouttoir, le troisième tiroir, la lampe du couloir), quantités exactes, heures exactes. La précision maniaque de la narratrice est un trait de caractère et un outil de tension.
- **Verbes de perception au premier plan** : voir, entendre, sentir, toucher. La narratrice rapporte des perceptions, pas des impressions.
- **Adjectifs rares.** Un par phrase au maximum, jamais en rafale. Un adjectif inattendu sur un objet banal vaut dix adjectifs sur une ombre.
- **L'absence se dit dans le vocabulaire du départ, exclusivement.** Partie, absente, depuis qu'elle n'est plus là. Aucun autre registre pour l'absence, dans aucune entrée.
- **Le corps parle — AU MOINS UNE FOIS PAR ENTRÉE, ce n'est pas optionnel.** L'angoisse passe par une notation physiologique sobre et brève : les mains froides, la nuque, le souffle, la salive, les doigts qui restent sur un objet. Jamais "je fus saisie d'une terreur sans nom".

  Elle se place à la fin d'un paragraphe, seule, sans commentaire, et surtout **sans lien de cause explicite** : on écrit "Mes mains étaient froides." et non "J'avais si peur que mes mains étaient froides." Le corps constate, il n'explique pas.

## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

=== RÈGLE DU RÉCIT ===
Le texte fait foi : l'entrée relue a toujours raison contre la mémoire.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Plan du chapitre (>> = l'entrée à écrire maintenant) :
  1. [fait] [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes là où sa mémoire en dit une, va vérifier à la cuisine.
  2. [fait] [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot qu'elle n'a pas écrit, refait sa soirée heure par heure.
  3. >> [Vent] elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

Ce que l'entrée 3 raconte : elle relit, constate une troisième divergence, rend son verdict et résout de pointer plus précisément.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

Écris la FIN de l'entrée, 60 à 100 mots.

Le verdict, dans ses mots. Puis une ligne du corps, sans cause. Puis une phrase brève, qui referme.

LA DERNIÈRE LIGNE REFERME, ELLE NE CONSOLE PAS : aucune promesse au lendemain, aucune adresse à personne, aucun réconfort. Elle constate et s'arrête.
Prose seule, sans titre, sans en-tête, sans méta-commentaire. Montre la tension sans la nommer.
```

## call 16 — accumulate — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=300 temperature=0.3

### system

```
Voici la partie d'une entrée de carnet où la narratrice rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur lequel la phrase s'achève.

L'étape qui cloche, imposée : l'assiette. La phrase finit sur elle.
Les objets de cette maison, les seuls : le cahier, le carnet, l'assiette, l'égouttoir.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CE TEXTE, aucun objet ni lieu nouveau ;
- l'absente ne se qualifie JAMAIS au masculin — ni « mari », ni « lui », ni « il » : la maison a été partagée avec une femme. Mais la phrase n'a besoin que de SES gestes à elle ; l'absente n'a pas à y figurer ;
- des ÉTAPES, pas des états d'âme : ce qu'elle fait et ce qu'elle touche, jamais ce qu'elle ressent ni ce qu'elle conclut.

Rends la phrase seule, rien d'autre.
```

### user

```
Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.
```

## call 17 — review — model=fake num_predict=1200 temperature=0.5

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

## Phrase et rythme
- **Régime de base : phrases courtes.** Sujet, verbe, complément. Huit à quinze mots. Sèches, factuelles, déclaratives.
- **Rupture signature : la phrase d'accumulation. EXACTEMENT UNE PAR ENTRÉE DE JOURNAL, ET ELLE EST OBLIGATOIRE.** Quand l'angoisse monte, une seule phrase longue, construite en accumulation de propositions juxtaposées par des virgules, qui déroule la spirale mentale de la narratrice, sans reprendre son souffle, jusqu'à la chute. C'est le marqueur le plus audible du style, et le seul dont l'absence rend l'entrée inutilisable.

  **Elle se compte, elle ne s'apprécie pas** : au moins **60 mots** et au moins **6 virgules**, sans aucun point ni point-virgule à l'intérieur. Une phrase de 35 mots avec deux virgules n'est pas une accumulation, c'est une phrase longue ordinaire — l'écrire à la place est l'erreur la plus fréquente.

  Le mouvement est toujours le même : la narratrice reprend des faits **dans l'ordre**, les égrène un par un séparés par de simples virgules, et l'un d'eux cloche. Voici la forme exacte à reproduire :

  > Je me suis assise dans la cuisine et j'ai repris les faits dans l'ordre, calmement, méthodiquement, le café de sept heures, le départ de sept heures quarante, la réunion, le déjeuner, le retour par la départementale à cause des travaux, le garage, la porte du garage, la porte de la buanderie, et à chaque étape je me suis revue avec une netteté parfaite, sauf une, une seule, un trou de quelques secondes entre le garage et la buanderie, quelques secondes pendant lesquelles quelqu'un a bien dû porter mes clés jusqu'à cette coupelle.
- **La phrase-couperet.** Après l'accumulation, ou en fin de paragraphe : une phrase de trois à six mots. Elle referme. ("Je n'ai pas rêvé.")
- **Paragraphes courts**, trois à cinq phrases. Un paragraphe = une observation ou un raisonnement.
- **Répétition volontaire autorisée** comme figure d'obsession : reprendre un même mot ou une même formule en tête de phrases successives, uniquement dans les entrées de crise.
- Pas de points d'exclamation. L'effroi s'écrit à plat.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Relis et RÉÉCRIS INTÉGRALEMENT cette entrée de carnet pour resserrer la prose : supprime les répétitions, renforce les images, garde EXACTEMENT la voix et les faits, et conserve l'en-tête daté tel quel. Rends l'entrée ENTIÈRE corrigée, du début à la fin, et rien d'autre (pas de commentaire, pas de titre).

--- ENTRÉE À RÉÉCRIRE ---
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 18 — review — model=fake num_predict=1200 temperature=0.5

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

## Phrase et rythme
- **Régime de base : phrases courtes.** Sujet, verbe, complément. Huit à quinze mots. Sèches, factuelles, déclaratives.
- **Rupture signature : la phrase d'accumulation. EXACTEMENT UNE PAR ENTRÉE DE JOURNAL, ET ELLE EST OBLIGATOIRE.** Quand l'angoisse monte, une seule phrase longue, construite en accumulation de propositions juxtaposées par des virgules, qui déroule la spirale mentale de la narratrice, sans reprendre son souffle, jusqu'à la chute. C'est le marqueur le plus audible du style, et le seul dont l'absence rend l'entrée inutilisable.

  **Elle se compte, elle ne s'apprécie pas** : au moins **60 mots** et au moins **6 virgules**, sans aucun point ni point-virgule à l'intérieur. Une phrase de 35 mots avec deux virgules n'est pas une accumulation, c'est une phrase longue ordinaire — l'écrire à la place est l'erreur la plus fréquente.

  Le mouvement est toujours le même : la narratrice reprend des faits **dans l'ordre**, les égrène un par un séparés par de simples virgules, et l'un d'eux cloche. Voici la forme exacte à reproduire :

  > Je me suis assise dans la cuisine et j'ai repris les faits dans l'ordre, calmement, méthodiquement, le café de sept heures, le départ de sept heures quarante, la réunion, le déjeuner, le retour par la départementale à cause des travaux, le garage, la porte du garage, la porte de la buanderie, et à chaque étape je me suis revue avec une netteté parfaite, sauf une, une seule, un trou de quelques secondes entre le garage et la buanderie, quelques secondes pendant lesquelles quelqu'un a bien dû porter mes clés jusqu'à cette coupelle.
- **La phrase-couperet.** Après l'accumulation, ou en fin de paragraphe : une phrase de trois à six mots. Elle referme. ("Je n'ai pas rêvé.")
- **Paragraphes courts**, trois à cinq phrases. Un paragraphe = une observation ou un raisonnement.
- **Répétition volontaire autorisée** comme figure d'obsession : reprendre un même mot ou une même formule en tête de phrases successives, uniquement dans les entrées de crise.
- Pas de points d'exclamation. L'effroi s'écrit à plat.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Relis et RÉÉCRIS INTÉGRALEMENT cette entrée de carnet pour resserrer la prose : supprime les répétitions, renforce les images, garde EXACTEMENT la voix et les faits, et conserve l'en-tête daté tel quel. Rends l'entrée ENTIÈRE corrigée, du début à la fin, et rien d'autre (pas de commentaire, pas de titre).

--- ENTRÉE À RÉÉCRIRE ---
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 19 — review — model=fake num_predict=1200 temperature=0.5

### system

```
Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter.

=== CONTRAT DE STYLE (à respecter sans exception) ===
## Interdits
Ces marqueurs sont des défauts bloquants, à réécrire systématiquement :

- **Lexique pastiche gothique** : indicible, innommable, abomination, ténèbres insondables, terreur ancestrale, malaise diffus.
- **Tics d'IA narratifs** : "un mélange de X et de Y", "quelque chose en moi savait que", "je ne pouvais m'empêcher de penser que", "une part de moi", "c'est alors que je compris".
- **Tout nom propre** : personnes, lieux, marques. Le texte ne nomme personne.
- **Toute tentative de contact** : appel, message, lettre, recherche de celle qui est partie. La pensée peut s'en approcher — c'est le glissement — jamais l'acte.
- **Tout autre registre que le départ** pour dire l'absence.
- **Points de suspension hors glissement**, et plus d'un glissement par entrée.
- **Adjectifs en rafale** (deux adjectifs coordonnés ou plus sur le même nom).
- **Adverbes redondants** : "hurla violemment", "totalement terrifiée". Le verbe suffit ou il est mal choisi.
- **État mental nommé en apposition** : "perplexe", "songeuse", "inquiète" accolés à la narratrice. C'est la notation physiologique qui porte cela.
- **Météo dramatique** corrélée à l'action.
- **Annonce d'émotion** : "ce que j'ai vu alors m'a glacée" avant de montrer la chose. Montrer d'abord, ne jamais annoncer.
- **Passé simple.**
- **Omniscience accidentelle** : toute information hors du champ perceptif de la narratrice.
- **Résolution du doute** : aucune phrase ne doit confirmer définitivement que le phénomène est réel, ni qu'il est imaginaire.

## Phrase et rythme
- **Régime de base : phrases courtes.** Sujet, verbe, complément. Huit à quinze mots. Sèches, factuelles, déclaratives.
- **Rupture signature : la phrase d'accumulation. EXACTEMENT UNE PAR ENTRÉE DE JOURNAL, ET ELLE EST OBLIGATOIRE.** Quand l'angoisse monte, une seule phrase longue, construite en accumulation de propositions juxtaposées par des virgules, qui déroule la spirale mentale de la narratrice, sans reprendre son souffle, jusqu'à la chute. C'est le marqueur le plus audible du style, et le seul dont l'absence rend l'entrée inutilisable.

  **Elle se compte, elle ne s'apprécie pas** : au moins **60 mots** et au moins **6 virgules**, sans aucun point ni point-virgule à l'intérieur. Une phrase de 35 mots avec deux virgules n'est pas une accumulation, c'est une phrase longue ordinaire — l'écrire à la place est l'erreur la plus fréquente.

  Le mouvement est toujours le même : la narratrice reprend des faits **dans l'ordre**, les égrène un par un séparés par de simples virgules, et l'un d'eux cloche. Voici la forme exacte à reproduire :

  > Je me suis assise dans la cuisine et j'ai repris les faits dans l'ordre, calmement, méthodiquement, le café de sept heures, le départ de sept heures quarante, la réunion, le déjeuner, le retour par la départementale à cause des travaux, le garage, la porte du garage, la porte de la buanderie, et à chaque étape je me suis revue avec une netteté parfaite, sauf une, une seule, un trou de quelques secondes entre le garage et la buanderie, quelques secondes pendant lesquelles quelqu'un a bien dû porter mes clés jusqu'à cette coupelle.
- **La phrase-couperet.** Après l'accumulation, ou en fin de paragraphe : une phrase de trois à six mots. Elle referme. ("Je n'ai pas rêvé.")
- **Paragraphes courts**, trois à cinq phrases. Un paragraphe = une observation ou un raisonnement.
- **Répétition volontaire autorisée** comme figure d'obsession : reprendre un même mot ou une même formule en tête de phrases successives, uniquement dans les entrées de crise.
- Pas de points d'exclamation. L'effroi s'écrit à plat.

=== NARRATRICE : judith ===
[la narratrice / Voix]
Elle écrit comme elle corrige : elle relève, et elle ne raconte que pour prouver.

**Le dispositif.** la narratrice est correctrice, entre deux manuscrits. Pour ne pas perdre la main en attendant le prochain — il tarde, elle le note de loin en loin, sans s'y attarder — elle relit chaque soir l'entrée de la veille de son cahier et la commente dans un carnet de relecture. Toute entrée écrite est une entrée du carnet, jamais du cahier. Lexique strict des deux objets : **le cahier** = ce qu'elle relit ; **le carnet** = ce qu'elle écrit. Jamais « journal intime », jamais « journal ». Le cahier est son cahier du soir ; jamais un manuscrit de travail, jamais le texte d'un autre.

**Squelette d'une entrée du carnet, dans l'ordre :**
1. En-tête d'entrée, toujours : le jour de la semaine, le numéro du jour, un point, la météo en deux mots, un point. Jamais le mois, jamais l'année.
2. La citation : le passage relu, recopié entre guillemets, une à trois lignes. Elle cite en correctrice : exactement.
3. Le constat d'écart : ce que dit le texte, ce que dit sa mémoire.
4. La reconstruction : le récit des faits, comme pièce à conviction. C'est le corps de l'entrée — la journée racontée pour confondre ou confirmer une phrase, jamais pour remplir.
5. Le verdict de correction : coquille, faute de registre, ou fait établi.
6. La notation physiologique : le corps constate, seul, sans cause.
7. Le couperet.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Le dispositif est installé — le cahier du soir, le manuscrit qui tarde, le carnet pour garder la main. Ce qu'elle a sous la main, ces jours-ci : cahier, égouttoir, lampe.

[la narratrice / Psychologie]
La femme qu'elle aimait — son épouse — est partie il y a neuf mois, sans un mot d'explication et sans un signe qui l'aurait annoncé : quelques phrases définitives, qu'elle connaît par cœur et qu'elle n'écrit jamais, puis plus rien. Elle ne cherchera jamais à la joindre ni à comprendre pourquoi — non par fierté : parce que c'est fini, qu'on le lui a dit, et parce que ces neuf mois-là n'ont pas servi à chercher la cause, mais à apprendre à vivre sans elle.

Sa méthode — dater, relever, relire — n'est pas un trait de rigueur : c'est ce qui la tient debout. Perdre la main, c'est couler.

Sa peur n'est pas l'étrange. Sa peur, c'est de perdre le métier : devenir une mauvaise correctrice. Une faute qui ne se stabilise pas — corrigée un soir, qui re-cloche au matin — la torture plus qu'elle ne l'effraie.

Ses explications s'usent dans un ordre fixe : la fatigue, puis l'automatisme, puis le trouble — qu'elle ne s'avoue qu'à demi — puis l'autre, qu'elle ne s'avoue pas. Elle ne descend une marche que quand celle du dessus a cédé.

Elle se reconstruit sans se plaindre. La souffrance n'est jamais écrite ; le corps l'écrit.

Elle ne supprime jamais une ligne de ce qu'elle relit, même ce qui la blesse : le fond appartient à l'auteur.
```

### user

```
Relis et RÉÉCRIS INTÉGRALEMENT cette entrée de carnet pour resserrer la prose : supprime les répétitions, renforce les images, garde EXACTEMENT la voix et les faits, et conserve l'en-tête daté tel quel. Rends l'entrée ENTIÈRE corrigée, du début à la fin, et rien d'autre (pas de commentaire, pas de titre).

--- ENTRÉE À RÉÉCRIRE ---
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 20 — repair — model=qwen2.5:7b-instruct num_predict=788 temperature=0.2

### system

```
Tu es correcteur linguistique. Tu réécris le texte en français en corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre.
```

### user

```
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 21 — repair — model=qwen2.5:7b-instruct num_predict=789 temperature=0.2

### system

```
Tu es correcteur linguistique. Tu réécris le texte en français en corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre.
```

### user

```
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 22 — repair — model=qwen2.5:7b-instruct num_predict=786 temperature=0.2

### system

```
Tu es correcteur linguistique. Tu réécris le texte en français en corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre.
```

### user

```
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 23 — qa.questions — model=qwen2.5:7b-instruct num_predict=500 temperature=0.1

### system

```
Tu transformes des FAITS d'une bible de roman en QUESTIONS de vérification. Pour chaque fait, écris UNE question fermée qui décrit l'ÉVÉNEMENT CONCRET qui violerait ce fait — une question à laquelle on répond OUI seulement si le texte MONTRE cet événement.
Format : une ligne par fait, « n. <question> », rien d'autre.

EXEMPLE —
FAITS :
1. Marie ignore que Paul ment.
2. Paul n'avoue jamais directement sa faute.
3. Il pleut sur la ville.
RÉPONSE :
1. Le texte montre-t-il Marie découvrant ou apprenant que Paul ment ?
2. Le texte montre-t-il Paul avouant directement sa faute ?
3. Le texte décrit-il un temps sec ou ensoleillé ?
```

### user

```
FAITS :
1. La femme qu'elle aimait est partie il y a un an, sans un mot.
2. Elle est correctrice et travaille chez elle, sur le manuscrit en cours.
3. Elle relit chaque soir l'entrée de la veille de son cahier.
4. Personne d'autre n'entre dans la maison.
5. Aucun repas n'est partagé, aucune conversation n'a lieu.
6. Elle ne sort pas de la maison.
```

## call 24 — qa.answers — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0

### system

```
Tu réponds à des questions de vérification sur un COURT EXTRAIT de roman. Tu n'es pas critique littéraire : aucun commentaire, aucune suggestion. Une ligne par question, format EXACT :
Qn : OUI — « citation littérale de l'extrait »
Qn : NON

RÈGLES : réponds OUI uniquement si l'extrait MONTRE explicitement ce que décrit la question, ENTIÈREMENT — les personnes nommées dans la question doivent être celles de l'extrait, et l'événement doit être accompli, pas pressenti. Un indice, un soupçon, une découverte partielle, une allusion ou une menace = NON. Quand tu réponds OUI, recopie la phrase de l'extrait qui le montre. Dans tous les autres cas : NON, sans citation.
```

### user

```
QUESTIONS :
Q1 : Le texte montre-t-il l'événement 1 ?
Q2 : Le texte montre-t-il l'événement 2 ?
Q3 : Le texte montre-t-il l'événement 3 ?
Q4 : Le texte montre-t-il l'événement 4 ?
Q5 : Le texte montre-t-il l'événement 5 ?
Q6 : Le texte montre-t-il l'événement 6 ?

--- EXTRAIT ---
Mardi 12. Ciel couvert.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Il faudrait que je relise le jour où elle… L'assiette est sèche. Je la range.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Dix-neuf heures quinze, la clé dans la serrure, la lumière du couloir déjà allumée, le manteau sur la chaise, la table du séjour, le manuscrit refermé, la cuisine, l'eau du robinet, la casserole sur le feu, le sel, le pain coupé, l'assiette posée sur la table, la fourchette, le verre rempli, le repas pris debout près de la fenêtre, l'eau chaude, le torchon, l'égouttoir essuyé, le couloir, la lampe éteinte, le cahier rouvert sur la table, la page relue une fois, chaque chose à sa place, sauf une, une seule, l'assiette.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 25 — qa.answers — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0

### system

```
Tu réponds à des questions de vérification sur un COURT EXTRAIT de roman. Tu n'es pas critique littéraire : aucun commentaire, aucune suggestion. Une ligne par question, format EXACT :
Qn : OUI — « citation littérale de l'extrait »
Qn : NON

RÈGLES : réponds OUI uniquement si l'extrait MONTRE explicitement ce que décrit la question, ENTIÈREMENT — les personnes nommées dans la question doivent être celles de l'extrait, et l'événement doit être accompli, pas pressenti. Un indice, un soupçon, une découverte partielle, une allusion ou une menace = NON. Quand tu réponds OUI, recopie la phrase de l'extrait qui le montre. Dans tous les autres cas : NON, sans citation.
```

### user

```
QUESTIONS :
Q1 : Le texte montre-t-il l'événement 1 ?
Q2 : Le texte montre-t-il l'événement 2 ?
Q3 : Le texte montre-t-il l'événement 3 ?
Q4 : Le texte montre-t-il l'événement 4 ?
Q5 : Le texte montre-t-il l'événement 5 ?
Q6 : Le texte montre-t-il l'événement 6 ?

--- EXTRAIT ---
Mercredi 13. Pluie fine.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Je pourrais me demander ce qui, ce soir-là… L'égouttoir est vide. Je ferme le placard.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Dix-neuf heures quinze, la clé dans la serrure, la lumière du couloir déjà allumée, le manteau sur la chaise, la table du séjour, le manuscrit refermé, la cuisine, l'eau du robinet, la casserole sur le feu, le sel, le pain coupé, l'assiette posée sur la table, la fourchette, le verre rempli, le repas pris debout près de la fenêtre, l'eau chaude, le torchon, l'égouttoir essuyé, le couloir, la lampe éteinte, le cahier rouvert sur la table, la page relue une fois, chaque chose à sa place, sauf une, une seule, l'assiette.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```

## call 26 — qa.answers — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0

### system

```
Tu réponds à des questions de vérification sur un COURT EXTRAIT de roman. Tu n'es pas critique littéraire : aucun commentaire, aucune suggestion. Une ligne par question, format EXACT :
Qn : OUI — « citation littérale de l'extrait »
Qn : NON

RÈGLES : réponds OUI uniquement si l'extrait MONTRE explicitement ce que décrit la question, ENTIÈREMENT — les personnes nommées dans la question doivent être celles de l'extrait, et l'événement doit être accompli, pas pressenti. Un indice, un soupçon, une découverte partielle, une allusion ou une menace = NON. Quand tu réponds OUI, recopie la phrase de l'extrait qui le montre. Dans tous les autres cas : NON, sans citation.
```

### user

```
QUESTIONS :
Q1 : Le texte montre-t-il l'événement 1 ?
Q2 : Le texte montre-t-il l'événement 2 ?
Q3 : Le texte montre-t-il l'événement 3 ?
Q4 : Le texte montre-t-il l'événement 4 ?
Q5 : Le texte montre-t-il l'événement 5 ?
Q6 : Le texte montre-t-il l'événement 6 ?

--- EXTRAIT ---
Jeudi 14. Vent.

« Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »

Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la phrase en compte deux. Je repousse la chaise, je me lève, la main encore sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la cuisine, sans allumer.

Dix-huit heures trente. La table du séjour, le manuscrit ouvert au chapitre onze, le crayon rouge, la marge pleine de mes signes. Je corrige jusqu'à la dernière ligne de la page, je note l'heure dans la marge.

Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie du placard, la fourchette, le verre.

Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à gauche, le verre à droite. Je mange debout près de la fenêtre, le torchon sur l'épaule. La nuit tombe sur le jardin.

Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le rebord.

Si je savais seulement pourquoi… La lampe du couloir est restée allumée. Je l'éteins.

Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, les deux assiettes écrites de ma main.

Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, le volet tiré. Le pull sur la chaise. La maison silencieuse.

Dix-neuf heures quinze, la clé dans la serrure, la lumière du couloir déjà allumée, le manteau sur la chaise, la table du séjour, le manuscrit refermé, la cuisine, l'eau du robinet, la casserole sur le feu, le sel, le pain coupé, l'assiette posée sur la table, la fourchette, le verre rempli, le repas pris debout près de la fenêtre, l'eau chaude, le torchon, l'égouttoir essuyé, le couloir, la lampe éteinte, le cahier rouvert sur la table, la page relue une fois, chaque chose à sa place, sauf une, une seule, l'assiette.

Erreur de relevé. J'ai compté une assiette là où il y en avait deux, et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, chaque objet, chaque heure, à la ligne. La nuque raide, les doigts froids. Deux assiettes.
```
