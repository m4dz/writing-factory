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
  MacBook Apple Silicon. État actuel : pipeline à ~12-19 min → on passe
  encore, mais la marge s'est resserrée, à surveiller (les mentions « / 35 min »
  ailleurs dans ce fichier sont historiques).
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

## État actuel

- [x] Structure du projet, template personnage 7 chunks
- [x] podman-compose : ChromaDB (port 8000) + indexeur (profil tools)
- [x] Indexeur idempotent testé (parsing/chunking validés hors connexion)
- [x] query_test.py pour valider le retrieval
- [x] Validation sur machine réelle (Ollama 127.0.0.1:11434 + ChromaDB) :
      connectivité conteneur→Ollama OK sans `--add-host`, embeddings 768d,
      index/query/purge/persistance validés. Bug purge sur bible vide corrigé.
- [~] Peupler le premier personnage principal : fiches SCAFFOLD temporaires
      (Élara, Kael, forge, scène) dans `bible/`, marquées à remplacer par le
      canon issu de la conversation littéraire dédiée.
- [x] Modèle auteur tranché : mistral-nemo Q8_0 (benchmark, cf. section Modèles).
- [x] Orchestrateur LangGraph (mode auteur) : `orchestrator/`, pipeline
      plan → écriture (boucle) → relecture → réparation → cohérence, RAG
      dynamique assemblé à la requête. Bout-en-bout, chapitre 4-5 scènes en
      ~12-19 min (marge large sur les 35 min). Répétition, écho RAG et
      troncature réglés.
