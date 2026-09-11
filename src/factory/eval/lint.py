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
from factory.paths import BIBLE_DIR, DATA_DIR
from factory.text import delint

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
    r"heures?(?:\s+\w+)?\b|"
    # QUANTITÉS EN TOUTES LETTRES devant un nom commun (session 6). Le motif
    # n'acceptait un nombre écrit que suivi de « heures » : « L'égouttoir, ce
    # soir : deux assiettes. » ne comptait pas. Or c'est la ligne d'inventaire
    # du chapitre — le motif le plus caractéristique de cette voix, et le fait
    # imposé du brief. Le lint de la « précision maniaque » ignorait l'exemple
    # même que le protocole donne.
    #
    # Le nom est exigé (deux mots au moins) pour ne pas ramasser « deux » seul,
    # qui est partout dans un chapitre sur deux assiettes ; les déterminants
    # sont exclus après le nombre (« deux de plus » n'est pas une quantité
    # d'objets comptés).
    r"\b(?:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze)\s+"
    r"(?!de\b|des\b|d'|à\b|au[x]?\b|fois\b|heures?\b)[a-zàâçéèêëîïôûùüœ]{3,}\b",
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


def etalon_accumulation(fiche: str = str(BIBLE_DIR / "style-auteur.md")) -> str:
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

# LA MACHINERIE — ce qui ne doit jamais figurer dans un contexte SERVI.
#
# Distinct des méta-termes : ceux-là sont des mots d'atelier littéraire (le
# couperet, le squelette), ceux-ci sont les noms de nos propres contrôles. Le
# §5 du brief v2 les sert tous : « L1, L2, lexiques, attracteurs, interdits
# matériels bloquants », « L3 exempté par la table », « possédés par le code,
# tamponnés en dernier ». Cette section est écrite pour l'implémenteur, pas
# pour le modèle — la servir telle quelle lui apprend nos lints.
#
# La garde d'entrée existante n'en voyait qu'un seul mot sur dix.
MACHINERIE = re.compile(
    # « la table » seule est un MEUBLE dans ce roman — c'est même l'un des
    # objets du chapitre 7. Seule « la table de pilotage » est de la machinerie.
    r"\bL[1-4]\b|\bla table de pilotage\b|\ble code\b|\bbloquants?\b"
    r"|\blint\w*\b|\bexempt[ée]\w*\b|\btamponn[ée]\w*\b|\blexiques?\b"
    r"|\bgrille\b|\bpipeline\b|\bhors [ée]chelle\b|\bcomposeur\b"
    r"|\bentrees_spec\b|\bv[ée]tos?\b", re.IGNORECASE)

# ATTRACTEURS : formules vers lesquelles le modèle glisse tout seul, relevées à
# la lecture des runs. Ce ne sont pas des fautes de langue, ce sont des tics
# d'entraînement — et « Demain est un autre jour » a été entendu à l'oral.
# ATTRACTEURS — par FAMILLES, plus par littéraux (session 6).
#
# La version précédente ne portait que trois chaînes exactes, si bien que
# « Demain tout sera clair » (accumulation de C2) et « je devenais folle »
# (run C, avant correctifs) passaient tous les deux. Le second est interdit
# NOMMÉMENT par la fiche — l'interdit était servi, il n'a pas tenu, et aucun
# lint ne le voyait. Un attracteur est une tournure vers laquelle le modèle
# glisse : c'est la famille qu'il faut nommer, pas l'occurrence qu'on a lue.
ATTRACTEURS = re.compile(
    # la folie nommée : « devenir folle », « perdre la tête / la raison »
    r"(devenir folle|devenais? folle|devenue folle|suis folle|"
    r"perdre la t[êe]te|perds? la t[êe]te|perdre la raison|"
    # LE LENDEMAIN QUI RÉSOUT — la fiche interdit que l'entrée soit apaisée.
    #
    # Élargi en session 7, et la famille était plus large qu'on ne croyait : la
    # version précédente ne connaissait que « demain EST un autre jour », si bien
    # que TROIS runs sur quatre de la session 6 ont fermé sur cet attracteur sans
    # une croix — « demain sera une journée meilleure » (S6-1), « demain sera un
    # autre jour » (S6-2), « demain sera une nouvelle journée » et « à la lumière
    # du jour » (S6-3). Un seul mot d'écart entre l'attrapé et le passé.
    # L'adjectif se place AVANT ou APRÈS le nom (« une nouvelle journée », « une
    # journée meilleure » — S6-1 écrivait la seconde forme). Les deux ordres,
    # sinon le motif attrape la moitié de la famille et le vert ment.
    r"demain (?:est|sera|serait)(?: un| une)? (?:"
    r"(?:autre|nouvelle?|meilleure?)(?: jour(?:née)?)?"
    r"|jour(?:née)? (?:meilleure?|nouvelle?|autre))|"
    r"demain,? tout (?:sera|ira|s'[ée]clairera)|"
    r"demain,? je (?:saurai|comprendrai|verrai)|"
    r"à la lumière du jour|"
    # L'ADRESSE CONSOLANTE. La dernière ligne referme, elle ne console pas —
    # et « Bonne nuit. » est la forme la plus pure du contraire : le carnet
    # cesse d'être un relevé pour devenir une adresse. Relevé sur S7-1, dans la
    # même phrase et demie que la fuite lexicale et l'attracteur du lendemain.
    # Ancré en DÉBUT DE PHRASE : « Bonne nuit. » est une adresse, « une bonne
    # nuit de sommeil » est un fait. Sans l'ancrage, le motif attrapait les deux.
    r"(?:^|[.!?…»\n]\s*)(?:bonne nuit|bonne soirée|dors bien|à demain)\b)|"
    # L'IMAGE D'ARME — le couperet contourné par la métaphore. Le lint des
    # méta-termes ne voit pas « le coup de couteau : je n'ai pas rêvé » (tirage
    # 6 du ch. 7) parce que ce n'est pas un mot d'atelier, c'est son image. Le
    # même contournement avait été mesuré en session 5 (« Le coup de couteau est
    # le suivant : »). Interdire un mot le fait revenir en figure.
    # « une lame » seule est un objet (« une lame de parquet ») ; c'est la
    # COMPARAISON qui fait l'image. On exige donc le comme, ou le coup.
    r"(?:coup de couteau|comme un couteau|comme une lame|comme un couperet|"
    r"coup de hache|couperet qui tombe|tranch\w+ comme)|"
    # LE DÉNI DE RÊVE. « Je n'ai pas rêvé » est une clôture qui rassure : elle
    # tranche le doute que l'entrée doit laisser ouvert.
    r"je n'ai pas r[êe]v[ée]|ce n'[ée]tait pas un r[êe]ve|je ne r[êe]ve pas|"
    # la métaphore maritime, tic mesuré aux premières sessions
    r"(bou[ée]e|oc[ée]an)", re.IGNORECASE)

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
# La décision notée, au PRÉSENT comme au PASSÉ COMPOSÉ (session 6). C1 écrivait
# « J'ai décidé de vérifier par moi-même » et le détecteur ne bornait que le
# présent : la grille a dû relever le couple à la main.
#
# « je vais » n'y figure PAS, délibérément : C3 écrit « Je vais vérifier dans la
# cuisine » et la grille le juge conforme. Le futur proche est un mouvement, pas
# une résolution notée au carnet — l'inclure aurait fait échouer un run que la
# lecture humaine avait validé.
# TROISIÈME FORME : le PARTICIPE APPOSÉ (session 7 bis). « Je me lève, décidée à
# vérifier » — la décision se glisse en apposition, et le candidat ne voyait ni
# celle-là ni sa cousine « résolue à ». S7-1 en portait DEUX, la grille les a
# relevés à la main. Le motif a maintenant les trois formes : présent, passé
# composé, participe.
_DECISION = re.compile(
    r"\b(?:je d[ée]cide de|j'ai d[ée]cid[ée] de|je d[ée]cidai de|"
    r"j'ai r[ée]solu de|je me suis promis[e]? de|je me r[ée]solus? à|"
    r"d[ée]cid[ée]e? à|r[ée]solue? à)\s+"
    r"(?:l[ae]\s+|l'|les\s+|me\s+|m'|y\s+|en\s+)?(\w{4,})",
    re.IGNORECASE)

