# Prompts servis — 21 appel(s)

## appel 1 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=136 temperature=0.7 gen_toks=136 wall_s=36.5

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
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : elle efface l'anniversaire — range les photos, supprime la musique, écarte le plat — et rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Ce qu'elle a décidé cet après-midi : ce jour n'aura pas lieu, elle l'efface.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Elle est seule, l'après-midi, et rien ne lui arrive : aucune voix, aucun bruit, personne ; elle décide, elle n'observe pas. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 2 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=136 temperature=0.7 gen_toks=136 wall_s=12.9

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
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : elle efface l'anniversaire — range les photos, supprime la musique, écarte le plat — et rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Ce qu'elle a décidé cet après-midi : ce jour n'aura pas lieu, elle l'efface.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Elle est seule, l'après-midi, et rien ne lui arrive : aucune voix, aucun bruit, personne ; elle décide, elle n'observe pas. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 3 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=136 temperature=0.7 gen_toks=136 wall_s=13.0

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
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : elle efface l'anniversaire — range les photos, supprime la musique, écarte le plat — et rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Ce qu'elle a décidé cet après-midi : ce jour n'aura pas lieu, elle l'efface.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Elle est seule, l'après-midi, et rien ne lui arrive : aucune voix, aucun bruit, personne ; elle décide, elle n'observe pas. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 4 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=88 wall_s=19.7

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  → 1. CE TEMPS-CI (ci-dessous) — il finit quand : elle a nommé l'écart — la ligne dit qu'elle a mis les couverts, elle ne s'en souvient pas.
  ○ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — écrit ensuite ; ne l'écris pas
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle relit la ligne qu'elle vient de recopier. Elle y relève un écart : ce que la ligne décrit — les deux couverts mis — elle l'a sous les yeux, mais elle ne se souvient pas de l'avoir fait.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
```

## appel 5 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=150 wall_s=14.4

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  → 1. CE TEMPS-CI (ci-dessous) — il finit quand : elle a nommé l'écart — la ligne dit qu'elle a mis les couverts, elle ne s'en souvient pas.
  ○ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — écrit ensuite ; ne l'écris pas
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle relit la ligne qu'elle vient de recopier. Elle y relève un écart : ce que la ligne décrit — les deux couverts mis — elle l'a sous les yeux, mais elle ne se souvient pas de l'avoir fait.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
```

## appel 6 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=150 wall_s=14.3

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  → 1. CE TEMPS-CI (ci-dessous) — il finit quand : elle a nommé l'écart — la ligne dit qu'elle a mis les couverts, elle ne s'en souvient pas.
  ○ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — écrit ensuite ; ne l'écris pas
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle relit la ligne qu'elle vient de recopier. Elle y relève un écart : ce que la ligne décrit — les deux couverts mis — elle l'a sous les yeux, mais elle ne se souvient pas de l'avoir fait.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »
```

## appel 7 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=240 temperature=0.7 gen_toks=240 wall_s=28.1

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  → 2. CE TEMPS-CI (ci-dessous) — il finit quand : elle a commencé à ranger ; les quatre objets ont été trouvés, chacun une fois.
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
```

## appel 8 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=240 temperature=0.7 gen_toks=240 wall_s=22.9

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  → 2. CE TEMPS-CI (ci-dessous) — il finit quand : elle a commencé à ranger ; les quatre objets ont été trouvés, chacun une fois.
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
```

## appel 9 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=240 temperature=0.7 gen_toks=240 wall_s=23.1

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  → 2. CE TEMPS-CI (ci-dessous) — il finit quand : elle a commencé à ranger ; les quatre objets ont été trouvés, chacun une fois.
  ○ 3. Elle ne cherche plus le verdict. — écrit ensuite ; ne l'écris pas

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.
```

## appel 10 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=150 wall_s=20.5

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  ✓ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — déjà écrit, plus haut ; ne le reprends pas
  → 3. CE TEMPS-CI (ci-dessous) — il finit quand : elle repose le crayon.

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle ne cherche plus le verdict. Ses mains sont froides, sa nuque raide, la page relue trois fois. Elle repose le crayon.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
```

## appel 11 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=150 wall_s=14.3

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  ✓ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — déjà écrit, plus haut ; ne le reprends pas
  → 3. CE TEMPS-CI (ci-dessous) — il finit quand : elle repose le crayon.

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle ne cherche plus le verdict. Ses mains sont froides, sa nuque raide, la page relue trois fois. Elle repose le crayon.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
```

