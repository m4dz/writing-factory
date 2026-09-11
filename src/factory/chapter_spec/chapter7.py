#!/usr/bin/env python3
"""Spécification du CHAPITRE 7 — source unique, partagée serveur/outillage.

Ce module PORTE la structure du chapitre 7 de « L'Involontaire » : deux entrées
du carnet le même jour (anniversaire), l'entrée 1 en deux phrases sans citation,
l'entrée 2 ancrée sur [CIT-2] et servie en trois beats bornés, chute posée par le
code (« Constat : anniversaire. »).

Extrait de `outillage/run_s4.py` le 2026-09-02 pour que le chemin LIVE de la
keynote (`orchestrator/api.py` → `POST /generate`) construise EXACTEMENT le même
état que le driver de calibration. Avant : la structure vivait dans un CLI de
calibration et l'API produisait une fantasy de démonstration ; les deux ont une
seule vérité désormais.

`etat_ch7()` rend le dict d'état passé à `graph.invoke` ; `MARQUEURS_CH7` porte
les paramètres d'assemblage (`chapitre.assembler`) propres au chapitre — bascule
sur le 2e en-tête daté, audio borné sur la chute.

⚠ FIREWALL : `mouvement()` lit `bible/profond/mouvements-chapitres.md` (PROFOND)
et n'en extrait QUE la ligne du chapitre en cours ; `brief_chapitre_7()` lit le
brief et retire toute mention de fichier de bible (assert anti-fuite). Tout cela
est du matériau de PROMPT (server-side), jamais servi à `/chapter`.
"""

import re

# Racine du projet : ch7.py vit dans orchestrator/, donc parent.parent == racine
# (même valeur que le RACINE de run_s4.py, qui part d'outillage/).
from factory.paths import REPO_ROOT as RACINE

# doc_id de la fiche narratrice (cf. bible/fiche-judith.md, `doc_id: judith`).
# Partagé : run_s4.py l'importe pour TOUS ses étages, pas seulement le ch. 7.
NARRATOR = ["judith"]


# --- CHAPITRE 7 — la répétition en conditions réelles ------------------------
#
# Le brief machine est LU dans `chapters/07-anniversaire/brief.md` (§3), jamais recopié
# ici : un brief modifié ne doit pas avoir deux vérités. C'est la règle posée en
# tête de ce fichier pour les briefs de session, et elle vaut d'autant plus pour
# celui qui part sur scène.
BRIEF_CH7_FILE = RACINE / "chapters" / "07-anniversaire" / "brief.md"

# La traduction en langue du monde du §5 du brief v2. Le contenu est le même,
# le destinataire change : le modèle, pas l'implémenteur.
SERVED_VETOS = (
    "Aucun nom propre, aucune marque. Aucun objet qui ne soit dans la maison. "
    "Les objets sont là, dans l'état de la fête — mais rien ne bouge de "
    "soi-même sous ses yeux : aucune présence, aucun autre dans la maison, "
    "personne qu'elle n'attende ; elle constate ce qu'elle trouve, elle ne "
    "surprend rien en train de se faire. Rien n'est entendu : aucun bruit, "
    "aucune sonnerie, aucun pas, aucun objet cassé — l'étrange se voit et se "
    "doute, il ne s'entend pas. Tu ne trouves chaque chose qu'une seule fois : "
    "quatre découvertes en tout, jamais reprises ni recomptées ; ne fais pas le "
    "tour de la maison. Elle ne raconte pas ce que l'autre a "
    "fait ou dit, ni pourquoi elle est partie : elle ne cherche pas la cause. "
    "La seule question est de savoir si ce n'est pas elle qui a tout mis en "
    "place sans s'en souvenir. Le mot du jour ne s'écrit qu'à la toute fin, "
    "une seule fois. Rien ne se résout, rien ne se console : pas de promesse "
    "au lendemain, pas d'adresse à personne. La voix ne cède pas — "
    "déclarative, tenue, pas de cri."
)

MOVEMENTS = RACINE / "bible" / "profond" / "mouvements-chapitres.md"
BRIEF_CH7_E2 = RACINE / "chapters" / "07-anniversaire" / "brief-entree-2.md"