# LE GESTE NARRÉ — seconde règle, et c'est elle qui attrape C1.
#
# La règle M3 dit que l'effet de « décision sans geste » vit dans le VIDE entre
# la décision notée et l'état constaté ensuite. Donc : décision → état constaté
# (impersonnel : « L'égouttoir, ce soir : deux assiettes. ») = conforme ;
# décision → geste raconté à la première personne = le vide est comblé, c'est le
# défaut.
#
# La règle lexicale seule ne pouvait pas voir C1 : la décision porte sur
# « vérifier » et l'exécution s'écrit « je les ai comptées ». Aucun radical
# commun. Mesuré avant d'élargir, plutôt que supposé.
# LE GESTE NARRÉ, AU PASSÉ COMPOSÉ **ET AU PRÉSENT**.
#
# La première version ne connaissait que les formes composées. Or les entrées
# de la session 7 sont écrites au PRÉSENT (« Je me lève », « Je note », « Je
# compte ») : dans une entrée au présent, aucun geste n'était jamais détecté, et
# le couple ne pouvait pas se refermer — quelle que soit la forme de la
# décision. Étendre la décision au participe sans étendre l'exécution au présent
# aurait fait un détecteur qui ne mord jamais : un lint fantôme de plus.
_GESTE_1P = re.compile(
    r"\b(?:j'ai|je les ai|je l'ai|je la ai|je me suis|je m'[ée]tais)\s+"
    r"(?:\w+\s+){0,2}?([a-zàâçéèêëîïôûùüœ]+(?:[ée]{1,2}s?|is|it|us|ut))\b"
    r"|\bje\s+(?:l[ae]s?\s+|l'|m[e\']\s*|y\s+|en\s+)?"
    r"([a-zàâçéèêëîïôûùüœ]{3,}(?:e|es|s|te|ds))\b",
    re.IGNORECASE)

# Participes d'ÉTAT et de PERCEPTION : constater n'est pas agir. « L'égouttoir
# était là », « je les ai vues » relèvent du constat que le style demande — les
# compter comme gestes ferait du contrôle un détecteur de première personne,
# c'est-à-dire de rien, dans un carnet écrit à la première personne.
# DÉCISIONS DE CARNET — exclues, et pas par commodité.
#
# M3 porte sur la décision d'un GESTE dans le monde, dont le style veut que
# l'exécution reste dans le vide. « Je décide de reprendre les faits dans
# l'ordre », « j'ai décidé de noter plus précisément » sont des opérations du
# carnet sur lui-même — et la seconde est la résolution que le brief IMPOSE au
# chapitre 2. Sans cette exclusion, le détecteur signalait C2, que la lecture
# humaine a jugé conforme : il aurait reproché au run d'obéir au brief.
_DECISIONS_DE_CARNET = re.compile(
    r"^(?:reprend|repass|not|point|reli|[ée]cri|consign|marqu|r[ée][ée]cri|"
    r"tenir|d[ée]tail)", re.IGNORECASE)

_PARTICIPES_ETAT = {
    "été", "eu", "vu", "vue", "vues", "aperçu", "aperçue", "senti", "sentie",
    "su", "sue", "cru", "crue", "pensé", "pensée", "compris", "comprise",
    "souvenu", "souvenue", "rappelé", "rappelée", "resté", "restée",
    "semblé", "paru", "revu", "revue", "relu", "relue", "lu", "lue",
    "regardé", "regardée", "observé", "observée", "remarqué", "remarquée",
    "trouvé", "trouvée", "réalisé", "réalisée", "demandé", "demandée",
    # les mêmes au PRÉSENT — constater n'est pas agir, quel que soit le temps
    "suis", "sais", "vois", "sens", "crois", "pense", "comprends", "regarde",
    "observe", "remarque", "trouve", "demande", "souviens", "rappelle",
    "relis", "lis", "reste", "semble", "veux", "peux", "dois", "espère",
}


def couples_decision_execution(texte: str) -> list[str]:
    """Décisions suivies de leur exécution apparente — CANDIDATS pour M3.

    Deux règles, et la sortie dit LAQUELLE a mordu : sur une ligne non
    bloquante, la lecture humaine tranche, et elle a besoin de savoir si le
    signalement est lexical (sûr) ou par geste narré (élargi).
    """
    out, phr = [], phrases(texte)
    for i, p in enumerate(phr):
        m = _DECISION.search(p)
        if not m:
            continue
        if _DECISIONS_DE_CARNET.match(m.group(1)):
            continue
        radical = m.group(1)[:-2] if len(m.group(1)) > 6 else m.group(1)
        # LA FENÊTRE COMPTE DES PHRASES NARRATIVES, pas des fragments.
        #
        # Les stations de reconstruction insèrent des lignes très courtes
        # (« 18h30. », « La table du séjour. »), et elles consommaient les deux
        # phrases de la fenêtre : le couple de S7-1 (« Je me lève, décidée à
        # vérifier » suivi, plus loin, de la vérification racontée) passait à
        # travers. Un dispositif de MASSE a donc aveuglé un détecteur de VOIX —
        # sans la lecture manuelle, on ne l'aurait pas su.
        suite_txt = [q for q in phr[i + 1:i + 8] if mots(q) >= 6]
        suite = " ".join(suite_txt)
        if re.search(rf"\b(?:j'ai |je )\w*{re.escape(radical)}", suite, re.I):
            out.append(f"[lexical] « {p.strip()[:70]}… » puis exécution : "
                       f"« {suite.strip()[:70]}… »")
            continue
        # Règle du geste narré : on ne regarde que DEUX phrases, pas trois. Le
        # vide que le style demande est immédiat ; au-delà, l'entrée a repris
        # son cours et un « j'ai rangé » n'exécute plus la décision.
        for q in suite_txt[:2]:
            # Deux groupes alternatifs (composé / présent) : on prend celui
            # qui a capturé.
            gestes = [(g.group(1) or g.group(2)).lower()
                      for g in _GESTE_1P.finditer(q)
                      if (g.group(1) or g.group(2))
                      and (g.group(1) or g.group(2)).lower()
                      not in _PARTICIPES_ETAT]
            if gestes:
                out.append(f"[geste narré] « {p.strip()[:70]}… » puis "
                           f"« {q.strip()[:70]}… » ({', '.join(gestes[:3])})")
                break
    return out


