#!/usr/bin/env python3
"""Deterministic lint of the style grid, without any model.

Fills mechanically PART of the `_scene-test-style.md` grid and cites its
evidence. The rest is left blank: that is the reviewer's judgement, and an
approximate pre-evaluation would cost more than it earns (a chunk of the
sheet that did nothing would get hardened).

Doctrine, extending the lesson learned with Qwen: give the small model a
READING task, never an INFERENCE task. Here one step lower: no model at all,
hence no inference false positive. What is mechanically decidable is decided;
what requires understanding the text goes back to the reviewer as is.

Three certainty levels, and they are displayed:
  EXACT     literal lists taken from the sheet, reliable decision.
  CANDIDAT  heuristic, to confirm by eye (passé simple).
  MANUEL    not automatable, left blank.

The module never MODIFIES the text: we measure what the model produces, not
what a post-filter rescues.

Usage:
  factory eval lint experiments/runs/<date>-<slug>/run-1.md
  factory eval lint --references                   # self-test against the sheet

Stdlib only.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

# delint() is reused rather than copying its detectors; factory.text imports only `re`.
from factory.paths import BIBLE_DIR, DATA_DIR
from factory.text import delint

# --- Thresholds --------------------------------------------------------------

# "Accumulation sentence": measurable proxy of the sheet's signature rupture
# (the sheet: one long sentence built by accumulating clauses juxtaposed with
# commas). Both thresholds are calibrated to separate reference 2 (the target)
# from the three other references; `--references` checks exactly that.
# Lowering either would let ordinary sentences through.
ACC_COMMAS = 4
ACC_WORDS = 45

# "Cleaver sentence": the sheet says « trois à six mots ».
CLEAVER_MIN, CLEAVER_MAX = 3, 6

# --- Session 3: L1-L4 controls of the chapter 2 calibration protocol ---------

# L3 takes the thresholds the sheet v3 states itself (60 words, 6 commas),
# stricter than those calibrated in session 1 (45/4). Both coexist: the
# historical line keeps sessions 1 and 2 comparable, L3 applies the written
# rule. Aligning them would erase the comparison.
L3_WORDS, L3_COMMAS = 60, 6

# L4: the drift is the ONLY allowed use of suspension points. The marker is
# countable only because it is unambiguous, hence the proximity measure with
# the departure field rather than a bare count.
L4_WORD_WINDOW = 15
DEPARTURE_FIELD = re.compile(
    r"\b(partie|parties|départ|departs|départs|absence|absente|quittée|quitté|"
    r"quitter|plus là|s'en est allée)\b",
    re.IGNORECASE,
)
SUSPENSION = re.compile(r"…|\.\.\.")

# L1: a capital is a PROPER NOUN candidate if it opens neither the text, nor a
# sentence, nor a line. Deliberate heuristic: the protocol demands zero
# tolerance, so flag wide and cite the context so the reading decides. `Je` is
# excluded: a pronoun, never a proper noun, and it shows up capitalised after a
# sentence cut the splitter sometimes misses.
L1_EXCEPTIONS = {"Je", "J", "L", "D", "C", "N", "S", "M", "T", "Y"}
UPPERCASE = re.compile(r"\b([A-ZÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ][\wàâäéèêëîïôöùûüç'’-]+)")

# A journal entry header: a short line carrying a date. Used for the per-entry
# re-scope (D1); without it L3 and L4 would count over the whole chapter and a
# two-entry chapter would be judged as one block.
# NORMALISED HEADER, composed by code (ADR-0018). Canonical format:
# « Jeudi 7. Beau temps. »: weekday, number, period, weather, period. Never
# the year.
#
# It replaced the session 3 date heuristic because the SAME marker serves three
# things: L3 entry counting, structure validation in the grid, and the audio
# switch point (the second header of chapter 7, ADR-0013). One shared
# deterministic marker beats three heuristics that diverge at showtime.
DAYS = r"Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche"
ENTRY_HEADER = re.compile(
    rf"^\s*(?:\*{{0,2}})?({DAYS})\s+(\d{{1,2}})\.\s+.{{2,40}}\.\s*(?:\*{{0,2}})?$",
    re.MULTILINE,
)


# --- Literal lists (source: the *Interdits* chunk of style-auteur.md, --------
# --- completed by the test-style package grid) -------------------------------

PASTICHE = re.compile(
    r"\b(indicible[s]?|innommable[s]?|abomination[s]?|t[ée]n[èe]bres|"
    r"insondable[s]?|ancestral(?:e|es|aux)?|effroi|"
    r"malaise\s+diffus)\b",
    re.IGNORECASE,
)

# TENSE variants count as much as the formula: « je ne peux m'empêcher »
# escaped the detector at session 3 run 3, which expected only the imperfect.
# A tic does not change nature by changing conjugation.
# The NEGATION slips in between and the pattern missed it: B′C wrote
# « je ne peux PAS m'empêcher de penser ». A negation adverb between auxiliary
# and verb was enough to let the tic through, the second consecutive run to do so.
AI_TICS = re.compile(
    r"(un m[ée]lange de\b|quelque chose en (?:moi|elle)\b|"
    r"(?:je|elle) ne (?:pouvais|pouvait|peux|peut|pourrais|pourrait)"
    r"(?: pas| plus| jamais)? [sm]'emp[êe]cher de\b|"
    r"une part de (?:moi|elle)\b|"
    r"c'(?:est|était) alors que (?:je|elle) (?:compris|comprit|sus|sut|"
    r"comprenais|comprends)\b|"
    r"ce fut alors que\b|il (?:y avait|y a) quelque chose de\b)",
    re.IGNORECASE,
)

# FORM-FILLING BY PARAPHRASE. Banning meta-terms did not kill form-filling
# mode, it mutated it: B′C wrote « Le coup de couteau est le suivant : »,
# « couperet » translated into a blade to dodge the lint. Catch the STRUCTURE,
# not the word: announcing what follows instead of writing it is the
# form-filling gesture, whatever the field is called.
FORM = re.compile(
    r"\b\w[^.!?\n]{0,60}\best (?:le|la|les) suivant(?:e|s|es)?\s*:",
    re.IGNORECASE,
)

# Adverbial dialogue tag: « s'exclama-t-il nerveusement ». The sheet imposes
# « dit-il », « a-t-elle répondu » and nothing more.
#
# `je` is in the pronoun list because the narration is FIRST person: « ai-je
# répondu distraitement » is the form nemo actually produces, and omitting it
# let the tag through for a whole run. The optional intervening word covers
# « ai-je répondu distraitement » (participle between inversion and adverb).
ADVERBIAL_INCISE = re.compile(
    r"-(?:t-)?(?:il|elle|on|je|ils|elles)\s+(?:\w+\s+)?\w+ment\b",
    re.IGNORECASE,
)

# Same prohibition, dodged: nemo rewrites the adverb as a prepositional group
# (« a-t-elle répété d'un ton surpris », « a-t-elle dit d'une voix enjouée »).
# Found rereading the runs, in two draws the grid had marked as held. A ban
# worded by grammatical CATEGORY is dodged by a change of category; detect the
# intent.
# Anchoring to a SPEECH VERB is mandatory: without it the pattern catches
# « J'ai refermé le cahier d'un geste sec », ordinary narration the sheet
# forbids nowhere. Found in run 2, and the stake was not cosmetic: that extra
# cross moved the tag from 1 run in 3 (noise) to 2 in 3 (harden the sheet),
# inverting the verdict.
PREPOSITIONAL_INCISE = re.compile(
    r"\b(?:dit|dis|dire|disant|r[ée]pond(?:it|u|re)|r[ée]p[ée]t(?:a|[ée])|"
    r"demand(?:a|[ée])|conclu[ts]?|lan[çc](?:a|[ée])|murmur(?:a|[ée])|"
    r"ajout(?:a|[ée])|repri[ts]|s'exclam(?:a|[ée])|soupir(?:a|[ée])|"
    r"souffl(?:a|[ée])|fit|questionn(?:a|[ée]))\b"
    r"[^.!?]{0,20}?"
    r"(?:d'un|d'une|sur un|sur une)\s+(?:ton|voix|air|sourire|souffle)\s+\w+",
    re.IGNORECASE,
)

# Missing elision: « je te appelle » instead of « je t'appelle ». A French
# defect `delint()` does not see (it only looks for English and glued tokens).
# The exclusions are the words before which French does NOT elide: `un/une`
# (`le un`, `la une`), aspirated h, `onze`, `huit`, `oui`, `yacht`.
#
# KNOWN LIMIT: the other form of the defect, the swallowed apostrophe that
# glues words (« jeté lemballage »), is NOT detected. Recognising it needs a
# French lexicon to know that « emballage » is a word; without a dictionary any
# detector here would be noise. Better a missing line than a wrong one.
MISSING_ELISION = re.compile(
    r"\b(je|me|te|se|le|la|ne|de|que|ce)\s+"
    r"(?!un\b|une\b|onze|huit|oui|yacht|yaourt|hasard|haut|haine|héros|"
    r"hibou|hall|hangar)"
    r"([aeiouéèêàâîôû]\w+)",
    re.IGNORECASE,
)

# Exact hour or quantity: the « précision maniaque » the sheet demands.
PRECISION = re.compile(
    r"\b\d{1,2}\s*h(?:\s*\d{2})?\b|"
    r"\b\d+[,.]?\d*\s*(?:heures?|minutes?|secondes?|jours?|"
    r"centim[èe]tres?|m[èe]tres?|kilom[èe]tres?|degr[ée]s?|euros?|"
    r"grammes?|litres?)\b|"
    r"\b(?:une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze)\s+"
    r"heures?(?:\s+\w+)?\b|"
    # QUANTITIES SPELLED OUT before a common noun (session 6). The pattern only
    # accepted a written number followed by « heures »: « L'égouttoir, ce soir :
    # deux assiettes. » did not count. Yet that is the chapter's inventory line,
    # the most characteristic motif of this voice and the brief's imposed fact.
    # The « précision maniaque » lint ignored the very example the protocol
    # gives.
    #
    # The noun is required (two words at least) so as not to pick up « deux »
    # alone, which is everywhere in a chapter about two plates; determiners are
    # excluded after the number (« deux de plus » is not a counted quantity).
    r"\b(?:deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze)\s+"
    r"(?!de\b|des\b|d'|à\b|au[x]?\b|fois\b|heures?\b)[a-zàâçéèêëîïôûùüœ]{3,}\b",
    re.IGNORECASE,
)

# --- Passé simple: UNAMBIGUOUS forms only -------------------------------------
# Prohibition no. 1 of the sheet, and the costliest to flag wrongly: a false
# positive would send someone hardening a chunk that is fine. So `dit`, `vit`,
# `rit`, `suit`, `fuit`, which are ALSO present tense, and the `-ra` forms
# (future) are deliberately left out.
PS_IRREGULARS = re.compile(
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
# `-èrent` exists only in the passé simple: no other French form ends that way.
# Safe detector.
PS_ERENT = re.compile(r"\b\w+[èe]rent\b", re.IGNORECASE)

# `-irent` / `-urent` are mostly passé simple (partirent, sortirent,
# coururent) but collide with the PRESENT 3pl of -irer/-urer verbs. The set
# below is that collision, enumerated: without it « ils murmurent » and « ils
# admirent » would pass for passé simple. The one place in the module where a
# list's completeness conditions correctness, hence CANDIDATES rather than a
# verdict.
PS_PRESENT_HOMONYMS = {
    "tirent", "attirent", "retirent", "étirent", "soutirent",
    "soupirent", "expirent", "respirent", "inspirent", "aspirent",
    "admirent", "chavirent", "virent", "délirent",
    "assurent", "rassurent", "murmurent", "susurrent", "procurent",
    "endurent", "mesurent", "figurent", "épurent", "saturent", "durent",
}
PS_IRENT_URENT = re.compile(r"\b\w+[iu]rent\b", re.IGNORECASE)

# Passé simple of -er verbs, anchored to a subject to avoid noise (« la »,
# « déjà », « voilà »). `{3,}` drops « il a » / « elle va »; excluding `-ra`
# drops the future (« elle regardera »).
PS_ANCHOR = re.compile(
    r"\b(?:il|elle|on|ils|elles)\s+((?!\w*ra\b)\w{3,}a)\b", re.IGNORECASE
)

# Past participle / 1st-2nd person passé simple collision: « pris », « mis »,
# « compris » are BOTH the participle (« j'ai pris ») and the passé simple
# (« je pris »). Found in real runs: the word came out in 3 draws of 4, always
# in the passé COMPOSÉ, i.e. always wrongly flagged. An auxiliary just before
# decides: participle, not passé simple.
PS_AMBIGUOUS_PARTICIPLES = {"pris", "mis", "fis", "vins", "pus", "sus", "dus",
                         "appris", "compris", "remis", "repris", "promis"}
AUXILIARY = re.compile(
    r"\b(?:ai|as|a|avons|avez|ont|avais|avait|avions|aviez|avaient|"
    r"aurai|aura|aurait|eu|est|es|suis|sommes|êtes|sont|était|étais|"
    r"étaient|étions|serai|serait|soit|été)\s+(?:\w+\s+)?$",
    re.IGNORECASE,
)
# First person, the most useful here since the sheet imposes « je ». The passé
# simple form (`je regardai`) differs from the future (`je regarderai`) only by
# the preceding `r`, and from the imperfect (`je regardais`) only by the final
# `s`: hence excluding `-rai` and anchoring strictly to `je ` (drops `j'ai`).
PS_FIRST_PERSON = re.compile(
    r"\bje\s+((?!\w*rai\b)\w{3,}ai)\b", re.IGNORECASE
)
# Proper-noun subject + elided object pronoun: « Élara l'écouta ». Anchoring
# to the PRONOUN is what makes the pattern safe: without it « Le cinéma »,
# « La véranda » or « Un agenda » would be flagged as passé simple, and a false
# positive against prohibition no. 1 sends someone hardening an innocent chunk.
PS_PROPER_NOUN = re.compile(
    r"\b[A-ZÉÈÀÂÎÔÛ]\w{2,}\s+(?:l'|lui\s|me\s|m'|se\s|s'|nous\s|vous\s|leur\s)"
    r"((?!\w*ra\b)\w{3,}a)\b"
)

# --- Splitting ---------------------------------------------------------------

_SENTENCE_END = re.compile(r"[.!?…]+(?:\s*[»\"'])?")
_APOSTROPHES = str.maketrans({"’": "'""'", "ʼ": "'""'"})


def normalize(text: str) -> str:
    """Typographic apostrophes to ASCII, at CONSTANT length.

    Models alternate « l’entrée » and « l'entrée » between draws; without this
    normalisation half the patterns would miss at random. The substitution is
    1:1 in characters, so positions stay valid to cite the ORIGINAL text.
    """
    return text.translate(_APOSTROPHES)


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return "\n".join(lines[i + 1:]).strip()
    return text.strip()


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def sentences(text: str) -> list[str]:
    """Naive sentence split. Enough for COUNTING (length, commas)."""
    out, start = [], 0
    for m in _SENTENCE_END.finditer(text):
        piece = text[start:m.end()].strip()
        if piece:
            out.append(piece)
        start = m.end()
    rest = text[start:].strip()
    if rest:
        out.append(rest)
    return out


def words(sentence: str) -> int:
    return len([m for m in re.split(r"\s+", sentence.strip()) if m])


def without_dialogue(text: str) -> str:
    """Remove dialogue lines to isolate the narrative voice.

    Three forms to remove. The first two are the sheet's: « … » spans and lines
    opened by an em dash. The third, straight double quotes, is not in the
    sheet but is what nemo produces in practice (seen in run 1): without it a
    « ! » inside a line of dialogue would count as an exclamation mark outside
    dialogue, a defect invented from nothing. The detector must read the text
    as it comes out, not as we wished it.
    """
    text = re.sub(r"«.*?»", " ", text, flags=re.DOTALL)
    text = re.sub(r'"[^"\n]*"', " ", text)      # straight quotes, single line
    kept = [l for l in text.splitlines()
               if not re.match(r"^\s*[—–-]\s", l)]
    return "\n".join(kept)


_ACC_REFERENCE: str | None = None


def accumulation_reference(sheet: str = str(BIBLE_DIR / "style-auteur.md")) -> str:
    """The reference accumulation, read from the sheet (loaded once).

    Used to detect COPYING. Loaded from the sheet rather than pasted here: the
    reference moves with the sheet, and a detector comparing to a stale version
    detects nothing.
    """
    global _ACC_REFERENCE
    if _ACC_REFERENCE is None:
        _ACC_REFERENCE = ""
        path = Path(sheet)
        if path.is_file():
            text = normalize(path.read_text(encoding="utf-8"))
            # Strip markup before splitting: the references live in `> ` blocks
            # under a bold title, and keeping it would glue « **Étalon 2 — …** »
            # to the head of the reference sentence.
            text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
            text = re.sub(r"^\s*\*\*.*?\*\*\s*$", "", text, flags=re.MULTILINE)
            candidates = [p for p in sentences(text)
                         if p.count(",") >= ACC_COMMAS and words(p) >= ACC_WORDS]
            if candidates:
                _ACC_REFERENCE = max(candidates, key=words).strip()
    return _ACC_REFERENCE


def reference_copy(sentence: str, threshold: float = 0.6) -> float:
    """Similarity of a sentence to the reference accumulation, 0 to 1.

    Born of a failure of this module: the reproach loop produced two
    « réussites » that were the reference copied CHARACTER FOR CHARACTER, in a
    scene about something else (the reference tells of keys, the scene of a
    coffee maker). Counting commas says nothing of meaning; a form detector
    must be able to say when the form was obtained by plagiarism.
    """
    ref = accumulation_reference()
    if not ref or not sentence:
        return 0.0
    r = difflib.SequenceMatcher(None, sentence.lower(), ref.lower()).ratio()
    return r if r >= threshold else 0.0



# --- Session 5, item 7: new lints --------------------------------------------

# META-TERMS. FABRICATION vocabulary has no place in the prose: « Couperet :
# erreur de relevé. » is a filled form, not a written entry. List frozen by the
# protocol. « constat » and « verdict » are deliberately ABSENT: they are the
# words of her proofreading trade, hence her language; banning them would
# impoverish the voice we are after.
META_TERMS = re.compile(
    r"\b(couperets?|squelettes?|beats?|ancres?|notation physiologique|"
    r"mat[ée]riaux?|briefs?)\b", re.IGNORECASE)

# THE MACHINERY: what must never appear in a SERVED context.
#
# Distinct from meta-terms: those are literary workshop words (the cleaver,
# the skeleton), these are the names of our own controls. §5 of brief v2
# served them all: « L1, L2, lexiques, attracteurs, interdits matériels bloquants »,
# « L3 exempté par la table », « possédés par le code, tamponnés en dernier ».
# That section was written for the implementer, not the model; serving it as
# is teaches it our lints.
#
# The previous entry guard saw one word in ten of these.
MACHINERY = re.compile(
    # « la table » alone is FURNITURE in this novel, one of the chapter 7
    # objects even. Only « la table de pilotage » is machinery.
    r"\bL[1-4]\b|\bla table de pilotage\b|\ble code\b|\bbloquants?\b"
    r"|\blint\w*\b|\bexempt[ée]\w*\b|\btamponn[ée]\w*\b|\blexiques?\b"
    r"|\bgrille\b|\bpipeline\b|\bhors [ée]chelle\b|\bcomposeur\b"
    r"|\bentrees_spec\b|\bentry_specs\b|\bv[ée]tos?\b", re.IGNORECASE)

# ATTRACTORS: formulas the model slides into by itself, noted while reading
# the runs. Not language faults but training tics; « Demain est un autre jour »
# was heard aloud. By FAMILIES, no longer by literals (session 6): the previous
# version held three exact strings, so « Demain tout sera clair » (C2's
# accumulation) and « je devenais folle » (run C, before fixes) both passed.
# The second is forbidden BY NAME in the sheet: the ban was served, did not
# hold, and no lint saw it. Name the family, not the occurrence that was read.
ATTRACTORS = re.compile(
    # madness named: « devenir folle », « perdre la tête / la raison »
    r"(devenir folle|devenais? folle|devenue folle|suis folle|"
    r"perdre la t[êe]te|perds? la t[êe]te|perdre la raison|"
    # THE MORNING THAT RESOLVES: the sheet forbids a soothed entry.
    #
    # Widened in session 7; the family was larger than believed: the previous
    # version knew only « demain EST un autre jour », so THREE session 6 runs
    # of four closed with this attractor without a cross:
    # « demain sera une journée meilleure » (S6-1), « demain sera un autre jour »
    # (S6-2), « demain sera une nouvelle journée » and « à la lumière du jour »
    # (S6-3). One word between caught and passed. The adjective comes BEFORE or
    # AFTER the noun (« une nouvelle journée », « une journée meilleure », S6-1
    # wrote the second). Both orders, else the pattern catches half the family
    # and the green lies.
    r"demain (?:est|sera|serait)(?: un| une)? (?:"
    r"(?:autre|nouvelle?|meilleure?)(?: jour(?:née)?)?"
    r"|jour(?:née)? (?:meilleure?|nouvelle?|autre))|"
    r"demain,? tout (?:sera|ira|s'[ée]clairera)|"
    r"demain,? je (?:saurai|comprendrai|verrai)|"
    r"à la lumière du jour|"
    # THE CONSOLING ADDRESS. The last line closes, it does not console, and
    # « Bonne nuit. » is the purest form of the opposite: the notebook stops
    # being a record and becomes an address. Seen in S7-1, in the same sentence
    # and a half as the lexical leak and the morning attractor. Anchored at
    # SENTENCE START: « Bonne nuit. » is an address,
    # « une bonne nuit de sommeil » a fact. Without the anchor the pattern
    # caught both.
    r"(?:^|[.!?…»\n]\s*)(?:bonne nuit|bonne soirée|dors bien|à demain)\b)|"
    # THE WEAPON IMAGE: the cleaver dodged through metaphor. The meta-term lint
    # does not see « le coup de couteau : je n'ai pas rêvé » (chapter 7 draw 6)
    # because it is not a workshop word, it is its image. The same dodge was
    # measured in session 5 (« Le coup de couteau est le suivant : »). Banning
    # a word brings it back as a figure. « une lame » alone is an object
    # (« une lame de parquet »); the COMPARISON makes the image, so require
    # `comme`, or `coup`.
    r"(?:coup de couteau|comme un couteau|comme une lame|comme un couperet|"
    r"coup de hache|couperet qui tombe|tranch\w+ comme)|"
    # THE DREAM DENIAL. « Je n'ai pas rêvé » is a reassuring closure: it
    # settles the doubt the entry must leave open.
    r"je n'ai pas r[êe]v[ée]|ce n'[ée]tait pas un r[êe]ve|je ne r[êe]ve pas|"
    # the maritime metaphor, a tic measured in the first sessions
    r"(bou[ée]e|oc[ée]an)", re.IGNORECASE)

# « je décide de »: capped at ONE occurrence per entry (owner arbitration,
# 2026-08-18). B1 carried four, each followed by its execution.
I_DECIDE = re.compile(r"\bje d[ée]cide de\b", re.IGNORECASE)

# DECISION-EXECUTION PAIR, as a non-blocking CANDIDATE. Rule M3 says the
# effect of « décision sans geste » lives in the GAP between the noted decision
# and the state observed afterwards; the pair closes it. Establishing it needs
# understanding the text: spot the decision's infinitive, look for it
# conjugated in the following sentences, and FLAG. M3 stays the manual line
# that decides; a false positive against a blocking line at stage C would cost
# a run.
# The noted decision, in the PRESENT as in the PASSÉ COMPOSÉ (session 6). C1
# wrote « J'ai décidé de vérifier par moi-même » and the detector only bounded
# the present: the grid had to record the pair by hand.
#
# « je vais » is deliberately NOT included: C3 writes
# « Je vais vérifier dans la cuisine » and the grid judges it conforming. The
# near future is a movement, not a resolution noted in the notebook; including
# it would have failed a run the human reading had validated.
# THIRD FORM: the APPOSED PARTICIPLE (session 7 bis). « Je me lève, décidée à
# vérifier »: the decision slips into apposition, and the candidate saw
# neither it nor its cousin « résolue à ». S7-1 carried TWO, recorded by hand
# in the grid. The pattern now has the three forms: present, passé composé,
# participle.
_DECISION = re.compile(
    r"\b(?:je d[ée]cide de|j'ai d[ée]cid[ée] de|je d[ée]cidai de|"
    r"j'ai r[ée]solu de|je me suis promis[e]? de|je me r[ée]solus? à|"
    r"d[ée]cid[ée]e? à|r[ée]solue? à)\s+"
    r"(?:l[ae]\s+|l'|les\s+|me\s+|m'|y\s+|en\s+)?(\w{4,})",
    re.IGNORECASE)

# THE NARRATED GESTURE, second rule, the one that catches C1.
#
# Rule M3: the effect of « décision sans geste » lives in the GAP between the
# noted decision and the state observed next. So decision → observed state
# (impersonal: « L'égouttoir, ce soir : deux assiettes. ») conforms; decision →
# gesture told in the first person fills the gap: the defect.
#
# The lexical rule alone could not see C1: the decision bears « vérifier » and
# the execution reads « je les ai comptées ». No common stem. Measured before
# widening, not assumed.
# THE NARRATED GESTURE, IN THE PASSÉ COMPOSÉ **AND THE PRESENT**.
#
# The first version knew only compound forms. Session 7 entries are written in
# the PRESENT (« Je me lève », « Je note », « Je compte »): in a present-tense
# entry no gesture was ever detected and the pair could never close, whatever
# the decision's form. Extending the decision to the participle without
# extending the execution to the present would have made a detector that
# never bites: one more ghost lint.
_GESTURE_1P = re.compile(
    r"\b(?:j'ai|je les ai|je l'ai|je la ai|je me suis|je m'[ée]tais)\s+"
    r"(?:\w+\s+){0,2}?([a-zàâçéèêëîïôûùüœ]+(?:[ée]{1,2}s?|is|it|us|ut))\b"
    r"|\bje\s+(?:l[ae]s?\s+|l'|m[e\']\s*|y\s+|en\s+)?"
    r"([a-zàâçéèêëîïôûùüœ]{3,}(?:e|es|s|te|ds))\b",
    re.IGNORECASE)

# STATE and PERCEPTION participles: observing is not acting. « L'égouttoir
# était là », « je les ai vues » belong to the observation the style asks for;
# counting them as gestures would turn the control into a first-person
# detector, i.e. a detector of nothing in a first-person notebook.
# NOTEBOOK DECISIONS, excluded, and not for convenience.
#
# M3 concerns the decision of a GESTURE in the world, whose execution the style
# wants left in the gap. « Je décide de reprendre les faits dans l'ordre »,
# « j'ai décidé de noter plus précisément » are operations of the notebook
# upon itself, and the second is the resolution the brief IMPOSES for
# chapter 2. Without this exclusion the detector flagged C2, which the human
# reading judged conforming: it would have blamed the run for obeying the
# brief.
_NOTEBOOK_DECISIONS = re.compile(
    r"^(?:reprend|repass|not|point|reli|[ée]cri|consign|marqu|r[ée][ée]cri|"
    r"tenir|d[ée]tail)", re.IGNORECASE)

_STATE_PARTICIPLES = {
    "été", "eu", "vu", "vue", "vues", "aperçu", "aperçue", "senti", "sentie",
    "su", "sue", "cru", "crue", "pensé", "pensée", "compris", "comprise",
    "souvenu", "souvenue", "rappelé", "rappelée", "resté", "restée",
    "semblé", "paru", "revu", "revue", "relu", "relue", "lu", "lue",
    "regardé", "regardée", "observé", "observée", "remarqué", "remarquée",
    "trouvé", "trouvée", "réalisé", "réalisée", "demandé", "demandée",
    # the same in the PRESENT: observing is not acting, whatever the tense
    "suis", "sais", "vois", "sens", "crois", "pense", "comprends", "regarde",
    "observe", "remarque", "trouve", "demande", "souviens", "rappelle",
    "relis", "lis", "reste", "semble", "veux", "peux", "dois", "espère",
}


def decision_execution_pairs(text: str) -> list[str]:
    """Decisions followed by their apparent execution: CANDIDATES for M3.

    Two rules, and the output says WHICH one bit: the line is non-blocking,
    the human reading decides, and it needs to know whether the flag is
    lexical (safe) or by narrated gesture (widened).
    """
    out, phr = [], sentences(text)
    for i, p in enumerate(phr):
        m = _DECISION.search(p)
        if not m:
            continue
        if _NOTEBOOK_DECISIONS.match(m.group(1)):
            continue
        radical = m.group(1)[:-2] if len(m.group(1)) > 6 else m.group(1)
        # THE WINDOW COUNTS NARRATIVE SENTENCES, not fragments.
        #
        # Reconstruction stations insert very short lines (« 18h30. »,
        # « La table du séjour. ») which ate the two sentences of the window:
        # the S7-1 pair (« Je me lève, décidée à vérifier » then, further down,
        # the narrated check) slipped through. A MASS device blinded a VOICE
        # detector; without the manual reading nobody would have known.
        continuation_txt = [q for q in phr[i + 1:i + 8] if words(q) >= 6]
        continuation = " ".join(continuation_txt)
        if re.search(rf"\b(?:j'ai |je )\w*{re.escape(radical)}", continuation, re.I):
            out.append(f"[lexical] « {p.strip()[:70]}… » puis exécution : "
                       f"« {continuation.strip()[:70]}… »")
            continue
        # Narrated-gesture rule: look at TWO sentences only, not three. The gap
        # the style asks for is immediate; beyond, the entry has resumed its
        # course and a « j'ai rangé » no longer executes the decision.
        for q in continuation_txt[:2]:
            # Two alternative groups (compound / present): take the one that
            # captured.
            gestures = [(g.group(1) or g.group(2)).lower()
                      for g in _GESTURE_1P.finditer(q)
                      if (g.group(1) or g.group(2))
                      and (g.group(1) or g.group(2)).lower()
                      not in _STATE_PARTICIPLES]
            if gestures:
                out.append(f"[geste narré] « {p.strip()[:70]}… » puis "
                           f"« {q.strip()[:70]}… » ({', '.join(gestures[:3])})")
                break
    return out


# ---------------------------------------------------------------------------
# Session 6: instances move down into the tooling
#
# Categories served, instances checked here (ADR-0011). Measured motive: B′2
# wrote « perplexe », served as a verbatim counter-example, then as the name
# of the prohibition. Naming what is forbidden is the only way to forbid it,
# and also shows it. So it is forbidden at the output.
# ---------------------------------------------------------------------------

# MENTAL STATES NAMED IN APPOSITION. The defect is not the word but the
# position: « Perplexe, je repose le cahier » names the state instead of
# making it felt. The apposition is spotted by the punctuation isolating it,
# or by the copula attributing it.
MENTAL_STATE_WORDS = (
    "perplexe", "songeuse", "songeur", "troublée", "troublé", "intriguée",
    "intrigué", "pensive", "pensif", "désemparée", "désemparé", "hébétée",
    "hébété", "incrédule", "abasourdie", "abasourdi", "déconcertée",
    "déconcerté", "dubitative", "dubitatif", "circonspecte", "circonspect",
)
# The apposition is NOT always closed by punctuation. The first version
# required a comma or period right after the adjective, and so let through
# « Je fronce les sourcils, intriguée PAR cette différence », seen in S6-1,
# exactly the defect the line exists to catch. A named state stays a named
# state when it trails a complement.
MENTAL_STATES = re.compile(
    r"(?:^|[.!?…»\n]\s*|,\s*)(" + "|".join(MENTAL_STATE_WORDS) + r")\b"
    r"|\bje (?:suis|étais|me sens|me sentais|restai?s?)\s+(?:\w+\s+){0,2}?"
    r"(" + "|".join(MENTAL_STATE_WORDS) + r")\b",
    re.IGNORECASE)


# MATERIAL PROHIBITIONS: nemo's generic world, documented by six runs.
#
# Not a style list: a list of DECOR. When the served matter is thin, the model
# fills the evening with the statistical furniture of a contemporary interior:
# television, handbag, tray of lasagne, coming home from work. This novel's
# house has none of it, and no sheet says so, since a sheet describes what is,
# not what is not.
#
# SCOPE PER CHAPTER: `chapter_min` is the first chapter where the term becomes
# legitimate. Phone memos appear at chapter 5 (the new notebook): forbidden
# before, expected after. A lint unaware of the chapter would forbid forever
# what the novel plans.
#
# Work UPON THE MANUSCRIPT is not targeted: her trade, practised at home. The
# target is work as a PLACE: leaving it, going there, coming back. Hence
# movement patterns, not the word « travail » alone.
MATERIAL_FORBIDDEN: tuple[tuple[str, str, int], ...] = (
    ("travail hors du domicile",
     r"\b(?:revenue?s?|rentr[ée]e?s?|retour|repartie?s?|partie)\s+"
     r"(?:tard\s+)?(?:du|de mon|au)\s+(?:travail|bureau)\b"
     r"|\bau bureau\b|\bmes coll[èe]gues\b|\bune r[ée]union\b"
     r"|\bjourn[ée]e de travail\b|\bj'ai travaill[ée] tard\b"
     # WORK AS A PERIOD, not only as a place one leaves. The pattern targeted
     # only movement verbs (« revenue du », « rentrée du ») and let
     # « épuisée par la semaine de travail » through, seen in the draw under
     # the movement method. She works at home: her days have neither work week
     # nor office hours.
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


def material_forbidden(text: str, chapter: int = 2) -> list[str]:
    """Generic decor terms present, for the given chapter.

    Returns « famille : extrait »: the family serves the grid, the excerpt the
    reading. A flag without its excerpt forces reopening the raw output.
    """
    out = []
    for family, pattern, chapter_min in MATERIAL_FORBIDDEN:
        if chapter >= chapter_min:
            continue
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - 30)
            out.append(f"{family} : …{text[start:m.end() + 20].strip()}…")
    return out


# THE ACCUMULATION THAT SUMMARISES: the validator born of C2's table of
# contents.
#
# C2 returned 131 words of table of contents:
# « perplexité, concentration sur les détails, rappel des faits, fatigue, panique… ».
# The validation counted words and commas, so it accepted a summary. *Counting
# is not reading*, episode two; the first was an English accumulation accepted
# by the same counters.
#
# ⚠ Protocol §3.1 PRESCRIBED a ratio of conjugated verbs per item
# (« propositions verbales exigées »). Implemented literally, that criterion
# REJECTS THE REFERENCE: the accumulation that defines the gesture is nominal
# in 88 % of its items (« le café de sept heures, le départ de sept heures quarante… »)
# and its verbal ratio falls to 12 %, lower than the six accumulations stage C
# produced. Measured, not assumed; the self-test against the references said so.
#
# The real discriminant is ABSTRACTION, which the grid already said by naming
# « méta-beats ». The reference lists THINGS and MOMENTS of the evening; C2
# lists the BEATS OF THE ENTRY, moods and verdict included.
#
#   reference 2: 0 %    the six stage C accumulations: 0 %    C2: 47 %
#
# Total separation, huge margin: the threshold sits at 20 % and need not be
# fine.
_ABSTRACT_ITEM = re.compile(
    # nominalisation suffixes: abstraction has a morphology
    r"\b\w*(?:it[ée]|tion|sion|ance|ence|itude|esse|isme)\b"
    # and the moods and mental operations that carry none
    r"|\b(?:fatigue|panique|doute|angoisse|peur|effroi|malaise|trouble|"
    r"verdict|souvenir|rappel|d[ée]tails?|faits?|m[ée]moire|esprit|corps)\b",
    re.IGNORECASE)

# A VERBAL item tells a step of the evening; it cannot be summary.
_VERBAL_ITEM = re.compile(
    r"\b(?:je|j'|elle|il|on|nous|ils|elles)\b"
    r"|\b(?:ai|as|avons|avez|ont|avais|avait|avions|avaient"
    r"|suis|es|est|sommes|êtes|sont|étais|était|étions|étaient)\b",
    re.IGNORECASE)

ACC_ABSTRACT_MAX = 0.20


# THIRD PERSON IN A NOTEBOOK WRITTEN IN THE FIRST.
#
# « Elle est revenue à vingt heures, a refermé le cahier, posé la lampe… »
# (S7-3): the accumulation node switched person in the middle of an entry
# wholly in the first. No lint saw it; the standing read-through did.
# Mechanical defect, trivial detection: the notebook has one subject, « je ».
_SUBJECT_3P = re.compile(
    r"\b(?:elle|il|on)\s+(?:[a-zàâçéèêëîïôûùüœ']+\s+){0,2}?"
    r"(?:est|a|était|avait|s'est|se|fut)\b"
    r"|\b(?:elle|il)\s+(?:rentre|revient|repose|referme|compte|note|vérifie)\b",
    re.IGNORECASE)


def accumulation_at_first_person(sentence: str) -> tuple[bool, str]:
    """Is the accumulation written in the first person?

    True when no third-person subject appears. A « je » is not required: an
    accumulation without any pronoun (the reference is largely nominal) must
    not be rejected for that.
    """
    if _SUBJECT_3P.search(sentence):
        m = _SUBJECT_3P.search(sentence)
        return False, f"troisième personne : « {sentence[max(0, m.start()-20):m.end()+30]} »"
    return True, ""


def summarizing_accumulation(sentence: str) -> tuple[float, list[str]]:
    """Share of abstract items in an accumulation, and which ones.

    The unit is the item between commas, the same unit the instruction is
    quantified in (« au moins douze étapes, séparées par des virgules »).
    Measuring in the instruction's unit avoids blaming the model for something
    other than what it was asked.

    Bare adverbs (« calmement », « méthodiquement » in the reference) are
    neutral: they modify the frame sentence, they are not a step.
    """
    items = [i.strip() for i in sentence.split(",") if i.strip()]
    if not items:
        return 0.0, []
    candidates = [i for i in items
                 if not _VERBAL_ITEM.search(i)
                 and not re.fullmatch(r"\w+ment", i, re.IGNORECASE)]
    abstract_items = [i for i in candidates if _ABSTRACT_ITEM.search(i)]
    return len(abstract_items) / len(items), abstract_items


# ---------------------------------------------------------------------------
# REPETITION: two detectors, session 7
#
# `_reattach` (factory.pipeline.graph) removes CHARACTER-EXACT overlap between
# two segments: it catches copying, not re-narration. S6-3 puts the two plates
# away at ¶10 then again at ¶13 in other words; and its ¶2 and ¶3 share two
# whole sentences, identical this time.
#
# ⚠ THE MEASURE IS CHARACTERS, NOT WORDS, and that is not a comfort detail.
# Measured against S6-3 before choosing:
#
#                                            characters   word overlap
#   ¶10/¶13  the same action put away twice      0.64          0.78
#   ¶5/¶8    the ACCUMULATION vs the recon-      0.02          0.52
#            struction it summarises
#   ¶4/¶9    two distinct observations           0.02          0.06
#
# Word overlap would trip the accumulation itself, which re-narrates the
# evening by definition, its reason to exist, against a blocking control. It
# would kill the gesture acquired the previous session. Character similarity
# separates the three cases without ambiguity.
#
# And NO length floor: ¶10 is seventeen words. An « at least twenty words »
# filter let it through, which is what made me conclude « no duplicate in
# S6-3 » at the first sweep: the filter was the bug, not the measure.
REPEAT_THRESHOLD = 0.50

# ⚠ THE RATIO ALONE IS NOT ENOUGH, found while falsifying the full assembly.
#
# French is full of function words, and two SHORT, wholly different paragraphs
# score high while sharing nothing real:
#
#   « Je relis l'entrée d'hier. Ma mémoire dit une assiette. »
#   « Je suis rentrée, j'ai posé le cahier, j'ai préparé le dîner. »   ratio 0.51
#
# The first deduplication attempt removed the second for that score. A
# blocking removal that errs costs a paragraph of narrative every run.
#
# The discriminant is the longest COMMON RUN: a repetition reuses a continuous
# fragment, two different texts share only articles:
#
#   the same action put away twice    ratio 0.64   block 42 chars
#   two distinct observations         ratio 0.51   block  6 chars
#   two short distinct sentences      ratio 0.67   block  6 chars
#
# Both conditions together, then. Neither holds alone.
REPEAT_BLOCK_MIN = 30


# WHAT THE CODE COMPOSES IS NEVER A REPETITION (ADR-0018).
#
# Found while falsifying the detector against S6-C, the second time a
# session 7 control aimed at what it had to protect. The three highest-ratio
# « doublons » of the chapter were ALL code artefacts:
#
#   ¶0/¶17  (0.55)  the HEADERS: removing them removes the audio switch;
#   ¶1/¶18  (0.96)  the quotation ANCHOR, re-posed at the head of each entry,
#                   the very one re-stamped at §2 of that session;
#   ¶11/¶28 (0.71)  the DRIFTS: three DIFFERENT approaches from the bank,
#   ¶11/¶51 (0.62)  but glued to the same material fact, hence similar by
#                   their tail. Removal would have killed the gesture held 4/4.
#
# A paragraph composed by code repeats because that is its function. The rule
# is not a finer threshold: the detector judges only what the MODEL wrote. The
# code knows what it posed; it need not guess.
def _is_protected(para: str, protected: tuple[str, ...] = ()) -> bool:
    """Was this paragraph composed by the code?

    Recognised WITHOUT knowing anything of the run, so that the grid, which
    reads only files, protects the same things as the assembly:
      · the dated header, whose format is ours;
      · the drift, which carries the suspension marker: the code removes those
        the model produces, so any remaining « … » comes from us;
      · the anchor, a paragraph wholly between quotation marks.
    `protected` adds what the caller knows besides.
    """
    para = para.strip()
    if ENTRY_HEADER.match(para) or SUSPENSION.search(para):
        return True
    if re.fullmatch(r"[«\"“].{10,}[»\"”]", para, re.DOTALL):
        return True
    return any(p.strip() and (p.strip() in para or para in p.strip())
               for p in protected)


def repeated_paragraphs(text: str, threshold: float = REPEAT_THRESHOLD,
                       protected: tuple[str, ...] = ()
                       ) -> list[tuple[int, int, float, str]]:
    """Pairs of paragraphs telling the same thing. (i, j, ratio, excerpt).

    The second member of each pair is the one to remove: it comes later, so
    it is the repetition.

    `protected`: the fragments composed by code (anchor, gestures). Headers
    are recognised by themselves.
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    out = []
    for i in range(len(paras)):
        if _is_protected(paras[i], protected):
            continue
        for j in range(i + 1, len(paras)):
            if _is_protected(paras[j], protected):
                continue
            m = difflib.SequenceMatcher(None, paras[i], paras[j])
            r = m.ratio()
            if r < threshold:
                continue
            block = m.find_longest_match(0, len(paras[i]), 0, len(paras[j])).size
            if block < REPEAT_BLOCK_MIN:
                continue
            out.append((i, j, round(r, 2), paras[j][:90]))
    return out


