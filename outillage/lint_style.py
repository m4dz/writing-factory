#!/usr/bin/env python3
"""Lint déterministe de la grille de style — SANS modèle.

Remplit mécaniquement une PARTIE de la grille de `_scene-test-style.md` et cite
ses preuves. Le reste est laissé vide : c'est le jugement du relecteur, et une
pré-évaluation approximative coûterait plus qu'elle ne rapporte (on irait durcir
un chunk de la fiche qui n'a rien fait).

Doctrine, prolongement de la leçon déjà acquise sur Qwen — « donner au petit
modèle une tâche de LECTURE, jamais d'INFÉRENCE ». Ici on descend d'un cran :
aucun modèle du tout, donc aucun faux positif d'inférence. Ce qui est
mécaniquement décidable est décidé ; ce qui demande de comprendre le texte est
rendu tel quel au relecteur.

Trois niveaux de certitude, et ils sont affichés :
  EXACT     — listes littérales tirées de la fiche, décision fiable.
  CANDIDAT  — heuristique, à confirmer à l'œil (passé simple).
  MANUEL    — non automatisable, laissé vide.

Le module ne MODIFIE jamais le texte : on mesure ce que le modèle produit, pas
ce qu'un post-filtre rattrape.

Usage :
  python3 outillage/lint_style.py runs/run-1.md
  python3 outillage/lint_style.py --etalons        # auto-test sur la fiche

Stdlib uniquement.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

# `orchestrator/` n'est pas installable : on l'ajoute au chemin pour réutiliser
# delint() plutôt que de recopier ses détecteurs. style.py n'importe que `re`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "orchestrator"))
from style import delint  # noqa: E402

# --- Seuils ------------------------------------------------------------------

# « Phrase d'accumulation » : proxy mesurable de la rupture signature de la
# fiche (« une seule phrase longue, construite en accumulation de propositions
# juxtaposées par des virgules »). Les deux seuils sont calibrés pour séparer
# l'étalon 2 (la cible) des trois autres étalons — c'est ce que vérifie
# `--etalons`. Baisser l'un des deux ferait passer des phrases ordinaires.
ACC_VIRGULES = 4
ACC_MOTS = 45

# « Phrase-couperet » : la fiche dit « trois à six mots ».
COUPERET_MIN, COUPERET_MAX = 3, 6

# --- Session 3 : contrôles L1-L4 du protocole de calibration ch. 2 ------------

# L3 reprend les seuils que la fiche v3 énonce elle-même (60 mots, 6 virgules),
# plus stricts que ceux calibrés en session 1 (45/4). Les deux coexistent : la
# ligne historique garde les sessions 1 et 2 comparables, L3 applique la règle
# écrite dans la fiche. Aligner les deux effacerait la comparaison.
L3_MOTS, L3_VIRGULES = 60, 6

# L4 : le glissement est le SEUL emploi autorisé des points de suspension. Le
# marqueur n'est comptable que parce qu'il est univoque — d'où la mesure de
# proximité avec le champ du départ plutôt qu'un simple comptage.
L4_FENETRE_MOTS = 15
CHAMP_DEPART = re.compile(
    r"\b(partie|parties|départ|departs|départs|absence|absente|quittée|quitté|"
    r"quitter|plus là|s'en est allée)\b",
    re.IGNORECASE,
)
SUSPENSION = re.compile(r"…|\.\.\.")

# L1 : une majuscule est un candidat NOM PROPRE si elle n'ouvre ni le texte, ni
# une phrase, ni une ligne. Heuristique assumée — le protocole demande zéro
# toléré, donc on signale large et on cite le contexte pour que la lecture
# tranche. `Je` est écarté : c'est un pronom, jamais un nom propre, et il
# apparaît capitalisé après une coupe de phrase que le découpage rate parfois.
L1_EXCEPTIONS = {"Je", "J", "L", "D", "C", "N", "S", "M", "T", "Y"}
MAJUSCULE = re.compile(r"\b([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ][\wàâäéèêëîïôöùûüç'’-]+)")

# Un en-tête d'entrée de journal : ligne courte portant une date. Sert au
# re-scope « par entrée » (D1) — sans lui, L3 et L4 compteraient sur le
# chapitre entier et un chapitre à deux entrées serait jugé comme un seul bloc.
# EN-TÊTE NORMALISÉ (notes d'outillage §1). Format canonique :
# « Jeudi 7. Beau temps. » — jour de semaine, numéro, point, météo, point.
# Jamais l'année.
#
# Il remplace l'heuristique de date de la session 3, et ce n'est pas une
# coquetterie : le MÊME repère sert à trois choses — le comptage d'entrées de
# L3, la validation de structure en grille, et le point de bascule de
# `lire_chapitre.py` (le second en-tête du chapitre 7). Un repère déterministe
# partagé vaut mieux que trois heuristiques qui divergent le jour J.
JOURS = r"Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche"
ENTETE_ENTREE = re.compile(
    rf"^\s*(?:\*{{0,2}})?({JOURS})\s+(\d{{1,2}})\.\s+.{{2,40}}\.\s*(?:\*{{0,2}})?$",
    re.MULTILINE,
)


# --- Listes littérales (source : chunk *Interdits* de style-auteur.md, --------
# --- complété par la grille du paquet test-style) ----------------------------

PASTICHE = re.compile(
    r"\b(indicible[s]?|innommable[s]?|abomination[s]?|t[ée]n[èe]bres|"
    r"insondable[s]?|ancestral(?:e|es|aux)?|effroi|"
    r"malaise\s+diffus)\b",
    re.IGNORECASE,
)

# Les variantes de TEMPS comptent autant que la formule : « je ne peux
# m'empêcher » a échappé au détecteur au run 3 de la session 3, qui n'attendait
# que l'imparfait (notes d'outillage §5). Un tic ne change pas de nature en
# changeant de conjugaison.
# La NÉGATION s'intercale, et le motif la ratait : B′C écrit « je ne peux PAS
# m'empêcher de penser ». Un adverbe de négation entre l'auxiliaire et le verbe
# suffisait à faire passer le tic — et c'est le deuxième run consécutif qu'il
# traverse (le run 3 de la session 3 l'avait déjà fait au présent).
TICS_IA = re.compile(
    r"(un m[ée]lange de\b|quelque chose en (?:moi|elle)\b|"
    r"(?:je|elle) ne (?:pouvais|pouvait|peux|peut|pourrais|pourrait)"
    r"(?: pas| plus| jamais)? [sm]'emp[êe]cher de\b|"
    r"une part de (?:moi|elle)\b|"
    r"c'(?:est|était) alors que (?:je|elle) (?:compris|comprit|sus|sut|"
    r"comprenais|comprends)\b|"
    r"ce fut alors que\b|il (?:y avait|y a) quelque chose de\b)",
    re.IGNORECASE,
)

# LE FORMULAIRE PAR PARAPHRASE. Bannir les méta-termes n'a pas tué le mode
# formulaire, il l'a fait muter : B′C écrit « Le coup de couteau est le
# suivant : » — « couperet » traduit en arme blanche pour contourner le lint.
# C'est la STRUCTURE qu'il faut attraper, pas le mot : annoncer ce qui suit au
# lieu de l'écrire est le geste du formulaire, quel que soit le nom du champ.
FORMULAIRE = re.compile(
    r"\b\w[^.!?\n]{0,60}\best (?:le|la|les) suivant(?:e|s|es)?\s*:",
    re.IGNORECASE,
)

# Incise adverbiale : « s'exclama-t-il nerveusement ». La fiche impose
# « dit-il », « a-t-elle répondu » et rien de plus.
#
# `je` est dans la liste des pronoms parce que la narration est à la PREMIÈRE
# personne : « ai-je répondu distraitement » est la forme que nemo produit
# réellement, et l'omettre laissait passer l'incise sur un run entier. Le mot
# intercalé optionnel couvre « ai-je répondu distraitement » (participe entre
# l'inversion et l'adverbe).
INCISE_ADVERBIALE = re.compile(
    r"-(?:t-)?(?:il|elle|on|je|ils|elles)\s+(?:\w+\s+)?\w+ment\b",
    re.IGNORECASE,
)

# Même interdit, contourné : nemo reformule l'adverbe en groupe prépositionnel
# (« a-t-elle répété d'un ton surpris », « a-t-elle dit d'une voix enjouée »).
# Trouvé à la relecture des runs, sur deux tirages que la grille avait marqués
# tenus. Un interdit formulé sur la CATÉGORIE grammaticale se contourne par un
# changement de catégorie ; c'est l'intention qu'il faut détecter.
# L'ancrage sur un VERBE DE PAROLE est obligatoire : sans lui, le motif attrape
# « J'ai refermé le cahier d'un geste sec », qui est de la narration ordinaire et
# que la fiche n'interdit nulle part. Trouvé sur le run 2 — et l'enjeu n'était pas
# cosmétique : cette croix de trop faisait passer l'incise de 1 run sur 3 (bruit)
# à 2 sur 3 (durcir la fiche), donc inversait le verdict.
INCISE_PREPOSITIONNELLE = re.compile(
    r"\b(?:dit|dis|dire|disant|r[ée]pond(?:it|u|re)|r[ée]p[ée]t(?:a|[ée])|"
    r"demand(?:a|[ée])|conclu[ts]?|lan[çc](?:a|[ée])|murmur(?:a|[ée])|"
    r"ajout(?:a|[ée])|repri[ts]|s'exclam(?:a|[ée])|soupir(?:a|[ée])|"
    r"souffl(?:a|[ée])|fit|questionn(?:a|[ée]))\b"
    r"[^.!?]{0,20}?"
    r"(?:d'un|d'une|sur un|sur une)\s+(?:ton|voix|air|sourire|souffle)\s+\w+",
    re.IGNORECASE,
)

# Élision manquante : « je te appelle » au lieu de « je t'appelle ». Défaut de
# français que `delint()` ne voit pas (il ne cherche que de l'anglais et des
# tokens collés). Les exclusions sont les mots devant lesquels le français NE
# fait PAS l'élision — `un/une` (le un, la une), les h aspirés, `onze`, `huit`,
# `oui`, `yacht`.
#
# LIMITE ASSUMÉE : l'autre forme du défaut, l'apostrophe avalée qui colle les
# mots (« jeté lemballage »), n'est PAS détectée. La reconnaître demanderait un
# lexique français pour savoir qu'« emballage » est un mot — sans dictionnaire,
# tout détecteur ici serait du bruit. Mieux vaut une ligne absente qu'une ligne
# fausse.
ELISION_MANQUANTE = re.compile(
    r"\b(je|me|te|se|le|la|ne|de|que|ce)\s+"
    r"(?!un\b|une\b|onze|huit|oui|yacht|yaourt|hasard|haut|haine|héros|"
    r"hibou|hall|hangar)"
    r"([aeiouéèêàâîôû]\w+)",
    re.IGNORECASE,
)

# Heure ou quantité exacte — la « précision maniaque » que la fiche réclame.
PRECISION = re.compile(
    r"\b\d{1,2}\s*h(?:\s*\d{2})?\b|"
    r"\b\d+[,.]?\d*\s*(?:heures?|minutes?|secondes?|jours?|"
    r"centim[èe]tres?|m[èe]tres?|kilom[èe]tres?|degr[ée]s?|euros?|"
    r"grammes?|litres?)\b|"
    r"\b(?:une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze)\s+"
    r"heures?(?:\s+\w+)?\b",
    re.IGNORECASE,
)

# --- Passé simple : formes NON AMBIGUËS seulement ----------------------------
# L'interdit n°1 de la fiche, et le plus coûteux à signaler à tort : un faux
# positif enverrait durcir un chunk qui va bien. On écarte donc délibérément
# `dit`, `vit`, `rit`, `suit`, `fuit` — qui sont AUSSI du présent — et les
# formes en `-ra` (futur simple).
PS_IRREGULIERS = re.compile(
    r"\b(fut|furent|eut|eurent|fis|fit|f[îi]mes|firent|"
    r"pris|prit|pr[îi]mes|prirent|reprit|reprirent|comprit|comprirent|"
    r"vins|vint|v[îi]nmes|vinrent|revint|revinrent|"
    r"pus|put|p[ûu]mes|purent|sus|sut|s[ûu]mes|surent|"
    r"mis|mit|m[îi]mes|mirent|remit|remirent|promit|promirent|"
    r"parut|parurent|tint|tinrent|dut|durent|voulut|voulurent|"
    r"crut|crurent|aper[çc]ut|aper[çc]urent|reconnut|reconnurent|"
    r"sentit|sentirent|ouvrit|ouvrirent|sortit|sortirent|"
    r"r[ée]pondit|r[ée]pondirent|assit|assirent|"
    r"all[âa]mes|allai|all[èe]rent)\b",
    re.IGNORECASE,
)
# `-èrent` n'existe qu'au passé simple : aucune autre forme française ne s'y
# termine. Détecteur sûr.
PS_ERENT = re.compile(r"\b\w+[èe]rent\b", re.IGNORECASE)

# `-irent` / `-urent` sont majoritairement du passé simple (partirent, sortirent,
# coururent), mais heurtent le PRÉSENT 3pl des verbes en -irer/-urer. La liste
# ci-dessous est cette collision, énumérée : sans elle, « ils murmurent » et
# « ils admirent » passeraient pour du passé simple. C'est le seul endroit du
# module où l'exhaustivité d'une liste conditionne la justesse — d'où le rendu
# en CANDIDATS et non en verdict.
PS_HOMONYMES_PRESENT = {
    "tirent", "attirent", "retirent", "étirent", "soutirent",
    "soupirent", "expirent", "respirent", "inspirent", "aspirent",
    "admirent", "chavirent", "virent", "délirent",
    "assurent", "rassurent", "murmurent", "susurrent", "procurent",
    "endurent", "mesurent", "figurent", "épurent", "saturent", "durent",
}
PS_IRENT_URENT = re.compile(r"\b\w+[iu]rent\b", re.IGNORECASE)

# Passé simple des verbes en -er, ancré sur un sujet pour éviter le bruit
# (« la », « déjà », « voilà »). `{3,}` écarte « il a » / « elle va » ;
# l'exclusion de `-ra` écarte le futur simple (« elle regardera »).
PS_ANCRE = re.compile(
    r"\b(?:il|elle|on|ils|elles)\s+((?!\w*ra\b)\w{3,}a)\b", re.IGNORECASE
)

# Collision participe passé / passé simple 1re-2e personne : « pris », « mis »,
# « compris » sont À LA FOIS le participe (« j'ai pris ») et le passé simple
# (« je pris »). Trouvé sur les runs réels — le mot sortait sur 3 tirages sur 4,
# toujours en passé COMPOSÉ, c'est-à-dire toujours à tort. Un auxiliaire juste
# devant tranche : c'est un participe, pas du passé simple.
PS_PARTICIPES_AMBIGUS = {"pris", "mis", "fis", "vins", "pus", "sus", "dus",
                         "appris", "compris", "remis", "repris", "promis"}
AUXILIAIRE = re.compile(
    r"\b(?:ai|as|a|avons|avez|ont|avais|avait|avions|aviez|avaient|"
    r"aurai|aura|aurait|eu|est|es|suis|sommes|êtes|sont|était|étais|"
    r"étaient|étions|serai|serait|soit|été)\s+(?:\w+\s+)?$",
    re.IGNORECASE,
)
# Première personne — la plus utile ici, la fiche imposant le « je ». La forme
# du passé simple (`je regardai`) ne diffère du futur (`je regarderai`) que par
# le `r` qui précède, et de l'imparfait (`je regardais`) que par le `s` final :
# d'où l'exclusion de `-rai` et l'ancrage strict sur `je ` (qui écarte `j'ai`).
PS_PREMIERE_PERSONNE = re.compile(
    r"\bje\s+((?!\w*rai\b)\w{3,}ai)\b", re.IGNORECASE
)
# Sujet nom propre + pronom objet élidé : « Élara l'écouta ». L'ancrage sur le
# PRONOM est ce qui rend le motif sûr — sans lui, « Le cinéma », « La véranda »
# ou « Un agenda » seraient signalés comme du passé simple, et un faux positif
# sur l'interdit n°1 enverrait durcir un chunk qui n'a rien fait.
PS_NOM_PROPRE = re.compile(
    r"\b[A-ZÉÈÀÂÎÔÛ]\w{2,}\s+(?:l'|lui\s|me\s|m'|se\s|s'|nous\s|vous\s|leur\s)"
    r"((?!\w*ra\b)\w{3,}a)\b"
)

# --- Découpage ---------------------------------------------------------------

_FIN_PHRASE = re.compile(r"[.!?…]+(?:\s*[»\"'])?")
_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'"})


def normalise(texte: str) -> str:
    """Apostrophes typographiques → ASCII, à longueur CONSTANTE.

    Les modèles alternent « l'entrée » et « l'entrée » selon les tirages ; sans
    cette normalisation, la moitié des motifs rateraient au hasard du run. La
    substitution est 1:1 en caractères, donc les positions restent valables pour
    citer le texte d'ORIGINE.
    """
    return texte.translate(_APOSTROPHES)


def strip_frontmatter(texte: str) -> str:
    lignes = texte.splitlines()
    if lignes and lignes[0].strip() == "---":
        for i, ligne in enumerate(lignes[1:], start=1):
            if ligne.strip() == "---":
                return "\n".join(lignes[i + 1:]).strip()
    return texte.strip()


def paragraphes(texte: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", texte) if p.strip()]


def phrases(texte: str) -> list[str]:
    """Découpe naïve en phrases. Suffit au COMPTAGE (longueur, virgules)."""
    out, debut = [], 0
    for m in _FIN_PHRASE.finditer(texte):
        bout = texte[debut:m.end()].strip()
        if bout:
            out.append(bout)
        debut = m.end()
    reste = texte[debut:].strip()
    if reste:
        out.append(reste)
    return out


def mots(phrase: str) -> int:
    return len([m for m in re.split(r"\s+", phrase.strip()) if m])


def sans_dialogue(texte: str) -> str:
    """Retire les répliques pour isoler la voix narrative.

    Trois formes à retirer. Les deux premières sont celles de la fiche : spans
    « … » et lignes de réplique ouvertes par un tiret cadratin. La troisième,
    les guillemets droits, n'est pas dans la fiche mais est ce que nemo produit
    en pratique (constaté au run 1) : sans elle, un « ! » de réplique serait
    compté comme un « point d'exclamation hors dialogue », c'est-à-dire un
    défaut inventé de toutes pièces. Le détecteur doit lire le texte tel qu'il
    sort, pas tel qu'on l'aurait voulu.
    """
    texte = re.sub(r"«.*?»", " ", texte, flags=re.DOTALL)
    texte = re.sub(r'"[^"\n]*"', " ", texte)      # guillemets droits, une ligne
    gardees = [l for l in texte.splitlines()
               if not re.match(r"^\s*[—–-]\s", l)]
    return "\n".join(gardees)


_ETALON_ACC: str | None = None


def etalon_accumulation(fiche: str = "bible/style-auteur.md") -> str:
    """L'accumulation de référence, lue dans la fiche (chargée une fois).

    Sert à détecter la RECOPIE. Chargée depuis la fiche plutôt que recopiée ici :
    l'étalon bougera avec la fiche, et un détecteur qui compare à une version
    périmée ne détecte plus rien.
    """
    global _ETALON_ACC
    if _ETALON_ACC is None:
        _ETALON_ACC = ""
        chemin = Path(fiche)
        if chemin.is_file():
            texte = normalise(chemin.read_text(encoding="utf-8"))
            # Retirer le balisage avant de découper : les étalons vivent dans
            # des blocs `> ` sous un titre en gras, et les garder collerait
            # « **Étalon 2 — …** » en tête de la phrase de référence.
            texte = re.sub(r"^\s*>\s?", "", texte, flags=re.MULTILINE)
            texte = re.sub(r"^\s*\*\*.*?\*\*\s*$", "", texte, flags=re.MULTILINE)
            candidats = [p for p in phrases(texte)
                         if p.count(",") >= ACC_VIRGULES and mots(p) >= ACC_MOTS]
            if candidats:
                _ETALON_ACC = max(candidats, key=mots).strip()
    return _ETALON_ACC


def recopie_etalon(phrase: str, seuil: float = 0.6) -> float:
    """Proximité d'une phrase avec l'accumulation étalon, entre 0 et 1.

    Née d'un échec de ce module : la boucle de renvoi a produit deux
    « réussites » qui étaient l'étalon copié CARACTÈRE POUR CARACTÈRE, dans une
    scène qui parlait d'autre chose (l'étalon raconte des clés, la scène une
    cafetière). Compter des virgules ne dit rien du sens — un détecteur de forme
    doit savoir dire quand la forme a été obtenue par plagiat.
    """
    ref = etalon_accumulation()
    if not ref or not phrase:
        return 0.0
    r = difflib.SequenceMatcher(None, phrase.lower(), ref.lower()).ratio()
    return r if r >= seuil else 0.0



# --- Session 5, item 7 : lints nouveaux --------------------------------------

# MÉTA-TERMES. Le vocabulaire de FABRICATION n'a rien à faire dans la prose :
# « Couperet : erreur de relevé. » est un formulaire rempli, pas une entrée
# écrite. Liste figée par le protocole. « constat » et « verdict » en sont
# volontairement ABSENTS : ce sont les mots de son métier de correctrice, donc
# sa langue — les bannir appauvrirait la voix qu'on cherche à obtenir.
META_TERMES = re.compile(
    r"\b(couperets?|squelettes?|beats?|ancres?|notation physiologique|"
    r"mat[ée]riaux?|briefs?)\b", re.IGNORECASE)

# ATTRACTEURS : formules vers lesquelles le modèle glisse tout seul, relevées à
# la lecture des runs. Ce ne sont pas des fautes de langue, ce sont des tics
# d'entraînement — et « Demain est un autre jour » a été entendu à l'oral.
ATTRACTEURS = re.compile(
    r"(demain est un autre jour|bou[ée]e|oc[ée]an)", re.IGNORECASE)

# « je décide de » : plafonné à UNE occurrence par entrée (arbitrage du
# 2026-08-18). B1 en portait quatre, chacune suivie de son exécution.
JE_DECIDE = re.compile(r"\bje d[ée]cide de\b", re.IGNORECASE)

# COUPLE DÉCISION-EXÉCUTION, en CANDIDAT non bloquant. La règle M3 dit que
# l'effet de « décision sans geste » vit dans le VIDE entre la décision notée et
# l'état constaté ensuite ; le couple le referme. Mais l'établir demande de
# comprendre le texte : on repère l'infinitif de la décision, on le cherche
# conjugué dans les phrases suivantes, et on SIGNALE. M3 reste la ligne manuelle
# qui tranche — un faux positif sur une ligne bloquante à l'étage C coûterait un
# run à tort.
_DECISION = re.compile(r"\bje d[ée]cide de\s+(?:l[ae]\s+|l'|les\s+)?(\w{4,})",
                       re.IGNORECASE)


def couples_decision_execution(texte: str) -> list[str]:
    """Décisions suivies de leur exécution apparente — CANDIDATS pour M3."""
    out, phr = [], phrases(texte)
    for i, p in enumerate(phr):
        m = _DECISION.search(p)
        if not m:
            continue
        radical = m.group(1)[:-2] if len(m.group(1)) > 6 else m.group(1)
        suite = " ".join(phr[i + 1:i + 4])
        if re.search(rf"\b(?:j'ai |je )\w*{re.escape(radical)}", suite, re.I):
            out.append(f"« {p.strip()[:70]}… » puis exécution : "
                       f"« {suite.strip()[:70]}… »")
    return out


def entetes_coherents(entetes: list[tuple[str, str]]) -> list[str]:
    """Séquence jour-de-semaine cohérente avec les numéros de jour.

    Deux en-têtes à un jour d'écart doivent avancer d'un jour de semaine. BC
    produisait « Vendredi 8 » puis « Jeudi 7 » : des dates qui reculent, dans un
    carnet tenu chaque soir.
    """
    ordre = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
             "Dimanche"]
    fautes = []
    for (j1, n1), (j2, n2) in zip(entetes, entetes[1:]):
        ecart_jour = (ordre.index(j2.capitalize()) - ordre.index(j1.capitalize())) % 7
        ecart_num = int(n2) - int(n1)
        if ecart_num <= 0:
            fautes.append(f"{j1} {n1} → {j2} {n2} : la date n'avance pas")
        elif ecart_num % 7 != ecart_jour:
            fautes.append(f"{j1} {n1} → {j2} {n2} : le jour de semaine ne suit "
                          f"pas l'écart de dates")
    return fautes


def entrees(texte: str) -> list[str]:
    """Découpe le texte en entrées de journal, sur les en-têtes datés.

    Rend `[texte]` si aucun en-tête n'est trouvé : un chapitre à une seule
    entrée non datée reste une entrée, et rendre une liste vide ferait passer
    tous les contrôles par entrée pour « rien à vérifier ».
    """
    marques = [m.start() for m in ENTETE_ENTREE.finditer(texte)]
    if not marques:
        return [texte]
    if marques[0] > 0:
        marques.insert(0, 0)          # matière avant la première date
    bornes = marques + [len(texte)]
    out = [texte[a:b].strip() for a, b in zip(bornes, bornes[1:])]
    return [e for e in out if e] or [texte]


def hors_guillemets(texte: str) -> str:
    """Retire le contenu cité, en gardant la longueur (donc les positions).

    Les lints de VOIX (tics d'IA, physiologie, état mental nommé, glissement)
    jugent la voix de la narratrice. Or ce qui est entre guillemets dans ce
    roman est le cahier — fabriqué à la main, et portant délibérément une AUTRE
    voix. Les y appliquer reviendrait à sanctionner la citation d'exister
    (notes d'outillage §7).

    Le contrat de prose, lui, s'applique partout, citations comprises : c'est
    la raison du remplacement par des espaces plutôt que d'une suppression —
    les deux couches lisent le même découpage, aux mêmes positions.
    """
    return re.sub(r"«[^»]*»|“[^”]*”",
                  lambda m: " " * len(m.group(0)), texte)


def dans_guillemets(texte: str) -> list[str]:
    """Les passages cités, pour ce qui doit s'y appliquer quand même."""
    return [m.group(0) for m in
            re.finditer(r"«[^»]*»|“[^”]*”", texte)]


# --- §3 et §4 : contraintes scopées par chapitre ------------------------------
#
# Les valeurs viennent de la table de pilotage de `chronologie-partie-double.md`.
# Ce fichier est FIREWALLÉ côté modèle — il n'est jamais indexé, jamais servi —
# mais l'outillage a le droit de le lire : un lint n'est pas un modèle, il ne
# raconte rien, il compare. C'est exactement la dissymétrie qu'on veut : la
# machine qui juge en sait plus que la machine qui écrit.

TABLE_PILOTAGE = "bible/profond/chronologie-partie-double.md"

# Réservés jusqu'au chapitre 9, 10, 11 respectivement : lintés en ABSENCE sur
# les chapitres 1 à 8 (notes d'outillage §3).
TERMES_RESERVES = ("la tierce", "l'errata", "le bon à tirer")

# Le quatuor du chapitre 7 : interdit partout ailleurs (notes d'outillage §4).
QUATUOR = ("photos", "playlist", "plat des anniversaires", "couverts")


def contraintes_chapitre(n: int, table: str = TABLE_PILOTAGE) -> dict:
    """Verdict imposé et interdits scopés d'un chapitre, lus dans la table."""
    verdict, objets = "", ""
    p = Path(table)
    if p.is_file():
        for ligne in p.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in ligne.split("|")]
            if len(cells) > 11 and cells[1] == str(n):
                verdict, objets = cells[5], cells[10]
                break
    return {
        "chapitre": n,
        "verdict": verdict,
        "objets_actifs": objets,
        # Le verdict « aucun » du chapitre 1 n'est pas un verdict à trouver.
        "verdict_attendu": verdict and not verdict.startswith("aucun")
                           and "hors échelle" not in verdict,
        "reserves": TERMES_RESERVES if 1 <= n <= 8 else (),
        "quatuor_interdit": n != 7,
    }


def controles_chapitre(texte: str, c: dict) -> dict:
    """Applique les contraintes d'un chapitre. Rend les manquements."""
    t = normalise(texte)
    out: dict[str, list[str]] = {"reserves": [], "quatuor": [], "verdict": []}

    for terme in c["reserves"]:
        for m in re.finditer(re.escape(normalise(terme)), t, re.I):
            a, b = max(0, m.start() - 40), min(len(t), m.end() + 40)
            out["reserves"].append(f"{terme} — …{t[a:b]}…".replace("\n", " "))

    if c["quatuor_interdit"]:
        for terme in QUATUOR:
            for m in re.finditer(rf"\b{re.escape(terme)}\b", t, re.I):
                a, b = max(0, m.start() - 40), min(len(t), m.end() + 40)
                out["quatuor"].append(f"{terme} — …{t[a:b]}…".replace("\n", " "))

    # §3 : le verdict se linte EN PRÉSENCE — il doit apparaître. Les autres
    # termes du lexique ne se lintent jamais en absence : la dérive synonymique
    # est tolérée, et même souhaitable à faible dose.
    if c["verdict_attendu"]:
        noyau = re.split(r"\s*\(", c["verdict"])[0].strip()
        if noyau and not re.search(re.escape(normalise(noyau)), t, re.I):
            out["verdict"].append(f"verdict « {noyau} » ABSENT du texte")
    return out


def _lexique_fuite(chemin: str = "outillage/lexique-fuite.txt") -> list[str]:
    """Champ lexical interdit, lu sur disque.

    Volontairement HORS du code et hors de `bible/` : ces mots ne doivent jamais
    se retrouver dans un fichier destiné à l'indexation RAG, où ils
    contamineraient le contexte du modèle par le retrieval même censé le
    cadrer.
    """
    p = Path(chemin)
    if not p.is_file():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]