## appel 12 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=150 temperature=0.7 gen_toks=150 wall_s=14.4

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
6. La notation physiologique : le corps constate, seul, sans cause.

**Sa langue.** Registre de base : le relevé. Déclaratives courtes, faits, heures, quantités. Des lignes d'inventaire, parfois : l'objet, deux-points, le compte ou l'état constaté — sèches, sans verbe quand le constat suffit. Ses verbes : consigner, relever, pointer, vérifier, relire, collationner. Elle ne « ressent » jamais par écrit. Jargon du métier, récurrent, jamais expliqué, à faible dose : une coquille, un bourdon, un doublon, une correction d'auteur.

**Son réflexe professionnel.** Une phrase qui cloche est d'abord une faute. Le texte fait foi : sa mémoire n'est pas un référentiel de travail. Elle corrige la forme, jamais le fond — le fond appartient à l'auteur.

**Ce qu'elle écrit à la place de décider.** Elle n'annonce pas ses résolutions, elle les **inscrit**. Une décision est une ligne de carnet, pas un état d'âme : « À reprendre demain : le relevé du soir. » La consigne se pose comme une ligne d'agenda — à l'infinitif, sans sujet, sans verbe de volonté — et son exécution n'est jamais racontée.

**Ce qu'elle écrit à la place de l'état.** Un état mental ne se nomme jamais en apposition ; il se constate par le corps, en une ligne, sans cause : une main froide, une nuque raide, la page relue trois fois. Le nom de l'état est ce qu'elle refuserait d'écrire dans un relevé — il ne se mesure pas.

**La dérive.** Des phrases plus longues, plus chaudes, adressées, apparaissent dans le cahier au fil des mois. Elle les recopie comme des fautes de registre. Elle les tolère mal, ne parvient pas à les réduire, et ne les supprime jamais.

[la narratrice / État narratif courant]
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
L'ENTRÉE ENTIÈRE, pour que tu saches d'où elle part et où elle va.

Ce que l'entrée accomplit : Elle a décidé que le jour n'aurait pas lieu ; la maison est pourtant dressée pour la fête, et chaque preuve qu'elle relève est une faute qu'elle ne parvient pas à classer — jusqu'à ce qu'il ne reste que le mot, qu'elle cesse de corriger et consigne.

Ce qui est là, à ta disposition, jamais une liste à épuiser :
  - La ligne du cahier relue en ouverture.
  - Le quatuor d'objets, dans l'état de la fête qu'elle n'a pas ordonnée : les photos étalées, la playlist qui joue, le plat des anniversaires au four, les deux couverts mis. Ce sont ses preuves, jamais des apparitions. **Chaque objet est trouvé UNE SEULE FOIS — jamais re-trouvé, jamais recompté.** Quatre découvertes en tout, pas une de plus.
  - Le vocabulaire du métier et ses verdicts, à dose : deux termes au plus, jamais définis en scène.
  - Le corps de l'entrée n'est PAS un catalogue ni le récit d'une journée : c'est la SUITE DE SES VERDICTS QUI FAIBLISSENT face à ces quatre preuves. Ce qui avance, ce n'est pas le nombre d'objets, c'est l'érosion de sa capacité à les classer. Ne pas faire le tour de la maison ; rester sur la faute qui ne tient pas.
  - Les heures, si elles servent le resserrement.
  - Les objets de la maison (fiche objets), rien d'autre.

Où tu en es :
  ✓ 1. Elle relit la ligne qu'elle vient de recopier. — déjà écrit, plus haut ; ne le reprends pas
  ✓ 2. Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. — déjà écrit, plus haut ; ne le reprends pas
  → 3. CE TEMPS-CI (ci-dessous) — il finit quand : elle repose le crayon.

