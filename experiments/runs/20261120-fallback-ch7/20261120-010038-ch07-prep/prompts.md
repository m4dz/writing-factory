# Prompts servis — 7 appel(s)

## appel 1 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=127 wall_s=46.4

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 2 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=118 wall_s=11.2

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 3 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=11.4

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 4 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=10.9

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 5 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=11.0

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 6 — model=ministral3-14b-q5 num_predict=136 temperature=0.7 gen_toks=136 wall_s=11.1

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
MOUVEMENT À ACCOMPLIR — Deux phrases, la porte fermée : la première décide que ce jour n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique supprimée, le plat écarté. Rien d'autre.

MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce mouvement, jamais une liste à épuiser :
  - Décision de l'après-midi : ce jour n'aura pas lieu, effacé.
  - Les gestes d'effacement, tenus en deux phrases : ranger les photos, supprimer la musique, ne pas sortir le plat des grandes occasions ; une journée ordinaire.

CE QUE LE TEXTE NE FAIT PAS :
  - Longueur visée : 25 à 60 mots.
  - Aucun verdict ne se rend : la dernière ligne en tient lieu, et elle est déjà écrite ailleurs.
  - Pas de phrase-récapitulatif.
  - Seule, l'après-midi ; rien n'arrive : aucune voix, aucun bruit, personne. Décider, pas observer. Le mot du jour ne s'écrit pas.

L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :
---
Samedi 14. Beau temps.
---
Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète ni l'en-tête ni la citation.

Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.
Prose seule, sans titre, sans en-tête, sans méta-commentaire.
```

## appel 7 — model=ministral3-14b-q5 num_predict=1200 temperature=0.5 gen_toks=53 wall_s=20.8

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

J’ai décidé que ce jour n’aurait pas lieu. Pas d’albums ouverts sur la table basse, pas de mélodies choisies pour traverser l’après-midi sans la voir.
```