# Signalés sans bloquer. `disparue` est ambigu (une chose disparaît sans que
# personne ne meure). `tombe` l'est davantage : c'est aussi le verbe, et le
# run 3 de la session 3 a été mis en échec sur « qu'elle ne glisse et ne tombe
# par terre » — un faux positif sur un homographe, exactement ce qu'un lint
# binaire ne doit pas coûter (notes d'outillage §5).
FUITE_AMBIGUE = {"disparue", "disparu", "tombe", "tombes"}


def fuite_lexicale(texte: str) -> tuple[list[str], list[str]]:
    """(matches bloquants, matches ambigus) du champ lexical interdit."""
    mots_interdits = _lexique_fuite()
    if not mots_interdits:
        return [], []
    # Le PLURIEL compte autant que le singulier — et il échappait à tout :
    # « feuilles mortes » dans BpC n'a pas été vu, alors que le brief appelle ce
    # lint « le firewall rendu vérifiable par grep ». Un firewall qui ne voit
    # pas les pluriels affiche vert sur des textes qu'il devrait bloquer, et
    # c'était le cas de toutes les sessions précédentes.
    motif = re.compile(r"\b(" + "|".join(re.escape(m) for m in mots_interdits)
                       + r")s?\b", re.IGNORECASE)
    durs, ambigus = [], []
    for m in motif.finditer(texte):
        # Le CONTEXTE est rendu avec le mot, pas seulement le mot. Plusieurs
        # entrées de la liste sont des homographes (« tombe » est aussi le
        # verbe tomber, « cendres » vaut au figuré) : sans l'extrait, un match
        # se lit comme une fuite avérée alors qu'il faut lire la phrase pour
        # trancher.
        a, b = max(0, m.start() - 45), min(len(texte), m.end() + 45)
        occ = f"{m.group(0).lower()} — …{texte[a:b]}…".replace("\n", " ")
        (ambigus if m.group(0).lower() in FUITE_AMBIGUE else durs).append(occ)
    return durs, ambigus