# ---------------------------------------------------------------------------
# Session 6 — les instances descendent dans l'outillage
#
# Doctrine du lexique de fuite, étendue (protocole §3.3) : la section
# *Interdits* servie au modèle ne garde que les CATÉGORIES (« un état mental
# nommé en apposition : interdit ») ; les instances vivent ici. Motif mesuré :
# B′2 a écrit « perplexe », qui était servi comme contre-exemple verbatim, puis
# comme nom de l'interdit. Nommer ce qui est interdit est le seul moyen de
# l'interdire — et c'est aussi le montrer. On l'interdit donc en sortie.
# ---------------------------------------------------------------------------

# ÉTATS MENTAUX NOMMÉS EN APPOSITION. Le défaut n'est pas le mot mais la
# position : « Perplexe, je repose le cahier » nomme l'état au lieu de le faire
# sentir. L'apposition est repérée par la ponctuation qui l'isole, ou par la
# copule qui l'attribue.
ETATS_MENTAUX_MOTS = (
    "perplexe", "songeuse", "songeur", "troublée", "troublé", "intriguée",
    "intrigué", "pensive", "pensif", "désemparée", "désemparé", "hébétée",
    "hébété", "incrédule", "abasourdie", "abasourdi", "déconcertée",
    "déconcerté", "dubitative", "dubitatif", "circonspecte", "circonspect",
)
# L'apposition N'EST PAS toujours fermée par une ponctuation. Première version :
# elle exigeait une virgule ou un point juste après l'adjectif, et laissait donc
# passer « Je fronce les sourcils, intriguée PAR cette différence » — relevé sur
# S6-1, où c'est exactement le défaut que la ligne existe pour attraper. Un
# état nommé reste un état nommé quand il traîne un complément.
ETATS_MENTAUX = re.compile(
    r"(?:^|[.!?…»\n]\s*|,\s*)(" + "|".join(ETATS_MENTAUX_MOTS) + r")\b"
    r"|\bje (?:suis|étais|me sens|me sentais|restai?s?)\s+(?:\w+\s+){0,2}?"
    r"(" + "|".join(ETATS_MENTAUX_MOTS) + r")\b",
    re.IGNORECASE)


# INTERDITS MATÉRIELS — le monde générique de nemo, documenté par six runs.
#
# Ce n'est pas une liste de style : c'est une liste de DÉCOR. Le modèle, quand
# la matière servie est mince, remplit la soirée avec le mobilier statistique
# d'un intérieur contemporain — télévision, sac à main, barquette de lasagnes,
# retour du travail. La maison de ce roman n'en a aucun, et rien dans les
# fiches ne le dit puisqu'une fiche décrit ce qui est, pas ce qui n'est pas.
#
# SCOPE PAR CHAPITRE : `chapitre_min` est le premier chapitre où le terme
# devient légitime. Les mémos téléphoniques apparaissent au chapitre 5 (le
# nouveau cahier) — interdits avant, attendus après. Un lint qui ne sait pas
# de quel chapitre on parle interdirait à jamais ce que le roman prévoit.
#
# Le travail SUR LE MANUSCRIT n'est pas visé : c'est son métier, elle l'exerce
# chez elle. Ce qui est visé est le travail comme LIEU — en sortir, y aller,
# en revenir. D'où des motifs de mouvement, pas le mot « travail » seul.
INTERDITS_MATERIELS: tuple[tuple[str, str, int], ...] = (
    ("travail hors du domicile",
     r"\b(?:revenue?s?|rentr[ée]e?s?|retour|repartie?s?|partie)\s+"
     r"(?:tard\s+)?(?:du|de mon|au)\s+(?:travail|bureau)\b"
     r"|\bau bureau\b|\bmes coll[èe]gues\b|\bune r[ée]union\b"
     r"|\bjourn[ée]e de travail\b|\bj'ai travaill[ée] tard\b"
     # LE TRAVAIL COMME PÉRIODE, pas seulement comme lieu qu'on quitte. Le
     # motif ne visait que les verbes de mouvement (revenue du, rentrée du) et
     # laissait passer « épuisée par la semaine de travail » — relevé sur le
     # tirage sous méthode du mouvement. Elle travaille chez elle : ses
     # journées n'ont ni semaine ni horaires de bureau.
     r"|\b(?:la |une |ma )?(?:semaine|journ[ée]e|matin[ée]e|apr[èe]s-midi) "
     r"de (?:travail|bureau)\b|\bapr[èe]s le (?:travail|bureau)\b", 99),
    ("télévision", r"\bt[ée]l[ée]vision\b|\bt[ée]l[ée]\b|\bla t[ée]l[ée]s?\b", 99),
    ("messages et téléphone",
     r"\bmes messages\b|\bt[ée]l[ée]phone\b|\bportable\b|\bSMS\b"
     r"|\bmessagerie\b|\bnotifications?\b", 5),
    ("lave-vaisselle", r"\blave-vaisselle\b", 99),
    ("sac à main", r"\bsac à main\b", 99),
    ("barquette", r"\bbarquettes?\b", 99),
    ("courses", r"\bles courses\b|\bfaire les courses\b|\bsupermarch[ée]\b"
                r"|\b[ée]picerie\b", 99),
)


def interdits_materiels(texte: str, chapitre: int = 2) -> list[str]:
    """Termes de décor génériques présents, pour le chapitre donné.

    Rend « famille : extrait » — la famille sert la grille, l'extrait sert la
    lecture. Un signalement sans son extrait oblige à rouvrir la sortie brute.
    """
    out = []
    for famille, motif, chapitre_min in INTERDITS_MATERIELS:
        if chapitre >= chapitre_min:
            continue
        for m in re.finditer(motif, texte, re.IGNORECASE):
            debut = max(0, m.start() - 30)
            out.append(f"{famille} : …{texte[debut:m.end() + 20].strip()}…")
    return out


