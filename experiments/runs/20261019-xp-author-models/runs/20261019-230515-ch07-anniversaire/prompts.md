# Prompts servis — 9 appel(s)

## appel 1 — model=xp-ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=40.1

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

## appel 2 — model=xp-ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=10.6

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

## appel 3 — model=xp-ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=10.6

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

## appel 4 — model=xp-ministral3-14b-q5 num_predict=150 temperature=0.7 gen_toks=150 wall_s=36.5

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

## appel 5 — model=xp-ministral3-14b-q5 num_predict=150 temperature=0.7 gen_toks=150 wall_s=11.8

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

## appel 6 — model=xp-ministral3-14b-q5 num_predict=150 temperature=0.7 gen_toks=150 wall_s=11.8

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

## appel 7 — model=xp-ministral3-14b-q5 num_predict=240 temperature=0.7 gen_toks=240 wall_s=25.6

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

La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
```

## appel 8 — model=xp-ministral3-14b-q5 num_predict=240 temperature=0.7 gen_toks=240 wall_s=19.0

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

La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
```

## appel 9 — model=xp-ministral3-14b-q5 num_predict=240 temperature=0.7 gen_toks=240 wall_s=18.9

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

La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète rien de ce qui précède.

CE TEMPS-CI :
Autour d'elle, la maison est dressée pour la fête qu'elle avait décidé de ne pas tenir : les photos étalées, la musique qui joue, le plat au four, les deux couverts. Elle ne se souvient d'avoir rien préparé. Elle se met à ranger — remettre chaque chose à sa place, c'est son métier. Chaque objet une seule fois ; ne fais pas le tour de la maison.

Prose seule, en français uniquement, sans en-tête, sans titre, sans méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — surtout, elle ne se retourne pas en certitude rassurante. Rien ne se produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui agit — tu constates seulement des états trouvés, des choses déplacées ou laissées, sans surprendre personne.
```

### début de la réponse (le modèle le continue)

```
La phrase est là, écrite hier soir, collée au papier comme une tache d'encre trop fraîche. Les couverts sont effectivement posés sur la table — un à gauche, un à droite, les bords légèrement décalés, comme si une main hésitante les avait installés sans vérifier l'alignement. Le métal est encore tiède, pas assez pour une assiette sortant du four, mais assez pour avoir été manipulés il y a peu. Je n'ai pas sorti les assiettes.
```