def noms_propres(texte: str) -> list[str]:
    """Candidats noms propres : majuscule qui n'ouvre ni phrase ni ligne."""
    out, vus = [], set()
    for m in MAJUSCULE.finditer(texte):
        mot = m.group(1)
        if mot in L1_EXCEPTIONS or mot.rstrip("'’") in L1_EXCEPTIONS:
            continue
        avant = texte[:m.start()].rstrip()
        if not avant:                              # tout début du texte
            continue
        # Ouverture de phrase, de citation — ou de CROCHET. Le crochet est là
        # parce que nemo produit des didascalies (« [Dans la cuisine] ») dont
        # le premier mot capitalisé n'est pas un nom propre. Sans cette
        # exception, un run entier sortait à 5 noms propres, tous faux, et
        # masquait le vrai défaut : le modèle écrit des didascalies au lieu
        # d'écrire un journal.
        # Le guillemet OUVRANT compte autant que le fermant : « La maison est
        # vide » faisait sortir « La » en nom propre. Ce n'est pas cosmétique —
        # l'interdit L1 est à zéro toléré, donc chaque faux positif noie la
        # seule occurrence qui compte (ici, un prénom réellement écrit).
        if avant[-1] in ".!?…:«»\"'—-–[(“":
            continue
        if texte[:m.start()].rstrip(" \t").endswith("\n"):   # début de ligne
            continue
        if mot.lower() in vus:
            continue
        vus.add(mot.lower())
        a, b = max(0, m.start() - 35), min(len(texte), m.end() + 35)
        out.append(f"{mot} — …{texte[a:b]}…".replace("\n", " "))
    return out