- [x] Modèle QA/lint tranché : **Qwen 2.5 7B** (benchmark, cf. section Modèles),
      phase POST-génération (swap nemo→Qwen unique, ~26 tok/s).
      * `repair()` : réécrit les fuites d'anglais de nemo → VALIDÉ, lint propre.
      * cohérence par faits : VALIDÉ sur fixture (protocole faits → questions
        de violation → réponses par scène, cf. Notes d'architecture). ~21 s
        pour 5 faits × 4 scènes.
- [x] **Run bout-en-bout post-correctifs (2026-08-06, 12 h 15)** : machine
      redémarrée, agent launchd en place, `NUM_CTX=8192`. Chapitre 3 scènes,
      17 appels, 8855 tokens, **877 s (14,6 min)** — sous les 25 min. Aucun
      `ctx_truncated`, aucun `done_reason: length`, `ctx_need` plafonne à 0,60 :
      la fenêtre de 8192 est confortable, la troncature silencieuse est bien
      éteinte. Zéro fuite d'anglais sur CE tirage — mais le run suivant en a
      produit trois (`of`, `the`, `sentantProbablement`) : `num_ctx` n'était
      donc PAS la cause des fuites, nemo leake bel et bien, et c'est la
      réparation par Qwen qui tient la ligne (texte final propre dans les deux
      cas). Ne pas conclure sur un tirage unique. Un seul défaut de génération
      (token collé
      `confessionUnexpected`), réparé par Qwen. Cohérence : 4 faits tenus,
      3 signalements tous écartés par le contre-appel ou la vérification de
      citation — aucun faux positif n'est passé. Mémoire : nemo 13,1 GB +
      embed 0,4 GB chauds pendant l'écriture, `unload()` confirmé au passage
      QA (Qwen 4,8 GB seul). Swap monté à 8 GB alloués / 600 MB libres sans
      incident, disque à 217 GB : aucune panique.
- [x] **Faits de la bible en CONTRAINTE du plan (2026-08-06, 13 h).** Le nœud
      de plan dérive d'abord les invariants (Qwen), planifie sous contrainte
      explicite (nemo), puis le plan est confronté aux faits AVANT d'écrire —
      même protocole que la cohérence (faits → questions de violation →
      lecture), appliqué à quatre lignes : ~13 s. Une replanification au plus
      (`MAX_PLAN_ATTEMPTS = 2`), au-delà on écrit quand même en signalant.
      Les faits dérivés une seule fois sont réutilisés par le rapport final :
      mêmes invariants pour contraindre et pour juger.
      * Validé en test ciblé : le plan fautif du run précédent (« Élara
        découvre les détournements ») est attrapé, un plan propre passe.
      * Validé en run complet : la première tentative a été REFUSÉE, la
        seconde est passée, le chapitre final tient les 5 faits. Le dispositif
        a donc travaillé pour de vrai, pas seulement en test.
      * Coût : ~2 min (dérivation 16 s, vérification 13 s, et surtout un
        rechargement de nemo à la replanification) contre 14 s avant.
      * **Run 2 : 1212 s (20,2 min) pour 4 scènes, 31 appels.** La marge sur
        les 25 min tombe à ~5 min, et c'est le PLAN À 4 SCÈNES qui coûte, pas
        la vérification (~4 min de rédaction/relecture/QA supplémentaires).
        Pour la scène, imposer 3 scènes plutôt que « 3 ou 4 » est le levier
        évident.
- [x] **Amputation par `num_predict` traitée (2026-08-06, 14 h).** Constat :
      l'écriture de la scène 3 du run 2 a fini en `length` (1400/1400), coupée
      en plein mot ; la relecture a travaillé sur un texte tronqué et la scène
      suivante a hérité d'un état narratif inachevé. Ollama ne signale rien
      d'autre que `done_reason: "length"`.
      * **Monter `num_predict` a été écarté** : un modèle qui n'a pas fini à
        1400 tokens ne finira pas davantage à 1800, il occupe l'espace offert.
        Ça déplace le plafond sans supprimer le cas.
      * **Retenu : continuation (une au plus) + coupe propre en filet**
        (`_generate_whole` dans `graph.py`). On renvoie la queue du texte avec
        consigne de terminer, on recolle ; si le modèle dépasse encore, on
        tronque à la dernière phrase complète (`trim_to_sentence`) plutôt que
        de laisser un mot coupé. Le filet n'est jamais le premier recours : il
        rend une scène sans l'état final que le plan lui demandait.
      * Coût : un appel seulement quand le cas se produit (~50-70 s mesurés).
        Le chemin normal est inchangé.
      * Deux pièges du recollement, trouvés au test et corrigés : le modèle
        reprend souvent par une phrase NEUVE au lieu de finir la précédente
        (« …dans un coin de la pièce Elle s'en approcha ») — on ferme le
        fragment orphelin, par des points de suspension devant une réplique
        (« Il hésita, puis… / — Tu mens ») et par un point devant une majuscule
        ordinaire ; et il recopie parfois toute la queue, dont il faut retirer
        le chevauchement AU CARACTÈRE près (un pas plus grossier laisse un
        résidu au milieu du texte).
      * Piège de typographie : la fin de phrase française admet une espace
        avant le guillemet fermant (« Va-t'en. »). L'oublier faisait classer un
        dialogue correctement terminé comme une phrase en cours.
- [ ] Mode acteur (roleplay) + mémoire conversationnelle rolling summary
- [ ] Intégration frontend (OpenWebUI via pipelines, ou interface dédiée —
      non tranché)
- [ ] Habillage démo : compte à rebours, affichage de la progression

## Prochaine étape convenue

Cohérence réglée, puis contrainte du plan par les faits (2026-08-06).
Chantiers restants, par ordre d'urgence pour la scène :

1. **Mode acteur (roleplay)** + mémoire conversationnelle à deux niveaux
   (N derniers échanges + rolling summary indexé, taggé par personnage).
2. **Habillage démo** : compte à rebours, affichage de progression du graphe.
3. **Frontend** (OpenWebUI via pipelines ou interface dédiée — non tranché).
4. **Peupler le canon** : remplacer les fiches SCAFFOLD par les fiches réelles.
5. **Stabilité machine** (crashes pendant les runs) — cf. Points de vigilance ;
   c'est le vrai risque jour J, un backend qui tombe à la 12ᵉ minute.

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

## Points de vigilance connus

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
  * `orchestrator/preflight.py` : refuse de démarrer si disque < 20 GB, si 2+
    LLM sont chauds simultanément (`/api/ps`), ou si le swap est saturé ET le
    disque sous 40 GB. Branché dans `run_chapter.py`, contournable par
    `--skip-preflight` (dev only). Deux subtilités apprises à l'usage :
    (i) un swap saturé n'est mortel que si le disque ne permet plus de
    l'agrandir — c'est la CONJONCTION qui a fait paniquer la machine, donc la
    saturation seule n'est qu'un avertissement ; (ii) après un redémarrage
    macOS n'a alloué AUCUN swapfile, `total = free = 0` — ne regarder que
    `free` faisait conclure « swap saturé, redémarrez » juste après un
    redémarrage. On lit donc `total` autant que `free`.
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
