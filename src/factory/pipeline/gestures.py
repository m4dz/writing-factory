#!/usr/bin/env python3
"""Assembly micro-nodes — the signature gestures of the style (stage C).

Two gestures that eight runs never produced spontaneously:

  `accumulate` — the accumulation sentence: one long sentence of comma-joined
      clauses that retraces the facts in order up to the one that is off.
      Four sessions established that neither the sheet (three formulations)
      nor a reproach loop yields it (never one authentic). It is therefore
      ASSEMBLED.

  `drift` — the drift passage: a sentence approaching the departure, cut at
      « … », immediately followed by a material fact. Zero occurrences in
      eight runs.

Division of labour, identical for both: the model supplies the MATTER (one
sentence), the code makes the FORM (the cut, the place, the count). Project
doctrine — the guard that holds is in the code — applied to building rather
than forbidding (ADR-0018).

Two assembly rules, explicit because they are easy to miss:

  1. **Never both gestures in the same paragraph.** The drift lives in the
     reconstruction, the accumulation goes before the verdict. Adjacent, they
     make not a style but a tic — the very defect stage C is meant to put out,
     and could manufacture itself.

  2. **Positions are computed against the ORIGINAL text, insertions applied
     from the END to the START.** Otherwise the first insertion shifts the
     offsets of the second and the drift lands off target. Costs nothing, and
     the kind of error seen one time in three.
"""

import random
import re

from factory.eval.lint import (ACC_ABSTRACT_MAX, L3_WORDS,
                        L3_COMMAS, summarizing_accumulation,
                        accumulation_at_first_person, accumulations_l3,
                        material_forbidden, sentences, reference_copy)
from factory.text import delint

MAX_ATTEMPTS = 2

# CEILING of the accumulation. The spec set only a floor (60 words), and the
# model fills the space offered: 214 words in C1 against 90 for the reference.
# A threshold without an upper bound frames nothing — the reasoning that
# rejected raising `num_predict` in session 1, taken from the other end.
ACC_WORDS_MAX = 120

# The verdict term is the PRIMARY landmark of the entry, and not an
# implementation detail: it is the only guaranteed point, because another
# check requires its presence (the verdict lint).
#
# Reconstruction markers serve only as fallback. They depend upon the chapter:
# « fatigue » is chapter 2's step, but the pilot table migrates it
# (automatisme, trouble, l'autre). Relying upon them as primary would have
# broken SILENTLY from chapter 3.
RECONSTRUCTION_MARKERS = re.compile(
    r"\b(dans l'ordre|reprends? les faits|repass\w+|reconstitu\w+|"
    r"fatigue|automatisme|trouble|distraction|inattention)\b", re.IGNORECASE)

# THE SUSPENDED PIVOT — what makes a sentence an approach.
#
# ⚠ This pattern REPLACED a check that required a departure word (partie,
# absence, quittée…) in the approach. That criterion was WRONG and cost the
# gesture: it rejected the THREE hand-written approaches delivered by the
# protocol (« Je pourrais me demander ce qui, ce soir-là », « Si je savais
# seulement pourquoi », « Il faudrait que je relise le jour où elle ») — none
# names the departure — and it is literally what rejected the model's approach
# in C2, two attempts in a row.
#
# The gesture is defined by the interruption BEFORE the departure is named.
# Requiring the departure word in the approach demands that the gesture not
# happen: the validator meant to guarantee the drift was what prevented it.
#
# What an approach really carries is a PIVOT left open — an interrogative or
# relative word after which the sentence cuts.
# The departure field, FORBIDDEN in a written passage: the gesture stops
# before naming. Same list as lint L4, used the other way round.
FORBIDDEN_DEPARTURE_FIELD = re.compile(
    r"\b(partie|départ|absence|absente|quittée|plus là)\b", re.IGNORECASE)
SUSPENSION_PASSAGE = re.compile(r"…|\.\.\.")

SUSPENDED_PIVOT = re.compile(
    r"\b(ce qui|ce que|pourquoi|comment|où|quand|le jour où|si elle|"
    r"ce qu'|qui a|quelle|lequel)\b", re.IGNORECASE)


def paragraphs(text: str) -> list[tuple[int, int, str]]:
    """(start, end, content) of each paragraph, offsets into the given text."""
    out, pos = [], 0
    for block in text.split("\n\n"):
        out.append((pos, pos + len(block), block))
        pos += len(block) + 2
    return [b for b in out if b[2].strip()]