def glissements(entree: str) -> tuple[int, list[str]]:
    """(nombre d'occurrences, occurrences HORS champ du départ) pour une entrée.

    Une occurrence est conforme si un terme du départ se trouve à moins de
    L4_FENETRE_MOTS mots — c'est ce qui distingue le glissement (la pensée qui
    bute sur le où/pourquoi) d'une simple suspension de style.
    """
    occurrences = list(SUSPENSION.finditer(entree))
    hors_champ = []
    for m in occurrences:
        jetons_avant = entree[:m.start()].split()[-L4_FENETRE_MOTS:]
        jetons_apres = entree[m.end():].split()[:L4_FENETRE_MOTS]
        fenetre = " ".join(jetons_avant + jetons_apres)
        if not CHAMP_DEPART.search(fenetre):
            a, b = max(0, m.start() - 60), min(len(entree), m.end() + 60)
            hors_champ.append(f"…{entree[a:b]}…".replace("\n", " "))
    return len(occurrences), hors_champ


def accumulations_l3(entree: str) -> list[str]:
    """Accumulations au sens de la fiche v3 : ≥60 mots, ≥6 virgules, sans point
    ni point-virgule interne. Le découpage en phrases garantit déjà l'absence de
    point ; le point-virgule, lui, doit être vérifié à la main."""
    return [p for p in phrases(entree)
            if mots(p) >= L3_MOTS and p.count(",") >= L3_VIRGULES
            and ";" not in p]