def repeated_sentences(text: str,
                    protected: tuple[str, ...] = ()) -> list[tuple[int, int, str]]:
    """Whole sentences repeated from one paragraph to another. (¶i, ¶j, sentence).

    A sharper defect than paragraph repetition, and distinct: S6-3's ¶2 and ¶3
    are globally different (0.15 similarity) yet share TWO sentences character
    for character. An average over the whole paragraph dilutes them; look at
    the sentences.

    Short sentences are dropped: « Rien. » or « Deux. » may recur without
    being a repetition; it is even a figure of the style.
    """
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    seen_counts: dict[str, int] = {}
    out = []
    for i, p in enumerate(paras):
        if _is_protected(p, protected):
            continue
        for ph in sentences(p):
            key = re.sub(r"\W+", " ", ph.lower()).strip()
            if words(ph) < 8:
                continue
            if key in seen_counts and seen_counts[key] != i:
                out.append((seen_counts[key], i, ph.strip()[:90]))
            else:
                seen_counts.setdefault(key, i)
    return out


# THE INVENTED QUOTATION. The notebook is supplied matter, never fabricated:
# when the model writes a quoted passage that is neither the served anchor nor
# its verdict, it FABRICATES notebook. S7-3 produced
# « "Les deux assiettes étaient bien là, sur l'égouttoir. Je ne me souviens pas…" ».
# Flag, not failure: the anchor and the final verdict are legitimately quoted,
# and top-down falsification demands it; a detector refusing the anchor would
# be the fourth of the series aiming at what it must protect.
QUOTATION = re.compile(r"[«\"“]([^«»\"”]{15,400})[»\"”]", re.DOTALL)