Ce que le texte ne fait pas : Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. Les objets sont là, dans l'état de la fête — mais rien ne bouge de soi-même sous ses yeux : aucune présence, aucun autre dans la maison, personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne surprend rien en train de se faire. Rien n'est entendu : aucun bruit, aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le tour de la maison. Elle ne raconte pas ce que l'autre a fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. La seule question est de savoir si ce n'est pas elle qui a tout mis en place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, une seule fois. Rien ne se résout, rien ne se console : pas de promesse au lendemain, pas d'adresse à personne. La voix ne cède pas — déclarative, tenue, pas de cri.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Elle ne cherche plus le verdict. Ses mains sont froides, sa nuque raide, la page relue trois fois. Elle repose le crayon.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.
```

## appel 13 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=300 temperature=0.3 gen_toks=152 wall_s=18.0

### system

```
Voici la partie d'une entrée de carnet où la narratrice rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur lequel la phrase s'achève.

L'étape qui cloche, imposée : la playlist qui tourne encore. La phrase finit sur elle.
Les objets de cette maison, les seuls : les photos, la playlist, le plat des anniversaires, les deux couverts, le cahier.

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
Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.

Je passe ensuite à la musique. Je me souviens avoir mis la playlist que nous aimions écouter ensemble, mais je ne me souviens pas avoir appuyé sur play. Je coupe la musique et je range la clé USB dans le tiroir où elle se trouve habituellement.

Ensuite, je me rends dans la cuisine pour vérifier le plat que j'ai préparé.
```

## appel 14 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=1200 temperature=0.5 gen_toks=487 wall_s=58.7

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
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
Samedi 14. Beau temps.

J'ai décidé aujourd'hui d'effacer l'anniversaire qui approche. Je ne veux pas être rappelée à cette date qui me fait tant de mal depuis qu'elle n'est plus là.
```

## appel 15 — model=mistral-nemo:12b-instruct-2407-q8_0 num_predict=1200 temperature=0.5 gen_toks=354 wall_s=35.4

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
Verdict rendu : mastic, la faute à elle. L'explication qu'elle s'est donnée : trouble à demi avoué. Elle a résolu de pointer plus précisément. Ce qu'elle a sous la main, ces jours-ci : téléphone.

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
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.

Je passe ensuite à la musique. Je me souviens avoir mis la playlist que nous aimions écouter ensemble, mais je ne me souviens pas avoir appuyé sur play. Je coupe la musique et je range la clé USB dans le tiroir où elle se trouve habituellement.

Ensuite, je me rends dans la cuisine pour vérifier le plat que j'ai préparé.
```

## appel 16 — model=qwen2.5:7b-instruct num_predict=865 temperature=0.2 gen_toks=543 wall_s=26.5

### system

```
Tu es correcteur linguistique. Tu réécris le texte en français en corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre.
```

### user

```
Samedi 14. Beau temps.

"Je ne veux pas célébrer cet anniversaire sans elle." Cette phrase, je l'ai lue hier soir dans le cahier, et elle m'a fait l'effet d'un coup de poing. Je me souviens très bien de cette date, c'était il y a neuf mois maintenant. Elle était encore là, à mes côtés, et nous avions fêté cet anniversaire ensemble, heureux et insouciants. Mais aujourd'hui, tout est différent. Elle est partie sans un mot d'explication, et cette date est devenue un rappel cruel de son absence.

J'ai passé la journée à essayer de me distraire, de penser à autre chose, mais c'était peine perdue. Cette date tournait en boucle dans ma tête, comme un refrain triste et obsédant. J'ai finalement décidé de prendre les choses en main et d'effacer cette date de mon calendrier. Je ne veux pas être rappelée à cette date qui me fait tant de mal. Je vais la remplacer par une autre, une date qui n'aura pas de signification particulière pour moi, une date qui sera simplement la mienne.

Je me suis donc mise à la tâche, et j'ai passé en revue tous mes calendriers, tous mes agendas, tous mes souvenirs qui étaient associés à cette date maudite. J'ai tout effacé, tout rayé, tout remplacé. J'ai même changé la date de mon prochain rendez-vous chez le médecin, qui tombait le même jour que cet anniversaire. J'ai tout fait pour effacer cette date de ma vie, pour ne plus avoir à y penser, pour ne plus avoir à souffrir.

Et maintenant, alors que je suis là, à écrire ces lignes dans mon carnet de relecture, je me sens mieux. J'ai l'impression d'avoir pris le contrôle de ma vie, d'avoir décidé de mon propre destin. Je sais que cette date sera toujours là, quelque part, mais je sais aussi que je ne la laisserai plus jamais me faire de mal. J'ai décidé de la remplacer, de la surmonter, de la surpasser. Et c'est ce que je vais faire, quoi qu'il arrive.