def _extraits(motif: re.Pattern, texte: str, *, marge: int = 40) -> list[str]:
    """Occurrences avec leur contexte, dédupliquées, pour justifier une croix."""
    vus, out = set(), []
    for m in motif.finditer(texte):
        cle = m.group(0).lower()
        if cle in vus:
            continue
        vus.add(cle)
        a, b = max(0, m.start() - marge), min(len(texte), m.end() + marge)
        bout = texte[a:b].replace("\n", " ")
        out.append(f"…{bout}…" if a > 0 or b < len(texte) else bout)
    return out


# --- Analyse -----------------------------------------------------------------

def analyse(texte_brut: str) -> dict:
    """Rend les lignes de grille décidables mécaniquement, avec leurs preuves."""
    texte = normalise(strip_frontmatter(texte_brut))
    paras = paragraphes(texte)
    toutes = phrases(texte)

    # --- Structure : accumulation ---
    brutes = [
        p for p in toutes
        if p.count(",") >= ACC_VIRGULES and mots(p) >= ACC_MOTS
    ]
    # Une accumulation recopiée de l'étalon N'EN EST PAS UNE : elle porte les
    # objets de l'exemple (des clés, une coupelle) dans une scène qui parle
    # d'autre chose. Elle est retirée du compte et signalée à part.
    plagiats = [(p, recopie_etalon(p)) for p in brutes]
    accumulations = [p for p, r in plagiats if r == 0.0]
    recopies = [(p, r) for p, r in plagiats if r > 0.0]

    # --- Structure : couperets (3-6 mots), et ceux en FIN de paragraphe ---
    couperets, couperets_fin = [], []
    for para in paras:
        ph = phrases(para)
        for i, p in enumerate(ph):
            if COUPERET_MIN <= mots(p) <= COUPERET_MAX:
                couperets.append(p)
                if i == len(ph) - 1:
                    couperets_fin.append(p)

    # --- Passé simple : trois détecteurs, tous rendus en CANDIDATS ---
    def _participe(m: re.Match) -> bool:
        """Vrai si l'occurrence est un participe passé, pas un passé simple."""
        if m.group(0).lower() not in PS_PARTICIPES_AMBIGUS:
            return False
        return bool(AUXILIAIRE.search(texte[max(0, m.start() - 30):m.start()]))

    ps = []
    ps += [m.group(0) for m in PS_IRREGULIERS.finditer(texte)
           if not _participe(m)]
    ps += [m.group(0) for m in PS_ERENT.finditer(texte)]
    ps += [m.group(0) for m in PS_IRENT_URENT.finditer(texte)
           if m.group(0).lower() not in PS_HOMONYMES_PRESENT]
    ps += [m.group(1) for m in PS_ANCRE.finditer(texte)]
    ps += [m.group(1) for m in PS_PREMIERE_PERSONNE.finditer(texte)]
    ps += [m.group(1) for m in PS_NOM_PROPRE.finditer(texte)]
    ps_uniques = sorted({p.lower() for p in ps})

    hors_dialogue = sans_dialogue(texte)
    # Couche VOIX : hors citations (§7). Le cité porte la voix du cahier.
    voix = hors_guillemets(texte)

    # --- Contrôles L1-L4 (protocole ch. 2), comptés PAR ENTRÉE quand la règle
    # le demande (D1 : l'unité de compte est l'entrée de journal, pas la scène).
    liste_entrees = entrees(texte)
    l1 = noms_propres(texte)
    l2_durs, l2_ambigus = fuite_lexicale(texte)
    l3_par_entree = [accumulations_l3(e) for e in liste_entrees]
    l4_par_entree = [glissements(e) for e in liste_entrees]
    # Recopie de l'étalon : elle disqualifie une accumulation L3 comme elle
    # disqualifie une accumulation ordinaire.
    l3_recopies = [[p for p in acc if recopie_etalon(p)] for acc in l3_par_entree]
    l3_propres = [[p for p in acc if not recopie_etalon(p)]
                  for acc in l3_par_entree]

    # delint() en LECTURE SEULE : on jette le texte corrigé, on ne garde que
    # les avertissements. Mesurer le modèle, pas le post-filtre.
    _, avert_delint = delint(texte)

    return {
        "mots": mots(texte),
        "paragraphes": len(paras),
        "phrases": len(toutes),
        # EXACT — échec si présent
        # Couche VOIX — hors citations (§7).
        "pastiche": _extraits(PASTICHE, voix),
        "tics_ia": _extraits(TICS_IA, voix),
        "exclamation_hors_dialogue": _extraits(
            re.compile(r"[^\s]{0,30}!"), hors_dialogue),
        "incise_adverbiale": (_extraits(INCISE_ADVERBIALE, texte)
                              + _extraits(INCISE_PREPOSITIONNELLE, texte)),
        "elision": _extraits(ELISION_MANQUANTE, texte),
        # EXACT — échec si absent
        "accumulations": accumulations,
        "accumulations_recopiees": recopies,
        "couperets_fin_para": couperets_fin,
        "couperets_tous": couperets,
        "precision": sorted({m.group(0) for m in PRECISION.finditer(texte)}),
        # CANDIDAT
        "passe_simple": ps_uniques,
        # Défauts nemo connus, hors grille du protocole
        "delint": avert_delint,
        # --- L1-L4 (session 3) ---
        "entrees": len(liste_entrees),
        "l1_noms_propres": l1,
        "l2_fuite": l2_durs,
        "l2_fuite_ambigue": l2_ambigus,
        "l3_par_entree": l3_propres,
        "l3_recopies": l3_recopies,
        "l4_par_entree": l4_par_entree,
        # --- session 5, item 7 ---
        "meta_termes": _extraits(META_TERMES, voix),
        "formulaire": _extraits(FORMULAIRE, voix),
        "attracteurs": _extraits(ATTRACTEURS, texte),
        "je_decide_par_entree": [len(JE_DECIDE.findall(e))
                                 for e in liste_entrees],
        "couples_m3": couples_decision_execution(texte),
        "entetes_incoherents": entetes_coherents(
            ENTETE_ENTREE.findall(texte)),
    }