def quotations_outside_anchor(text: str, anchor: str = "",
                         verdict: str = "") -> list[str]:
    """Quoted passages that are neither the served anchor nor the rendered verdict."""
    anchor_core = re.sub(r"[«»\"“”]", "", anchor).strip().lower()
    verdict_core = re.split(r"\s*\(", verdict or "")[0].strip().lower()
    # THE ANCHOR IS THE FIRST ISOLATED QUOTATION OF EACH ENTRY: one, at the
    # head, posed by code and put back by the stamp after repair (ADR-0018).
    #
    # ⚠ « paragraphe entièrement cité » IS NOT ENOUGH: S7-3's two fabricated
    # quotations are isolated paragraphs too, and exempting by form alone let
    # both through. RANK discriminates, because the code poses the anchor
    # once, and first.
    only_ones, entry_seen = set(), set()
    e = 0
    for b in text.split("\n\n"):
        if ENTRY_HEADER.match(b.strip()):
            e += 1
            continue
        if re.fullmatch(r'\s*[«"“].{10,}[»"”]\s*', b, re.DOTALL) and e not in entry_seen:
            entry_seen.add(e)
            only_ones.add(" ".join(b.split()).strip('«»"“” '))
    out = []
    for m in QUOTATION.finditer(text):
        body = " ".join(m.group(1).split())
        lowered = body.lower()
        if body.strip("«»\"“” ") in only_ones:
            continue
        if anchor_core and (lowered in anchor_core or anchor_core in lowered
                            or difflib.SequenceMatcher(
                                None, lowered, anchor_core).ratio() > 0.75):
            continue
        if verdict_core and verdict_core in lowered:
            continue
        out.append(body[:100])
    return out