# L'ACCUMULATION QUI SE RÉSUME — le validateur né du sommaire de C2.
#
# C2 a rendu 131 mots de table des matières : « perplexité, concentration sur
# les détails, rappel des faits, fatigue, panique, respiration calme,
# explication rationnelle, corps qui parle, verdict d'erreur de relevé… ». La
# validation comptait des mots et des virgules, donc elle a accepté un sommaire.
# *Compter n'est pas lire*, épisode deux — le premier était une accumulation en
# anglais acceptée par les mêmes compteurs.
#
# ⚠ LE PROTOCOLE §3.1 PRESCRIVAIT « propositions verbales exigées — ratio de
# verbes conjugués par item ». Implémenté au mot, ce critère REJETTE L'ÉTALON :
# l'accumulation qui définit le geste est nominale à 88 % de ses items (« le
# café de sept heures, le départ de sept heures quarante, la réunion, le
# déjeuner, le garage, la porte de la buanderie »), et son ratio verbal tombe à
# 12 % — plus bas que les six accumulations que l'étage C a produites. Mesuré,
# pas supposé, et c'est l'auto-test sur les étalons qui l'a dit.
#
# Le vrai discriminant est l'ABSTRACTION, ce que la grille disait déjà en
# nommant des « méta-beats ». L'étalon énumère des CHOSES et des MOMENTS de la
# soirée ; C2 énumère les BEATS DE L'ENTRÉE, dont les états d'âme et le verdict.
#
#   étalon 2 : 0 %    les six accumulations de l'étage C : 0 %    C2 : 47 %
#
# Séparation totale, marge énorme : le seuil est à 20 % et n'a pas besoin d'être
# fin.
_ITEM_ABSTRAIT = re.compile(
    # suffixes de nominalisation — l'abstraction a une morphologie
    r"\b\w*(?:it[ée]|tion|sion|ance|ence|itude|esse|isme)\b"
    # et les états d'âme et opérations mentales qui n'en portent pas
    r"|\b(?:fatigue|panique|doute|angoisse|peur|effroi|malaise|trouble|"
    r"verdict|souvenir|rappel|d[ée]tails?|faits?|m[ée]moire|esprit|corps)\b",
    re.IGNORECASE)

# Un item VERBAL raconte un pas de la soirée ; il ne peut pas être du sommaire.
_ITEM_VERBAL = re.compile(
    r"\b(?:je|j'|elle|il|on|nous|ils|elles)\b"
    r"|\b(?:ai|as|avons|avez|ont|avais|avait|avions|avaient"
    r"|suis|es|est|sommes|êtes|sont|étais|était|étions|étaient)\b",
    re.IGNORECASE)

ACC_ABSTRAIT_MAX = 0.20


# LA TROISIÈME PERSONNE DANS UN CARNET ÉCRIT À LA PREMIÈRE.
#
# « Elle est revenue à vingt heures, a refermé le cahier, posé la lampe… »
# (S7-3) : le nœud d'accumulation a basculé de personne au milieu d'une entrée
# entièrement à la première. Aucun lint ne le voyait — c'est la lecture debout
# qui l'a relevé. Défaut mécanique, détection triviale : le carnet n'a qu'un
# sujet, et ce sujet est « je ».
_SUJET_3P = re.compile(
    r"\b(?:elle|il|on)\s+(?:[a-zàâçéèêëîïôûùüœ']+\s+){0,2}?"
    r"(?:est|a|était|avait|s'est|se|fut)\b"
    r"|\b(?:elle|il)\s+(?:rentre|revient|repose|referme|compte|note|vérifie)\b",
    re.IGNORECASE)


def accumulation_a_la_premiere(phrase: str) -> tuple[bool, str]:
    """L'accumulation est-elle écrite à la première personne ?

    Rendue vraie si aucun sujet de troisième personne n'apparaît ET qu'un « je »
    est présent : les deux conditions, parce qu'une accumulation sans aucun
    pronom (l'étalon est ainsi, en grande partie nominale) ne doit pas être
    rejetée pour autant.
    """
    if _SUJET_3P.search(phrase):
        m = _SUJET_3P.search(phrase)
        return False, f"troisième personne : « {phrase[max(0, m.start()-20):m.end()+30]} »"
    return True, ""


def accumulation_resumante(phrase: str) -> tuple[float, list[str]]:
    """Part d'items abstraits d'une accumulation, et lesquels.

    L'unité est l'item entre virgules — la même unité que celle par laquelle la
    consigne est chiffrée (« au moins douze étapes, séparées par des virgules »).
    Mesurer dans l'unité de la consigne évite de reprocher au modèle autre chose
    que ce qu'on lui a demandé.

    Les adverbes nus (« calmement », « méthodiquement » de l'étalon) sont
    neutres : ils modifient la phrase-cadre, ils ne sont pas une étape.
    """
    items = [i.strip() for i in phrase.split(",") if i.strip()]
    if not items:
        return 0.0, []
    candidats = [i for i in items
                 if not _ITEM_VERBAL.search(i)
                 and not re.fullmatch(r"\w+ment", i, re.IGNORECASE)]
    abstraits = [i for i in candidats if _ITEM_ABSTRAIT.search(i)]
    return len(abstraits) / len(items), abstraits


# ---------------------------------------------------------------------------
# LA REDITE — deux détecteurs, session 7
#
# `_recoller` retire le chevauchement AU CARACTÈRE PRÈS entre deux segments :
# il attrape la recopie, pas la re-narration. S6-3 range les deux assiettes au
# ¶10 puis les range à nouveau au ¶13, avec d'autres mots ; et ses ¶2 et ¶3
# partagent deux phrases entières, identiques celles-là.
#
# ⚠ LA MESURE EST DES CARACTÈRES, PAS DES MOTS, et ce n'est pas un détail de
# confort. Mesuré sur S6-3 avant de choisir :
#
#                                            caractères   recouvrement de mots
#   ¶10/¶13  la même action rangée deux fois     0,64            0,78
#   ¶5/¶8    l'ACCUMULATION contre la recon-     0,02            0,52
#            struction qu'elle résume
#   ¶4/¶9    deux constats distincts             0,02            0,06
#
# Un recouvrement de mots ferait sauter l'accumulation elle-même — qui re-narre
# la soirée par définition, c'est sa raison d'être — sur un contrôle bloquant.
# On tuerait le geste acquis à la session précédente. La similarité de
# caractères sépare les trois cas sans ambiguïté.
#
# Et AUCUN plancher de longueur : ¶10 fait dix-sept mots. Un filtre « au moins
# vingt mots » le laissait passer, et c'est ce qui m'a fait conclure « aucun
# doublon dans S6-3 » au premier balayage — le filtre était le bug, pas la
# mesure.
REDITE_SEUIL = 0.50

# ⚠ LE RATIO SEUL NE SUFFIT PAS — trouvé en falsifiant l'assemblage complet.
#
# Le français est plein de mots-outils, et deux paragraphes COURTS et
# entièrement différents montent haut sans rien partager de réel :
#
#   « Je relis l'entrée d'hier. Ma mémoire dit une assiette. »
#   « Je suis rentrée, j'ai posé le cahier, j'ai préparé le dîner. »   ratio 0,51
#
# Le premier essai de dédoublonnage a supprimé la seconde sur ce score. Un
# retrait bloquant qui se trompe coûte un paragraphe de récit à chaque run.
#
# Le discriminant est la plus longue SUITE COMMUNE — une redite reprend un
# fragment continu, deux textes différents ne partagent que des articles :
#
#   la même action rangée deux fois   ratio 0,64   bloc 42 car.
#   deux constats distincts           ratio 0,51   bloc  6 car.
#   deux phrases courtes distinctes   ratio 0,67   bloc  6 car.
#
# Les deux conditions ensemble, donc. Ni l'une ni l'autre ne tient seule.
REDITE_BLOC_MIN = 30