Je ne rêve pas, je sais ce que j'ai fait. J'ai décidé de prendre mon destin en main, et je suis déterminée à aller de l'avant, quoi qu'il arrive.
```

## appel 17 — model=qwen2.5:7b-instruct num_predict=681 temperature=0.2 gen_toks=401 wall_s=15.5

### system

```
Tu es correcteur linguistique. Tu réécris le texte en français en corrigeant TOUT passage qui n'est pas en français (mot ou phrase). Tu ne changes NI le sens, NI le style, NI l'ordre, NI la ponctuation des dialogues. Tu rends UNIQUEMENT le texte corrigé, rien d'autre.
```

### user

```
Samedi 14. Beau temps.

"Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours."

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit - les deux couverts mis - je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.

Je passe ensuite à la musique. Je me souviens avoir mis la playlist que nous aimions écouter ensemble, mais je ne me souviens pas avoir appuyé sur play. Je coupe la musique et je range la clé USB dans le tiroir où elle se trouve habituellement.

Ensuite, je me rends dans la cuisine pour vérifier le plat que j'ai préparé.
```

## appel 18 — model=qwen2.5:7b-instruct num_predict=400 temperature=0.1 gen_toks=132 wall_s=8.6

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

## appel 19 — model=qwen2.5:7b-instruct num_predict=500 temperature=0.1 gen_toks=217 wall_s=8.9

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
1. La narratrice a 38 ans et est correctrice depuis quinze ans.
2. La narratrice ne cherchera jamais à joindre Romane ni à comprendre pourquoi elle est partie.
3. La narratrice utilise une méthode de dater, relever, relire pour se tenir debout.
4. La narratrice ne descend une marche que quand celle du dessus a cédé.
5. La narratrice ne supprime jamais une ligne de ce qu'elle relit, même si cela la blesse.
6. La narratrice envisage par moments de consulter une thérapeute mais ne le fait jamais.
7. Personne d'autre n'entre dans la maison.
8. Aucun repas n'est partagé, aucune conversation n'a lieu.
9. Elle ne sort pas de la maison.
```

## appel 20 — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0 gen_toks=45 wall_s=4.9

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
Q1 : Le texte montre-t-il la narratrice cherchant à joindre Romane ou à comprendre pourquoi elle est partie ?
Q2 : Le texte montre-t-il la narratrice tentant de joindre quelqu'un d'autre que Romane ?
Q3 : Le texte montre-t-il la narratrice utilisant une autre méthode pour se tenir debout ?
Q4 : Le texte montre-t-il la narratrice descendant une marche sans attendre que celle du dessus ait cédé ?
Q5 : Le texte montre-t-il la narratrice supprimant une ligne de ce qu'elle relit, même si cela la blesse ?
Q6 : Le texte montre-t-il la narratrice consultant une thérapeute ?
Q7 : Le texte montre-t-il quelqu'un d'autre entrant dans la maison ?
Q8 : Le texte montre-t-il des repas partagés ou des conversations se produisant dans la maison ?
Q9 : Le texte montre-t-il la narratrice sortant de la maison ?

--- EXTRAIT ---
Samedi 14. Beau temps.

"Je ne veux pas célébrer cet anniversaire sans elle." Cette phrase, je l'ai lue hier soir dans le cahier, et elle m'a fait l'effet d'un coup de poing. Je me souviens très bien de cette date, c'était il y a neuf mois maintenant. Elle était encore là, à mes côtés, et nous avions fêté cet anniversaire ensemble, heureux et insouciants. Mais aujourd'hui, tout est différent. Elle est partie sans un mot d'explication, et cette date est devenue un rappel cruel de son absence.

J'ai passé la journée à essayer de me distraire, de penser à autre chose, mais c'était peine perdue. Cette date tournait en boucle dans ma tête, comme un refrain triste et obsédant. J'ai finalement décidé de prendre les choses en main et d'effacer cette date de mon calendrier. Je ne veux pas être rappelée à cette date qui me fait tant de mal. Je vais la remplacer par une autre, une date qui n'aura pas de signification particulière pour moi, une date qui sera simplement la mienne.