def accumulation_position(text: str, verdict: str) -> int:
    """Insertion offset: just BEFORE the verdict paragraph.

    Falls back to the last paragraph carrying reconstruction markers, then to
    the second-to-last paragraph. Always returns a valid position: a gesture
    we give up placing is a gesture lost.
    """
    paras = paragraphs(text)
    if verdict:
        core = re.split(r"\s*\(", verdict)[0].strip()
        for start, _, content in paras:
            if core and core.lower() in content.lower():
                return start
    for start, _, content in reversed(paras):
        if RECONSTRUCTION_MARKERS.search(content):
            return start
    return paras[-1][0] if len(paras) > 1 else len(text)


def drift_position(text: str, acc_position: int,
                        reconstruction_bounds: tuple[int, int] | None = None
                        ) -> int:
    """Insertion offset of the drift, inside the reconstruction.

    RULE 1: never in the paragraph that will receive the accumulation. If the
    only candidate is that one, step back one paragraph.

    When `write` generates in three segments, the BOUNDS of the reconstruction
    are known and authoritative. A gain of substance, not of comfort: the
    fallback to `RECONSTRUCTION_MARKERS` keys off *fatigue* and *automatisme*,
    values of the « marche des explications » column that the pilot table
    migrates (fatigue → automatisme → trouble → l'autre), so it would have
    broken SILENTLY from chapter 3. Segmenting makes the reconstruction
    locatable by construction rather than by lexicon.
    """
    paras = paragraphs(text)
    # THE LAST THIRD IS OFF LIMITS TO THE DRIFT (micro-batch, item 3).
    #
    # In S7-2 it landed as the LAST LINE of the entry, after the « couperet »
    # and the physiology: there a suspended sentence suspends nothing, it
    # consoles. The gesture lives in the reconstruction, where it interrupts a
    # thought in progress; at the close it undoes the fall the ending just set.
    last_third = int(len(text) * 2 / 3)
    if reconstruction_bounds:
        a, b = reconstruction_bounds
        b = min(b, last_third) if a < last_third else b
        inner = [p for p in paras if a <= p[0] < b]
        # NOT ADJACENT, not merely « pas dans le même paragraphe ». The
        # protocol's §2 says « jamais adjacent à l'accumulation », and the
        # nuance matters: set at the end of the reconstruction's last
        # paragraph, the drift lands right above the accumulation — two
        # signatures glued together, a tic rather than a style. Prefer a
        # paragraph that does not touch the splice point. Measured before
        # being written: a two-paragraph reconstruction produced exactly this
        # collision.
        distant = [p for p in inner if p[1] + 2 != acc_position]
        for start, end, _ in reversed(distant or inner):
            if start != acc_position:
                return end
    candidates = [p for p in paras if RECONSTRUCTION_MARKERS.search(p[2])
                 and p[0] < last_third]
    if not candidates:
        candidates = [p for p in paras[1:-1] if p[0] < last_third] or paras[1:-1] or paras
    for start, end, _ in reversed(candidates):
        if start != acc_position:
            return end
    previous_ones = [p for p in paras if p[0] < acc_position]
    return previous_ones[-1][1] if previous_ones else paras[0][1]


# The drift bank — approaches and material facts, written by hand — is chapter
# knowledge and lives in the chapter spec (`drift_bank`); the loader asserts
# each approach against `approach_valid` at load time.


def approach_valid(approach: str) -> tuple[bool, str]:
    """Is an approach usable? BANK ASSERTION.

    Since the matter is written by hand, this function no longer filters a
    model output: it checks that the bank conforms. Kept because
    « avant de faire confiance à un contrôle, exiger qu'il échoue sur un cas connu »
    presumes a check, and a hand-edited bank can take a faulty line like any
    file.

    Three criteria, not one more: long enough to be a sentence, not a dated
    header (the model once returned « Mardi 12. Pluie fine » as an approach,
    and the code composed a false header mid-entry from it), and a pivot left
    open.
    """
    a = approach.strip()
    if len(a.split()) < 5:
        return False, f"trop courte ({len(a.split())} mots)"
    if re.match(r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d",
                a, re.IGNORECASE):
        return False, "c'est un en-tête daté, pas une approche"
    if not SUSPENDED_PIVOT.search(a):
        return False, "aucun pivot resté ouvert (ce qui, pourquoi, le jour où…)"
    return True, ""