def movement(chapter: int, entry: int | None = None) -> str:
    """La ligne « mouvement » d'UN chapitre — jamais le fichier.

    ⚠ `mouvements-chapitres.md` est PROFOND : ses lignes 9 à 11 énoncent la
    vérité de fin du roman. Servir le fichier entier au modèle auteur ferait
    exactement ce que tout le firewall existe pour empêcher.
    #
    On extrait donc la ligne du chapitre EN COURS, par son numéro — même
    discipline que `build_etat_narratif.lire_table()`, qui saute délibérément la
    colonne réelle. Le chapitre 7 a deux lignes, une par entrée.
    """
    if not MOVEMENTS.is_file():
        return ""
    target = f"{chapter} — entrée {entry}" if entry else str(chapter)
    for line in MOVEMENTS.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 2 and cells[1] == target:
            return cells[2]
    return ""


def brief_entry2_v2() -> dict:
    """Le brief v2 de l'entrée 2, découpé en ses quatre blocs de service.

    Le fichier est la vérité : on le LIT, on ne le recopie pas. Un brief
    modifié ne doit pas avoir deux versions — la règle vaut depuis la session 4,
    et d'autant plus pour celui qui monte sur scène.
    """
    txt = BRIEF_CH7_E2.read_text(encoding="utf-8")

    def section(title: str, next_one: str) -> str:
        body = txt.split(title, 1)[1].split(next_one, 1)[0]
        return body.strip()

    def bullets(block: str) -> list[str]:
        return [l.lstrip("- ").strip() for l in block.splitlines()
                if l.strip().startswith("-")]

    drift = section("## 4. Glissement", "## 5.")
    drift_text = next((l.lstrip("> ").strip() for l in drift.splitlines()
                       if l.strip().startswith(">")), "")
    position = next((l.split(":", 1)[1].strip() for l in drift.splitlines()
                     if l.startswith("Position")), "")

    def beats() -> list[str]:
        # Le §7 porte les libellés des trois beats du cap-code (v5). Le corps de
        # chaque beat est le paragraphe qui SUIT sa ligne de titre. Beat C court
        # jusqu'à la fin du fichier — il n'a pas de section suivante.
        if "## 7." not in txt:
            return []
        seg7 = txt.split("## 7.", 1)[1]

        def body(block: str) -> str:
            lines = [l for l in block.strip().splitlines() if l.strip()]
            # La première ligne non vide est le reste du titre (« — la relève »).
            return " ".join(lines[1:]).strip() if len(lines) > 1 else ""

        a = (seg7.split("### Beat A", 1)[1].split("### Beat B", 1)[0]
             if "### Beat A" in seg7 else "")
        b = (seg7.split("### Beat B", 1)[1].split("### Beat C", 1)[0]
             if "### Beat B" in seg7 else "")
        c = seg7.split("### Beat C", 1)[1] if "### Beat C" in seg7 else ""
        return [body(a), body(b), body(c)]

    return {
        "beats": beats(),
        "intention": section("## 1. Intention", "## 2."),
        "trajectoire": bullets(section("## 2. Trajectoire", "## 3.")),
        "matiere": bullets(section("## 3. Matière disponible", "## 4.")),
        # LES VÉTOS NE SONT PAS SERVIS TELS QUELS. Le §5 est écrit pour
        # l'implémenteur : il nomme L1, L2, L3, la table, le code, les lints.
        # Servi verbatim, il apprend au modèle l'existence de nos contrôles —
        # et la session 6 a mesuré ce que coûte un mot d'atelier dans un
        # contexte servi (« Couperet : » sorti en texte).
        #
        # Ce qui est servi est ce que le TEXTE ne doit pas faire, en langue du
        # monde. Le reste — quel lint, quel seuil, qui possède quoi — reste ici.
        "vetos": SERVED_VETOS,
        "glissement": {"texte": drift_text, "position": position},
    }