# TRADEMARKS. « L'enceinte Bluetooth » (chapter 7 draw 6): a brand is a proper
# noun, so L1 saw it already, but drowned among proper nouns, with no sign it
# was a brand. A brand in this novel is worse than an ordinary proper noun: it
# dates the text and takes it out of the closed world of the house. Named so
# it can be removed.
MARKS = re.compile(
    r"\b(Bluetooth|Wi-?Fi|iPhone|iPad|Android|Spotify|Netflix|YouTube|"
    r"Google|Apple|Samsung|Facebook|Instagram|WhatsApp|Tupperware|Post-it|"
    r"Kleenex|Frigidaire|Thermos)\b", re.IGNORECASE)


# PROMPT COPY: the missing control.
#
# Chapter 7 draw 6 opens with the opening instruction, transcribed at 0.94
# similarity. Nobody saw it before reading: no lint compared the produced text
# with what had been served. Everything was measured except provenance
# (ADR-0019).
#
# Threshold 0.50: the chapter 2 runs, where the instruction legitimately
# described the subject, peaked at 0.37.
PROMPT_COPY_THRESHOLD = 0.50


def prompt_copy(text: str, prompt: str,
                      threshold: float = PROMPT_COPY_THRESHOLD
                      ) -> list[tuple[float, str]]:
    """Sentences of the text too close to a line of the served prompt.

    Compares SENTENCE TO LINE: an instruction is copied by block, and an
    average over whole texts would dilute it into invisibility.
    """
    lines = [" ".join(l.split()) for l in prompt.splitlines()
              if len(l.split()) >= 8]
    out = []
    for ph in sentences(text):
        p = " ".join(ph.split())
        if len(p.split()) < 8:
            continue
        best = max((difflib.SequenceMatcher(None, p.lower(), l.lower()).ratio()
                        for l in lines), default=0.0)
        if best >= threshold:
            out.append((round(best, 2), p[:100]))
    return out