# --- Rapport -----------------------------------------------------------------

def _marque(present: bool) -> str:
    """✗ = défaut, ✓ = tenu."""
    return "✗" if present else "✓"


def rapport(res: dict, titre: str = "") -> str:
    l = []
    if titre:
        l.append(f"### {titre}")
    cible = "OK" if 400 <= res["mots"] <= 550 else "HORS CIBLE"
    l.append(f"{res['mots']} mots [{cible}] · {res['paragraphes']} paragraphes "
             f"· {res['phrases']} phrases")
    l.append("")

    l.append("**Mécanique — EXACT (✗ = défaut présent)**")
    for cle, libelle in [
        ("pastiche", "Lexique pastiche gothique"),
        ("tics_ia", "Tic d'IA"),
        ("exclamation_hors_dialogue", "Point d'exclamation hors dialogue"),
        ("incise_adverbiale", "Incise adverbiale (ou son équivalent prépositionnel)"),
        ("elision", "Élision manquante"),
    ]:
        occ = res[cle]
        l.append(f"- {_marque(bool(occ))} {libelle}"
                 + (f" → {len(occ)}" if occ else ""))
        for e in occ[:3]:
            l.append(f"    - `{e}`")

    l.append("")
    l.append("**Structure — EXACT (✗ = attendu absent)**")
    n_acc = len(res["accumulations"])
    etat_acc = "✓" if n_acc == 1 else "✗"
    detail = {0: "zéro = plat", 1: "exactement une"}.get(n_acc, f"{n_acc} = tic")
    l.append(f"- {etat_acc} Phrase d'accumulation : {detail}")
    for a in res["accumulations"]:
        l.append(f"    - `{a[:120]}…`" if len(a) > 120 else f"    - `{a}`")
    for a, r in res.get("accumulations_recopiees", []):
        l.append(f"    - ⛔ **ÉTALON RECOPIÉ à {r:.0%}** (ne compte pas) : "
                 f"`{a[:90]}…`")
    n_coup = len(res["couperets_fin_para"])
    l.append(f"- {_marque(n_coup == 0)} Phrase-couperet en fin de paragraphe "
             f"→ {n_coup} (dont {len(res['couperets_tous'])} couperets au total)")
    for c in res["couperets_fin_para"][:3]:
        l.append(f"    - `{c}`")
    l.append(f"- {_marque(not res['precision'])} Heure ou quantité exacte "
             f"→ {len(res['precision'])}")
    if res["precision"]:
        l.append("    - " + ", ".join(f"`{p}`" for p in res["precision"][:6]))

    l.append("")
    l.append("**Passé simple — CANDIDATS, à confirmer à l'œil**")
    if res["passe_simple"]:
        l.append(f"- ⚠ {len(res['passe_simple'])} forme(s) : "
                 + ", ".join(f"`{p}`" for p in res["passe_simple"][:12]))
    else:
        l.append("- ✓ aucune forme non ambiguë détectée")

    if res["delint"]:
        l.append("")
        l.append("**Défauts nemo (hors grille du protocole)**")
        for w in res["delint"]:
            l.append(f"- ⚠ {w}")

    l.append("")
    l.append("**Laissé au relecteur** (non automatisable) : adjectifs "
             "coordonnés · émotion annoncée · météo corrélée · omniscience · "
             "doute résolu · vérification matérielle décrite · décalage du "
             "dialogue · les 5 beats dans l'ordre · les 3 lignes orales.")
    return "\n".join(l)