# CE QUE LE CODE COMPOSE N'EST JAMAIS UNE REDITE.
#
# Trouvé en falsifiant le détecteur sur S6-C, et c'est la deuxième fois qu'un
# contrôle de session 7 vise ce qu'il devait protéger. Les trois « doublons » de
# plus fort ratio du chapitre étaient TOUS des artefacts du code :
#
#   ¶0/¶17  (0,55)  les EN-TÊTES — les retirer supprime la bascule audio ;
#   ¶1/¶18  (0,96)  l'ANCRE de citation, reposée en tête de chaque entrée —
#                   celle-là même qu'on re-tamponne au §2 de cette session ;
#   ¶11/¶28 (0,71)  les GLISSEMENTS — trois approches DIFFÉRENTES de la banque,
#   ¶11/¶51 (0,62)  mais collées au même fait matériel, donc similaires par la
#                   queue. Le retrait aurait tué le geste acquis à 4/4.
#
# Un paragraphe composé par le code se répète parce que c'est sa fonction. La
# règle n'est donc pas un seuil plus fin : c'est que le détecteur ne juge que ce
# que le MODÈLE a écrit. Le code sait ce qu'il a posé — il n'a pas à le deviner.
def _est_protege(para: str, proteges: tuple[str, ...] = ()) -> bool:
    """Ce paragraphe a-t-il été composé par le code ?

    Reconnu SANS rien savoir du run, pour que la grille — qui ne lit que des
    fichiers — protège les mêmes choses que l'assemblage :
      · l'en-tête daté, dont le format est notre propriété ;
      · le glissement, qui porte le marqueur de suspension — le code retire
        ceux que le modèle produit, donc tout « … » restant vient de nous ;
      · l'ancre, un paragraphe entièrement entre guillemets.
    `proteges` complète avec ce que l'appelant sait en plus.
    """
    para = para.strip()
    if ENTETE_ENTREE.match(para) or SUSPENSION.search(para):
        return True
    if re.fullmatch(r"[«\"“].{10,}[»\"”]", para, re.DOTALL):
        return True
    return any(p.strip() and (p.strip() in para or para in p.strip())
               for p in proteges)


def paragraphes_redits(texte: str, seuil: float = REDITE_SEUIL,
                       proteges: tuple[str, ...] = ()
                       ) -> list[tuple[int, int, float, str]]:
    """Paires de paragraphes qui racontent la même chose. (i, j, ratio, extrait).

    Le second membre de chaque paire est celui qu'on retirerait : il arrive
    après, donc c'est lui la redite.

    `proteges` : les fragments composés par le code (ancre, gestes). Les
    en-têtes sont reconnus tout seuls.
    """
    paras = [p.strip() for p in texte.split("\n\n") if p.strip()]
    out = []
    for i in range(len(paras)):
        if _est_protege(paras[i], proteges):
            continue
        for j in range(i + 1, len(paras)):
            if _est_protege(paras[j], proteges):
                continue
            m = difflib.SequenceMatcher(None, paras[i], paras[j])
            r = m.ratio()
            if r < seuil:
                continue
            bloc = m.find_longest_match(0, len(paras[i]), 0, len(paras[j])).size
            if bloc < REDITE_BLOC_MIN:
                continue
            out.append((i, j, round(r, 2), paras[j][:90]))
    return out


def phrases_redites(texte: str,
                    proteges: tuple[str, ...] = ()) -> list[tuple[int, int, str]]:
    """Phrases entières reprises d'un paragraphe à l'autre. (¶i, ¶j, phrase).

    Défaut plus net que la redite de paragraphe, et distinct : les ¶2 et ¶3 de
    S6-3 sont globalement différents (0,15 de similarité) mais partagent DEUX
    phrases au caractère près. Une moyenne sur le paragraphe entier les dilue ;
    il faut regarder les phrases.

    Les phrases courtes sont écartées : « Rien. » ou « Deux. » peuvent revenir
    sans être une redite — c'est même une figure du style.
    """
    paras = [p.strip() for p in texte.split("\n\n") if p.strip()]
    vues: dict[str, int] = {}
    out = []
    for i, p in enumerate(paras):
        if _est_protege(p, proteges):
            continue
        for ph in phrases(p):
            cle = re.sub(r"\W+", " ", ph.lower()).strip()
            if mots(ph) < 8:
                continue
            if cle in vues and vues[cle] != i:
                out.append((vues[cle], i, ph.strip()[:90]))
            else:
                vues.setdefault(cle, i)
    return out


# LA CITATION INVENTÉE. Le cahier est une matière fournie, jamais fabriquée :
# quand le modèle écrit un passage entre guillemets qui n'est ni l'ancre servie
# ni son verdict, il FABRIQUE du cahier — S7-3 a produit « "Les deux assiettes
# étaient bien là, sur l'égouttoir. Je ne me souviens pas de la deuxième." ».
#
# Drapeau, pas échec : l'ancre et le verdict final sont légitimement cités, et
# la falsification par le haut l'exige — un détecteur qui refuserait l'ancre
# serait le quatrième de la série à viser ce qu'il doit protéger.
CITATION = re.compile(r"[«\"“]([^«»\"”]{15,400})[»\"”]", re.DOTALL)


def citations_hors_ancre(texte: str, ancre: str = "",
                         verdict: str = "") -> list[str]:
    """Passages cités qui ne sont ni l'ancre servie ni le verdict rendu."""
    noyau_ancre = re.sub(r"[«»\"“”]", "", ancre).strip().lower()
    noyau_verdict = re.split(r"\s*\(", verdict or "")[0].strip().lower()
    # L'ANCRE EST LA PREMIÈRE CITATION ISOLÉE DE CHAQUE ENTRÉE — une seule, en
    # tête, posée par le code et remise là par le tampon après réparation.
    #
    # ⚠ « paragraphe entièrement cité » NE SUFFIT PAS : les deux citations
    # fabriquées de S7-3 sont elles aussi des paragraphes isolés, et exempter
    # par la forme seule les laissait passer toutes les deux. C'est le RANG qui
    # discrimine, parce que le code ne pose l'ancre qu'une fois et en premier.
    seuls, entree_vue = set(), set()
    e = 0
    for b in texte.split("\n\n"):
        if ENTETE_ENTREE.match(b.strip()):
            e += 1
            continue
        if re.fullmatch(r'\s*[«"“].{10,}[»"”]\s*', b, re.DOTALL) and e not in entree_vue:
            entree_vue.add(e)
            seuls.add(" ".join(b.split()).strip('«»"“” '))
    out = []
    for m in CITATION.finditer(texte):
        corps = " ".join(m.group(1).split())
        bas = corps.lower()
        if corps.strip("«»\"“” ") in seuls:
            continue
        if noyau_ancre and (bas in noyau_ancre or noyau_ancre in bas
                            or difflib.SequenceMatcher(
                                None, bas, noyau_ancre).ratio() > 0.75):
            continue
        if noyau_verdict and noyau_verdict in bas:
            continue
        out.append(corps[:100])
    return out