def consistent_headers(headers: list[tuple[str, str]]) -> list[str]:
    """Weekday sequence consistent with the day numbers.

    Two headers one day apart must advance one weekday. BC produced « Vendredi
    8 » then « Jeudi 7 »: dates going backwards in a notebook kept every
    evening.
    """
    order = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
             "Dimanche"]
    faults = []
    for (j1, n1), (j2, n2) in zip(headers, headers[1:]):
        day_gap = (order.index(j2.capitalize()) - order.index(j1.capitalize())) % 7
        number_gap = int(n2) - int(n1)
        # TWO ENTRIES THE SAME DAY are legitimate (session 7). Chapter 7 makes
        # them its structure: the afternoon and the night of the anniversary,
        # « Samedi 14. » twice, and the SECOND header carries the audio switch
        # (ADR-0013). The lint refused this form: it would have marked as a
        # defect the exact structure the brief imposes.
        #
        # What stays faulty: a date going BACKWARDS (B′C produced
        # [8,7,7,7,7,9,10,7]), and a weekday not following the gap.
        if number_gap == 0 and j1.lower() == j2.lower():
            continue
        if number_gap < 0:
            faults.append(f"{j1} {n1} → {j2} {n2} : la date recule")
        elif number_gap == 0:
            faults.append(f"{j1} {n1} → {j2} {n2} : même date, jour différent")
        elif number_gap % 7 != day_gap:
            faults.append(f"{j1} {n1} → {j2} {n2} : le jour de semaine ne suit "
                          f"pas l'écart de dates")
    return faults


def entries(text: str) -> list[str]:
    """Split the text into journal entries at the dated headers.

    Returns `[text]` if no header is found: a chapter with a single undated
    entry is still an entry, and an empty list would make every per-entry
    control read as « nothing to check ».
    """
    marks = [m.start() for m in ENTRY_HEADER.finditer(text)]
    if not marks:
        return [text]
    if marks[0] > 0:
        marks.insert(0, 0)          # matter before the first date
    bounds = marks + [len(text)]
    out = [text[a:b].strip() for a, b in zip(bounds, bounds[1:])]
    return [e for e in out if e] or [text]


def outside_quotes(text: str) -> str:
    """Remove quoted content, keeping the length (hence the positions).

    VOICE lints (AI tics, physiology, named mental state, drift) judge the
    narrator's voice. What sits between quotation marks in this novel is the
    notebook, hand-made and deliberately in ANOTHER voice. Applying them there
    would punish the quotation for existing (tooling notes, step 3 extraction).

    The prose contract applies everywhere, quotations included: that is why
    spaces replace rather than delete; both layers read the same split at the
    same positions.
    """
    return re.sub(r"«[^»]*»|“[^”]*”",
                  lambda m: " " * len(m.group(0)), text)


def in_quotes(text: str) -> list[str]:
    """The quoted passages, for what must apply to them anyway."""
    return [m.group(0) for m in
            re.finditer(r"«[^»]*»|“[^”]*”", text)]


# --- §3 and §4: chapter-scoped constraints ------------------------------------
#
# Values come from the pilot table of `chronologie-partie-double.md`. That file
# is FIREWALLED from the model, never indexed, never served (ADR-0017), but
# the tooling may read it: a lint is not a model, it tells nothing, it
# compares. Exactly the asymmetry we want: the judging machine knows more than
# the writing one.

PILOT_TABLE = str(BIBLE_DIR / "profond" / "chronologie-partie-double.md")

# Reserved until chapters 9, 10, 11 respectively: linted for ABSENCE in
# chapters 1 to 8 (tooling notes, step 3 extraction).
RESERVED_TERMS = ("la tierce", "l'errata", "le bon à tirer")

# The chapter 7 quartet: forbidden everywhere else (tooling notes, step 3 extraction).
QUARTET = ("photos", "playlist", "plat des anniversaires", "couverts")


def chapter_constraints(n: int, table: str = PILOT_TABLE) -> dict:
    """Imposed verdict and scoped prohibitions of a chapter, read from the table."""
    verdict, objects = "", ""
    p = Path(table)
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 11 and cells[1] == str(n):
                verdict, objects = cells[5], cells[10]
                break
    return {
        "chapter": n,
        "verdict": verdict,
        "active_objects": objects,
        # Chapter 1's verdict « aucun » is not a verdict to find.
        "verdict_attendu": verdict and not verdict.startswith("aucun")
                           and "hors échelle" not in verdict,
        "reserves": RESERVED_TERMS if 1 <= n <= 8 else (),
        "quatuor_interdit": n != 7,
    }