Je me suis donc mise à la tâche, et j'ai passé en revue tous mes calendriers, tous mes agendas, tous mes souvenirs qui étaient associés à cette date maudite. J'ai tout effacé, tout rayé, tout remplacé. J'ai même changé la date de mon prochain rendez-vous chez le médecin, qui tombait le même jour que cet anniversaire. J'ai tout fait pour effacer cette date de ma vie, pour ne plus avoir à y penser, pour ne plus avoir à souffrir.

Et maintenant, alors que je suis là, à écrire ces lignes dans mon carnet de relecture, je me sens mieux. J'ai l'impression d'avoir pris le contrôle de ma vie, d'avoir décidé de mon propre destin. Je sais que cette date sera toujours là, quelque part, mais je sais aussi que je ne la laisserai plus jamais me faire de mal. J'ai décidé de la remplacer, de la surmonter, de la surpasser. Et c'est ce que je vais faire, quoi qu'il arrive.

Je ne rêve pas, je sais ce que j'ai fait. J'ai décidé de prendre mon destin en main, et je suis déterminée à aller de l'avant, quoi qu'il arrive.
```

## appel 21 — model=qwen2.5:7b-instruct num_predict=400 temperature=0.0 gen_toks=45 wall_s=3.7

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
Q1 : Le texte montre-t-il la narratrice cherchant à joindre Romane ou à comprendre pourquoi elle est partie ?
Q2 : Le texte montre-t-il la narratrice tentant de joindre quelqu'un d'autre que Romane ?
Q3 : Le texte montre-t-il la narratrice utilisant une autre méthode pour se tenir debout ?
Q4 : Le texte montre-t-il la narratrice descendant une marche sans attendre que celle du dessus ait cédé ?
Q5 : Le texte montre-t-il la narratrice supprimant une ligne de ce qu'elle relit, même si cela la blesse ?
Q6 : Le texte montre-t-il la narratrice consultant une thérapeute ?
Q7 : Le texte montre-t-il quelqu'un d'autre entrant dans la maison ?
Q8 : Le texte montre-t-il des repas partagés ou des conversations se produisant dans la maison ?
Q9 : Le texte montre-t-il la narratrice sortant de la maison ?

--- EXTRAIT ---
Samedi 14. Beau temps.

« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »

J'allais poser le verdict quand la main s'est arrêtée. Neuf ans, et j'aurais dû demander, quand il était encore temps, ce qui l'a… La marge reste blanche. Le crayon ne biffe pas.

Je rentre à la maison à 19h, je pose mes clés sur la console de l'entrée, je me dirige vers le salon, je vois les photos étalées sur la commode, je les range dans l'album, je passe dans la cuisine, je sors le plat des anniversaires du four, je le pose sur la table, je sors les deux couverts du tiroir, je les place sur la table, je vais dans le salon, je vois la playlist qui tourne encore, je l'arrête, je range la clé USB dans le tiroir, je me souviens que je n'avais pas prévu de célébrer notre anniversaire de mariage, je décide de ranger, je me demande comment tout cela a pu m'échapper.

Je relis la ligne que je viens de recopier, et je relève un écart. Ce que la ligne décrit — les deux couverts mis — je l'ai sous les yeux, mais je ne me souviens pas de l'avoir fait. Mon regard se pose sur la table dressée pour deux, et je me demande comment cela a pu m'échapper. J'ai pourtant décidé de ne pas tenir cette fête, de ne pas célébrer notre anniversaire de mariage.

Autour de moi, la maison est dressée pour la fête que je n'avais pas prévue : les photos étalées sur la commode, la musique qui joue en sourdine dans le salon, le plat que j'avais préparé pour l'occasion au four, les deux couverts mis sur la table. Je ne me souviens pas d'avoir fait tout cela. Je décide de ranger, de remettre chaque chose à sa place. Je commence par les photos, que je replace dans l'album où elles étaient avant. Je me souviens alors que je les avais sorties la veille pour les regarder, mais je ne me souviens pas les avoir étalées comme ça.

Je passe ensuite à la musique. Je me souviens avoir mis la playlist que nous aimions écouter ensemble, mais je ne me souviens pas avoir appuyé sur play. Je coupe la musique et je range la clé USB dans le tiroir où elle se trouve habituellement.

Ensuite, je me rends dans la cuisine pour vérifier le plat que j'ai préparé.

Constat : anniversaire.
```