# MARQUES DÉPOSÉES. « L'enceinte Bluetooth » (tirage 6 du ch. 7) : une marque
# est un nom propre, donc L1 la voyait déjà — mais noyée parmi les noms propres,
# sans qu'on sache que c'en était une. Une marque dans ce roman est pire qu'un
# nom propre ordinaire : elle date le texte et le sort du monde clos de la
# maison. On la nomme pour pouvoir la retirer.
MARQUES = re.compile(
    r"\b(Bluetooth|Wi-?Fi|iPhone|iPad|Android|Spotify|Netflix|YouTube|"
    r"Google|Apple|Samsung|Facebook|Instagram|WhatsApp|Tupperware|Post-it|"
    r"Kleenex|Frigidaire|Thermos)\b", re.IGNORECASE)


# LA RECOPIE DU PROMPT — le contrôle qui manquait.
#
# Le tirage 6 du chapitre 7 s'ouvre sur la consigne d'ouverture, transcrite à
# 0,94 de similarité. Personne ne l'a vu avant la lecture : aucun lint ne
# comparait le texte produit à ce qu'on avait servi. On mesurait tout du texte
# sauf sa provenance.
#
# Le seuil est à 0,50 — les runs du chapitre 2, où la consigne décrivait
# légitimement le sujet, plafonnaient à 0,37.
RECOPIE_PROMPT_SEUIL = 0.50


def recopie_du_prompt(texte: str, prompt: str,
                      seuil: float = RECOPIE_PROMPT_SEUIL
                      ) -> list[tuple[float, str]]:
    """Phrases du texte trop proches d'une ligne du prompt servi.

    Compare PHRASE À LIGNE : une consigne se recopie par bloc, et une moyenne
    sur les textes entiers la diluerait au point de la rendre invisible.
    """
    lignes = [" ".join(l.split()) for l in prompt.splitlines()
              if len(l.split()) >= 8]
    out = []
    for ph in phrases(texte):
        p = " ".join(ph.split())
        if len(p.split()) < 8:
            continue
        meilleur = max((difflib.SequenceMatcher(None, p.lower(), l.lower()).ratio()
                        for l in lignes), default=0.0)
        if meilleur >= seuil:
            out.append((round(meilleur, 2), p[:100]))
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
        # DEUX ENTRÉES LE MÊME JOUR sont légitimes (session 7). Le chapitre 7
        # en fait sa structure : l'après-midi et la nuit de l'anniversaire,
        # « Samedi 14. » deux fois, et c'est le SECOND en-tête qui porte la
        # bascule audio. Le lint refusait cette forme — il aurait marqué en
        # défaut la structure exacte que le brief impose.
        #
        # Ce qui reste fautif : une date qui RECULE (B′C produisait
        # [8,7,7,7,7,9,10,7]), et un jour de semaine qui ne suit pas l'écart.
        if ecart_num == 0 and j1.lower() == j2.lower():
            continue
        if ecart_num < 0:
            fautes.append(f"{j1} {n1} → {j2} {n2} : la date recule")
        elif ecart_num == 0:
            fautes.append(f"{j1} {n1} → {j2} {n2} : même date, jour différent")
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

TABLE_PILOTAGE = str(BIBLE_DIR / "profond" / "chronologie-partie-double.md")

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
    out: dict[str, list[str]] = {"reserves": [], "quatuor": [], "verdict": [],
                                 # Session 6 : le décor générique, scopé lui
                                 # aussi (les mémos téléphoniques deviennent
                                 # légitimes au chapitre 5).
                                 "materiels": interdits_materiels(
                                     t, c["chapitre"])}

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


def _lexique_fuite(chemin: str = str(DATA_DIR / "lexique-fuite.txt")) -> list[str]:
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


# LE PIVOT RESTÉ OUVERT. Un glissement est une phrase qui s'approche du où ou du
# pourquoi et se coupe AVANT d'y arriver : le mot du départ n'y est pas, c'est
# tout l'objet du geste.
#
# ⚠ Ce motif s'AJOUTE à `CHAMP_DEPART` dans le contrôle L4, et il n'est pas
# cosmétique. Mesuré : les trois glissements écrits main et livrés par le
# protocole (« Je pourrais me demander ce qui, ce soir-là… », « Si je savais
# seulement pourquoi… », « Il faudrait que je relise le jour où elle… ») étaient
# TOUS LES TROIS classés « hors champ du départ » par la version précédente.
# L4 aurait donc affiché trois croix sur le geste enfin correct, et on en aurait
# conclu que le glissement ne marchait toujours pas — après trois sessions à
# chercher pourquoi.
PIVOT_OUVERT = re.compile(
    r"\b(ce qui|ce que|ce qu'|pourquoi|comment|où|quand|si je|si elle|"
    r"le jour|qui a|quelle|lequel)\b", re.IGNORECASE)