def chapter_checks(text: str, c: dict) -> dict:
    """Apply a chapter's constraints. Returns the breaches."""
    t = normalize(text)
    out: dict[str, list[str]] = {"reserves": [], "quatuor": [], "verdict": [],
                                 # Session 6: generic decor, scoped too (phone
                                 # memos become legitimate at chapter 5).
                                 "materiels": material_forbidden(
                                     t, c["chapter"])}

    for term in c["reserves"]:
        for m in re.finditer(re.escape(normalize(term)), t, re.I):
            a, b = max(0, m.start() - 40), min(len(t), m.end() + 40)
            out["reserves"].append(f"{term} — …{t[a:b]}…".replace("\n", " "))

    if c["quatuor_interdit"]:
        for term in QUARTET:
            for m in re.finditer(rf"\b{re.escape(term)}\b", t, re.I):
                a, b = max(0, m.start() - 40), min(len(t), m.end() + 40)
                out["quatuor"].append(f"{term} — …{t[a:b]}…".replace("\n", " "))

    # §3: the verdict is linted for PRESENCE, it must appear. Other lexicon
    # terms are never linted for absence: synonymic drift is tolerated, even
    # desirable in small doses.
    if c["verdict_attendu"]:
        core = re.split(r"\s*\(", c["verdict"])[0].strip()
        if core and not re.search(re.escape(normalize(core)), t, re.I):
            out["verdict"].append(f"verdict « {core} » ABSENT du texte")
    return out


def _leak_lexicon(path: str = str(DATA_DIR / "lexique-fuite.txt")) -> list[str]:
    """Forbidden lexical field, read from disk.

    Deliberately OUTSIDE the code and outside `bible/`: these words must never
    end up in a file meant for RAG indexing, where they would contaminate the
    model's context through the very retrieval meant to frame it (ADR-0017).
    """
    p = Path(path)
    if not p.is_file():
        return []
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()]


# Flagged without blocking. `disparue` is ambiguous (a thing disappears
# without anyone dying). `tombe` more so: it is also the verb, and session 3
# run 3 was failed over « qu'elle ne glisse et ne tombe par terre », a false
# positive against a homograph, exactly what a binary lint must not cost.
AMBIGUOUS_LEAK = {"disparue", "disparu", "tombe", "tombes"}


def lexical_leak(text: str) -> tuple[list[str], list[str]]:
    """(blocking matches, ambiguous matches) of the forbidden lexical field."""
    forbidden_words = _leak_lexicon()
    if not forbidden_words:
        return [], []
    # The PLURAL counts as much as the singular, and escaped everything:
    # « feuilles mortes » in BpC was not seen, while the brief calls this lint
    # « le firewall rendu vérifiable par grep ». A firewall blind to plurals
    # shows green over texts it should block, and that was the case for every
    # previous session.
    pattern = re.compile(r"\b(" + "|".join(re.escape(m) for m in forbidden_words)
                       + r")s?\b", re.IGNORECASE)
    hard_ones, ambiguous = [], []
    for m in pattern.finditer(text):
        # The CONTEXT is returned with the word, not the word alone. Several
        # list entries are homographs (« tombe » is also the verb tomber,
        # « cendres » works figuratively): without the excerpt a match reads as
        # a proven leak when the sentence must be read to decide.
        a, b = max(0, m.start() - 45), min(len(text), m.end() + 45)
        occ = f"{m.group(0).lower()} — …{text[a:b]}…".replace("\n", " ")
        (ambiguous if m.group(0).lower() in AMBIGUOUS_LEAK else hard_ones).append(occ)
    return hard_ones, ambiguous


def proper_nouns(text: str) -> list[str]:
    """Proper-noun candidates: a capital opening neither sentence nor line."""
    out, seen_map = [], set()
    for m in UPPERCASE.finditer(text):
        word = m.group(1)
        if word in L1_EXCEPTIONS or word.rstrip("'’") in L1_EXCEPTIONS:
            continue
        before = text[:m.start()].rstrip()
        if not before:                              # very start of the text
            continue
        # Sentence, quotation, or BRACKET opening. The bracket is there because
        # nemo produces stage directions (« [Dans la cuisine] ») whose first
        # capitalised word is not a proper noun. Without this exception a whole
        # run came out at 5 proper nouns, all false, masking the real defect:
        # the model writes stage directions instead of a journal.
        # The OPENING quotation mark counts as much as the closing one:
        # « La maison est vide » made « La » come out as a proper noun. Not
        # cosmetic: L1 is zero-tolerance, so each false positive drowns the
        # one occurrence that matters (here, a first name actually written).
        if before[-1] in ".!?…:«»\"'—-–[(“":
            continue
        if text[:m.start()].rstrip(" \t").endswith("\n"):   # start of line
            continue
        if word.lower() in seen_map:
            continue
        seen_map.add(word.lower())
        a, b = max(0, m.start() - 35), min(len(text), m.end() + 35)
        out.append(f"{word} — …{text[a:b]}…".replace("\n", " "))
    return out


# THE PIVOT LEFT OPEN. A drift is a sentence approaching the where or the why
# and cutting off BEFORE getting there: the departure word is absent, that is
# the whole point of the gesture.
#
# ⚠ This pattern is ADDED to `DEPARTURE_FIELD` in the L4 control, and it is
# not cosmetic. Measured: the three hand-written drifts delivered by the
# protocol (« Je pourrais me demander ce qui, ce soir-là… », « Si je savais
# seulement pourquoi… », « Il faudrait que je relise le jour où elle… ») were
# ALL THREE classed « hors champ du départ » by the previous version. L4 would
# have shown three crosses against the gesture finally correct, and we would
# have concluded the drift still did not work, after three sessions asking why.
OPEN_PIVOT = re.compile(
    r"\b(ce qui|ce que|ce qu'|pourquoi|comment|où|quand|si je|si elle|"
    r"le jour|qui a|quelle|lequel)\b", re.IGNORECASE)


def drifts(entry: str) -> tuple[int, list[str]]:
    """(occurrence count, NON-CONFORMING occurrences) for one entry.

    An occurrence conforms if, within L4_WORD_WINDOW words, EITHER a named
    departure term OR an open pivot is found: that is what separates the drift
    (thought stumbling against the where/why) from a mere stylistic
    suspension. Both paths, because the gesture may name the departure or
    stop just short, and the second form is the most characteristic.
    """
    occurrences = list(SUSPENSION.finditer(entry))
    out_of_field = []
    for m in occurrences:
        tokens_before = entry[:m.start()].split()[-L4_WORD_WINDOW:]
        tokens_after = entry[m.end():].split()[:L4_WORD_WINDOW]
        window = " ".join(tokens_before + tokens_after)
        # The pivot is searched BEFORE the cut only: after it the sentence has
        # returned to the material, and a following « où » says nothing of the
        # gesture.
        before = " ".join(tokens_before)
        if not (DEPARTURE_FIELD.search(window) or OPEN_PIVOT.search(before)):
            a, b = max(0, m.start() - 60), min(len(entry), m.end() + 60)
            out_of_field.append(f"…{entry[a:b]}…".replace("\n", " "))
    return len(occurrences), out_of_field


def accumulations_l3(entry: str) -> list[str]:
    """Accumulations in the sense of sheet v3: ≥60 words, ≥6 commas, no inner
    period or semicolon. The sentence split already guarantees no period; the
    semicolon must be checked by hand."""
    return [p for p in sentences(entry)
            if words(p) >= L3_WORDS and p.count(",") >= L3_COMMAS
            and ";" not in p]


def _excerpts(pattern: re.Pattern, text: str, *, margin: int = 40) -> list[str]:
    """Occurrences with their context, deduplicated, to justify a cross."""
    seen_map, out = set(), []
    for m in pattern.finditer(text):
        key = m.group(0).lower()
        if key in seen_map:
            continue
        seen_map.add(key)
        a, b = max(0, m.start() - margin), min(len(text), m.end() + margin)
        piece = text[a:b].replace("\n", " ")
        out.append(f"…{piece}…" if a > 0 or b < len(text) else piece)
    return out


# --- Analysis ----------------------------------------------------------------