def passage_valid(passage: str) -> tuple[bool, str]:
    """The WRITTEN drift, delivered whole by the brief. Symmetric validation.

    Two conditions, the second new:
      · a PIVOT left open — the sentence approaches, then cuts;
      · NO word of the departure field — naming the departure is a refusal.

    Session 6 removed the opposite requirement (a departure word IN the
    approach), which rejected the three delivered approaches and blocked the
    gesture. The rule turns around here and gets stronger: the gesture is to
    break off BEFORE naming, so naming disqualifies (ADR-0019).

    Falsified both ways, against the delivered passage and a variant that
    names the departure — otherwise it would be a mere preference.
    """
    p = passage.strip()
    if len(p.split()) < 8:
        return False, f"trop court ({len(p.split())} mots)"
    if not SUSPENDED_PIVOT.search(p):
        return False, "aucun pivot resté ouvert (ce qui, pourquoi, quand…)"
    if FORBIDDEN_DEPARTURE_FIELD.search(p):
        m = FORBIDDEN_DEPARTURE_FIELD.search(p)
        return False, (f"nomme le départ (« {m.group(0)} ») — le geste "
                       "s'interrompt AVANT")
    if not SUSPENSION_PASSAGE.search(p):
        return False, "aucune interruption marquée par des points de suspension"
    if len(SUSPENSION_PASSAGE.findall(p)) > 1:
        return False, f"{len(SUSPENSION_PASSAGE.findall(p))} interruptions — une seule"
    return True, ""


def draw_approach(bank: dict, already_drawn: list[str],
                   seed: int) -> tuple[str, str]:
    """Draw an approach not yet used in this chapter, and the fact.

    RANDOM DRAW WITHOUT REPLACEMENT, seed supplied by the caller and recorded
    in the run's frontmatter. Determinism by entry index would have put the
    same sentence at the same place at every run: a liturgy of our own
    template, exactly the defect measured three times (the reference recited,
    the counter-examples reused). The seed keeps the run replayable (ADR-0018).

    Returns `("", "")` when the chapter has no bank (`{approaches, facts}` in
    the spec): a chapter with no planned drift is not an error, and M1 reads
    it as « non prévu ».
    """
    approaches = list((bank or {}).get("approaches") or ())
    facts = list((bank or {}).get("facts") or ())
    if not approaches or not facts:
        return "", ""
    # The fact rotates WITH the approach, at its own index: two drifts of the
    # same chapter share neither head nor tail.
    fact = facts[len(already_drawn) % len(facts)]
    remaining_ones = [a for a in approaches if a not in already_drawn]
    if not remaining_ones:
        # No fresh approach left: return empty rather than repeat. The same
        # sentence twice in a chapter is the tic we are trying to put out.
        return "", fact
    return random.Random(seed + len(already_drawn)).choice(remaining_ones), fact


def compose_drift(approach: str, material_fact: str) -> str:
    """Cut the approach at « … » and append the material fact.

    The code COMPOSES: that is what makes the gesture conform by construction
    — at most one occurrence, the cut at the right place, the immediate return
    to the material. The model supplied only a sentence.
    """
    a = approach.strip().rstrip(" .!?…")
    # If the model already put suspension points, cut there.
    a = re.split(r"\s*(?:…|\.\.\.)", a)[0].rstrip(" ,;")
    return f"{a}… {material_fact.strip()}"