# --- Auto-test sur les étalons de la fiche ------------------------------------

def _etalons(fiche: Path) -> list[tuple[str, str]]:
    """Extrait les blocs `> …` de la section `## Extraits étalons`."""
    texte = fiche.read_text(encoding="utf-8")
    section = re.search(r"^## Extraits étalons(.*)\Z", texte,
                        re.MULTILINE | re.DOTALL)
    if not section:
        return []
    out, titre, bloc = [], None, []
    for ligne in section.group(1).splitlines():
        entete = re.match(r"^\*\*(Étalon.*?)\*\*", ligne)
        if entete:
            if titre and bloc:
                out.append((titre, "\n".join(bloc).strip()))
            titre, bloc = entete.group(1), []
        elif ligne.startswith(">"):
            bloc.append(ligne.lstrip("> ").rstrip())
        elif not ligne.strip() and bloc:
            bloc.append("")
    if titre and bloc:
        out.append((titre, "\n".join(bloc).strip()))
    return out


def autotest(fiche: Path) -> int:
    """Le test du test : un détecteur qui rate sa propre cible ne vaut rien.

    Les quatre étalons DÉFINISSENT le style. Ils doivent donc sortir propres sur
    les lignes exactes, et l'étalon 2 — qui existe pour montrer l'accumulation —
    doit être compté comme exactement une.
    """
    etalons = _etalons(fiche)
    if not etalons:
        print("ERREUR : aucun étalon trouvé dans la fiche.", file=sys.stderr)
        return 1

    echecs = []
    for titre, texte in etalons:
        r = analyse(texte)
        print(f"\n{'=' * 70}\n{titre}\n{'=' * 70}")
        print(rapport(r))
        for cle, libelle in [("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                             ("incise_adverbiale", "incise adverbiale")]:
            if r[cle]:
                echecs.append(f"{titre} : {libelle} détecté à tort → {r[cle]}")
        if r["passe_simple"]:
            echecs.append(f"{titre} : passé simple à tort → {r['passe_simple']}")
        # On somme les accumulations et les « recopies » : ici la source EST
        # l'étalon, donc il est trivialement identique à lui-même. Ce qu'on
        # valide dans cet auto-test est le détecteur de FORME, pas celui de
        # plagiat — lequel se teste sur des runs, où la question a un sens.
        attendu = 1 if titre.startswith("Étalon 2") else 0
        trouve = len(r["accumulations"]) + len(r["accumulations_recopiees"])
        if trouve != attendu:
            echecs.append(f"{titre} : {trouve} accumulation(s), "
                          f"attendu {attendu}")

    print(f"\n{'=' * 70}")
    if echecs:
        print(f"AUTO-TEST ÉCHOUÉ — {len(echecs)} problème(s) :")
        for e in echecs:
            print(f"  ✗ {e}")
        return 1
    print("AUTO-TEST OK — les 4 étalons sortent propres, "
          "l'accumulation est isolée sur l'étalon 2.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fichiers", nargs="*", help="Runs à analyser")
    parser.add_argument("--etalons", action="store_true",
                        help="Auto-test sur les étalons de la fiche")
    parser.add_argument("--fiche", default="bible/style-auteur.md")
    args = parser.parse_args()

    if args.etalons:
        return autotest(Path(args.fiche))
    if not args.fichiers:
        parser.error("donne au moins un fichier, ou --etalons")

    for chemin in args.fichiers:
        p = Path(chemin)
        print(rapport(analyse(p.read_text(encoding="utf-8")), titre=p.name))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