def analyze(raw_text: str) -> dict:
    """Returns the mechanically decidable grid lines, with their evidence."""
    text = normalize(strip_frontmatter(raw_text))
    paras = paragraphs(text)
    all_sentences = sentences(text)

    # --- Structure: accumulation ---
    raw_items = [
        p for p in all_sentences
        if p.count(",") >= ACC_COMMAS and words(p) >= ACC_WORDS
    ]
    # An accumulation copied from the reference IS NOT ONE: it carries the
    # example's objects (keys, a small dish) in a scene about something else.
    # Removed from the count and flagged apart.
    plagiarisms = [(p, reference_copy(p)) for p in raw_items]
    accumulations = [p for p, r in plagiarisms if r == 0.0]
    copies = [(p, r) for p, r in plagiarisms if r > 0.0]

    # --- Structure: cleavers (3-6 words), and those CLOSING a paragraph ---
    cleavers, closing_cleavers = [], []
    for para in paras:
        ph = sentences(para)
        for i, p in enumerate(ph):
            if CLEAVER_MIN <= words(p) <= CLEAVER_MAX:
                cleavers.append(p)
                if i == len(ph) - 1:
                    closing_cleavers.append(p)

    # --- Passé simple: three detectors, all returned as CANDIDATES ---
    def _participe(m: re.Match) -> bool:
        """True if the occurrence is a past participle, not a passé simple."""
        if m.group(0).lower() not in PS_AMBIGUOUS_PARTICIPLES:
            return False
        return bool(AUXILIARY.search(text[max(0, m.start() - 30):m.start()]))

    ps = []
    ps += [m.group(0) for m in PS_IRREGULARS.finditer(text)
           if not _participe(m)]
    ps += [m.group(0) for m in PS_ERENT.finditer(text)]
    ps += [m.group(0) for m in PS_IRENT_URENT.finditer(text)
           if m.group(0).lower() not in PS_PRESENT_HOMONYMS]
    ps += [m.group(1) for m in PS_ANCHOR.finditer(text)]
    ps += [m.group(1) for m in PS_FIRST_PERSON.finditer(text)]
    ps += [m.group(1) for m in PS_PROPER_NOUN.finditer(text)]
    ps_uniques = sorted({p.lower() for p in ps})

    outside_dialogue = without_dialogue(text)
    # VOICE layer: outside quotations. Quoted text carries the notebook's voice.
    voice = outside_quotes(text)

    # --- L1-L4 controls (chapter 2 protocol), counted PER ENTRY when the rule
    # asks (D1: the unit of count is the journal entry, not the scene).
    list_entries = entries(text)
    l1 = proper_nouns(text)
    l2_hard, l2_ambiguous = lexical_leak(text)
    l3_per_entry = [accumulations_l3(e) for e in list_entries]
    l4_per_entry = [drifts(e) for e in list_entries]
    # Reference copy disqualifies an L3 accumulation as it disqualifies an
    # ordinary one.
    l3_copies = [[p for p in acc if reference_copy(p)] for acc in l3_per_entry]
    l3_clean = [[p for p in acc if not reference_copy(p)]
                  for acc in l3_per_entry]

    # delint() READ-ONLY: the corrected text is dropped, only the warnings
    # kept. Measure the model, not the post-filter.
    _, delint_warnings = delint(text)

    return {
        "mots": words(text),
        "paragraphes": len(paras),
        "phrases": len(all_sentences),
        # EXACT: failure if present
        # VOICE layer, outside quotations.
        "pastiche": _excerpts(PASTICHE, voice),
        "tics_ia": _excerpts(AI_TICS, voice),
        "exclamation_hors_dialogue": _excerpts(
            re.compile(r"[^\s]{0,30}!"), outside_dialogue),
        "incise_adverbiale": (_excerpts(ADVERBIAL_INCISE, text)
                              + _excerpts(PREPOSITIONAL_INCISE, text)),
        "elision": _excerpts(MISSING_ELISION, text),
        # EXACT: failure if absent
        "accumulations": accumulations,
        "accumulations_recopiees": copies,
        "couperets_fin_para": closing_cleavers,
        "couperets_tous": cleavers,
        "precision": sorted({m.group(0) for m in PRECISION.finditer(text)}),
        # CANDIDAT
        "passe_simple": ps_uniques,
        # Known nemo defects, outside the protocol grid
        "delint": delint_warnings,
        # --- L1-L4 (session 3) ---
        "entrees": len(list_entries),
        "l1_noms_propres": l1,
        "l2_fuite": l2_hard,
        "l2_fuite_ambigue": l2_ambiguous,
        "l3_par_entree": l3_clean,
        "l3_recopies": l3_copies,
        "l4_par_entree": l4_per_entry,
        # --- session 5, item 7 ---
        "meta_termes": _excerpts(META_TERMS, voice),
        "formulaire": _excerpts(FORM, voice),
        "attracteurs": _excerpts(ATTRACTORS, text),
        "je_decide_par_entree": [len(I_DECIDE.findall(e))
                                 for e in list_entries],
        "couples_m3": decision_execution_pairs(text),
        "entetes_incoherents": consistent_headers(
            ENTRY_HEADER.findall(text)),
        # --- Session 6 -----------------------------------------------------
        # Instances moved down from the served sheet into the tooling: no
        # longer shown to the model, checked at the output (ADR-0011).
        "marques": _excerpts(MARKS, text),
        "etats_mentaux": sorted({(m.group(1) or m.group(2)).lower()
                                 for m in MENTAL_STATES.finditer(voice)}),
        # The accumulation that summarises. The RATIO is returned, not a
        # boolean: the threshold is an arbitration (0.20), and a grid line
        # hiding the measure behind its threshold forbids rediscussing it with
        # numbers. The reference and the six stage C accumulations sit at
        # 0.00; C2's summary at 0.47.
        # REPETITION (session 7). `_reattach` catches copying; this catches
        # re-narration: S6-3 puts the two plates away twice, in other words,
        # and its ¶2/¶3 share two whole sentences.
        "paragraphes_redits": repeated_paragraphs(text),
        # Fabricated quotations: the anchor and the verdict are exempted by the
        # caller, who alone knows them. Without them every quoted passage
        # counts; the grid supplies them.
        "citations": quotations_outside_anchor(text),
        "accumulations_3p": [a for a in accumulations_l3(text)
                             if not accumulation_at_first_person(a)[0]],
        "phrases_redites": repeated_sentences(text),
        "accumulations_abstraction": [
            summarizing_accumulation(a)[0]
            for a in accumulations_l3(text)],
    }


# --- Report ------------------------------------------------------------------

def _mark(present: bool) -> str:
    """✗ = defect, ✓ = held."""
    return "✗" if present else "✓"