# [CIT-2] — l'ancre de l'entrée 2, verbatim du brief. Elle est POSÉE par le code
# en tête de l'entrée 2 seulement : l'entrée 1 ne cite pas, c'est la première
# entorse au rituel et le premier signal du chapitre.
QUOTE_2 = ("« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, "
         "exprès cette fois, et j'ai redit oui tout haut dans la cuisine. "
         "Je t'aime toujours. »")

# DEUX ENTRÉES DU MÊME JOUR. Le code dérive les dates par défaut (elles sont
# consécutives par construction depuis la session 5) ; ici le brief les impose
# identiques, et c'est le SECOND en-tête qui porte la bascule audio.
_B2 = brief_entry2_v2()

# Bornes CODE des beats d'entrée 2 (cap-code v5). num_predict et phrases_max
# sont du RÉGLAGE, pas du canon — les libellés vivent dans le brief §7. La
# borne en phrases est le vrai cap : v5 a prouvé que le budget de tokens seul
# n'arrête pas la litanie. (nom, num_predict, phrases_max)
_BEATS_CAPS = (("relève", 150, 4), ("découverte", 240, 5), ("doute", 150, 4))
CH7_E2_BEATS = [(name, npd, pmax, txt)
                for (name, npd, pmax), txt in zip(_BEATS_CAPS, _B2["beats"])]

ENTRIES_CH7 = [
    # L'après-midi : deux phrases, sans citation, sans découpage. Servir trois
    # segments à une entrée de deux phrases n'a aucun sens — et c'est l'entrée
    # que le locuteur lit à voix nue.
    {"jour": "Samedi", "numero": 14, "meteo": "Beau temps",
     "mots": (25, 60), "segments": False, "citation": "",
     # Ni accumulation ni glissement : deux phrases n'ont pas la place. Au
     # tirage précédent l'accumulation y a été épissée quand même, et l'entrée
     # est passée de deux phrases à 471 mots.
     "gestures": False,
     "mouvement": movement(7, 1),
     # MATIÈRE D'ENTRÉE 1 (v5). Servie seule, sans matière, l'entrée lue à voix
     # nue a rempli son vide par une voix spectrale (« j'ai entendu la voix de
     # ma compagne »). On lui donne sa matière : la résolution d'effacement.
     # Nommer les objets ici est VOULU — la liste d'effacement EST les deux
     # phrases.
     "matiere": [
         "Ce qu'elle a décidé cet après-midi : ce jour n'aura pas lieu, elle "
         "l'efface.",
         "Les gestes d'effacement, tenus en deux phrases : ranger les photos, "
         "supprimer la musique, ne pas sortir le plat des grandes occasions ; "
         "une journée ordinaire.",
     ],
     # Le véto qui tue la voix spectrale : l'après-midi, seule, rien ne lui
     # arrive — elle DÉCIDE, elle n'observe pas.
     "vetos": ("Elle est seule, l'après-midi, et rien ne lui arrive : aucune "
               "voix, aucun bruit, personne ; elle décide, elle n'observe "
               "pas. Le mot du jour ne s'écrit pas."),
     # BEST-OF-3 sur l'entrée lue à voix nue : le modèle dérive une fois sur
     # deux vers « ranger le cahier / le grenier » et l'effacement de
     # l'anniversaire (photos, musique, plat) tombe en phrase 3+, coupée. Le
     # scorer garde le variant dont les DEUX phrases servies nomment
     # l'effacement.
     "best_of": 3,
     "critere": "effacement-anniversaire",
     # BORNE EN PHRASES. La borne en mots avait divisé l'entrée par cinq sans
     # jamais compter les phrases : huit produites là où le brief en demande
     # deux, et c'est l'entrée que le locuteur lit à voix nue. Une contrainte de
     # scène se compte dans l'unité de la scène.
     "phrases_max": 2,
     "forme": {"accumulation": "absente", "verdict": "absent"}},
    # La nuit : l'entrée pleine, découpée, ancrée sur [CIT-2].
    {"jour": "Samedi", "numero": 14, "meteo": "Beau temps",
     # UN SEUL APPEL. Le découpage en trois a produit TROIS ARCS : chaque
     # segment recevait le brief entier — intention, trajectoire, les quatre
     # retours — avec un budget taillé pour un tiers, donc il tentait
     # d'accomplir tout le mouvement, débordait, se faisait relancer par la
     # continuation, et recommençait. La cuisine est jouée deux fois, le
     # cahier deux fois, et la présence apparaît là où le modèle doit conclure
     # une troisième fois une histoire déjà conclue.
     #
     # Mesuré : ouverture 77 s et fermeture 81 s (toutes deux en continuation)
     # contre 41 s pour la reconstruction, qui devait être « la partie la plus
     # longue, et de loin ».
     #
     # Le risque du découpage était la masse ; il ne s'applique pas ici —
     # l'entrée est sortie à 710 mots AVEC trois appels. On ne perd pas de la
     # masse en en retirant deux, on retire de la redite.
     # LEVIER 3 (v5) : cible abaissée 450-600 → 300-400. L'intériorité pure ne
     # tient pas 550 mots — le modèle pad par litanie (v4 : ~400 mots de boucle
     # « bruit dans le salon / j'ai trouvé »). Entrée courte et dense qui TIENT
     # bat une longue qui boucle. L'entrée 2 n'est PAS lue à voix nue (c'est
     # l'entrée 1), sa longueur est donc libre côté keynote.
     "mots": (300, 400), "segments": False, "citation": QUOTE_2,
     "gestures": True,
     # La capitulation lexicale, au mot près : le jour gagne en entrant dans
     # son vocabulaire. Manquée 3/3 par le modèle — le code la pose.
     "chute": "Constat : anniversaire.",
     # CAP-CODE STRUCTUREL (v5) : l'entrée 2 est servie en trois beats bornés,
     # pas d'un tenant. La présence de ce champ ROUTE `write_node` vers la
     # branche `beats`, qui court-circuite `_prompt_mouvement` (sinon chaque
     # beat recevrait le mouvement entier — les « trois arcs »). mouvement,
     # trajectoire, matiere, vetos restent présents : ils ne servent plus le
     # write, mais le glissement, la chute et la ligne de mouvement en aval.
     "beats": CH7_E2_BEATS,
     # LA MÉTHODE DU MOUVEMENT — tout vient du brief, lu, jamais recopié.
     "mouvement": movement(7, 2),
     "trajectoire": _B2["trajectoire"],
     "matiere": _B2["matiere"],
     "vetos": _B2["vetos"],
     "forme": {"accumulation": "autorisée", "verdict": "absent"},
     # Le glissement n'est PAS servi : il est écrit, le composeur l'insère.
     "glissement": _B2["glissement"]},
]