def glissements(entree: str) -> tuple[int, list[str]]:
    """(nombre d'occurrences, occurrences NON CONFORMES) pour une entrée.

    Une occurrence est conforme si, à moins de L4_FENETRE_MOTS mots, on trouve
    SOIT un terme du départ nommé, SOIT un pivot resté ouvert — c'est ce qui
    distingue le glissement (la pensée qui bute sur le où/pourquoi) d'une simple
    suspension de style. Les deux voies, parce que le geste peut nommer le
    départ ou s'arrêter juste avant, et que la seconde forme est la plus
    caractéristique.
    """
    occurrences = list(SUSPENSION.finditer(entree))
    hors_champ = []
    for m in occurrences:
        jetons_avant = entree[:m.start()].split()[-L4_FENETRE_MOTS:]
        jetons_apres = entree[m.end():].split()[:L4_FENETRE_MOTS]
        fenetre = " ".join(jetons_avant + jetons_apres)
        # Le pivot se cherche AVANT la coupe seulement : après, la phrase est
        # revenue au matériel, et un « où » qui suit ne dit rien du geste.
        avant = " ".join(jetons_avant)
        if not (CHAMP_DEPART.search(fenetre) or PIVOT_OUVERT.search(avant)):
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
        # --- Session 6 -----------------------------------------------------
        # Les instances descendues de la fiche servie vers l'outillage : elles
        # ne sont plus montrées au modèle, elles sont vérifiées en sortie.
        "marques": _extraits(MARQUES, texte),
        "etats_mentaux": sorted({(m.group(1) or m.group(2)).lower()
                                 for m in ETATS_MENTAUX.finditer(voix)}),
        # L'accumulation qui se résume. On rend le RATIO et non un booléen : le
        # seuil est un arbitrage (0,20), et une ligne de grille qui cache la
        # mesure derrière son seuil interdit de le rediscuter avec des chiffres.
        # L'étalon et les six accumulations de l'étage C sont à 0,00 ; le
        # sommaire de C2 est à 0,47.
        # LA REDITE (session 7). `_recoller` attrape la recopie ; ceci attrape
        # la re-narration — S6-3 range les deux assiettes deux fois, en d'autres
        # mots, et ses ¶2/¶3 partagent deux phrases entières.
        "paragraphes_redits": paragraphes_redits(texte),
        # Citations fabriquées : l'ancre et le verdict sont exemptés par
        # l'appelant, qui seul les connaît. Sans eux, tout passage cité compte —
        # la grille les fournit.
        "citations": citations_hors_ancre(texte),
        "accumulations_3p": [a for a in accumulations_l3(texte)
                             if not accumulation_a_la_premiere(a)[0]],
        "phrases_redites": phrases_redites(texte),
        "accumulations_abstraction": [
            accumulation_resumante(a)[0]
            for a in accumulations_l3(texte)],
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
        # --- Session 6 : les détecteurs descendus de la fiche vers l'outillage.
        # Les étalons DÉFINISSENT le style : tout ce qui mord ici est un faux
        # positif, et c'est cette clause qui a rattrapé le critère « propositions
        # verbales » du protocole — il rejetait l'accumulation de l'étalon 2.
        for cle, libelle in [("etats_mentaux", "état mental en apposition"),
                             ("attracteurs", "attracteur")]:
            if r[cle]:
                echecs.append(f"{titre} : {libelle} détecté à tort → {r[cle]}")
        if r["couples_m3"]:
            echecs.append(f"{titre} : couple décision-exécution à tort → "
                          f"{r['couples_m3']}")
        if interdits_materiels(normalise(texte), chapitre=2):
            echecs.append(f"{titre} : interdit matériel détecté à tort → "
                          f"{interdits_materiels(normalise(texte), 2)}")
        for ratio in r["accumulations_abstraction"]:
            if ratio > ACC_ABSTRAIT_MAX:
                echecs.append(f"{titre} : accumulation jugée résumante à tort "
                              f"({ratio:.0%} d'items abstraits)")

    # LES CAS CONNUS, EN NÉGATIF. Un détecteur muet sur les étalons peut être
    # muet partout : le vert ci-dessus ne distingue pas « rien à trouver » de
    # « incapable de trouver ». Chaque motif doit donc MORDRE sur le défaut
    # qu'on a lu à la main, et les extraits ci-dessous sortent tous des runs de
    # l'étage C.
    for attendu_vrai, texte, quoi in [
        (True, "J'ai décidé de vérifier par moi-même. Dans la cuisine, "
               "l'égouttoir était là. Incrédule, je les ai comptées à nouveau.",
         "couple M3 au passé composé (C1)"),
        (False, "Je vais vérifier dans la cuisine. L'égouttoir, ce soir : "
                "deux assiettes.", "futur proche — conforme (C3)"),
        (False, "Je décide de reprendre les faits dans l'ordre. J'ai préparé "
                "le dîner, j'ai mangé.", "décision de carnet — conforme (C2)"),
    ]:
        trouve = bool(couples_decision_execution(texte))
        if trouve is not attendu_vrai:
            echecs.append(f"cas connu « {quoi} » : "
                          f"{'raté' if attendu_vrai else 'faux positif'}")
    for motif_attendu, texte, quoi in [
        (True, "L'égouttoir, ce soir : deux assiettes.", "quantité en lettres"),
        (True, "Demain, tout sera clair.", "attracteur du lendemain"),
        (True, "je me demandais si je devenais folle", "attracteur de la folie"),
        (True, "Perplexe, je repose le cahier.", "état mental en apposition"),
    ]:
        r = analyse(texte)
        vu = bool(r["precision"] or r["attracteurs"] or r["etats_mentaux"])
        if vu is not motif_attendu:
            echecs.append(f"cas connu « {quoi} » : raté")
    for terme, texte in [("télévision", "j'ai allumé la télévision"),
                         ("travail", "Je suis revenue du travail"),
                         ("sac à main", "j'ai posé mon sac à main"),
                         ("barquette", "j'ai sorti une barquette de lasagnes")]:
        if not interdits_materiels(texte, chapitre=2):
            echecs.append(f"cas connu « {terme} » : interdit matériel raté")
    # Le scope par chapitre doit se RELÂCHER, pas seulement se serrer.
    if not interdits_materiels("j'ai regardé mon téléphone", chapitre=2):
        echecs.append("cas connu « téléphone au ch. 2 » : raté")
    if interdits_materiels("j'ai regardé mon téléphone", chapitre=5):
        echecs.append("cas connu « téléphone au ch. 5 » : faux positif — les "
                      "mémos deviennent légitimes, le scope ne s'ouvre pas")
    # LA REDITE — session 7. Les deux sens, parce que le contrôle est bloquant
    # et qu'il RETIRE du texte : un faux positif coûte un paragraphe de récit.
    _VRAI = ("Je range les deux assiettes dans le lave-vaisselle, en prenant "
             "soin de les placer côte à côte.",
             "En attendant, je décide de ranger les deux assiettes dans le "
             "lave-vaisselle. Je les place côte à côte, en prenant soin de bien "
             "les essuyer avant de les mettre à l'intérieur.")
    _FAUX = ("Je relis l'entrée d'hier. Ma mémoire dit une assiette.",
             "Je suis rentrée, j'ai posé le cahier, j'ai préparé le dîner.")
    if not paragraphes_redits("\n\n".join(_VRAI)):
        echecs.append("cas connu « la même action rangée deux fois » (S6-3 "
                      "¶10/¶13) : redite non détectée")
    if paragraphes_redits("\n\n".join(_FAUX)):
        echecs.append("cas connu « deux constats distincts » : FAUX POSITIF — "
                      "le contrôle retirerait un paragraphe de récit")
    if not phrases_redites(
            "Je me souviens pourtant distinctement d'avoir mangé seule hier "
            "soir.\n\nJe me souviens pourtant distinctement d'avoir mangé "
            "seule hier soir. Et pourtant."):
        echecs.append("cas connu « phrase reprise d'un ¶ à l'autre » (S6-3 "
                      "¶2/¶3) : non détectée")
    # LES ARTEFACTS DU CODE ne sont jamais une redite — falsifié parce que sans
    # cette protection, les trois plus fortes similarités de S6-C étaient
    # l'en-tête, l'ancre et le glissement : le retrait aurait supprimé la
    # bascule audio et le geste acquis à 4/4.
    _ARTEFACTS = "\n\n".join([
        "Mardi 12. Ciel couvert.", "Mercredi 13. Pluie fine.",
        "« Deux assiettes mises, sans y penser. »",
        "« Deux assiettes mises, sans y penser. »",
        "Si je savais seulement pourquoi… L'assiette est sèche. Je la range.",
        "Je pourrais me demander ce qui, ce soir-là… L'assiette est sèche. "
        "Je la range."])
    if paragraphes_redits(_ARTEFACTS) or phrases_redites(_ARTEFACTS):
        echecs.append("cas connu « artefacts du code » : FAUX POSITIF — "
                      "en-tête, ancre ou glissement comptés comme redite")

    # LES ATTRACTEURS de la session 7 : trois runs sur quatre ont fermé sur
    # cette famille sans une croix, à un mot près du motif attrapé.
    for _t in ("demain sera un autre jour", "demain sera une nouvelle journée",
               "demain sera une journée meilleure", "à la lumière du jour"):
        if not ATTRACTEURS.search(_t):
            echecs.append(f"cas connu « {_t} » : attracteur raté")
    for _t in ("demain je relirai le cahier", "une journée ordinaire",
               "la lumière du couloir"):
        if ATTRACTEURS.search(_t):
            echecs.append(f"cas connu « {_t} » : FAUX POSITIF d'attracteur")

    # --- MICRO-LOT PRÉ-RÉPÉTITION (2026-08-26) ------------------------------
    # Les trois cibles nommées par la grille remplie de la session 7.
    if not couples_decision_execution(
            "Je me lève, décidée à vérifier cette erreur. "
            "Je compte les assiettes sur l'égouttoir."):
        echecs.append("cas connu « couple M3 au participe » (S7-1) : raté — "
                      "le motif ne borne pas « décidée à »")
    if accumulation_a_la_premiere(
            "Elle est revenue à vingt heures, a refermé le cahier, "
            "posé la lampe, compté les assiettes")[0]:
        echecs.append("cas connu « accumulation à la troisième personne » "
                      "(S7-3) : raté")
    if not accumulation_a_la_premiere(
            "Je suis rentrée, j'ai posé le cahier, j'ai compté les assiettes")[0]:
        echecs.append("cas connu « accumulation à la première personne » : "
                      "FAUX POSITIF — une accumulation conforme rejetée")
    _AVEC_CIT = ('Mardi 12. Ciel couvert.\n\n« Deux assiettes mises. »\n\n'
                 'Je relis le cahier.\n\n'
                 '"Les deux assiettes étaient bien là, sur l\'égouttoir."\n\n'
                 'Erreur de relevé.')
    _cits = citations_hors_ancre(_AVEC_CIT, verdict="erreur de relevé")
    if len(_cits) != 1:
        echecs.append(f"cas connu « citation inventée » (S7-3) : {len(_cits)} "
                      "signalement(s) au lieu d'un — l'ancre est-elle exemptée "
                      "par son rang ?")
    for _t in ("Je referme le carnet. Bonne nuit.",):
        if not ATTRACTEURS.search(_t):
            echecs.append("cas connu « Bonne nuit » : attracteur raté")
    if ATTRACTEURS.search("j'ai passé une bonne nuit de sommeil"):
        echecs.append("cas connu « une bonne nuit de sommeil » : FAUX POSITIF")

    # --- LOT ORTHOGONAL DU CHAPITRE 7 (2026-08-27) --------------------------
    # L'image d'arme : le couperet contourné par la métaphore, relevé deux fois
    # (session 5 et tirage 6 du ch. 7). Le lint des méta-termes ne peut pas le
    # voir — ce n'est pas un mot d'atelier.
    for _t in ("le coup de couteau : je n'ai pas rêvé", "comme une lame",
               "comme un couteau", "ce n'était pas un rêve"):
        if not ATTRACTEURS.search(_t):
            echecs.append(f"cas connu « {_t} » : attracteur raté")
    # Et les objets qui ne sont PAS des images : une lame de parquet, un couteau
    # posé sur la table. Un contrôle bloquant qui confond les deux retire du
    # récit.
    for _t in ("une lame de parquet", "le couteau est sur la table",
               "j'ai rêvé de la maison"):
        if ATTRACTEURS.search(_t):
            echecs.append(f"cas connu « {_t} » : FAUX POSITIF d'attracteur")
    if not MARQUES.search("l'enceinte Bluetooth allumée"):
        echecs.append("cas connu « Bluetooth » (tirage 6 du ch. 7) : "
                      "marque déposée ratée")
    if MARQUES.search("l'enceinte du salon, allumée"):
        echecs.append("cas connu « enceinte sans marque » : FAUX POSITIF")

    # --- MÉTHODE DU MOUVEMENT (2026-08-27) ----------------------------------
    # LA RECOPIE DU PROMPT, sur son cas connu : le tirage 6 du chapitre 7 a
    # transcrit la consigne d'ouverture à 0,94, et rien ne le voyait.
    _CONS = ("Le soir, le cahier ouvert : la phrase relue, l'écart entre ce "
             "qu'elle lit et ce dont elle se souvient, la chaise repoussée.")
    _TXT = ("Le soir, le cahier ouvert : la phrase relue, l'écart entre ce que "
            "je lis et ce dont je me souviens, la chaise repoussée.")
    if not recopie_du_prompt(_TXT, _CONS):
        echecs.append("cas connu « consigne recopiée » (tirage 6 du ch. 7) : "
                      "la recopie du prompt n'est pas détectée")
    if recopie_du_prompt("Je relis l'entrée d'hier. Ma mémoire dit une "
                         "assiette, un dîner seule.", _CONS):
        echecs.append("cas connu « texte propre » : FAUX POSITIF de recopie")

    # LA MACHINERIE dans un contexte servi. Le §5 du brief v2 la servait tel
    # quel ; l'ancienne garde n'en voyait qu'un mot sur dix.
    for _t in ("L3 exempté par la table de pilotage", "interdits bloquants",
               "possédés par le code, tamponnés en dernier"):
        if not MACHINERIE.search(_t):
            echecs.append(f"cas connu « {_t[:34]} » : machinerie non détectée")
    # « la table » est un MEUBLE dans ce roman — et l'un des objets du ch. 7.
    for _t in ("les photos sont sur la table", "la table du séjour"):
        if MACHINERIE.search(_t):
            echecs.append(f"cas connu « {_t} » : FAUX POSITIF de machinerie")

    # L4 CONTRE LA BANQUE. Les trois glissements écrits main sont la définition
    # du geste : L4 doit les compter conformes. La version précédente les
    # classait tous les trois « hors champ du départ » — un vert impossible
    # transformé en trois croix sur le geste enfin correct.
    for _appr in ("Je pourrais me demander ce qui, ce soir-là",
                  "Si je savais seulement pourquoi",
                  "Il faudrait que je relise le jour où elle"):
        _n, _hors = glissements(
            f"J'ai mangé seule. {_appr}… L'assiette est sèche. Je la range.")
        if _n != 1 or _hors:
            echecs.append(f"cas connu « banque du glissement » : "
                          f"« {_appr}… » compté {_n} fois, {len(_hors)} hors "
                          f"champ — L4 refuse la définition du geste")
    if accumulation_resumante(
            "perplexité, concentration sur les détails, rappel des faits, "
            "fatigue, panique, respiration calme, explication rationnelle, "
            "corps qui parle, verdict d'erreur de relevé, épuisement, "
            "endormissement, vigilance")[0] <= ACC_ABSTRAIT_MAX:
        echecs.append("cas connu « sommaire nominal de C2 » : raté")

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
    parser.add_argument("--fiche", default=str(BIBLE_DIR / "style-auteur.md"))
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