def report(res: dict, title: str = "") -> str:
    l = []
    if title:
        l.append(f"### {title}")
    target = "OK" if 400 <= res["mots"] <= 550 else "HORS CIBLE"
    l.append(f"{res['mots']} mots [{target}] · {res['paragraphes']} paragraphes "
             f"· {res['phrases']} phrases")
    l.append("")

    l.append("**Mécanique — EXACT (✗ = défaut présent)**")
    for key, label in [
        ("pastiche", "Lexique pastiche gothique"),
        ("tics_ia", "Tic d'IA"),
        ("exclamation_hors_dialogue", "Point d'exclamation hors dialogue"),
        ("incise_adverbiale", "Incise adverbiale (ou son équivalent prépositionnel)"),
        ("elision", "Élision manquante"),
    ]:
        occ = res[key]
        l.append(f"- {_mark(bool(occ))} {label}"
                 + (f" → {len(occ)}" if occ else ""))
        for e in occ[:3]:
            l.append(f"    - `{e}`")

    l.append("")
    l.append("**Structure — EXACT (✗ = attendu absent)**")
    n_acc = len(res["accumulations"])
    acc_state = "✓" if n_acc == 1 else "✗"
    detail = {0: "zéro = plat", 1: "exactement une"}.get(n_acc, f"{n_acc} = tic")
    l.append(f"- {acc_state} Phrase d'accumulation : {detail}")
    for a in res["accumulations"]:
        l.append(f"    - `{a[:120]}…`" if len(a) > 120 else f"    - `{a}`")
    for a, r in res.get("accumulations_recopiees", []):
        l.append(f"    - ⛔ **ÉTALON RECOPIÉ à {r:.0%}** (ne compte pas) : "
                 f"`{a[:90]}…`")
    n_cleavers = len(res["couperets_fin_para"])
    l.append(f"- {_mark(n_cleavers == 0)} Phrase-couperet en fin de paragraphe "
             f"→ {n_cleavers} (dont {len(res['couperets_tous'])} couperets au total)")
    for c in res["couperets_fin_para"][:3]:
        l.append(f"    - `{c}`")
    l.append(f"- {_mark(not res['precision'])} Heure ou quantité exacte "
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


# --- Self-test against the sheet's reference excerpts -------------------------

def _references(sheet: Path) -> list[tuple[str, str]]:
    """Extract the `> …` blocks of the `## Extraits étalons` section."""
    text = sheet.read_text(encoding="utf-8")
    section = re.search(r"^## Extraits étalons(.*)\Z", text,
                        re.MULTILINE | re.DOTALL)
    if not section:
        return []
    out, title, block = [], None, []
    for line in section.group(1).splitlines():
        header = re.match(r"^\*\*(Étalon.*?)\*\*", line)
        if header:
            if title and block:
                out.append((title, "\n".join(block).strip()))
            title, block = header.group(1), []
        elif line.startswith(">"):
            block.append(line.lstrip("> ").rstrip())
        elif not line.strip() and block:
            block.append("")
    if title and block:
        out.append((title, "\n".join(block).strip()))
    return out


def autotest(sheet: Path) -> int:
    """The test of the test: a detector missing its own target is worthless.

    The four references DEFINE the style. They must come out clean against
    the exact lines, and reference 2, which exists to show the accumulation,
    must be counted as exactly one.
    """
    references = _references(sheet)
    if not references:
        print("ERREUR : aucun étalon trouvé dans la fiche.", file=sys.stderr)
        return 1

    failures = []
    for title, text in references:
        r = analyze(text)
        print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
        print(report(r))
        for key, label in [("pastiche", "pastiche"), ("tics_ia", "tic d'IA"),
                             ("incise_adverbiale", "incise adverbiale")]:
            if r[key]:
                failures.append(f"{title} : {label} détecté à tort → {r[key]}")
        if r["passe_simple"]:
            failures.append(f"{title} : passé simple à tort → {r['passe_simple']}")
        # Accumulations and « recopies » are summed: here the source IS the
        # reference, trivially identical to itself. This self-test validates
        # the FORM detector, not the plagiarism one, which is tested against
        # runs, where the question has a meaning.
        expected = 1 if title.startswith("Étalon 2") else 0
        found_item = len(r["accumulations"]) + len(r["accumulations_recopiees"])
        if found_item != expected:
            failures.append(f"{title} : {found_item} accumulation(s), "
                          f"attendu {expected}")
        # --- Session 6: the detectors moved down from the sheet into the
        # tooling. The references DEFINE the style: anything biting here is a
        # false positive, and this clause is what caught the protocol's
        # « propositions verbales » criterion, which rejected reference 2's
        # accumulation.
        for key, label in [("etats_mentaux", "état mental en apposition"),
                             ("attracteurs", "attracteur")]:
            if r[key]:
                failures.append(f"{title} : {label} détecté à tort → {r[key]}")
        if r["couples_m3"]:
            failures.append(f"{title} : couple décision-exécution à tort → "
                          f"{r['couples_m3']}")
        if material_forbidden(normalize(text), chapter=2):
            failures.append(f"{title} : interdit matériel détecté à tort → "
                          f"{material_forbidden(normalize(text), 2)}")
        for ratio in r["accumulations_abstraction"]:
            if ratio > ACC_ABSTRACT_MAX:
                failures.append(f"{title} : accumulation jugée résumante à tort "
                              f"({ratio:.0%} d'items abstraits)")

    # THE KNOWN CASES, IN NEGATIVE. A detector silent against the references
    # may be silent everywhere: the green above does not separate « nothing to
    # find » from « unable to find ». Each pattern must therefore BITE the
    # defect read by hand, and the excerpts below all come from stage C runs.
    for expected_true, text, what in [
        (True, "J'ai décidé de vérifier par moi-même. Dans la cuisine, "
               "l'égouttoir était là. Incrédule, je les ai comptées à nouveau.",
         "couple M3 au passé composé (C1)"),
        (False, "Je vais vérifier dans la cuisine. L'égouttoir, ce soir : "
                "deux assiettes.", "futur proche — conforme (C3)"),
        (False, "Je décide de reprendre les faits dans l'ordre. J'ai préparé "
                "le dîner, j'ai mangé.", "décision de carnet — conforme (C2)"),
    ]:
        found_item = bool(decision_execution_pairs(text))
        if found_item is not expected_true:
            failures.append(f"cas connu « {what} » : "
                          f"{'raté' if expected_true else 'faux positif'}")
    for expected_pattern, text, what in [
        (True, "L'égouttoir, ce soir : deux assiettes.", "quantité en lettres"),
        (True, "Demain, tout sera clair.", "attracteur du lendemain"),
        (True, "je me demandais si je devenais folle", "attracteur de la folie"),
        (True, "Perplexe, je repose le cahier.", "état mental en apposition"),
    ]:
        r = analyze(text)
        seen = bool(r["precision"] or r["attracteurs"] or r["etats_mentaux"])
        if seen is not expected_pattern:
            failures.append(f"cas connu « {what} » : raté")
    for term, text in [("télévision", "j'ai allumé la télévision"),
                         ("travail", "Je suis revenue du travail"),
                         ("sac à main", "j'ai posé mon sac à main"),
                         ("barquette", "j'ai sorti une barquette de lasagnes")]:
        if not material_forbidden(text, chapter=2):
            failures.append(f"cas connu « {term} » : interdit matériel raté")
    # The per-chapter scope must LOOSEN, not only tighten.
    if not material_forbidden("j'ai regardé mon téléphone", chapter=2):
        failures.append("cas connu « téléphone au ch. 2 » : raté")
    if material_forbidden("j'ai regardé mon téléphone", chapter=5):
        failures.append("cas connu « téléphone au ch. 5 » : faux positif — les "
                      "mémos deviennent légitimes, le scope ne s'ouvre pas")
    # REPETITION, session 7. Both directions, because the control is blocking
    # and REMOVES text: a false positive costs a paragraph of narrative.
    _TRUE = ("Je range les deux assiettes dans le lave-vaisselle, en prenant "
             "soin de les placer côte à côte.",
             "En attendant, je décide de ranger les deux assiettes dans le "
             "lave-vaisselle. Je les place côte à côte, en prenant soin de bien "
             "les essuyer avant de les mettre à l'intérieur.")
    _FALSE = ("Je relis l'entrée d'hier. Ma mémoire dit une assiette.",
             "Je suis rentrée, j'ai posé le cahier, j'ai préparé le dîner.")
    if not repeated_paragraphs("\n\n".join(_TRUE)):
        failures.append("cas connu « la même action rangée deux fois » (S6-3 "
                      "¶10/¶13) : redite non détectée")
    if repeated_paragraphs("\n\n".join(_FALSE)):
        failures.append("cas connu « deux constats distincts » : FAUX POSITIF — "
                      "le contrôle retirerait un paragraphe de récit")
    if not repeated_sentences(
            "Je me souviens pourtant distinctement d'avoir mangé seule hier "
            "soir.\n\nJe me souviens pourtant distinctement d'avoir mangé "
            "seule hier soir. Et pourtant."):
        failures.append("cas connu « phrase reprise d'un ¶ à l'autre » (S6-3 "
                      "¶2/¶3) : non détectée")
    # CODE ARTEFACTS are never a repetition; falsified because without this
    # protection the three strongest similarities of S6-C were the header, the
    # anchor and the drift: removal would have deleted the audio switch and
    # the gesture held 4/4.
    _ARTIFACTS = "\n\n".join([
        "Mardi 12. Ciel couvert.", "Mercredi 13. Pluie fine.",
        "« Deux assiettes mises, sans y penser. »",
        "« Deux assiettes mises, sans y penser. »",
        "Si je savais seulement pourquoi… L'assiette est sèche. Je la range.",
        "Je pourrais me demander ce qui, ce soir-là… L'assiette est sèche. "
        "Je la range."])
    if repeated_paragraphs(_ARTIFACTS) or repeated_sentences(_ARTIFACTS):
        failures.append("cas connu « artefacts du code » : FAUX POSITIF — "
                      "en-tête, ancre ou glissement comptés comme redite")

    # Session 7 ATTRACTORS: three runs of four closed with this family without
    # a cross, one word away from the caught pattern.
    for _t in ("demain sera un autre jour", "demain sera une nouvelle journée",
               "demain sera une journée meilleure", "à la lumière du jour"):
        if not ATTRACTORS.search(_t):
            failures.append(f"cas connu « {_t} » : attracteur raté")
    for _t in ("demain je relirai le cahier", "une journée ordinaire",
               "la lumière du couloir"):
        if ATTRACTORS.search(_t):
            failures.append(f"cas connu « {_t} » : FAUX POSITIF d'attracteur")

    # --- PRE-REPETITION MICRO-BATCH (2026-08-26) -----------------------------
    # The three targets named by the session 7 filled grid.
    if not decision_execution_pairs(
            "Je me lève, décidée à vérifier cette erreur. "
            "Je compte les assiettes sur l'égouttoir."):
        failures.append("cas connu « couple M3 au participe » (S7-1) : raté — "
                      "le motif ne borne pas « décidée à »")
    if accumulation_at_first_person(
            "Elle est revenue à vingt heures, a refermé le cahier, "
            "posé la lampe, compté les assiettes")[0]:
        failures.append("cas connu « accumulation à la troisième personne » "
                      "(S7-3) : raté")
    if not accumulation_at_first_person(
            "Je suis rentrée, j'ai posé le cahier, j'ai compté les assiettes")[0]:
        failures.append("cas connu « accumulation à la première personne » : "
                      "FAUX POSITIF — une accumulation conforme rejetée")
    _WITH_QUOTE = ('Mardi 12. Ciel couvert.\n\n« Deux assiettes mises. »\n\n'
                 'Je relis le cahier.\n\n'
                 '"Les deux assiettes étaient bien là, sur l\'égouttoir."\n\n'
                 'Erreur de relevé.')
    _quotes = quotations_outside_anchor(_WITH_QUOTE, verdict="erreur de relevé")
    if len(_quotes) != 1:
        failures.append(f"cas connu « citation inventée » (S7-3) : {len(_quotes)} "
                      "signalement(s) au lieu d'un — l'ancre est-elle exemptée "
                      "par son rang ?")
    for _t in ("Je referme le carnet. Bonne nuit.",):
        if not ATTRACTORS.search(_t):
            failures.append("cas connu « Bonne nuit » : attracteur raté")
    if ATTRACTORS.search("j'ai passé une bonne nuit de sommeil"):
        failures.append("cas connu « une bonne nuit de sommeil » : FAUX POSITIF")

    # --- ORTHOGONAL BATCH OF CHAPTER 7 (2026-08-27) --------------------------
    # The weapon image: the cleaver dodged through metaphor, seen twice
    # (session 5 and chapter 7 draw 6). The meta-term lint cannot see it; it
    # is not a workshop word.
    for _t in ("le coup de couteau : je n'ai pas rêvé", "comme une lame",
               "comme un couteau", "ce n'était pas un rêve"):
        if not ATTRACTORS.search(_t):
            failures.append(f"cas connu « {_t} » : attracteur raté")
    # And the objects that are NOT images: a floorboard, a knife set down. A
    # blocking control confusing the two removes narrative.
    for _t in ("une lame de parquet", "le couteau est sur la table",
               "j'ai rêvé de la maison"):
        if ATTRACTORS.search(_t):
            failures.append(f"cas connu « {_t} » : FAUX POSITIF d'attracteur")
    if not MARKS.search("l'enceinte Bluetooth allumée"):
        failures.append("cas connu « Bluetooth » (tirage 6 du ch. 7) : "
                      "marque déposée ratée")
    if MARKS.search("l'enceinte du salon, allumée"):
        failures.append("cas connu « enceinte sans marque » : FAUX POSITIF")

    # --- MOVEMENT METHOD (2026-08-27, ADR-0019) ------------------------------
    # PROMPT COPY, against its known case: chapter 7 draw 6 transcribed the
    # opening instruction at 0.94, and nothing saw it.
    _CONS = ("Le soir, le cahier ouvert : la phrase relue, l'écart entre ce "
             "qu'elle lit et ce dont elle se souvient, la chaise repoussée.")
    _TXT = ("Le soir, le cahier ouvert : la phrase relue, l'écart entre ce que "
            "je lis et ce dont je me souviens, la chaise repoussée.")
    if not prompt_copy(_TXT, _CONS):
        failures.append("cas connu « consigne recopiée » (tirage 6 du ch. 7) : "
                      "la recopie du prompt n'est pas détectée")
    if prompt_copy("Je relis l'entrée d'hier. Ma mémoire dit une "
                         "assiette, un dîner seule.", _CONS):
        failures.append("cas connu « texte propre » : FAUX POSITIF de recopie")

    # MACHINERY in a served context. §5 of brief v2 served it as is; the
    # former guard saw one word in ten.
    for _t in ("L3 exempté par la table de pilotage", "interdits bloquants",
               "possédés par le code, tamponnés en dernier"):
        if not MACHINERY.search(_t):
            failures.append(f"cas connu « {_t[:34]} » : machinerie non détectée")
    # « la table » is FURNITURE in this novel, and one of the chapter 7 objects.
    for _t in ("les photos sont sur la table", "la table du séjour"):
        if MACHINERY.search(_t):
            failures.append(f"cas connu « {_t} » : FAUX POSITIF de machinerie")

    # L4 AGAINST THE BANK. The three hand-written drifts are the definition of
    # the gesture: L4 must count them conforming. The previous version classed
    # all three « hors champ du départ »: an impossible green turned into
    # three crosses against the gesture finally correct.
    for _appr in ("Je pourrais me demander ce qui, ce soir-là",
                  "Si je savais seulement pourquoi",
                  "Il faudrait que je relise le jour où elle"):
        _n, _outside = drifts(
            f"J'ai mangé seule. {_appr}… L'assiette est sèche. Je la range.")
        if _n != 1 or _outside:
            failures.append(f"cas connu « banque du glissement » : "
                          f"« {_appr}… » compté {_n} fois, {len(_outside)} hors "
                          f"champ — L4 refuse la définition du geste")
    if summarizing_accumulation(
            "perplexité, concentration sur les détails, rappel des faits, "
            "fatigue, panique, respiration calme, explication rationnelle, "
            "corps qui parle, verdict d'erreur de relevé, épuisement, "
            "endormissement, vigilance")[0] <= ACC_ABSTRACT_MAX:
        failures.append("cas connu « sommaire nominal de C2 » : raté")

    print(f"\n{'=' * 70}")
    if failures:
        print(f"AUTO-TEST ÉCHOUÉ — {len(failures)} problème(s) :")
        for e in failures:
            print(f"  ✗ {e}")
        return 1
    print("AUTO-TEST OK — les 4 étalons sortent propres, "
          "l'accumulation est isolée sur l'étalon 2.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="factory eval lint")
    parser.add_argument("files", nargs="*", help="Runs à analyser")
    parser.add_argument("--references", action="store_true",
                        help="Auto-test sur les étalons de la fiche")
    parser.add_argument("--sheet", default=str(BIBLE_DIR / "style-auteur.md"))
    args = parser.parse_args(argv)

    if args.references:
        return autotest(Path(args.sheet))
    if not args.files:
        parser.error("donne au moins un fichier, ou --references")

    for path in args.files:
        p = Path(path)
        print(report(analyze(p.read_text(encoding="utf-8")), title=p.name))
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