VERDICT_CH7 = "anniversaire"
OBJECTS_CH7 = ("les photos, la playlist, le plat des anniversaires, "
              "les deux couverts, le cahier")


def beats_chapter_7() -> list[str]:
    """Un beat PAR ENTRÉE, découpé dans le brief — jamais demandé au modèle.

    Le premier tirage a montré pourquoi : le nœud de plan n'a produit AUCUNE
    ligne numérotée sur ce brief (il est en prose formatée, pas en liste), il
    est retombé sur « le brief entier fait office de beat », et le code a
    dupliqué ce beat pour les deux entrées. Les deux entrées ont donc reçu la
    consigne décrivant LES DEUX — d'où une entrée 1 de 340 mots là où le brief
    en demande deux phrases, et c'est l'entrée que le locuteur lit à voix nue.

    Le brief porte lui-même son découpage (« **Entrée 1 — … **», « **Entrée
    2 — …** »). Quand la structure est donnée, on la LIT au lieu de la
    redemander : planifier ce qui est déjà écrit, c'est offrir au modèle
    l'occasion de le défaire.
    """
    brief = brief_chapter_7()
    parts = re.split(r"(?=\*\*Entrée \d)", brief)
    common = parts[0].strip()
    # La matière partagée (matériau, progression, chute, interdits) est collée à
    # la fin du dernier bloc d'entrée : elle vaut pour les deux.
    entries, queue = [], ""
    for block in parts[1:]:
        m = re.search(r"\n\*\*(?:Matériau|Progression|Chute|Interdits)", block)
        if m:
            queue = block[m.start():].strip()
            block = block[:m.start()]
        entries.append(block.strip())
    return [f"{common}\n\n{e}\n\n{queue}".strip() for e in entries]