def validate_accumulation(sentence: str, last_attempt: bool = False,
                         chapter: int = 2) -> tuple[bool, str]:
    """COUNTING check, with an anti-copy guard.

    An accumulation copied from the reference is not one: session 3 saw two
    « réussites » that were the reference to the character, in a scene about
    something else.
    """
    # LANGUAGE FIRST. An English accumulation is not « un peu courte », it is
    # not an accumulation: this check runs before any threshold tolerance,
    # otherwise the last-attempt tolerance accepted it (gap found by the
    # step 2 safety net, fixed at step 5).
    _, alerts = delint(sentence)
    leaks = [a for a in alerts if "anglais" in a]
    if leaks:
        return False, f"langue : {leaks[0]}"
    if not accumulations_l3(sentence):
        # THE MESSAGE SAYS WHAT THE GATE MEASURED, not what the candidate weighs.
        #
        # The old version counted the WHOLE candidate (`len(split())`) while
        # `accumulations_l3` measures the longest SENTENCE and refuses any
        # semicolon. Hence the impossible message of S6-2, refused:
        # « 60 mots, 10 virgules ; il faut 60 et 6 ». The candidate carried
        # an inner period or a `;`, not eight words too few. Session 7's
        # protocol diagnosed « perdue pour huit mots » from that message and
        # asked to symmetrise the thresholds: a check that reports something
        # other than what it measures gets the wrong part fixed.
        segments = sentences(sentence)
        longest = max(segments, key=lambda p: len(p.split()), default=sentence)
        cause = []
        if len(segments) > 1:
            cause.append(f"{len(segments)} phrases (un point à l'intérieur)")
        if ";" in sentence:
            cause.append("un point-virgule")
        m, v = len(longest.split()), longest.count(",")
        if m < L3_WORDS:
            cause.append(f"{m} mots au lieu de {L3_WORDS}")
        if v < L3_COMMAS:
            cause.append(f"{v} virgules au lieu de {L3_COMMAS}")
        detail = ", ".join(cause) + f" (candidat entier : {len(sentence.split())} mots)"
        # THRESHOLD SYMMETRY (session 7). The ceiling was tolerated at the last
        # attempt, the floor was not: S6-2 returned an accumulation eight words
        # short and lost it while S6-1 kept one of 215. A slightly short
        # accumulation is a style defect; a missing one is a blocking failure —
        # the asymmetry punished the lesser evil.
        #
        # The tolerance covers ONLY the count. A sentence cut in two or carrying
        # a semicolon is not a short accumulation, it is something else: the
        # form stays refused to the end.
        broken_form = len(segments) > 1 or ";" in sentence
        if not last_attempt or broken_form:
            return False, "seuils non atteints — " + detail
        return True, f"ACCEPTÉE malgré des seuils non atteints — {detail} — dernier essai"
    if reference_copy(sentence):
        return False, "étalon recopié — ce n'est pas une accumulation"
    # The ceiling is STRICT at the first attempt, TOLERATED at the last: an
    # over-long accumulation is a style defect, a missing one a blocking
    # failure. Refuse excess while a relaunch is still possible; accept and
    # flag it at the last round.
    n = len(sentence.split())
    # HARD CEILING (1.4× the soft ceiling). The last-attempt tolerance had NO
    # limit: one draw returned 190 words (~30 steps), accepted as
    # « malgré 190 mots — dernier essai », and was cut mid-word when served.
    # Beyond ~1.5× the ceiling this is not « un peu longue », it is a runaway.
    # The accumulation is optional: none beats a truncated litany.
    if n > int(ACC_WORDS_MAX * 1.4):
        return False, (f"emballement ({n} mots ; plafond dur "
                       f"{int(ACC_WORDS_MAX * 1.4)}) — rejetée même au dernier "
                       "essai, l'accumulation est droppée")
    if n > ACC_WORDS_MAX and not last_attempt:
        return False, (f"trop longue ({n} mots ; plafond {ACC_WORDS_MAX})")
    # (Language was checked first: at the first stage-C run, `accumulate`
    # returned 75 words and 7 commas — in ENGLISH — and validation accepted it
    # because it counted words, not a language. Counting is not reading;
    # FRENCH_GUARD in the system prompt is not enough.)
    # THE ACCUMULATION THAT SUMMARISES (session 6). C2 returned 131 words of
    # table of contents — « perplexité, concentration, rappel, fatigue, panique… »
    # — and the counters accepted it: *counting is not reading* a second time,
    # after English.
    #
    # ⚠ The protocol prescribed « propositions verbales exigées ». Measured:
    # that criterion REJECTS THE REFERENCE, whose accumulation is nominal in
    # 88 % of its items (« le café de sept heures, le départ, la réunion… »).
    # The real discriminant is ABSTRACTION — the reference lists things and
    # moments, C2 listed the entry's beats. Reference: 0 %. Six stage-C
    # accumulations: 0 %. C2: 47 %.
    # THE PERSON. The notebook has one subject. S7-3 returned
    # « Elle est revenue à vingt heures, a refermé le cahier… » in the middle
    # of an entry wholly in the first person — a switch only a standing
    # read-through saw.
    # Rejected at the gate: mechanical, and an accumulation in the wrong person
    # cannot be repaired downstream.
    person_ok, person_reason = accumulation_at_first_person(sentence)
    if not person_ok:
        return False, person_reason
    part, abstract_items = summarizing_accumulation(sentence)
    if part > ACC_ABSTRACT_MAX:
        return False, (f"elle se résume au lieu de compter : {part:.0%} d'items "
                       f"abstraits ({', '.join(abstract_items[:4])})")
    # GENERIC DECOR, blocking HERE and nowhere else. `accumulate` became stage
    # C's famine channel: receiving only the entry and a form instruction, the
    # node invented the missing steps from its priors — television and
    # messages (C1), « revenue du travail » though she works at home (C3),
    # handbag and tray (CC). Nemo's generic world, driven out of `write` by the
    # RAG, came back in here.
    #
    # Blocking in this node, a mere flag in the writing text: automating a
    # check and making it blocking are two distinct decisions, and §4.2
    # demands « zéro terme » in PRODUCED accumulations.
    scenery = material_forbidden(sentence, chapter)
    if scenery and not last_attempt:
        return False, (f"décor hors du monde : "
                       f"{'; '.join(d.split(' : ')[0] for d in scenery[:3])}")
    if len(sentence.split()) > ACC_WORDS_MAX:
        return True, (f"ACCEPTÉE malgré {len(sentence.split())} mots (plafond "
                      f"{ACC_WORDS_MAX}) — dernier essai")
    return True, ""


