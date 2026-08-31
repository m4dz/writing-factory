# CLAUDE.md — fiction-assistant

## Ce qu'est ce projet

Démonstrateur d'IA locale pour la rédaction littéraire, support technique de la
keynote « L'IA devant soi » (50', keynote de clôture). Deux fonctions :

1. **Assistant d'écriture** (« mode auteur ») : maintien d'une bible monde
   (personnages, lieux, props), planification de chapitres, ghostwriting.
2. **Roleplay** (« mode acteur ») : dialoguer avec les personnages pour
   explorer leur personnalité, sans sortie de personnage.

**Règle d'or, non négociable : tout tourne en local.** La fabrique reste à
notre main. Aucune API cloud, aucun logging externe. C'est la thèse même du
talk : une œuvre dont la fabrique est locale est inauditable.

## Contraintes de scène (keynote)

- La démo est lancée en début de talk et récoltée **~25 minutes** plus tard
  (budget abaissé de 35' à 25' — 2026-08-06) : la génération complète d'un
  chapitre (plan de scènes + rédaction) doit tenir dans ce budget sur un
  MacBook Apple Silicon. **La vraie échéance est le compteur du deck (28'),
  génération ET voix clonée comprises.** Mesuré bout-en-bout par l'API le
  2026-08-09 : **14 min 02** pour 3 scènes (dont 2 min de TTS), soit 17-18 min
  attendues à 4 scènes → 10 min de marge. Mais cette marge suppose une machine
  SANS entretien macOS en cours : les runs lancés pendant `mediaanalysisd` ont
  dépassé 32 et 49 minutes. **Le vrai risque de scène est là, pas dans le
  pipeline** (les mentions « / 35 min » ailleurs dans ce fichier sont
  historiques).
- Un compte à rebours est affiché pendant la génération.
- Le pipeline montré sur scène : plan de scènes → écriture → relecture →
  cohérence (c'est la « strate 4 » du talk, LangGraph).

## Architecture décidée (ne pas rediscuter sans raison forte)

- **Rejet du multi-instances** (un modèle par personnage) : la cohérence
  vient d'une mémoire externe partagée, pas de la multiplication des modèles.
  Les modèles ne sont que des *lecteurs* de la vérité stockée hors d'eux.
- **Trois couches** :
  - *Stockage* : Markdown canonique dans `bible/` (édité par l'humain) →
    ChromaDB (mode serveur HTTP, conteneurisé). ChromaDB est TOUJOURS généré
    depuis la source Markdown, jamais l'inverse.
  - *Retrieval/orchestration* : LangGraph, RAG contextuel dynamique — le
    contexte est assemblé à la requête (fiches des personnages présents,
    lieu, scènes précédentes pertinentes) en un prompt système de 2-3k tokens.
  - *Modèles* : trois rôles. « Auteur » = **`mistral-nemo`
    (Q8_0, 12B)**, tranché au benchmark sur M3 Pro 18 GB : ~10 tok/s →
    chapitre complet ~20 min (2× de marge sur les 35 min), leak anglais
    quasi nul. Mistral-small 24B a une prose supérieure (place les deux
    répliques signature, zéro leak) mais plombe à ~3 tok/s sous pression
    mémoire (14 GB / 18 GB) → chapitre ~1 h, hors budget scène. Small
    reste l'option qualité pour l'écriture HORS-démo (non chronométrée).
    « Acteur » (roleplay) = même modèle nemo, prompt système interdisant
    la sortie de personnage (modèle chaud partagé, pas de reload).
    « QA/lint » = **`qwen2.5:7b-instruct`** (Q4_K_M, ~4,7 GB, ~26 tok/s),
    tranché au benchmark : d'un autre lignage que nemo (pas sa tendance au
    leak), fiable en FR, bon suivi de format. Phase POST-génération → un seul
    swap nemo→Qwen, pas de co-résidence. Réparation linguistique validée ;
    cohérence par faits encore à fiabiliser (cf. Prochaine étape).
- **Ollama hors conteneur** (accès GPU Apple Silicon direct), joint depuis
  les conteneurs via `http://host.containers.internal:11434`.
  Embeddings : `nomic-embed-text` (768 dims, cosine).
- **Mémoire conversationnelle à deux niveaux** pour le roleplay (à
  implémenter) : N derniers échanges en contexte + rolling summary indexé
  dans ChromaDB, taggé par personnage, retrievé en début de session.
- **Limite connue** : Mistral-small rate parfois la cohérence causale longue
  distance. Mitigation : rendre EXPLICITES dans les fiches les liens de
  cause à effet (le template le rappelle), ne jamais supposer l'inférence.

## Structure

```
bible/                    # source canonique, éditée à la main
  characters/principals/  # fiches 7 chunks (voir _template.md)
  characters/secondaires/ # fiches allégées (3-4 chunks suffisent)
  lieux/  props/  scenes/ # scènes rédigées et validées
indexer/                  # index.py + query_test.py, conteneurisé
data/chromadb/            # volume persistant
podman-compose.yml        # openwebui + chromadb + indexer (profil tools)
```

## Conventions établies

- Un chunk = une section `## ` d'une fiche. ID déterministe `{id}::{slug}`.
- Chunk préfixé `[doc_id / Titre]` avant embedding (améliore le matching).
- Fichiers `_*.md` jamais indexés (templates).
- Commentaires HTML `<!-- -->` = instructions pour l'humain, purgés avant
  embedding.
- Métadonnées scalaires uniquement (listes → CSV). Filtres : `type`
  (character, lieu, prop, scene), `rank`, `doc_id`, `section`, `tags`.
- Sept chunks par personnage principal : psychologie, comportement et
  présentation, voix et expression, histoire, compétences et capacités,
  relations, **état narratif courant** — ce dernier est le SEUL mis à jour
  régulièrement (incrémenter `version`, réindexer).
- Le chunk voix contient des répliques typiques ET des contre-exemples
  (« ne dirait jamais ») : les exemples négatifs ancrent mieux la voix.
- Personnages du récit : 2 principaux, 3 secondaires (à créer).

## État actuel — au 2026-08-27, après sept sessions de mesure

**La synthèse complète est dans `docs/passation-generale.md`** (couche PROFONDE,
hors `bible/`, donc hors de portée de l'indexeur par construction). Ce qui suit
est l'état opérationnel ; l'historique run par run vit dans `journal-des-murs/`,
les grilles `grille-lint-*.md` et les archives `retour-*/`.

**La machine est à pied d'œuvre.** Chaîne complète validée : `POST /generate` →
chapitre → voix clonée → `/chapter` + `/audio`. Répétition du chapitre 7
chronométrée bout à bout : **7,6 min, 20,4 de marge sur les 28** du compteur du
deck, deux horloges coïncidentes, veille nulle.

### Acquis, chiffré

- **Zéro fuite lexicale** sur tous les runs scorés depuis B′.
- **Ancre, en-têtes et chute possédés par le CODE** — préfixage par
  concaténation réelle, puis tampon APRÈS `repair`, qui les réécrivait. Sur un
  run, `repair` avait supprimé l'en-tête entier, donc la bascule audio.
- **Glissement composé** : zéro sur onze runs, puis 4/4. Il n'a jamais manqué au
  modèle — il était refusé par nos propres validateurs.
- **Accumulation composée** 6/6, 2-5 % de similarité à l'étalon.
- **Méta-termes 0/4**, garde d'entrée alignée sur le lint de sortie.
- **Étanchéité** : 27 chunks, cinq contrôles verts, plus aucun terme réservé
  indexé. Elle se REPROUVE à chaque réindexation, jamais présumée.
- **Méthode du mouvement** (2026-08-27) : ordre de service intention →
  trajectoire → matière → vétos. Mesuré contre le tirage de référence — recopie
  du prompt **0,94 → 0**, entrée d'ouverture 90 mots → **19**, masse en cible
  pour la première fois (557 sur 450-600), présence et départ nommé disparus.

### Non acquis

- **La voix à l'oral.** Verdict constant depuis le 2026-08-19 : la restitution
  chevrote — de la texture par endroits, jamais soutenue. C'est LE sujet.
- **La trajectoire.** Le dernier tirage ne monte pas, il BOUCLE : les
  découvertes se répètent au lieu de se rapprocher, et le récit se met à noter
  ce qu'il vient de raconter. Sujet de brief, pas de câblage.
- **Le texte de secours.** Structurellement complet, scéniquement fautif.

### Point d'arrêt en cours

**La lecture debout tranche, et rien ne se généralise sans elle.** La grille
porte une ligne manuelle unique en tête — *le mouvement déclaré est-il
accompli ?* — et son verdict ouvre trois routes exclusives : généralisation aux
scene briefs (~30 mouvements à rédiger, écriture d'auteur), ouverture du dossier
du rythme, ou itération sur la trajectoire.

## Intégration deck / TTS — décisions du 2026-08-07

Le contrat HTTP vient du talk et est gelé (cf. « API de démo » ci-dessus).
Trois décisions du propriétaire complètent la cible :

- **TTS dans le MÊME venv que l'orchestrateur** (`orchestrator/tts.py`), pas en
  sous-processus vers le venv du dépôt TTS. `mlx-audio` déclare
  `Requires-Python: >=3.10` et s'importe sans broncher sur notre 3.10.9
  (vérifié) : le `python3.11` du RUNBOOK est un choix d'installation, pas une
  contrainte. Un seul venv à recréer le jour J. Coût : +542 MB de paquets
  (mlx, transformers, scipy), sans torch. Import PARESSEUX dans la fonction de
  rendu — le serveur vit des heures et ne synthétise qu'une fois.
  * **On n'importe PAS `../TTS/lire_chapitre.py`.** Sa boucle de rendu est
    enfermée dans `main()`, et son `charger_texte()` appelle `sys.exit()` :
    dans un serveur, `SystemExit` est une `BaseException`, elle traverse
    `except Exception`, tue le thread en silence et laisse le job bloqué en
    « generating » pour toujours. Ce que les deux dépôts partagent, c'est la
    VOIX (`TTS/voix/`) et l'identifiant du modèle, pas du code : les deux sont
    des clients minces de `mlx_audio`. `TTS/RUNBOOK.md` reste la référence des
    paramètres — si l'un bouge là-bas, il bouge ici.
  * Un échec de TTS ne fait PAS échouer le job : le chapitre est valide et
    servi, seul `/audio` reste en 204. Le contrat gèle un fallback PAR
    RESSOURCE — replier sur les deux parce que la voix a manqué serait perdre
    du bon travail.
- **Mode acteur : notre propre `POST /chat` + une page dédiée servie par l'API**,
  pas OpenWebUI. Raison : notre mémoire est STATEFUL côté serveur (résumé
  glissant, souvenirs indexés) alors que le contrat OpenAI est
  stateless-avec-historique-complet — OpenWebUI renverrait tout l'historique à
  chaque tour et contournerait le résumeur. Bonus : une page à nous peut
  s'afficher en iframe dans une slide. `chat_character.py` reste le plan B.
- **Bascule après la DEUXIÈME PHRASE, posée par le code** (`chapitre.py`).
  Repère strictement reproductible : sur scène, il lit deux phrases puis lance
  l'audio. Ma proposition initiale (« frontière de paragraphe ») dépendait du
  découpage de nemo, donc variait d'un run à l'autre — inutilisable comme repère.
- **Lecture clonée bornée en SECONDES, pas en mots** (`AUDIO_SECONDES=165`,
  soit 2 min 45 — milieu de la fenêtre 2'30-3'00 demandée par le deck, extrait
  joué EN ENTIER). La borne est exprimée dans l'unité du besoin ; la conversion
  en mots passe par le débit mesuré du clone.
  * ⚠ **Le deck raisonnait à ~150 mots/min, le clone parle à 190** (mesuré).
    Leurs 450 mots auraient donné 2'22, SOUS leur propre plancher de 2'30 —
    un trou, puisque l'extrait n'est plus coupé en cours de route. La
    conversion se fait donc chez nous : 165 s × 190 = 522 mots.
  * Ce débit vient d'UN échantillon de 117 mots. `tts.rendre` compare la durée
    obtenue à la cible et émet une note dans `/status` au-delà de 20 s d'écart,
    avec le débit réel à reporter. L'hypothèse se signalera au lieu de se
    découvrir sur scène.
  * MESURÉ sur cette machine (et non repris du RUNBOOK) : **1,57× temps réel**
    modèle chaud. Donc 2'45 d'audio ≈ **1,8 min de calcul** → **~19 min au
    total**, 9 min de marge sur les 28' du compteur. Le deck estimait 3 min de
    TTS en supposant 1× temps réel.
  * Le premier rendu mesuré donnait 0,93× : il portait l'échauffement des
    noyaux Metal. Ne pas conclure sur un segment de six secondes.
  * ⚠ J'avais justifié le bornage par « 15 min de calcul pour tout le
    chapitre » : c'était FAUX (8 min au facteur réel). La décision tient sur le
    TEMPS D'ÉCOUTE — 12,6 min de lecture dans une keynote de 50, c'est non — qui
    était de toute façon l'argument solide.
  * `chapitre.py` pose aussi `<!-- FIN AUDIO -->`, additif : il dit au deck où
    s'arrête la voix clonée. Le chapitre servi reste ENTIER, c'est la pièce à
    conviction de la démo.
- **Notifications téléphone par Telegram (`orchestrator/notify.py`), coupées par
  défaut, charge utile verrouillée.** Exception assumée à la règle d'or
  « aucune API cloud » : ce qui reste local, c'est la FABRIQUE de l'œuvre ; ceci
  est le BIPEUR DE L'OPÉRATEUR. Son intérêt est d'être hors-bande (cellulaire)
  quand le wifi de la conférence lâche — le cas même qu'il doit signaler.
  * Activation : `TELEGRAM_BOT_TOKEN` (via @BotFather) + `TELEGRAM_CHAT_ID`.
    Sans les deux, tout appel est un no-op silencieux — vérifié, zéro octet
    sur le réseau.
  * **La protection est MÉCANIQUE, pas disciplinaire.** Les messages sont
    composés à partir de CHAMPS STRUCTURÉS (phase, pourcentage, durées,
    compteurs, classe d'erreur) ; il n'existe volontairement pas de
    `notify.texte()` générique, qui serait la porte par laquelle le contenu
    finirait par sortir. Second rideau : un filtre retire tout ce qui est entre
    guillemets avant l'envoi, et borne à 200 caractères.
  * Ce filtre n'est pas théorique : nos propres notes citent la bible
    (« PLAN REFUSÉ — contredit « … » ») et le chapitre (« fin coupée — « … » »).
    Les relayer verbatim aurait exporté l'œuvre chez Telegram. Testé sur les
    trois cas réels : rien ne passe.
  * Débit : un battement d'avancement toutes les 5 min au plus (sur une montre,
    une rafale est pire que rien) ; démarrage, échec, annulation et « prêt »
    passent en priorité. Envoi dans un THREAD : la génération n'attend jamais
    le réseau — mesuré à 0 ms de retour avec des identifiants injoignables.

⚠ **Le budget de 25 min de notre CLAUDE.md ne couvre que la génération.** La
vraie échéance est le compteur du deck (28') MOINS le temps de TTS. Avec la
lecture bornée : 17 + ~4 = ~21 min.

## Prochaine étape convenue

**La lecture debout du propriétaire sur le dernier tirage du chapitre 7.** Rien
ne se généralise avant — c'est le point d'arrêt du protocole, et il vaut aussi
contre la session.

Ce qui suit, selon le verdict :

1. **Si le mouvement est accompli** — généralisation aux scene briefs : une
   trentaine de mouvements par entrée, format départ/bascule/arrivée. C'est de
   l'écriture d'auteur, jamais générée ni reformulée par le pipeline.
2. **Sinon** — le dossier du rythme de phrase s'ouvre, avec trois tirages
   comparables pour le documenter (cases / mouvement à trois appels / mouvement
   à un appel). Options connues : passe de révision dédiée (risquée, `review` a
   toujours abîmé), réserves lourdes, ou passe humaine assumée — qui est
   thématiquement le sujet même du roman.
3. **Entre les deux** — itérer sur la trajectoire du brief, pas sur
   l'architecture.

**Chantiers indépendants du verdict :**

- **Lot bible différé** : clôtures en fiche (comment une station se ferme, ce
  que la dernière ligne ne doit pas faire), symétrisation du prénom de celle qui
  est partie à l'indexation — il est servi dans dix chunks alors que le roman ne
  le nomme jamais. Réindexation, puis étanchéité EN ENTIER.
- **Trois items du lot chapitre-7** que la grille remplie nomme et dont la liste
  ne m'est pas parvenue (cinq sur huit sont faits).
- **Keynote** : WAV de secours rendu et archivé, répétition générale complète
  (préchauffage TTS inclus — 0,60× à froid contre 1,55 chaud), sections figées
  avec les chiffres.
- **Question ouverte, à trancher par le propriétaire** : le cadrage public
  local/cloud. Les travaux fondateurs (bible, calibration, arbitrages) ont été
  menés en cloud, l'exécution est locale, et le talk affirme que la fabrique
  locale rend l'œuvre inauditable. C'est la seule ligne qui peut abîmer la thèse
  en public si elle est mal posée — elle mérite d'être dite tôt, pas masquée.

## Documents de référence

- `docs/passation-generale.md` — **la synthèse générale du projet** : le roman,
  la keynote, l'état des deux, les doctrines, les décisions ouvertes et le rôle
  attendu de la session. Couche PROFONDE : il contient la vérité de fin, il ne
  va jamais dans `bible/` et n'est jamais servi. Il vit dans `docs/`, que
  l'indexeur ne lit pas — l'exclusion est structurelle, pas déclarative.
- `docs/RUNBOOK.md` — toutes les opérations : backends, jetons Telegram,
  génération, préparation des assets, séquence du jour J, pannes courantes.
  C'est LUI qu'on suit sous pression, pas ce fichier.
- `docs/contrat-api-pour-le-deck.md` — artefact de passation vers la session
  Code du talk (rév. 4). Décrit la surface HTTP réelle, les écarts assumés au
  contrat gelé (`phase` peut valoir `error` et `idle`), et les mesures.
- Côté talk : `openspec/changes/remote-integration-contract/` FIGE le contrat
  HTTP. On l'implémente, on ne le rediscute pas.

## Notes d'architecture (orchestrateur)

- `orchestrator/` tourne en **venv host** (pas conteneur) pour l'itération
  rapide ; conteneurisation = étape packaging démo. Joint Ollama et ChromaDB
  en `localhost`.
- **Cohérence (`qa.py`) : faits → QUESTIONS DE VIOLATION → réponses par scène.**
  Trois échecs ont dicté ce protocole. (a) Vérifier sur le chapitre entier
  (~2000 mots) fait basculer Qwen en critique d'atelier. (b) Un binaire
  OUI/NON range le « non mentionné » dans NON → faux positifs partout ; une
  étiquette ABSENT aide mais ne suffit pas. (c) Classer un fait ABSTRAIT, et
  surtout NÉGATIF (« Élara ignore que… », « Kael n'avoue jamais »), reste hors
  de portée d'un 7B : il a lu l'aveu complet de Kael et l'a classé CONFORME au
  fait « Élara ignore ». C'est de l'inférence (entailment), pas de la lecture.
  → On convertit chaque fait en question d'événement dont le OUI vaut
  violation (« Le texte montre-t-il Élara découvrant que… ? »), puis on la pose
  scène par scène. Répondre « ce texte montre-t-il X ? » EST de la lecture.
  Chaque OUI doit citer le texte, et le CODE vérifie que la citation s'y trouve
  vraiment (le modèle recopie parfois le fait au lieu de la scène) ; sinon le
  signalement est relégué en « à vérifier à la main », jamais compté comme
  violation. Deux filtres complètent le dispositif, tous deux nés de faux
  positifs observés sur un vrai chapitre : (i) `derive_facts` exclut
  explicitement l'ÉTAT TRANSITOIRE des fiches (« vient d'arriver à… »,
  objectif immédiat, émotion du moment) — ce sont justement les choses que le
  chapitre doit faire évoluer, les vérifier revient à sanctionner le récit
  d'avancer ; (ii) chaque OUI subit un CONTRE-APPEL (`_confirm`) qui repose la
  question SEULE, en mode sévère, réponse en un mot — le questionnaire groupé
  dilue l'attention et produit des OUI complaisants (« comptant mentalement
  les pierres » lu comme une délégation de tâche). Coût : ~8 s. Leçon
  générale, réutilisable pour le mode acteur : donner au petit modèle une
  tâche de LECTURE, jamais d'INFÉRENCE.
- Retrieval à deux stratégies (`retrieval.py`) : DÉTERMINISTE par id pour les
  chunks d'écriture des personnages présents (voix, état courant, psychologie),
  SÉMANTIQUE top-k pour lieu et scènes précédentes.
- **Ollama écoute sur `127.0.0.1` SEULEMENT** (`scripts/local.ollama.plist`,
  2026-08-06). On a longtemps cru que l'indexeur conteneurisé imposait
  `0.0.0.0` : faux avec podman 5 (applehv + gvproxy).
  `host.containers.internal` résout vers `192.168.127.254`, qui n'est pas une
  interface de l'hôte mais gvproxy lui-même ; gvproxy compose ensuite la
  connexion DEPUIS l'hôte et atteint donc le loopback. Vérifié de bout en
  bout : hôte 200, LAN `192.168.6.17:11434` refusé, conteneur → `/api/embed`
  768 dims OK. Enjeu réel : sur le WiFi de la conférence, `0.0.0.0` exposait
  l'API Ollama sans authentification à tout le réseau.
- Le service Ollama de brew est régénéré au `brew services start`, ce qui
  efface les vars ajoutées à la main — d'où l'agent launchd du projet. Ne pas
  revenir à `brew services` (les deux agents se disputeraient le port 11434,
  celui de brew ayant `RunAtLoad`).

## Règle de méthode — un instrument se falsifie avant de servir

**Avant de faire confiance à un contrôle, exiger qu'il ÉCHOUE sur un cas
connu** : injecter le défaut, ou le rejouer sur des sorties dont on sait déjà, à
la main, qu'elles sont fautives. Un contrôle qui n'a jamais échoué n'a rien
prouvé — il peut porter sur un ensemble vide, tester une condition impossible,
ou être débranché de son rapport.

**Le lint fantôme** — un détecteur juste dont le résultat n'atteint jamais la
grille — est la forme la plus coûteuse, parce qu'elle se lit comme un succès.

Le principe a sauvé le projet trois fois, et à chaque fois le contrôle était
VERT avant qu'on le falsifie :
- **Étanchéité (session 4)** : le test interrogeait la collection auteur pour
  vérifier qu'aucun chunk profond n'en sortait — or le profond vivait dans une
  autre collection. Il passait *par construction*. Le remède est le témoin
  positif : on injecte volontairement un chunk profond, il DOIT remonter.
- **Splitter (session 4)** : le contrôle filtrait les chunks par préfixe d'id,
  et une divergence de `doc_id` le laissait porter sur **zéro chunk**. Vert sur
  l'ensemble vide. Il échoue désormais explicitement si l'ensemble est vide.
- **Grille (session 5)** : cinq détecteurs existaient dans `lint_style.py` et
  aucun n'avait de ligne dans `grille_session.py`. Ils calculaient, on jetait le
  résultat — d'où un attracteur passé sans croix sur un run entier.

Corollaire pratique : **automatiser un contrôle et le rendre bloquant sont deux
décisions distinctes.** Les confondre fait échouer un run sur un tic mineur
pendant que les critères qui comptent passent.

**Et il se falsifie DANS LES DEUX SENS.** Pas seulement « rate-t-il le
défaut ? », mais « refuse-t-il la référence ? ». Les erreurs des sessions 6 et 7
sont presque toutes du second type — des contrôles justes en apparence qui
rejetaient l'étalon, la banque, l'accumulation, ou la structure imposée par le
brief. Quatre occurrences : `CHAMP_DEPART` exigeait le mot du départ dans une
phrase dont l'objet est de s'interrompre avant ; le critère « propositions
verbales » rejetait l'accumulation de l'étalon, nominale à 88 % ; la similarité
de mots aurait supprimé l'accumulation elle-même ; un filtre de longueur
masquait le seul vrai doublon.

## Les doctrines — l'acquis le plus précieux, les tenir

Sept sessions les ont établies, chacune payée par un run raté. Elles sont
développées dans `docs/passation-generale.md` §4.

1. **Le modèle fournit la matière, le code tient le geste.** Chute, ancre,
   en-têtes, glissement, assemblage : au code.
2. **La chaleur ne se génère pas, elle se compose.** Le cloisonnement affame
   le modèle en matière chaude par construction : sa chaleur spontanée est
   donc inventée de toutes pièces, toujours dans les passages chauds.
3. **Compter n'est pas lire.** La grille automatique est un VÉTO ; le juge est
   la lecture debout.
4. **Falsifier dans les deux sens** (ci-dessus).
5. **Les instruments mentent** : lint fantôme, message qui rapporte autre chose
   que ce que la porte mesure, chronomètre qui s'arrête en veille. Aucun
   détecteur sans sa ligne de grille ; aucun chiffre sans son horloge.
6. **Montré = récité.** Tout ce qui est servi peut ressortir verbatim — les
   contre-exemples autant que les exemples, et jusqu'aux mots de nos propres
   consignes (une consigne d'ouverture est sortie recopiée à 0,94). Les
   instances vivent dans l'outillage ; le contexte servi ne porte que des
   catégories.
7. **Un vide dans la matière servie se remplit toujours** — par le monde
   générique du modèle, ou par un emprunt à un autre chapitre. Le vide s'écrit.
8. **Une consigne qui décrit ce que le personnage décide produit un personnage
   qui décrit ses décisions.** Les consignes énoncent des faits et des
   trajectoires, jamais des intentions.
9. **L'exception se déclare en DONNÉES, jamais en assouplissement de règle**
   (`entrees_spec`). Corollaire : tout validateur écrit avant une structure la
   lit comme une anomalie.
10. **L'interdit seul déplace le défaut** : la fiche dit ce que le personnage
    fait *à la place*.
11. **Toute fiction imbriquée est un tunnel sous le cloisonnement lexical.**
12. **Chaque dispositif qui règle un défaut en crée un à l'endroit qu'il
    touche** — l'y chercher, systématiquement. Le découpage a réglé la masse et
    fabriqué trois arcs ; les stations ont réglé le plancher et fabriqué une
    litanie.
13. **Une seule variable entre deux mesures ; les runs ratés sont de la
    matière** (`journal-des-murs/`, une pièce par cause).
14. **Le lint d'archive porte sur l'ensemble FINAL, juste avant l'envoi.**
    Deux archives sont parties avec un fichier non vérifié : le README avait été
    écrit APRÈS la passe de lint. Linter puis ajouter puis expédier, c'est ne
    pas avoir linté — la doctrine 5 appliquée à sa propre procédure. Rien ne
    part sans une passe sur le répertoire complet, à la seconde qui précède
    l'archivage.

## Points de vigilance connus

- **LA MISE EN VEILLE CASSE OLLAMA, ET `/api/ps` NE LE DIT PAS (2026-08-07).**
  Après une nuit de veille, le démon Ollama était toujours vivant (10 h
  d'uptime, port ouvert, `/api/ps` → 200) mais INCAPABLE de charger un modèle :
  `Load failed … error="timed out waiting for llama-server to start"`, et toutes
  les requêtes de génération en 500. Le préflight ne regardait que `/api/ps`,
  qui répond 200 avec une liste vide quand rien n'est chargé — indiscernable
  d'une machine saine. Il mentait par omission.
  * Remède immédiat : `launchctl kickstart -k gui/$(id -u)/local.ollama`
    (vérifié, service rétabli).
  * Le préflight fait désormais RÉELLEMENT générer un token
    (`_probe_generation`, sur le petit modèle Qwen : on vérifie que le serveur
    sait lancer un llama-server, pas que nemo tient en mémoire). La sonde passe
    `keep_alive: 0` — sans quoi elle laisserait un modèle chaud et le run
    démarrerait en co-résidence, exactement la pression mémoire que ce préflight
    existe pour empêcher. Coût : ~10 s à froid, 0,7 s si le modèle est déjà là.
  * **Avant la scène : empêcher la veille** (`caffeinate -is`, ou réglages
    d'énergie). Un portable qui s'endort avant la démo la tue.
- **L'ENTRETIEN macOS EST LE PREMIER RISQUE DE SCÈNE (2026-08-06, 21 h).**
  Deux runs successifs ont produit des **trous de 5 à 18 minutes entre deux
  appels au modèle**, modèle chaud, processus à 0,8 s de CPU consommé en
  49 minutes — il dormait sur une socket, il ne calculait pas. Les appels de
  génération, eux, tenaient leur vitesse nominale (1 min 46, 1 min 16,
  1 min 30). Cause : `mediaanalysisd` à **197-227 % de CPU** (deux cœurs),
  réveillé par le redémarrage, plus `apfsd` — contre un processus de génération
  lancé en tâche de fond, donc à `nice 5`, qui perd l'arbitrage.
  * **J'ai d'abord attribué ces trous à la PAGINATION** (swap saturé, 56 MB de
    RAM libre au run 3). C'était faux : le run 4 a reproduit exactement le même
    motif sur une machine fraîchement redémarrée, swap à zéro au départ et
    14 GB de mémoire libre annoncés par Ollama. La saturation du swap était
    réelle mais concomitante, pas causale. Leçon de méthode : deux symptômes
    simultanés ne font pas une cause, et le signal qui tranchait était le
    temps CPU du processus (0,8 s), pas les compteurs mémoire.
  * Le préflight bloque désormais sur les démons d'entretien (`NOISY_DAEMONS`,
    seuil 80 % de CPU) — il aurait refusé de lancer les runs 3 ET 4.
  * **Aucune mesure de temps ne vaut quelque chose pendant l'entretien.**
    Vérifier `ps -Ao %cpu,comm -r | head` avant de chronométrer, et laisser
    `mediaanalysisd` finir (il peut tourner longtemps après un redémarrage ou
    un gros transfert).
  * **Lancer le run au PREMIER PLAN** (terminal, `nice 0`). Un lancement
    détaché (`nohup … & disown`) hérite d'une priorité basse : à ce niveau,
    n'importe quel démon le double.
- **LE CHRONOMÈTRE S'ARRÊTAIT PENDANT LA VEILLE (2026-08-25).** `time.monotonic()`
  ne compte pas le sommeil système sur macOS, `time.time()` si — et le budget de
  scène est du temps de MUR : le compteur du deck tourne pendant que le public
  attend. Un run annonçait 374 s de calcul pour 2682 s réelles, et la métrique
  disait que tout allait bien. Les deux horloges sont désormais relevées, l'écart
  est au frontmatter (`veille_s`), et au-delà de 30 s le run se signale comme
  NON COMPARABLE.
  * ⚠ **`caffeinate -is` NE SUFFIT PAS sur batterie** : le « Maintenance Sleep »
    passe outre. 737 s de veille mesurées pendant un rejeu sous caffeinate.
    **Machine branchée pour toute mesure qui compte.**
- **`BG_NICE` DE ZSH MET LES JOBS D'ARRIÈRE-PLAN À NICE 5 (2026-08-25).** C'est
  le mécanisme exact derrière « lancer le run au premier plan » : à ce niveau,
  n'importe quel démon d'entretien double le processus de génération.
  `unsetopt BG_NICE` avant tout lancement détaché, et vérifier avec
  `ps -o ni= -p $$`.
- **`python … | tee` REND LE CODE DE `tee`.** Sans `set -o pipefail`, un
  abandon-sur-échec ne se déclenche jamais : une série a enchaîné trois runs
  vides en deux secondes en croyant les avoir joués.
- **EN SÉRIE, LE SUCCÈS DU RUN N BLOQUE LE RUN N+1.** Le préflight a été conçu
  pour UN run sur machine fraîche ; le run précédent laisse nemo chaud (13 GB) et
  le garde du swap refuse le suivant. Décharger les modèles ET attendre un
  préflight vert AVANT CHAQUE RUN, pas une seule fois au début.
- **LE GARDE DU SWAP NE POUVAIT PAS REDEVENIR VERT (2026-08-25).**
  `free = total - used`, et macOS dimensionne `total` juste au-dessus de `used` :
  `free < 2 GB` est l'état stationnaire normal, pas un symptôme. Le garde mesure
  désormais ce que la règle NOMME — le débit de pageouts. Un swap consommé mais
  froid est de la mémoire que personne ne relit.
- **~~UN RUN PAR DÉMARRAGE~~ — RÉVISÉ LE 2026-08-09, LA RÈGLE ÉTAIT FAUSSE.**
  On lisait ici que « le swap ne se rend pas à chaud ». Mesuré, sans autre
  intervention que l'expiration de `keep_alive` d'Ollama : mémoire libre
  **11 % → 87 %**, swap `used` **−1,35 GB**, et `total` **4096 → 3072 MB**.
  macOS rend les pages ET rétrécit les swapfiles dès que le consommateur lâche
  la mémoire. Décharger le modèle suffit ; redémarrer était un rituel.
  * Pire, le blocage était un PROXY de deux causes déjà mesurées ailleurs, et
    le dossier le disait déjà : les kernel panics venaient d'un **disque à 99 %**
    (couvert par `MIN_DISK_GB`), les trous de 5 à 18 minutes de
    **`mediaanalysisd`** (couvert par `NOISY_DAEMONS`, et explicitement
    disculpés du swap par le run 4, reproduit swap à zéro). Il coûtait un
    redémarrage par session de test sans apporter un signal propre.
  * Ce qui restait vrai, et qui est conservé : une machine qui vit sur son swap
    ne donne pas des DURÉES fiables. D'où `preflight(chrono=True)` — bloquant
    pour `run_chapter.py` et l'API, où le chiffre est l'objet ; simple
    avertissement pour l'outillage de calibration, qui juge de la prose.
  * Remède, dans l'ordre : `ollama stop <modèle>`, puis `sudo purge` si besoin.
    Redémarrer en dernier recours.
  * Leçon de méthode, la même qu'au run 4 : un seuil qui corrèle n'est pas un
    seuil qui cause. Avant d'imposer un rituel, vérifier que le signal bloquant
    n'est pas déjà couvert par un signal direct.
- **Sessions de roleplay REJOUABLES (2026-08-08)** — le fichier de session porte
  désormais DEUX sections : `## Ce qui s'est dit` (le résumé glissant, c'est lui
  qui est indexé et qui nourrit les sessions suivantes) et `## Transcription`
  (les échanges verbatim, c'est elle qu'on rejoue sur scène). Élaguer une
  réplique ratée dans la transcription ne touche pas à la mémoire du personnage.
  Nécessaire parce que **les sessions sont pré-générées pour la scène** : la
  mémoire seule ne dit pas ce que le personnage a DIT.
  * `GET /sessions?character=` et `GET /session/<perso>/<horodatage>` ; la page
    a un sélecteur « rejouer » qui déroule l'échange **sans toucher au modèle**
    (zéro latence, zéro sortie de personnage en direct, et ça marche pendant
    qu'un chapitre se génère).
  * Identifiants filtrés par LISTE BLANCHE avant de toucher un chemin de
    fichier — ce serveur écoute sur le réseau d'une conférence. Cinq tentatives
    de traversée (`../`, `..%2f`, `%2e%2e`) rejetées en 400 par le serveur
    lui-même, vérifié avec `curl --path-as-is` pour ne pas mesurer la
    normalisation du client.
  * `POST /chat {"session": id, "close": true}` écrit et indexe ; la purge
    d'inactivité ferme aussi (une session qui s'évapore sans trace, c'est un
    contenu de démo perdu).
- **TICS DE JEU RÉSIDUELS : c'est la CURATION qui les traite, pas le prompt.**
  Chaque consigne ajoutée déplace le défaut ailleurs — mesuré en séquence :
  répliques préfixées du nom du personnage (« Kael : Ah… ») → corrigé au code ;
  recopie quasi verbatim de la réplique précédente (similarité 0,55) → consigne
  anti-répétition, tombée à 0,05 ; le personnage appelait son interlocuteur
  « Élara » → consigne « tu ne le connais pas », d'où un « cher inconnu » à
  chaque tour ; reformulée, et il s'interpelle maintenant lui-même à la
  troisième personne. Les sessions étant pré-générées et éditables à la main,
  la curation est le bon outil. Le garde-fou dans le CODE reste réservé à ce qui
  est inacceptable en toutes circonstances : la sortie de personnage.
- **`Session` ne validait pas la fiche à la construction (2026-08-08).** Elle ne
  lisait la bible qu'au premier `say()`. Conséquences trouvées en testant
  l'API : un personnage inconnu rendait `503` (« la machine a un problème »)
  au lieu de `404` (« ce personnage n'existe pas »), et le `except ValueError`
  de `chat_character.py` — écrit en supposant l'inverse — ne se déclenchait
  jamais. Corrigé : la fiche est lue et validée dans `__init__`.
- **LE PROMPT NE SUFFIT PAS À TENIR UN PERSONNAGE (2026-08-07).** Premier test
  du mode acteur, avec des interdits explicites et nommés dans le prompt système
  (« tu ne mentionnes jamais l'intelligence artificielle, un modèle, un
  prompt ») : nemo a répondu **« je suis simplement un programme informatique
  conçu pour simuler des conversations »** à trois questions de provocation sur
  sept. Deux enseignements et un piège :
  * Ma propre consigne ouvrait la porte : « tu ne comprends pas la question et
    tu le dis à ta manière » invite littéralement « je ne comprends pas cette
    question », qui est l'amorce du registre assistant. Les tournures
    d'assistant sont maintenant interdites NOMMÉMENT.
  * Le remède qui marche est le même que partout ailleurs ici : un garde-fou
    dans le CODE. `hors_role()` détecte les marqueurs, `say()` relance UNE fois
    en citant la faute au modèle, et une réplique encore fautive est rendue à
    l'écran mais **exclue de la mémoire**. Résultat : zéro sortie de personnage
    sur les mêmes provocations.
  * **Le piège, c'est la mémoire.** Au premier test, le résumé glissant a
    enregistré l'aveu (« car elle est une intelligence artificielle ») et
    l'aurait rechargé à chaque session suivante : une sortie de rôle non filtrée
    ne fait pas un incident, elle fait une CROYANCE persistante du personnage.
  * Donner des exemples de répliques les fait RECOPIER mot pour mot (deux
    spectateurs posant la même question obtenaient la même ligne scriptée) : les
    exemples sont désormais formulés comme des attitudes, pas comme du texte.
  * Limites qui restent : le modèle ne comprend pas vraiment un anachronisme, il
    improvise autour ; et il lui arrive de prononcer le mot inconnu
    (« je n'ai que faire des smartphones »). Le personnage tient, sa
    compréhension est approximative.
- **Le lint doit s'appliquer AUSSI au plan**, pas seulement à la prose (leçon
  du run 2 : le token collé `maisonly` est passé du plan au brief de la scène 4,
  donc au prompt d'écriture). La réparation par Qwen n'arrive qu'en fin de
  pipeline : bien trop tard pour un brief. Corrigé — ne pas régresser.
- **Ne jamais conclure sur un seul run.** « Zéro fuite d'anglais » au run 1
  m'a fait écrire que `num_ctx=4096` expliquait les fuites ; le run 2 en a
  produit trois. Deux tirages d'un modèle à température 0,7 ne prouvent pas la
  même chose qu'un protocole.
- **Marge de temps resserrée** : 20,2 min sur les 25 au run 2, contre 14,6 au
  run 1. Le facteur dominant est le nombre de scènes retenues par le plan
  (4 contre 3), pas la QA. **Arbitrage du propriétaire (2026-08-06) : on RESTE
  sur 3-4 scènes** — trois scènes risquent de faire court, et le vrai juge sera
  la répétition en conditions réelles. À mesurer là, pas à corriger par le
  prompt.
- Le rapport de lint mélangeait les alertes d'écriture/relecture (état AVANT
  réparation) avec ce qui subsiste réellement. Corrigé dans `run_chapter.py` —
  ne pas régresser : sur scène, une alerte périmée se lit comme une panne.
- Sortie de `run_chapter.py` bufferisée dès qu'on redirige (`> run.log`) : le
  log reste à 0 octet pendant les 15 minutes de génération. Lancer avec
  `python -u` pour suivre en direct — et c'est le vrai sujet de l'habillage
  démo (progression du graphe, compte à rebours).

- `host.containers.internal` peut nécessiter `--add-host=...:host-gateway`
  selon la version de Podman. Inutile ici : podman 5.7.1 le résout tout seul
  vers gvproxy (`192.168.127.254`), vérifié sur cette machine.
- Le chemin de persistance de l'image ChromaDB varie selon les versions
  (`/data` vs `/chroma/chroma`) — vérifier que les données survivent à un
  restart.
- Budget temps de la démo : profiler tôt la génération complète d'un
  chapitre sur la machine de scène. C'est LA contrainte dure du projet.
- **Stabilité machine — ÉLUCIDÉ (2026-08-06).** Les crashes en session de
  tests étaient des kernel panics `watchdog timeout: no checkins from
  watchdogd in 91 seconds`. Cause racine : **disque à 99 % (6 GB libres)**,
  donc macOS incapable d'agrandir le swap (`13 swapfiles and LOW swap space`
  dans le paniclog) sous la pression d'un modèle de 13 GB sur 18 GB unifiés.
  Le pageout stalle, watchdogd n'est plus ordonnancé, panic. Ce n'est ni
  thermique ni un bug Ollama. Correctifs appliqués :
  * Purge disque : 9 GB → 127 GB libres (LM Studio 52 GB supprimé, cache
    HuggingFace 18 GB, 5 modèles Ollama inutilisés 54 GB). `~/.ollama` = 31 GB,
    strictement les 4 modèles du projet.
  * `orchestrator/preflight.py` : refuse de démarrer si disque < 20 GB, si le
    swap est saturé, ou si 2+ LLM sont chauds simultanément (`/api/ps`). Il
    rapporte aussi la RAM libre (`vm_stat`, pages free + speculative — pas
    « inactive », dont la récupération suppose justement de la pagination), en
    avertissement seulement : un modèle légitimement chaud fait chuter ce
    chiffre. Branché dans `run_chapter.py`, contournable par `--skip-preflight`
    (dev only). Deux subtilités apprises à l'usage : (i) après un redémarrage
    macOS n'a alloué AUCUN swapfile, `total = free = 0` — ne regarder que
    `free` faisait conclure « swap saturé, redémarrez » juste après un
    redémarrage, d'où la lecture de `total` autant que `free` ; (ii) **un swap
    saturé est bloquant même avec du disque libre** — voir la leçon du run 3
    ci-dessous, j'avais d'abord raisonné le contraire.
  * `scripts/local.ollama.plist` : agent launchd du projet, remplace
    `brew services`. Fixe `OLLAMA_MAX_LOADED_MODELS=2` (sans quoi Ollama
    autorise 3 modèles chauds = 27+ GB demandés) et `OLLAMA_NUM_PARALLEL=1`.
  * Fait (2026-08-06, 12 h) : redémarrage effectué (swap remis à zéro), agent
    launchd installé et vérifié (`launchctl print gui/501/local.ollama` montre
    bien les cinq variables), `brew services` désactivé. Préflight vert :
    217 GB libres, aucun swapfile, aucun LLM chaud.
  * Le ménage disque a emporté `orchestrator/.venv` : il se recrée en une
    minute (`python3 -m venv orchestrator/.venv` + `pip install -r
    orchestrator/requirements.txt`). Le volume `data/chromadb` a survécu
    (collection `bible`, 8 chunks), le conteneur se rallume par
    `podman start stackfictionalwriting_chromadb_1`.
- **`num_ctx` était implicite à 4096** (`llm.py` ne le passait pas). Or un
  appel d'écriture pèse 2-3k tokens de prompt + 1400 générés → jusqu'à 4400.
  Au dépassement, Ollama fait GLISSER la fenêtre et ampute le DÉBUT du prompt
  système, c'est-à-dire `FRENCH_GUARD` puis les faits de la bible — sans
  aucune erreur. **Piste sérieuse pour les fuites d'anglais et les ratés de
  cohérence attribués à nemo.** Corrigé : `NUM_CTX=8192` explicite.
  À VÉRIFIER au prochain run : si les fuites disparaissent, la conclusion
  « nemo leake » du benchmark est à réviser.
  * ⚠ `ctx_fill` (= `prompt_eval_count / num_ctx`) **ne peut pas** servir
    d'alarme : Ollama tronque PUIS ne rapporte que ce qu'il a évalué, donc le
    ratio est plafonné à 1 par construction. Vérifié : prompt de ~3800 tokens
    envoyé avec `num_ctx=512` → `prompt_eval_count: 258`, `ctx_fill 0.54`.
    Les deux signaux fiables, désormais dans les métriques : `ctx_need`
    (estimation client du prompt + `num_predict`, sur `num_ctx`) et
    `ctx_truncated` (Ollama dit avoir lu < 75 % de ce qu'on a envoyé).
- **Déchargement de nemo au passage écriture → QA** (`llm.unload()`, appelé
  par `repair_node`). `OLLAMA_MAX_LOADED_MODELS=2` AUTORISE nemo (13 GB) +
  Qwen (4,8 GB) chauds ensemble = 17,8 GB sur 19,3 GB : la limite compte les
  modèles, pas les gigaoctets, et 2 modèles suffisent à recréer la pression
  qui a fait paniquer la machine. nemo n'a plus rien à produire à ce stade.
- Après un `brew services start ollama`, le plist est régénéré : les vars
  ajoutées manuellement sautent (bind repasse à 127.0.0.1). C'est la raison
  d'être de `scripts/local.ollama.plist` — ne pas revenir à `brew services`.

## Style de travail du propriétaire

Challenger les propositions plutôt qu'acquiescer. Expliquer les *pourquoi*
architecturaux. Pas de listes à puces gratuites dans la prose. Le contenu
littéraire est en français ; le code et ses commentaires aussi.