def brief_chapter_7() -> str:
    """Le brief machine du chapitre 7, extrait du §3 du fichier de brief.

    On prend la citation en bloc (les lignes préfixées « > ») : c'est ce qui est
    projeté sur scène pendant la génération, et l'honnêteté du dispositif veut
    que le prompt servi SOIT le brief affiché.
    """
    txt = BRIEF_CH7_FILE.read_text(encoding="utf-8")
    body = txt.split("## 3. Brief machine", 1)[1].split("## 4.", 1)[0]
    lines = [l.lstrip("> ").rstrip() for l in body.splitlines()
              if l.startswith(">")]
    brief = "\n".join(l for l in lines if l).strip()

    # LE BRIEF NE NOMME AUCUNE SOURCE FIREWALLÉE. Trouvé au lint de l'archive :
    # le §3 dit « pré-écrite selon `fiche-romane.md` §1 » — une note de
    # fabrication, utile à l'humain qui a écrit l'ancre, et qui APPREND AU
    # MODÈLE AUTEUR qu'un fichier de la couche cachée existe.
    #
    # Le texte généré est resté propre, et le lint des noms propres garde la
    # sortie. Mais tout le firewall repose sur l'idée que l'auteur ignore
    # jusqu'à l'existence du profond : le lui nommer, c'est lui donner le fil.
    # Retiré au SERVICE, pas dans le brief — la note reste utile là où elle est.
    brief = re.sub(r",?\s*pré-écrite selon\s*`[^`]+`\s*§?\d*\s*:", " :", brief)
    brief = re.sub(r"\s*\(?\s*(?:cf\.|voir)\s*`?[\w-]+\.md`?[^)\n]*\)?", "",
                   brief)
    leaks = re.findall(r"`?\b[\w-]+\.md\b`?", brief)
    assert not leaks, (f"le brief servi nomme des fichiers de bible : {leaks} "
                        "— le modèle auteur ne doit pas savoir qu'ils existent")
    return brief


# Paramètres d'assemblage propres au chapitre 7, pour `chapitre.assembler` :
# la bascule audio se pose sur le SECOND en-tête daté (les deux entrées portent
# le même jour), et l'extrait audio est borné sur la chute imposée pour se
# terminer sur « Constat : anniversaire. » plutôt que sur un plafond de mots.
MARKERS_CH7 = {"on_second_header": True, "fall": "Constat : anniversaire."}


def ch7_state(seed: int | None = None) -> dict:
    """État complet passé à `graph.invoke` pour générer le chapitre 7.

    Reproduit VERBATIM la branche CH7 de `run_s4.py` (le dict d'état), pour que
    le chemin live et le driver de calibration convergent sur un seul chapitre.
    `graine` aléatoire par défaut (décision propriétaire 2026-09-02 : vraie
    variance live du best-of-3 de l'entrée 1 et du tirage du glissement).
    """
    import random

    return {
        "brief": brief_chapter_7(),
        "characters": NARRATOR,
        "rag": True,
        "expected_entries": len(ENTRIES_CH7),
        "entry_specs": ENTRIES_CH7,
        "imposed_plan": beats_chapter_7(),
        # L'ancre du ch. 7 est PAR ENTRÉE (l'entrée 1 ne cite pas) : elle vit
        # dans `entrees_spec`, pas dans le préfixe global.
        "prefix": "",
        "micro_nodes": True,
        "segments": True,
        "seed": seed if seed is not None else random.randrange(1, 10**6),
        # Le numéro de chapitre commande le SCOPE des interdits matériels et la
        # chute imposée de l'accumulation.
        "chapter": 7,
        "drawn_approaches": [],
        "start_day": "Samedi",
        "start_number": 14,
        "verdict": VERDICT_CH7,
        "active_objects": OBJECTS_CH7,
        "start_weather": "Beau temps",
        "accumulation": "",
    }