# The brief declares the frontier as a French sentence
# (« à la frontière entre la découverte de la musique et celle du plat »).
# The composer derives the DOWNSTREAM anchor from it: the passage goes just
# before what follows the frontier.
# The lexical anchors of a frontier are chapter knowledge: `drift_anchors` in
# the chapter spec, `{key: [phrases]}`, compiled here (ADR-0025).
def compile_anchors(anchors: dict) -> dict[str, re.Pattern]:
    return {key: re.compile(r"\b(?:" + "|".join(re.escape(p) for p in phrases) + r")\b",
                            re.IGNORECASE)
            for key, phrases in (anchors or {}).items() if phrases}


def frontier_position(text: str, position: str, anchors: dict | None = None) -> int | None:
    """Insertion offset of a passage at a frontier declared in French.

    Looks for the DOWNSTREAM anchor — « la frontière entre la musique et le plat »
    places the passage just before the « plat » paragraph. The position is
    thus a place in the NARRATIVE, not an offset: the return to the material
    that closes the passage IS the next discovery, and the gesture becomes the
    hinge instead of an added part.

    Returns None when the anchor cannot be found — a gesture placed at random
    is worse than none, and the caller must be able to say so. `anchors` is
    the chapter spec's `drift_anchors`; without it nothing can be placed.
    """
    words = position.lower()
    patterns = compile_anchors(anchors)
    # DOWNSTREAM is the last term named IN THE SENTENCE, not in the dict.
    # « entre la découverte de la musique et celle du plat »: downstream is
    # « plat ». The first version iterated over the keys and kept « musique »
    # — the passage landed one paragraph too early, at the wrong frontier.
    named = [(words.rindex(key), pattern)
              for key, pattern in patterns.items() if key in words]
    if not named:
        return None
    downstream = max(named)[1]
    for start, _, content in paragraphs(text):
        if downstream.search(content):
            return start
    return None


def assemble(text: str, accumulation: str, drift: str, verdict: str,
              reconstruction_bounds: tuple[int, int] | None = None,
              frontier: int | None = None) -> tuple[str, list[str]]:
    """Insert both gestures. RULE 2: positions against the original, from the
    end to the start (ADR-0018)."""
    notes: list[str] = []
    pos_acc = accumulation_position(text, verdict) if accumulation else -1
    pos_gli = (frontier if frontier is not None else
               drift_position(text, pos_acc, reconstruction_bounds)
               ) if drift else -1

    inserts = []
    if accumulation:
        inserts.append((pos_acc, accumulation.strip() + "\n\n"))
    if drift:
        # THE FRAGMENT'S SHAPE DEPENDS UPON THE LANDMARK, and it is easy to
        # miss: `drift_position` returns a paragraph END (the gesture goes
        # after, hence « \n\n » in front), `frontier_position` a START (the
        # gesture goes before, hence « \n\n » behind). Mixing them up yields
        # one blank line too many at one side and a collage at the other —
        # exactly what the first attempt produced.
        inserts.append((pos_gli, drift.strip() + "\n\n"
                        if frontier is not None
                        else "\n\n" + drift.strip()))
    if accumulation and drift and pos_acc == pos_gli:
        notes.append("les deux gestes visaient le même point — glissement "
                     "reculé (règle d'assemblage 1)")

    # From the END to the START: offsets computed against the original stay
    # valid for the insertions that precede them.
    for position, fragment in sorted(inserts, key=lambda x: -x[0]):
        text = text[:position] + fragment + text[position:]
    return text, notes
