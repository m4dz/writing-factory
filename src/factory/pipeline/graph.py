#!/usr/bin/env python3
"""The author-mode orchestrator (LangGraph).

The pipeline shown onstage (layer 4 of the talk):

    entry plan → writing entry by entry → review → coherence

A SEQUENTIAL graph with one loop over the entries. Flow control is
deterministic (LangGraph); the model supplies the matter at each node. The
context is re-assembled from the bible at every entry (dynamic RAG,
`factory.retrieval.context`), never frozen.

The unit of composition is the DATED notebook ENTRY: L'Involontaire is a
journal, and the style-sheet quotas count per entry. The state field `rag`
switches retrieval — the one variable that separates the two stages of
session 4; it lives in the state so it cannot drift between two runs.
"""

import difflib
import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END



from factory.infra import progress
from factory.eval.lint import (ENTRY_HEADER, MACHINERY,
                        MARKS, META_TERMS, material_forbidden)
from factory.infra.ollama import chat, unload
from factory.retrieval.context import REVIEW_STYLE, assemble_system_prompt
from factory.text import delint, ends_mid_sentence, sentence_ends, trim_to_sentence
from factory.pipeline.qa import repair, derive_facts, check_facts, check_plan
from factory.chapter_spec.model import EMPTY_ENTRY, EntrySpec
from factory.pipeline import scorers
from factory.eval import style
from factory.pipeline.nodes.narrative_state import narrative_state_node
from factory.pipeline.nodes.preflight import preflight_node
from factory.pipeline.nodes.render import render_node
from factory.settings import settings
from factory.pipeline.gestures import (assemble, compose_drift, passage_valid,
                    frontier_position, draw_approach,
                    validate_accumulation)
from factory.eval.lint import repeated_paragraphs

# Model of the gesture micro-nodes: nemo, not Qwen. They run INSIDE the writing
# loop with nemo warm; a Qwen call there costs two swaps per entry (139-222 s
# measured in `plan_node`, session 4). And `accumulate` writes the most audible
# marker of the style, a sentence that stays in the chapter: voice, not QA
# (ADR-0008). `settings.gesture_model` keeps the alternative measurable.
# Assembly pass: DETERMINISTIC pruning of the diffuse residue (day outside,
# presence, recursion, resolution tell) that best-of-N cannot catch when ALL
# variants carry it. The cross-model Qwen route was falsified: as editor Qwen
# cuts the good sentences, as detector it misses the oblique outing (« NON » to
# « le départ, la réunion, la départementale, le garage » — the coherence node
# has the same blind spot). Code matches without ambiguity (ADR-0020).
# Switched off by `settings.pruning_enabled`.

# The unit of composition is the DATED notebook ENTRY, not the scene. The novel
# is a journal: what the plan cuts are evenings. The sheet's quotas
# (accumulation, physiology, cleaver) count per entry — counting them per
# « scène » would make the machine and the grid count different units.
WORDS_PER_ENTRY = (450, 600)

# One replan only. Replanning costs a reload of nemo (13 GB): beyond that we
# lose more stage time than we save, and a model that misses the constraint
# twice will not get it the third time.
MAX_PLAN_ATTEMPTS = 2

# One continuation per cut generation. Raising `num_predict` solves nothing — a
# model that has not finished at 1400 tokens fills 1800 just as well: it
# occupies the space offered. A continuation costs only when the case occurs
# (one scene in four in the 2026-08-06 run, ~50 s).
MAX_CONTINUATIONS = 1

# Two attempts for the accumulation, as the protocol sets.
MAX_GESTURE_ATTEMPTS = 2


# --- Graph state -------------------------------------------------------------

class ChapterState(TypedDict):
    brief: str            # chapter objective (human input)
    characters: list[str] # doc_ids of the characters present
    facts: list[str]      # invariants derived from the bible (constrain the plan)
    plan: list[str]       # scene beats (output of the plan node)
    plan_report: str      # the plan checked against the facts, BEFORE writing
    idx: int              # index of the scene being written
    scenes: list[str]     # raw prose, one item per scene
    reviewed: list[str]   # prose after review (nemo)
    repaired: list[str]   # prose after linguistic repair (Qwen QA)
    coherence: str        # fact-by-fact coherence report (Qwen QA)
    metrics: list[dict]   # timing per LLM call (countdown / profiling)
    warnings: list[str]   # style-lint alerts (leaks, corrupted tokens)
    rag: bool             # stage A (False) or B (True) — the one variable
    expected_entries: int  # 1 = single-entry brief, the plan is short-circuited
    prefix: str          # quotation anchor, POSED BY THE CODE (item 5)
    start_day: str      # « Mardi » — anchor of the header sequence
    start_number: int    # 12 — the following dates derive from it, consecutive
    micro_nodes: bool    # stage C: accumulate + drift active
    active_objects: str    # the chapter's material, source of the material fact
    verdict: str          # the chapter's verdict — splice LANDMARK of the accumulation
    start_weather: str     # weather of the 1st entry, when the plan is short-circuited
    accumulation: str     # sentence produced by accumulate, set aside
    gestures: list[dict]    # one gesture set per entry, posed after repair
    segments: bool        # session 6: `write` in three calls — THE measured variable
    reconstruction: str   # the middle segment, accumulate's own context
    entry_specs: list    # explicit entry plan — ch. 7 has two entries the SAME day
    imposed_plan: list     # one beat per entry, cut from the brief: the plan is not asked
    placed_fall: str      # last line imposed word for word — posed by the code
    served_prompts: list  # (segment, prompt) — deliverable, and the copy measurement
    placed_header: str      # the header composed for the current entry — re-stamped
    placed_anchor: str      # the quotation anchor posed — re-stamped after repair
    seed: int           # drift draw, recorded in the run frontmatter
    chapter: int         # chapter number — scope of the material interdicts
    drawn_approaches: list[str]  # never the same one twice in a chapter
    # --- chapter knowledge, from the spec (step 5) ---------------------------
    stations: list[str]   # stations of the reconstruction segment
    accumulation_fall: str  # the object the accumulation ends upon
    drift_bank: dict      # {approaches: [...], facts: [...]} for the drift draw
    drift_anchors: dict   # {key: [phrases]} placing a written drift at its frontier
    # --- machine nodes (ADR-0002, item 5) ------------------------------------
    preflight: object     # None/False: skipped; True or {strict, timer}: checked first
    narrative_state: bool  # generate and index the chapter's narrative state chunk
    narrative_state_path: str
    artifacts_dir: str    # the run directory the render node writes into ("" : output/)
    preflight_warnings: list[str]
    render: bool          # write `chapitre.md` and render the WAV after coherence
    assembly: dict        # kwargs of assembly.assemble (switch mode, imposed fall)
    chapter_md: str       # the assembled chapter, both markers, always produced
    audio: object         # TTS metrics dict, or None when the voice failed / was not asked


# --- Nodes -------------------------------------------------------------------


# --- Headers composed by the CODE (block B) ---------------------------------
#
# The plan emits no header text. B′C produced « Lundi 2, nuageux. » — a comma
# instead of the period: detection broke, and the audio switch with it. A
# format the stage depends upon is not asked of a model, it is composed
# (ADR-0018).
#
# DATES are not even asked: they DERIVE from an anchor (weekday + start number,
# given by the brief). B′C produced [8, 7, 7, 7, 7, 9, 10, 7] — dates that go
# back and repeat. Derived, they are consecutive by construction, and the
# day ↔ date coherence the lint checks becomes true by construction, not by
# luck.
#
# Only the WEATHER comes from the plan: hard-coding it would bring the same
# weather back every run, one liturgy replacing another.
WEEKDAYS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi",
                 "Dimanche"]


def header(start_day: str, start_number: int, offset: int,
           weather: str) -> str:
    """« Mardi 12. Ciel couvert. » — canonical format, composed, never asked."""
    i = WEEKDAYS.index(start_day.capitalize())
    day = WEEKDAYS[(i + offset) % 7]
    weather = (weather or "Temps calme").strip().rstrip(".")
    return f"{day} {start_number + offset}. {weather[0].upper()}{weather[1:]}."


# The weather asked of the plan, as an isolated field: `1. [Ciel couvert] ce qu'elle…`
BEAT_WEATHER = re.compile(r"^\s*\[([^\]]{2,40})\]\s*(.*)$")

# A dated header emitted BY THE MODEL, anywhere in its generation. The code owns
# the format and composes one per entry, so any header the model produces is
# parasitic by definition. C1 invented a second one (« Vendredi 15. Pluie
# fine. ») in an entry meant to be unique, and the lint split two entries where
# there was one.
# The number is OPTIONAL: the model also produces « Samedi. Beau temps. », a
# dateless header that passed every filter and ended up under the code's own,
# in the text read by the cloned voice. An approximate imitation is still one.
STRAY_HEADER = re.compile(
    # ⚠ NO global `re.IGNORECASE`: it would make the [A-Z] class match lowercase,
    # and the weather's capital is precisely what tells a header from a sentence
    # opening with a weekday. Case-insensitivity is limited to the day names, by
    # an inline group.
    r"^[ \t]*(?i:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)"
    r"(?:"
    # with number: the full form, the one the code composes
    r"[ \t]+\d{1,2}[.,][^\n]{0,40}"
    # WITHOUT number: « Samedi. Beau temps. » — a dateless header that passed
    # every filter and reached the text read by the cloned voice. Recognised by
    # the weather's capital and the end of line.
    r"|[.,][ \t]*[A-ZÀÂÇÉÈÊËÎÏÔÛÙÜŒ][^\n,]{1,28}\."
    r")[ \t]*\n+", re.MULTILINE)

# The model's SUSPENSION POINTS. The sheet is explicit: they exist nowhere but
# as the drift marker — « c'est leur seul emploi ». The code owns this marker as
# it owns the headers, so any « … » the model produces is parasitic by the same
# logic. In C2 BOTH occurrences came from the model —
# « une, deux, trois... trois assiettes », « depuis... depuis qu'elle est partie »
# — while the composed gesture had been abandoned: M1 fell to 2 without a single
# drift existing. They are replaced by the punctuation the context asks for.
# Two forms, in this order. The marker often CARRIED a repetition
# (« depuis… depuis son départ », « trois… trois assiettes »): removing it alone
# left the doubled word, broken text in place of a style defect. The repetition
# is absorbed with it; failing that, a comma — the punctuation the hesitation
# called for.
REPEATED_SUSPENSION = re.compile(
    r"\b(\w+)\s*(?:…|\.\.\.)\s*\1\b", re.IGNORECASE)
STRAY_SUSPENSION = re.compile(r"\s*(?:…|\.\.\.)\s*")


def split_weather(beat: str) -> tuple[str, str]:
    """Split the weather from the beat body. Returns ('', beat) when absent."""
    m = BEAT_WEATHER.match(beat)
    return (m.group(1).strip(), m.group(2).strip()) if m else ("", beat)


def _tag(metrics: list[dict], node: str) -> list[dict]:
    """Label the metrics with the node that produced them.

    The session deliverable asks for durations PER NODE — the margin of the
    keynote's 28 minutes is computed from them. Without the label the list of
    calls only gives the total, and a node that slips stays invisible.
    """
    for m in metrics:
        m.setdefault("noeud", node)
    return metrics


def _strip_approximate_restart(prefix: str, continuation: str) -> str:
    """Remove from the start of `continuation` an APPROXIMATE restart of the prefix.

    `_reattach` only removes an EXACT overlap. The defect measured in B′1 is
    not a copy but a RECOMPOSITION: « Je les ai laissées » for « Je l'ai
    laissée ». Without this filter the concatenation gives the correct anchor
    from the prefix FOLLOWED by the model's faulty version — a doublet, one
    half of it wrong.

    The first quoted passage of the continuation is compared with the last
    quoted passage of the prefix: above 70 % similarity it is the same
    sentence badly copied.
    """
    start = continuation.lstrip()
    # The HEADER first. The model re-emits its own « Mardi 12. Ciel couvert. »
    # — the brief still asked for it — and the code's prefix landed in front:
    # two headers, two anchors. The filter only looked at the quoted passage.
    for _ in range(2):
        m_tete = re.match(
            r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}[.,]"
            r"[^\n]{0,40}\n+", start, re.IGNORECASE)
        if not m_tete:
            break
        start = start[m_tete.end():].lstrip()
    continuation = start

    prefix_quotes = re.findall(r"[«\"][^»\"]{20,}[»\"]", prefix)
    if not prefix_quotes:
        return continuation
    anchor = prefix_quotes[-1]
    m = re.match(r"[«\"][^»\"]{20,}[»\"]", start)
    if not m:
        return continuation
    ratio = difflib.SequenceMatcher(None, m.group(0), anchor).ratio()
    return start[m.end():].lstrip() if ratio > 0.70 else continuation


def _style_tiebreak_note(label: str, ranked: list[dict]) -> list[str]:
    """One warning when the style marks, not the defects, chose the winner."""
    if len(ranked) < 2 or ranked[0]["score"] != ranked[1]["score"]:
        return []
    if ranked[0]["style"] == ranked[1]["style"]:
        return []
    return [f"{label} : départage par les marques de style — variant {ranked[0]['k'] + 1} "
            f"({ranked[0]['style']}) devant "
            + ", ".join(f"#{v['k'] + 1} ({v['style']})" for v in ranked[1:]
                        if v["score"] == ranked[0]["score"])]


def _strip_attack_echo(attack: str, continuation: str) -> str:
    """Remove from the start of `continuation` a repeat of the author's attack.

    The doctrine says shown is recited: a beat that opens on the owner's
    sentence may give it back, verbatim or recomposed, before going on. An
    exact copy is caught by the character overlap; a paraphrase by comparing
    the first sentence of the continuation with the attack (70 %, the ratio
    `_strip_approximate_restart` uses for the anchor).
    """
    s = continuation.lstrip()
    head = attack.strip()
    if s.startswith(head):
        return s[len(head):].lstrip()
    ends = sentence_ends(s)
    if not ends:
        return s
    first = s[:ends[0]]
    ratio = difflib.SequenceMatcher(None, first.lower(), head.lower()).ratio()
    return s[ends[0]:].lstrip() if ratio > 0.70 else s


def _reattach(start: str, continuation: str) -> str:
    """Reattach a continuation, removing the overlap.

    The model gladly restarts with the last sentence it just wrote, despite
    the instruction: the longest prefix of the continuation already present at
    the tail of the start is found and removed.

    The join needs care. If the cut fell mid-sentence and the continuation
    opens a NEW sentence instead of finishing the previous one (observed:
    « …dans un coin de la pièce Elle s'en approcha »), the fragment is
    orphaned. It is closed rather than deleted — deleting it would cost a
    whole sentence of narrative:
      * before a line of speech (em dash, guillemet), suspension points, the
        French punctuation of interrupted speech or thought. A period would
        give « Il hésita, puis. — Tu mens » ;
      * before an ordinary capital, a plain period.
    """
    s = continuation.lstrip()
    queue = start[-800:]
    # EXACT overlap, searched character by character: a coarser step leaves a
    # cutting residue in the middle of the text (« du marteau u qui »). 30
    # characters minimum, so a coincidence is not taken for a copy.
    for k in range(min(len(queue), len(s)), 29, -1):
        if s.startswith(queue[-k:]):
            s = s[k:].lstrip()
            break

    d = start.rstrip()
    if not ends_mid_sentence(d):
        return d + "\n\n" + s
    if s[:1] in "—–-«\"":
        return d + "…\n\n" + s
    if s[:1].isupper():
        return d + ". " + s
    return d + " " + s


def _generate_whole(system: str, user: str, *, num_predict: int,
                    temperature: float, label: str,
                    keep_going: bool = True) -> tuple[str, list[dict], list[str]]:
    """Generate a WHOLE text: relaunch if `num_predict` cut the generation.

    Ollama signals the amputation only through `done_reason: "length"` — the
    text comes back cut mid-word, without error. Observed in the 2026-08-06
    run (one scene at 1400/1400 tokens): review then worked from a truncated
    text, and the next scene inherited an unfinished narrative state.

    Two devices, in this order: a continuation (the text is returned whole),
    then as a net a cut at the last complete sentence if the model still
    overflows. The net is never the first resort: it returns a scene that
    stops early, so without the final state the plan asked of it.
    """
    text, m = chat(system, user, num_predict=num_predict, temperature=temperature,
                   on_token=progress.token_sink())
    metrics = [m]
    warns: list[str] = []

    for _ in range(MAX_CONTINUATIONS if keep_going else 0):
        if m.get("done_reason") != "length":
            break
        progress.note(f"{label} : génération coupée à {num_predict} tokens, "
                      "continuation demandée")
        continuation_user = (
            f"{user}\n\n=== CE QUI EST DÉJÀ ÉCRIT (fin du texte) ===\n"
            f"{text[-600:]}\n\n"
            "Ta génération a été coupée en cours de route. REPRENDS EXACTEMENT "
            "là où le texte s'arrête — sans le répéter, sans le résumer, sans "
            "recommencer — et TERMINE en quelques paragraphes. Écris seulement "
            "la suite."
        )
        continuation, m = chat(system, continuation_user,
                        num_predict=max(300, num_predict // 3),
                        temperature=temperature, on_token=progress.token_sink())
        metrics.append(m)
        text = _reattach(text, continuation)
        warns.append(f"{label} : génération coupée, continuation demandée")

    if ends_mid_sentence(text):
        cut = trim_to_sentence(text)
        if cut != text:
            # Say WHAT is removed, not only that something was. In the
            # 2026-08-06 run the net cut two scenes neither of which
            # `num_predict` had truncated (nemo sometimes emits its EOS
            # mid-sentence): without the excerpt there is no telling a dangling
            # fragment rightly removed from a real scene ending misread by the
            # punctuation detection.
            removed = text[len(cut):].strip()
            warns.append(
                f"{label} : fin coupée à la dernière phrase complète, "
                f"{len(removed)} caractères retirés — « {removed[:80]} »"
            )
            text = cut
        else:
            warns.append(f"{label} : texte encore amputé, aucune coupe propre "
                         "possible (à reprendre à la main)")
    return text, metrics, warns


def _parse_beats(text: str) -> list[str]:
    """Extract the numbered lines « 1. … » from a plan answer."""
    beats = [
        re.sub(r"^\s*\d+[.)]\s*", "", line).strip()
        for line in text.splitlines()
        if re.match(r"^\s*\d+[.)]\s", line)
    ]
    return [b for b in beats if b]


def _plan_user(brief: str, facts: list[str], feedback: str) -> str:
    """Planning prompt, with the bible invariants as constraints."""
    constraints = ""
    if facts:
        listing = "\n".join(f"  - {f}" for f in facts)
        constraints = (
            "\nCONTRAINTES INVIOLABLES tirées de la bible du récit. Le plan ne "
            "doit RIEN prévoir qui les contredise — ni une révélation, ni un "
            f"aveu, ni une découverte qu'elles excluent :\n{listing}\n"
        )
    # The format instruction opens AND closes the prompt. At the first try it
    # sat only at the end, behind a long, detailed brief: nemo WROTE the
    # chapter instead of planning it — three entries of full prose, with
    # invented elements (a voice, an intruder). A brief that looks like a
    # writing instruction gets executed as one if nothing contradicts it from
    # both sides.
    return (
        "Tu es un PLANIFICATEUR, pas un rédacteur. Tu ne produis QUE des "
        "lignes numérotées. Tu n'écris AUCUNE prose, AUCUN dialogue, AUCUNE "
        "entrée de carnet.\n\n"
        f"Objectif du chapitre : {brief}\n"
        f"{constraints}\n"
        "Le chapitre est un carnet. Découpe-le en ENTRÉES DATÉES, une par "
        "soir. **Respecte le nombre d'entrées que l'objectif impose** : s'il "
        "dit « entrée unique », ton plan fait UNE ligne ; s'il dit trois "
        "entrées, il en fait trois. Jamais plus de trois.\n\n"
        "Format EXACT, une ligne par entrée, rien d'autre. Entre crochets, la "
        "météo du jour en deux mots ; puis le contenu :\n"
        "1. [Ciel couvert] ce qu'elle relit, ce qu'elle constate — l'état "
        "NOUVEAU à la fin.\n"
        "2. [Pluie fine] …\n\n"
        "N'écris AUCUN en-tête daté : les dates sont posées ailleurs.\n"
        "RÈGLE ABSOLUE : chaque entrée fait AVANCER d'un cran. Aucune entrée "
        "ne rejoue ni ne re-décrit ce qu'une autre a déjà noté. N'invente "
        "aucun élément que l'objectif ne fournit pas.\n\n"
        "Rends uniquement les lignes numérotées."
        f"{feedback}"
    )


def _plan_feedback(violations: list[tuple[int, str, str]]) -> str:
    """Reproach addressed to the planner: the violated constraint, and where."""
    lines = "\n".join(
        f"  - tu avais prévu « {quotation} », ce qui contredit : {fact}"
        for _, fact, quotation in violations
    )
    return (
        "\n\nTON PLAN PRÉCÉDENT ÉTAIT REFUSÉ. Il programmait des événements "
        f"interdits par la bible :\n{lines}\n"
        "Refais le plan en atteignant l'objectif du chapitre AUTREMENT : garde "
        "la tension, mais n'organise pas ces événements-là."
    )


def plan_node(state: ChapterState) -> dict:
    """Derive the bible invariants, then plan UNDER that constraint.

    The model order is dictated by memory, not elegance: the facts are derived
    by Qwen (4.8 GB) BEFORE nemo (13 GB) warms up, and each swap unloads the
    previous one. Both together make 17.8 GB of 19.3 GB — the exact pressure
    that panicked the machine (ADR-0008).

    Why check the plan here rather than trust the final coherence report: that
    report comes after fourteen minutes of writing. It observes, it does not
    prevent, and onstage nothing is rewritten. A plan is four lines: checking
    it costs seconds, fixing it costs a reload of nemo — no comparison with a
    chapter to throw away (ADR-0010).
    """
    metrics: list[dict] = []
    warnings: list[str] = []
    rag = state.get("rag", True)

    # SINGLE-ENTRY SHORT-CIRCUIT (item 10). Planning a single entry is
    # degenerate: the model writes instead of cutting, and the fallback is the
    # brief. In stage B this detour cost 139 to 222 seconds — for nothing.
    # SHORT-CIRCUIT WHEN THE PLAN IS GIVEN. When the brief already carries one
    # beat per entry (`imposed_plan`), planning adds nothing and can undo
    # everything: at the first draw of chapter 7 the node produced no numbered
    # line from a brief in formatted prose, and the fallback gave the WHOLE
    # brief to each entry — both received the instruction describing both.
    # Planning what is already written is an invitation to undo it.
    if state.get("imposed_plan"):
        progress.phase("Plan", f"fourni par le brief "
                               f"({len(state['imposed_plan'])} entrées)")
        return {
            "plan": list(state["imposed_plan"]), "facts": [],
            "plan_report": "plan FOURNI par le brief — nœud court-circuité "
                           "(structure imposée, un beat par entrée)",
            "idx": 0, "scenes": [], "metrics": [], "warnings": [],
        }

    if state.get("expected_entries", 0) == 1:
        progress.phase("Plan", "court-circuité (brief mono-entrée)")
        return {
            "plan": [state["brief"]], "facts": [],
            "plan_report": "plan court-circuité — brief mono-entrée (item 10)",
            "idx": 0, "scenes": [], "metrics": [], "warnings": [],
        }

    # Without RAG the facts have no source: `derive_facts` reads the sheets
    # through Chroma. The whole constraint chain (plan check, coherence report)
    # is therefore inert in stage A — by construction, not by accident. The
    # A → B gap carries this variable AS WELL AS the matter served to the
    # writing: keep it in mind when reading the grids.
    if not rag:
        facts: list[str] = []
        warnings.append(
            "étage A (rag=False) : aucun fait dérivé — plan non contraint et "
            "rapport de cohérence inerte, par construction"
        )
        progress.note("sans RAG : ni invariants, ni contrôle du plan")
    else:
        progress.phase("Invariants de la bible", "(Qwen)")
        facts, mf = derive_facts(state["characters"])
        metrics.extend(_tag([mf], "plan/faits"))
        progress.note(f"{len(facts)} faits dérivés, ils contraignent le plan")
        unload(settings.qa_model)  # clear the deck before loading nemo

    beats: list[str] = []
    report = "Plan non vérifié (aucun fait dérivé de la bible)."
    feedback = ""
    for attempt in range(1, MAX_PLAN_ATTEMPTS + 1):
        progress.phase("Plan d'entrées",
                       f"(nemo, tentative {attempt}/{MAX_PLAN_ATTEMPTS})")
        # The plan is structure, not prose: it gets the preamble and the rule
        # of the narrative, not the style contract — serving *Narration* and
        # *Interdits* to a planner inflates the prompt and frames nothing.
        system = assemble_system_prompt(
            characters=state["characters"], scene_brief=state["brief"],
            rag=rag, style=(), include_scenes=False,
            chapter=state.get("chapter"),
        )
        text, m = chat(system, _plan_user(state["brief"], facts, feedback),
                       num_predict=500, temperature=0.5,
                       on_token=progress.token_sink())
        metrics.extend(_tag([m], "plan"))
        # The plan goes through the lint like prose: a glued token in a beat
        # (« maisonly », 2026-08-06 run) then contaminates the scene brief, so
        # the writing prompt. Qwen's repair only comes at the end of the
        # pipeline, far too late for a brief.
        text, w = delint(text)
        warnings.extend(f"plan (tentative {attempt}): {x}" for x in w)
        candidate = _parse_beats(text)
        # An unreadable plan is not a violation: keep the previous one if there
        # was one, otherwise let the rest of the graph notice.
        if candidate:
            beats = candidate
        if not facts or not beats:
            break

        unload()  # nemo → Qwen for the check
        progress.phase("Contrôle du plan contre la bible", "(Qwen)")
        violations, report, mv = check_plan(facts, beats)
        metrics.extend(_tag(mv, "plan/controle"))
        # Trace the attempt: a plan refused THEN corrected is the most telling
        # moment of the device, and without this line the final report is
        # indistinguishable from a plan right the first time.
        report = f"tentative {attempt}/{MAX_PLAN_ATTEMPTS} — {report}"
        if not violations or attempt == MAX_PLAN_ATTEMPTS:
            if violations:
                report += (
                    "\n  [replanification épuisée — le chapitre est écrit "
                    "malgré la contradiction, à arbitrer à la main]"
                )
            break
        refusal = "; ".join(f"contredit « {fact} »" for _, fact, _ in violations)
        warnings.append(f"plan (tentative {attempt}) refusé : {refusal}")
        progress.note(f"PLAN REFUSÉ — {refusal}. Replanification.")
        feedback = _plan_feedback(violations)
        unload(settings.qa_model)  # Qwen → nemo for the retry

    # Net: an unreadable plan must not bring the graph down. `write_node`
    # indexes `plan[idx]` and would raise IndexError — a chapter generation
    # lost because the planner misformatted its answer. The brief itself then
    # serves as the single entry: the right behaviour for a single-entry
    # brief, the least bad for the others.
    if not beats:
        beats = [state["brief"]]
        warnings.append(
            "plan sans ligne numérotée — repli sur une entrée unique tirée du "
            "brief. Attendu sur un brief mono-entrée, où planifier est "
            "dégénéré : le modèle rédige au lieu de découper, et le brief fait "
            "lui-même office de beat"
        )
        progress.note("plan non découpé : le brief fait office d'entrée unique")

    # THE ENTRY PLAN RULES THE COUNT (micro-batch, chapter 7 fix).
    #
    # `entry_specs` describes a structure imposed by the brief — two entries
    # the same day for chapter 7. The plan node knew nothing of it: it returned
    # FOUR beats, and entries 3 and 4, outside the spec, fell back to derived
    # dates (« Lundi 16 », « Mardi 17 »). A chapter of 2281 words where the
    # brief asks for two entries, and a destroyed scene structure — the switch
    # sits at the second header; it would have opened the audio at an entry
    # the brief does not have.
    #
    # A given structure is not negotiable: cut. And SAY so — a plan truncated
    # in silence reads as a plan obeyed.
    spec = state.get("entry_specs") or []
    if spec and len(beats) != len(spec):
        warnings.append(
            f"plan à {len(beats)} entrée(s) contre {len(spec)} imposée(s) par "
            f"le brief — tronqué. Beats écartés : "
            f"{[b[:60] for b in beats[len(spec):]] or 'aucun'}")
        progress.note(f"plan ramené de {len(beats)} à {len(spec)} entrées")
        beats = beats[:len(spec)]
        while len(beats) < len(spec):
            beats.append(state["brief"])

    # Writing wants nemo alone: Qwen may have stayed warm after the check.
    # Without RAG Qwen was never loaded — nothing to unload.
    if rag:
        unload(settings.qa_model)
    return {
        "plan": beats, "facts": facts, "plan_report": report,
        "idx": 0, "scenes": [], "metrics": metrics, "warnings": warnings,
    }


def write_node(state: ChapterState) -> dict:
    """Write the current scene (state['idx']) with a re-assembled context.

    Anti-repetition (defect of the previous milestone: scenes replayed each
    other): the model gets the FULL PLAN with its position marked (it knows
    what is covered and what comes next) and an explicit instruction to
    CONTINUE without replaying. Previous entries are no longer served (see
    the anchor continuity below).
    """
    idx = state["idx"]
    beat = state["plan"][idx]
    # THIS entry's sheet, read at the top of the node: it commands the header,
    # the quotation, the word target and the cut. Empty outside chapter 7 —
    # the rest of the pipeline is then unchanged.
    spec = state.get("entry_specs") or []
    sheet: EntrySpec = spec[idx] if idx < len(spec) else EMPTY_ENTRY
    progress.phase("Écriture", f"entrée {idx + 1}/{len(state['plan'])} (nemo)",
                   i=idx + 1, n=len(state["plan"]))
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=beat,
        include_scenes=False,  # continuity handled by the explicit threading below
        chapter=state.get("chapter"),
        rag=state.get("rag", True),
    )

    # Annotated plan: [fait] / >> to write / [à venir].
    plan_lines = []
    for j, b in enumerate(state["plan"]):
        mark = ">>" if j == idx else ("[fait]" if j < idx else "[à venir]")
        plan_lines.append(f"  {j + 1}. {mark} {b}")
    plan_txt = "\n".join(plan_lines)

    # CONTINUITY BY ANCHOR (item 4). The last two full entries are no longer
    # injected: showing whole entries made the model copy paragraphs from one
    # entry to the next — AC produced eight headers, one repeated five times.
    # Continuity now goes through the NARRATIVE STATE, already served in the
    # system prompt, and the annotated plan above that says what is done. An
    # anchor says where we are; a full text invites word-for-word continuation.
    prior_block = ""

    lo, hi = sheet.words or WORDS_PER_ENTRY  # the entry's own target
    # PREFIXING BY THE CODE (item 5): the header and the anchor quotation are
    # not ASKED of the model, they are GIVEN already written — it continues.
    # A3 had altered the anchor and corrupted beats 2-3 that depended upon it;
    # an instruction does not prevent an alteration, a text already posed does.
    # By REAL CONCATENATION, not by instruction. The previous version said
    # « recopie-le à l'identique »: an INSTRUCTION, so B′1 could alter it — and
    # did, to the plural (« Je les ai laissées » for « Je l'ai laissée »). The
    # code writes this start and the model only continues: the anchor is
    # unalterable by construction (ADR-0018).
    # The header is COMPOSED here, never asked, and concatenated with the
    # anchor quotation when the brief gives one. Weather comes from the plan;
    # the date derives from the sequence anchor, so the entries of a chapter
    # are consecutive without a check.
    weather, beat = split_weather(beat)
    # EXPLICIT ENTRY PLAN (session 7) — the brief supplies it instead of the
    # code deriving it. Without it nothing changes: dates derive as since
    # session 5, chapters 1-6 and 8-11 are untouched.
    #
    # It exists for CHAPTER 7, which asks for TWO ENTRIES THE SAME DAY
    # (« Samedi 14. » twice: the afternoon and the night of the anniversary).
    # Three devices stood against it, all built deliberately:
    #   · `header()` derives `start_number + idx` — entry 2 came out
    #     « Dimanche 15 », and the chapter structure was impossible;
    #   · `consistent_headers` refuses two identical headers;
    #   · 450-600 words in three segments against « entrée 1 : DEUX PHRASES ».
    # The stake is not cosmetic: the audio switch sits at the SECOND normalised
    # header. No conforming header, no stage coincidence (ADR-0013).
    start_day = state.get("start_day") or "Mardi"
    start_number = state.get("start_number") or 12
    if sheet.weekday:
        head = header(sheet.weekday, sheet.number, 0,
                      sheet.weather or weather or "")
    else:
        head = header(start_day, start_number, idx,
                      weather or (state.get("start_weather") if idx == 0 else ""))
    # The anchor quotation becomes an entry field: in chapter 7, entry 1 does
    # NOT quote (« première entorse au rituel, premier signal ») and entry 2
    # opens with [CIT-2]. Serving the same anchor to both would kill the signal.
    anchor = (sheet.citation if sheet.citation is not None
             else state.get("prefix") or "")
    prefix = f"{head}\n\n{anchor}" if anchor else head
    prefix_block = (
        "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris PAS :\n"
        f"---\n{prefix}\n---\n"
        "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne répète "
        "ni l'en-tête ni la citation.\n"
        if prefix else
        "Elle s'ouvre par son en-tête : jour de la semaine, numéro, point, "
        "météo en deux mots, point. Jamais le mois, jamais l'année.\n"
    )
    user = (
        f"Plan du chapitre (>> = l'entrée à écrire maintenant) :\n{plan_txt}\n"
        f"{prior_block}\n"
        f"Écris UNIQUEMENT l'entrée {idx + 1} ({lo}-{hi} mots) : {beat}\n"
        f"{prefix_block}"
        "NE réécris AUCUN événement déjà noté ci-dessus — tu enchaînes dans la "
        "continuité stricte. Montre la tension sans la nommer. Prose seule, "
        "sans titre ni méta-commentaire.\n"
        # MASS INSTRUCTION (block B). Runs plateau at 185-366 words: the
        # skeleton gets ticked, not filled — and the oral verdict of 2026-08-19
        # traces the absence of voice to this lack. Not « plus long »: say
        # WHERE the length comes from.
        "La reconstruction occupe au moins la moitié de l'entrée — la soirée "
        "entière, du retour à la cuisine au coucher, avant le verdict."
        # « fais entendre les voix distinctes » is gone: one voice, no dialogue.
        # The instruction pushed towards what the sheet forbids.
    )
    # --- THE MEASURED VARIABLE OF SESSION 6 -------------------------------
    # One call handled five beats: the model wrote one paragraph per beat and
    # stopped. The mass lives in ONE beat — the reconstruction — and it never
    # had a call of its own. Decompose: the principle that just won the
    # accumulation, applied one level up.
    #
    # Outside stage S6 the original branch stays intact TO THE BYTE: the whole
    # pipeline was timed through it, and dressing one stage must never replay
    # the validation of another.
    reconstruction = ""
    # The SERVED PROMPT is kept: a deliverable of the movement method
    # (« dump du prompt servi »), and what measures copying — the check draw 6
    # lacked.
    served_prompts: list[tuple[str, str]] = []
    if sheet.strategy == "beats" and sheet.beats:
        # STRUCTURAL CODE CAP (entry 2, v5). Each beat is a short call, served
        # ALONE (not the whole movement — see `_prompt_beat`), bounded in
        # sentences AND tokens by the code. The text already written becomes
        # the prefix of the next beat (prefixing doctrine), and `_reattach`
        # absorbs a restart. Drift and fall stay posed downstream by
        # `place_gestures_node`: nothing new in the gesture pipeline (ADR-0020).
        text, ms, wg = "", [], []
        # ROOT FIX: voice served WITHOUT the verdict/cleaver steps (see
        # `_VERDICT_VOICE`). Local reassignment — the other branches are
        # `elif`, and the common tail does not use `system` to generate.
        system = _VERDICT_VOICE.sub("", system)
        beats = sheet.beats
        first_name = beats[0].name
        for b in beats:
            name, num_predict, max_sentences, instruction = (
                b.name, b.num_predict, b.sentences_max, b.instruction)
            is_first = (name == first_name)
            already = f"{prefix}\n\n{text}".strip() if prefix else text.strip()
            # AUTHOR ATTACK (quality campaign, lever 1). The owner's first
            # sentence(s) of the beat are POSED, not asked: they close the
            # "already written" block, so the model continues in their
            # register. The attack counts against the beat's sentence cap;
            # what the model adds is bounded to the remainder.
            attack = b.attack.strip()
            model_cap = max_sentences
            if attack:
                already = f"{already}\n\n{attack}".strip() if already else attack
                model_cap = max(1, max_sentences - len(sentence_ends(attack)))
            block = (
                "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris "
                f"PAS :\n---\n{already}\n---\n"
                "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne "
                "répète rien de ce qui précède.\n" if already else "")
            beat_user = _prompt_beat(instruction, block)
            served_prompts.append((name, beat_user))
            # BEST-OF-N per beat. nemo's failures are CORRELATED (it resolves /
            # restarts in every draw, differently): N variants are drawn and
            # the code keeps the one with the FEWEST named defects
            # (`_score_beat`). Selection is a deterministic reading, not a
            # judge of taste — falsifiable, so trustworthy.
            variants = []
            beats_n = settings.beats_n
            for k in range(beats_n):
                progress.phase("Écriture",
                               f"entrée {idx + 1} — {name} ({k + 1}/{beats_n})",
                               i=idx + 1, n=len(state["plan"]))
                seg, m, w = _generate_whole(
                    system, beat_user, num_predict=num_predict,
                    temperature=settings.write_temperature,
                    label=f"entrée {idx + 1}/{name}#{k + 1}", keep_going=False)
                seg, wn = _clean_segment(seg, f"entrée {idx + 1}/{name}#{k + 1}")
                if attack:
                    seg = _strip_attack_echo(attack, seg)
                seg, wb = _bound_sentences(seg, model_cap, idx, "")
                # The attack is the author's: scored is what the model added.
                sc, defects = _score_beat(seg, is_first,
                                           state.get("chapter") or 0)
                variants.append({"score": sc, "k": k, "seg": seg,
                                  "defauts": defects, "m": m, "w": w + wn + wb,
                                  "style": style.score(seg)})
            # Best defect score; among equals the countable style marks
            # (quality campaign, lever 4); then the first drawn (stable).
            variants.sort(key=lambda v: (-v["score"], -v["style"], v["k"]))
            winner = variants[0]
            wg += _style_tiebreak_note(f"entrée {idx + 1}/{name}", variants)
            seg = winner["seg"]
            if attack:
                seg = f"{attack} {seg}".strip()
                wg.append(f"entrée {idx + 1}/{name} : attaque d'auteur posée "
                          f"({len(sentence_ends(attack))} phrase(s)), le modèle borné à "
                          f"{model_cap}")
            wg += winner["w"]
            wg.append(
                f"entrée {idx + 1}/{name} : best-of-{beats_n} — variant "
                f"{winner['k'] + 1} retenu (score {winner['score']}, "
                + (", ".join(winner["defauts"]) if winner["defauts"]
                   else "propre")
                + ") ; rejetés : "
                + " ; ".join(f"#{v['k'] + 1} score {v['score']}"
                             for v in variants[1:]))
            text = _reattach(text, seg) if text else seg
            # Metrics of ALL variants — rejected tokens were spent (doctrine 5:
            # no figure without its clock).
            ms += [dict(m2, beat=name, variant=v["k"])
                   for v in variants for m2 in v["m"]]
        # The accumulation takes the whole entry as context: it is short.
        reconstruction = text
    elif sheet.uses_segments(state.get("segments")):
        text, ms, wg = "", [], []
        for name, num_predict, target_words, instruction in SEGMENTS:
            progress.phase("Écriture", f"entrée {idx + 1}/"
                           f"{len(state['plan'])} — {name}",
                           i=idx + 1, n=len(state["plan"]))
            # The text already written becomes the PREFIX of the next segment:
            # the prefixing doctrine extended, no new mechanism. Continuity is
            # guaranteed by construction, and `_reattach` absorbs the restart
            # if the model repeats the end despite the instruction.
            already = f"{prefix}\n\n{text}".strip() if prefix else text.strip()
            block = (
                "L'entrée est DÉJÀ COMMENCÉE par ce texte, que tu ne réécris "
                f"PAS :\n---\n{already}\n---\n"
                "Écris uniquement CE QUI SUIT, en enchaînant directement. Ne "
                "répète rien de ce qui précède.\n" if already else "")
            material = (_reconstruction_material(state)
                       if name == "reconstruction" else "")
            stations = "\n".join(
                f"  {k}. {place_name}" for k, place_name in
                enumerate(state.get("stations") or (), 1))
            if sheet.movement:
                # Movement method: the brief carries everything, the segment
                # instructions only carry the POSITION in the trajectory.
                seg_user = _movement_prompt(
                    sheet, target_words, TRAJECTORY_POSITION[name], block)
            else:
                seg_user = (
                    f"Plan du chapitre (>> = l'entrée à écrire maintenant) :\n"
                    f"{plan_txt}\n\n"
                    f"Ce que l'entrée {idx + 1} raconte : {beat}\n\n"
                    f"{block}\n"
                    + instruction.format(words=target_words, material=material,
                                    stations=stations) + "\n"
                    "Prose seule, sans titre, sans en-tête, sans "
                    "méta-commentaire. Montre la tension sans la nommer."
                )
            served_prompts.append((name, seg_user))
            seg, m, w = _generate_whole(
                system, seg_user, num_predict=num_predict,
                temperature=settings.write_temperature,
                label=f"entrée {idx + 1}/{name}")
            # The code's proprietary filters apply TO THE SEGMENT, before it
            # becomes the next prefix: a header re-emitted at the top of the
            # reconstruction would be copied by the closing, which reads it as
            # legitimate text already written.
            seg, wn = _clean_segment(seg, f"entrée {idx + 1}/{name}")
            wg += w + wn
            if name == "reconstruction":
                reconstruction = seg.strip()
            text = _reattach(text, seg) if text else seg
            ms += [dict(m2, segment=name) for m2 in m]
    else:
        # `num_predict` DERIVED FROM THE TARGET when the brief gives one.
        #
        # The model occupies the space offered — measured three times (the
        # accumulation at 214 words without a cap, the scene at 1400/1400, and
        # here entry 1 of chapter 7 at 471 words where the brief asks for TWO
        # SENTENCES). Offering 1400 tokens for sixty words asks for sixty and
        # allows six hundred: the instruction says one thing, the budget
        # another, and the budget wins.
        # THE MOVEMENT METHOD ALSO HOLDS WITHOUT SEGMENTATION. When the sheet
        # carries a movement, the single call gets the same order of service —
        # otherwise we would fall back to the box prompt the method replaces,
        # and the comparison would no longer bear upon the number of calls
        # alone.
        if sheet.movement:
            user = _movement_prompt(
                sheet, f"{lo} à {hi} mots",
                "Tu écris cette trajectoire ENTIÈRE, d'un seul tenant.",
                prefix_block)
            served_prompts.append(("entrée entière", user))
        budget = (int(hi * 1.6) + 40 if sheet.words else 1400)
        # NO CONTINUATION when brevity is WANTED. Continuation exists against
        # accidental amputation — a text cut mid-word at 1400 tokens. For an
        # entry bounded at sixty words, `done_reason: length` is the REQUESTED
        # result, and relaunching undoes the bound: the previous draw went
        # back for 300 tokens and returned 314 words. Cut at the last complete
        # sentence, which `_generate_whole` already does as a net.
        best_of = sheet.best_of.n if sheet.best_of else 0
        if best_of:
            # BEST-OF-N over the WHOLE entry (entry 1). The version bounded to
            # `sentences_max` — what is really served — is SCORED through the
            # scorer named by the spec criterion. Same principle as the beats:
            # selection is a deterministic reading, not a judge of taste.
            phr = sheet.sentences_max
            cont = not sheet.words
            cands = []
            for k in range(best_of):
                progress.phase("Écriture",
                               f"entrée {idx + 1} ({k + 1}/{best_of})",
                               i=idx + 1, n=len(state["plan"]))
                t, m, w = _generate_whole(
                    system, user, num_predict=budget,
                    temperature=settings.write_temperature,
                    label=f"entrée {idx + 1}#{k + 1}", keep_going=cont)
                # Strip the stray header BEFORE scoring: otherwise the
                # two-sentence bound captures « Samedi 14. Beau temps. » (two
                # sentence ends) instead of the body, and all three variants
                # score alike — the selection stops discriminating (measured
                # in the previous run).
                t_clean = STRAY_HEADER.sub("", t).strip()
                to_score = (_bound_sentences(t_clean, phr, idx, "")[0]
                            if phr else t_clean)
                sc, defects = scorers.score(to_score, sheet.best_of)
                cands.append({"score": sc, "k": k, "t": t, "m": m, "w": w,
                              "def": defects, "style": style.score(to_score)})
            cands.sort(key=lambda c: (-c["score"], -c["style"], c["k"]))
            g = cands[0]
            text, wg = g["t"], list(g["w"])
            wg += _style_tiebreak_note(f"entrée {idx + 1}", cands)
            wg.append(
                f"entrée {idx + 1} : best-of-{best_of} — variant {g['k'] + 1} "
                f"retenu (score {g['score']}, "
                + (", ".join(g["def"]) if g["def"] else "propre")
                + ") ; rejetés : "
                + " ; ".join(f"#{c['k'] + 1} score {c['score']}"
                             for c in cands[1:]))
            ms = [dict(m2, variant=c["k"]) for c in cands for m2 in c["m"]]
        else:
            text, ms, wg = _generate_whole(
                system, user, num_predict=budget,
                temperature=settings.write_temperature,
                label=f"entrée {idx + 1}", keep_going=not sheet.words)
    # The concatenation itself. `_reattach` removes the overlap character by
    # character if the model repeated the header or the anchor despite the
    # instruction — neither a doublet nor a recomposed anchor is wanted.
    # The code OWNS the header format and composes one per entry. Any dated
    # header the model produces is parasitic by definition — C1 invented a
    # second one (« Vendredi 15. Pluie fine. ») in an entry meant to be unique,
    # and the lint split two entries where there was one. They are removed
    # without asking the model again: one more instruction would join the one
    # it just ignored.
    text, repeated = REPEATED_SUSPENSION.subn(r"\1", text)
    text, isolated = STRAY_SUSPENSION.subn(", ", text)
    suspensions = repeated + isolated
    if suspensions:
        wg.append(f"entrée {idx + 1} : {suspensions} point(s) de suspension "
                  "produit(s) par le modèle, retiré(s) — le marqueur est "
                  "réservé au glissement, que le code compose")
    text, removed_count = STRAY_HEADER.subn("", text)
    if removed_count:
        wg.append(f"entrée {idx + 1} : {removed_count} en-tête(s) daté(s) produit(s) "
                  "par le modèle, retiré(s) — le code compose les en-têtes")
    if prefix:
        text = _reattach(prefix, _strip_approximate_restart(prefix, text))

    # THE VETOS OVER THE SCENE TEXT (orthogonal batch of chapter 7).
    #
    # Until here the material interdicts and the brands were blocking only IN
    # `accumulate`: they lived in the writing text, where nothing relaunched
    # them. In a chapter that goes onstage, generic decor is not a style
    # defect, it is an object that does not exist — and a brand dates the text
    # and takes it out of the closed world of the house.
    #
    # One relaunch, as everywhere else: beyond that, keep and shout.
    text, wv = _scene_vetos(text, idx, state, attempt_no=1)
    wg += wv

    # SENTENCE BOUND when the brief sets one. The word bound divided entry 1 of
    # chapter 7 by five without ever counting sentences: eight produced where
    # the brief asks for two, and that is the entry the speaker reads with the
    # bare voice. A stage constraint is counted in the stage's unit.
    if sheet.sentences_max:
        text, wp = _bound_sentences(text, sheet.sentences_max, idx, prefix)
        wg += wp

    text, w = delint(text)
    return {
        "scenes": state["scenes"] + [text],
        "idx": idx + 1,
        # The reconstruction segment is set aside for `accumulate`: IT becomes
        # its context, not the whole entry. The cut makes this matter
        # identifiable without guessing it inside the text.
        "reconstruction": reconstruction,
        # What the code COMPOSED for this entry, set aside for the stamp of
        # `place_gestures_node`: it alone can re-pose it identically after the
        # repair has rewritten it.
        "placed_header": head,
        "placed_anchor": anchor,
        "placed_fall": sheet.fall,
        "served_prompts": (state.get("served_prompts") or []) + served_prompts,
        "metrics": state["metrics"] + _tag(ms, f"write/{idx + 1}"),
        "warnings": state["warnings"] + wg
        + [f"entrée {idx + 1}: {x}" for x in w],
    }



# --- `write` in three segments (session 6, §1) --------------------------------
#
# Three sequential calls, each prefixed with the previous one. The cut adds no
# mechanism: it reuses prefixing by real concatenation, already proven for the
# header and the anchor. What it changes is the BALANCE OF POWER between the
# beats — the reconstruction stops being one beat among five and becomes a fed
# narrative task, with its own served matter.
#
# None of these instructions names a workshop term: our own served skeleton had
# made « Couperet : » come out as text in C2 and C3. An assertion checks it
# below — proofreading is not enough, it already let the case through.
# THE INSTRUCTIONS ARE IN FACTS, NO LONGER IN INTENTIONS (session 7).
#
# « Elle rétablit sa soirée » names what the character DECIDES to do, and the
# model renders the decision as text: « Je décide de rétablir ma soirée »,
# « Je décide de refaire le fil de ma soirée ». Measured ×3 for « je décide de »
# in session 6 (seven occurrences in S6-1, six in S6-3), SCATTERED through the
# entry — so not the segment seam but the form of the instruction. An
# instruction that describes an intention produces a character who describes
# her intentions (doctrine 8).
#
# So no intention is asked; FACTS and PLACES are given.
_SEG_OPENING = """Écris seulement le DÉBUT de l'entrée, {words}.

Le soir, le cahier ouvert : la phrase relue, l'écart entre ce qu'elle lit et \
ce dont elle se souvient, la chaise repoussée.

ARRÊTE-TOI AU SEUIL DE LA CUISINE. N'écris pas ce qu'elle y trouve."""

# THE STATIONS (session 7). The mass floor becomes mechanical: no more
# « raconte longuement » — a length instruction the model reads as a tone —
# but places to go through. A station gone through is a paragraph; six
# stations make a reconstruction.
#
# No station brings the narrator back from outside: she works at the
# living-room table. That door let « je suis revenue du travail » in (S6-3,
# C3), while she does not go out.
_SEG_RECONSTRUCTION = """Écris maintenant le MILIEU de l'entrée, {words} — \
c'est la partie la plus longue, et de loin.

Sa soirée, heure par heure, station par station. Chaque station tient en \
quelques lignes : l'heure, ce qu'elle a dans les mains, ce qu'elle voit.

{stations}

Un relevé, pas un résumé : aucune station n'est sautée, aucune n'est résumée \
en une proposition. Les heures sont écrites.

CHAQUE STATION SE FERME SUR UN FAIT — jamais sur un commentaire, jamais sur \
une question, jamais sur ce qu'elle en pense. Le relevé enchaîne sans \
récapituler : on passe à la station suivante, c'est tout.

{material}
Aucun verdict ici, aucune conclusion : ce segment ne fait que relever."""

_SEG_CLOSING = """Écris la FIN de l'entrée, {words}.

Le verdict, dans ses mots. Puis une ligne du corps, sans cause. Puis une \
phrase brève, qui referme.

LA DERNIÈRE LIGNE REFERME, ELLE NE CONSOLE PAS : aucune promesse au \
lendemain, aucune adresse à personne, aucun réconfort. Elle constate et \
s'arrête."""

# Stations of the reconstruction segment come from the chapter spec
# (`state["stations"]`), the pilot table's PERCEIVED side: the CONSTATED state
# of each object, never the intention — repeating it in intention language
# brings back « je décide de ».

# (name, num_predict, target words, instruction)
#
# `num_predict` is sized segment by segment rather than left at 1400 for all:
# offering the whole entry's space to the opening invites it to write the
# whole entry — the model occupies the space offered, measured twice (the
# accumulation at 214 words without a cap, the scene at 1400/1400).
SEGMENTS = (
    ("ouverture", 300, "80 à 120 mots", _SEG_OPENING),
    ("reconstruction", 800, "250 à 350 mots", _SEG_RECONSTRUCTION),
    ("fermeture", 260, "60 à 100 mots", _SEG_CLOSING),
)


# --- THE MOVEMENT METHOD (2026-08-27, ADR-0019) ------------------------------
#
# The prompt stops describing boxes to go through. It declares a MOVEMENT to
# accomplish, PROSE directives, an available MATERIAL — in this order, and the
# order is part of the method: intention before matter.
#
# What made the change necessary is measured. Draw 6 of chapter 7 opens with
# « Le soir, le cahier ouvert : la phrase relue, […] la chaise repoussée » — the
# opening instruction, COPIED, at 0.94 similarity. In the chapter 2 runs it
# stays under 0.37: there it describes the chapter's ritual and blends in. In
# chapter 7 it is foreign, so the model transcribed it.
#
# Session 3's lesson (« ce qui est montré se recopie ») turned against our own
# fix: session 6 had written the instructions « en faits, plus en intentions »
# to kill « je décide de ». Having become prose, they got copied. An
# instruction must be an INSTRUCTION, recognisable as such.
TRAJECTORY_POSITION = {
    "ouverture": "Tu écris le DÉBUT de cette trajectoire.",
    "reconstruction": "Tu écris la SUITE de cette trajectoire — c'est la partie "
                      "la plus longue, et de loin.",
    "fermeture": "Tu écris la FIN de cette trajectoire.",
}


def _without_machinery(directive: str) -> str:
    """Remove from a served directive the clause that speaks of our machinery.

    The brief is written for two readers at once: the implementer and the
    model. The directive
    « Rien ne se résout… : la dernière ligne est posée d'office par le code »
    is half a prose directive, half an implementation note. Serving the second
    half teaches the model that a code poses lines behind it, exactly what the
    meta-term firewall exists to prevent.
    """
    pieces = re.split(r"\s*(?:—|:)\s*", directive)
    guards = [m for m in pieces if not MACHINERY.search(m)]
    if len(guards) == len(pieces):
        return directive
    return (" : ".join(guards) if guards else "").rstrip(" :,;") + "."


# SELECTION CRITERIA for a beat variant (best-of-N). READING checks,
# deterministic and falsifiable — never a judge of taste (doctrine 3: counting
# is not reading). Prose is not graded; named defects that ten draws made
# recurrent are REJECTED. The retained variant carries the fewest.
_BEAT_RESOLVES = re.compile(
    r"je\s+me\s+(?:souviens|rappelle)\s+(?:soudain|maintenant|enfin|"
    r"à\s+nouveau|de\s+tout|de\s+chaque|bien|parfaitement)"
    r"|(?:cela|ça)\s+me\s+revient"
    r"|\bverdict\s*:\s*\w"
    r"|(?:m'a\s+jou\w+\s+un|me\s+joue\s+(?:des?|un))\s+tours?"
    r"|je\s+n'ai\s+pas\s+rêvé"
    r"|j'ai\s+bien\s+(?:mis|fait|noté)", re.IGNORECASE)
_BEAT_DISMISS = re.compile(
    r"je\s+(?:dois|ai\s+dû)\s+me\s+tromper|je\s+me\s+suis\s+trompée"
    r"|machinalement|sans\s+(?:y\s+penser|réfléchir)"
    r"|oubli[ée]\s+de\s+(?:le\s+)?noter|me\s+résous\s+à\s+croire"
    r"|j'avais\s+(?:simplement|juste)\s+oublié"
    r"|j'ai\s+dû\s+m'endormir|je\s+me\s+suis\s+endormie", re.IGNORECASE)
# METAFICTIONAL RECURSION: the beat re-reads the previous beat's line
# (« je relis la phrase que j'ai écrite hier soir : "…" ») or reuses the
# template « je relève un détail qui me trouble » — a new form of litany (v14).
# Distinct from the legitimate note (« la phrase que je viens de recopier »),
# which does not borrow from the past.
_BEAT_RECURSION = re.compile(
    r"je\s+relis\s+(?:la|cette|ma|une|l')\s*(?:phrase|entrée)\s+"
    r"(?:d'hier|que\s+j'ai\s+[ée]crite?)"
    r"|je\s+rel[èe]ve\s+un\s+d[ée]tail\s+qui\s+me\s+trouble", re.IGNORECASE)
_BEAT_WAKING = re.compile(
    r"je\s+me\s+suis\s+(?:réveillée|levée)|à\s+mon\s+réveil", re.IGNORECASE)
_BEAT_PRESENCE = re.compile(
    r"\b(?:un\s+bruit|une\s+sonnerie|des\s+pas|une\s+voix|quelqu'un"
    r"|un\s+mouvement\s+qui\s+n'|surprendre)\b", re.IGNORECASE)
_BEAT_DOUBT = re.compile(
    r"je\s+ne\s+me\s+(?:souviens|rappelle)\s+pas|aucun\s+souvenir"
    r"|sans\s+(?:m'en\s+souvenir|le\s+savoir)", re.IGNORECASE)


def _score_beat(variant: str, is_first: bool,
                 chapter: int = 2) -> tuple[int, list[str]]:
    """Score a beat variant by reading checks. Higher is better.

    Falsified both ways (doctrine 4): it MUST reject the resolution / presence
    / restart / recursion / forbidden-decor paragraphs of draws v8–v14 and
    ACCEPT the open doubt. The restart (waking) is a defect only OUTSIDE the
    first beat.
    """
    defects: list[str] = []
    score = 0
    if _BEAT_RESOLVES.search(variant):
        score -= 10
        defects.append("résout (souvenir retrouvé / verdict rendu)")
    if _BEAT_DISMISS.search(variant):
        score -= 4
        defects.append("congédie (je dois me tromper / je me suis endormie)")
    if not is_first and _BEAT_WAKING.search(variant):
        score -= 5
        defects.append("redémarre (réveil déjà servi)")
    if _BEAT_PRESENCE.search(variant):
        score -= 5
        defects.append("présence perçue")
    if _BEAT_RECURSION.search(variant):
        score -= 6
        defects.append("récursion (re-lit sa propre ligne / gabarit répété)")
    # FORBIDDEN DECOR: the detector already exists (`material_forbidden`); it
    # is WIRED into the selection. A beat that names the television, the
    # dishwasher, the handbag… must never win (v14: it won).
    forbidden = material_forbidden(variant, chapter)
    if forbidden:
        score -= 8
        defects.append(f"décor interdit ({len(forbidden)})")
    if _BEAT_DOUBT.search(variant):
        score += 3
    return score, defects


# The criterion of the best-of over a whole entry is named by the chapter spec
# (`best_of.criterion`) and resolved in `factory.pipeline.scorers`; its lexical
# lists travel with the spec.


# ROOT FIX (xp C5, 2026-08-31): the served voice skeleton ends with « 5. verdict
# de correction … 7. couperet ». The xp measured that THIS skeleton (not the
# model) forces the resolution of the doubt — 12/12 draws hold the doubt when
# it is not served. Steps 5 and 7 are amputated IN THE PROMPT SERVED TO THE
# BODY BEATS, never in the sheet (the skeleton stays the canonical voice
# elsewhere). The « Constat » fall stays posed last by the code; step 6
# (physiological notation) is kept — it is the body beat (ADR-0020).
_VERDICT_VOICE = re.compile(
    r"^\s*(?:5\. Le verdict de correction|7\. Le couperet)[^\n]*\n?",
    re.MULTILINE)


_BEAT_SUFFIX = (
    "Prose seule, en français uniquement, sans en-tête, sans titre, sans "
    "méta-commentaire. AUCUNE étiquette de section : jamais un mot seul suivi "
    "de deux-points en tête de phrase (pas de « Verdict : », pas de « Note : », "
    "pas de « Constat : »). Aucun nom propre. Tu ne rends AUCUN verdict et tu "
    "ne résous rien : le doute reste ouvert, la faute ne se stabilise pas — "
    "surtout, elle ne se retourne pas en certitude rassurante. Rien ne se "
    "produit sous tes yeux : aucune voix, aucun bruit, aucun pas, personne qui "
    "agit — tu constates seulement des états trouvés, des choses déplacées ou "
    "laissées, sans surprendre personne."
)


def _prompt_beat(instruction: str, block: str) -> str:
    """Assemble the prompt of ONE beat — structural code cap of entry 2 (v5).

    Serves ONLY this beat and the common veto, NEVER the whole movement.
    Segment mode re-served `_movement_prompt` at each segment (intention +
    four directives + matter + vetos) with a bare position line: each segment
    then attempted the whole arc — the measured cause of the « trois arcs ».
    Here each call receives only its own short task, and the code bounds the
    generation in sentences. The « je vais tout noter » spiral of v5 has no
    call left to be written in: the doubt beat stops at its question, and the
    fall is posed downstream.

    Same entry guard as `_movement_prompt`: the served assembly must carry no
    workshop or machinery term.
    """
    prompt = "\n\n".join(b for b in (instruction.strip(), block.strip(),
                                     _BEAT_SUFFIX) if b)
    leaks = sorted({m.group(0).lower() for m in META_TERMS.finditer(prompt)}
                    | {m.group(0).lower() for m in MACHINERY.finditer(prompt)}
                    | set(re.findall(r"\b[\w-]+\.md\b", prompt)))
    assert not leaks, (f"le prompt de beat porte des termes d'atelier ou de "
                        f"machinerie : {leaks}")
    return prompt


def _movement_prompt(sheet: EntrySpec, target_words: str, position: str,
                      prefix_block: str) -> str:
    """Assemble the prompt of an entry under the movement method.

    STRICT order: intention → trajectory → matter → vetos. Nothing before the
    intention; the matter comes only after the prose behaviour, because it is
    available, not to be ticked (ADR-0019).
    """
    blocks = [f"MOUVEMENT À ACCOMPLIR — {sheet.movement}"]
    if sheet.trajectory:
        blocks.append("COMPORTEMENT DE LA PROSE :\n"
                     + "\n".join(f"  - {_without_machinery(d)}"
                                   for d in sheet.trajectory))
    if sheet.material:
        blocks.append("MATIÈRE DISPONIBLE — à ta disposition pour accomplir ce "
                     "mouvement, jamais une liste à épuiser :\n"
                     + "\n".join(f"  - {_without_machinery(m)}"
                                   for m in sheet.material))
    form = sheet.form or {}
    vetos = [f"Longueur visée : {target_words}."]
    if form.get("verdict") == "absent":
        vetos.append("Aucun verdict ne se rend : la dernière ligne en tient "
                     "lieu, et elle est déjà écrite ailleurs.")
    if form.get("accumulation") == "absent":
        vetos.append("Pas de phrase-récapitulatif.")
    if sheet.vetos:
        vetos.append(sheet.vetos)
    # The label is served too: « VÉTOS » is a word of our workshop. What the
    # model must read is what the text does not do.
    blocks.append("CE QUE LE TEXTE NE FAIT PAS :\n"
                 + "\n".join(f"  - {v}" for v in vetos))
    blocks.append(prefix_block.strip() if prefix_block else "")
    blocks.append(position + "\nProse seule, sans titre, sans en-tête, sans "
                 "méta-commentaire.")
    prompt = "\n\n".join(b for b in blocks if b)

    # THE ENTRY GUARD, over the ASSEMBLED prompt and not its pieces: the
    # assembly is what is served. It already caught « matériau » (session 6)
    # and `fiche-romane.md` (session 7); widened to machinery, it catches the
    # nine terms §5 of the brief served as is.
    leaks = sorted({m.group(0).lower() for m in META_TERMS.finditer(prompt)}
                    | {m.group(0).lower() for m in MACHINERY.finditer(prompt)}
                    | set(re.findall(r"\b[\w-]+\.md\b", prompt)))
    assert not leaks, (f"le prompt servi porte des termes d'atelier ou de "
                        f"machinerie : {leaks}")
    return prompt


def _reconstruction_material(state: ChapterState) -> str:
    """The reconstruction call's own matter.

    ⚠ The protocol says
    « la micro-scène du chapitre (grade, objet, événement) — depuis la table de pilotage ».
    Taken literally this reads `bible/profond/chronologie-partie-double.md`,
    whose « Événement réel payeur » column is THE REAL COLUMN of the double
    entry: the truth the whole firewall exists to hide from the author model.
    Harmless by coincidence in chapter 2, it says « *ce genre de veuve* écrit »
    in chapter 3.

    That is the exact error of session 5, where the diegetic translation read
    this column and produced « le journal prescrit ». So we go through the two
    functions that already know where to look: `read_table` (which SKIPS that
    column, comment to match) and `read_anchors`, which reads the Ancre of the
    [VALEURS] block — the event as the narrator PERCEIVES it (ADR-0017).

    Material interdicts are served as CATEGORIES, never as instances. Naming
    « télévision » and « sac à main » to forbid them shows them, and the
    project measured three times that what is shown gets copied. What holds
    the interdict is the blocking validator of `accumulate`; the prompt only
    prepares the ground — by giving REAL furniture, because the node invented
    for lack of it.
    """
    ch = state.get("chapter") or 0
    objects = state.get("active_objects") or ""
    lines = []
    try:
        from factory.chapter_spec.narrative_state import read_anchors, read_table
        table, anchors = read_table().get(ch) or {}, read_anchors()
        objects = objects or table.get("objets", "")
        if anchors.get(ch):
            lines.append(f"Où elle en est ce soir : {anchors[ch]}.")
        if table.get("marche"):
            lines.append(f"Ce par quoi elle explique l'écart : "
                          f"{table['marche']}.")
    except Exception as exc:                       # pragma: no cover
        # A read failure must not cost the entry: write without this matter,
        # and SAY so. A silently amputated context is what produced B′C's
        # inner manuscript.
        progress.note(f"matière de reconstruction indisponible ({exc}) — "
                      "l'appel se fait sans elle")
    if objects:
        lines.append(f"Dans cette maison, ce soir : {objects}.")
    lines.append(
        "Elle travaille chez elle et ne sort pas ce soir-là ; personne d'autre "
        "n'entre ; il n'y a aucun écran dans cette maison, et rien qui vienne "
        "d'un magasin. Tout ce qu'elle touche est déjà là.")
    return "\n".join(lines) + "\n"


def _scene_vetos(text: str, idx: int, state: ChapterState,
                    attempt_no: int) -> tuple[str, list[str]]:
    """Flag generic decor and brands in the writing text.

    FLAG without rewriting: unlike the header or the anchor, the code does not
    own these sentences — removing « l'enceinte Bluetooth » would leave a hole
    in a sentence that would need re-sewing, and re-sewing prose is exactly
    what six sessions have refused to do. The warning names the object and
    quotes the excerpt; the veto lives in the grid.
    """
    warns: list[str] = []
    ch = state.get("chapter") or 0
    for excerpt in material_forbidden(text, ch):
        warns.append(f"entrée {idx + 1} : VÉTO décor — {excerpt[:110]}")
    for m in MARKS.finditer(text):
        a = max(0, m.start() - 40)
        warns.append(f"entrée {idx + 1} : VÉTO marque déposée — "
                     f"« {' '.join(text[a:m.end() + 30].split())} »")
    return text, warns


def _bound_sentences(text: str, maximum: int, idx: int,
                       prefix: str) -> tuple[str, list[str]]:
    """Cut the entry to `maximum` sentences AFTER the prefix, at a sentence end.

    The prefix (header, anchor) is not counted: the code posed it, it does not
    belong to the text the brief bounds.
    """
    body = text[len(prefix):] if prefix and text.startswith(prefix) else text
    ends = sentence_ends(body)
    if len(ends) <= maximum:
        return text, []
    cut = ends[maximum - 1]
    removed = body[cut:].strip()
    return (text[:len(text) - len(body)] + body[:cut].rstrip(),
            [f"entrée {idx + 1} : bornée à {maximum} phrase(s) — "
             f"{len(ends) - maximum} retirée(s), à partir de "
             f"« {' '.join(removed.split())[:80]}… »"])


def _clean_segment(seg: str, label: str) -> tuple[str, list[str]]:
    """Remove from the segment the markers the CODE owns.

    Applied segment by segment, not only to the assembled entry: a header
    re-emitted at the top of the reconstruction would become the closing's
    prefix, which would read it as legitimate text already written and
    continue from it. The code that owns a marker must clean it everywhere —
    and « partout » includes the intermediate states.
    """
    warns: list[str] = []
    seg, repeated = REPEATED_SUSPENSION.subn(r"\1", seg)
    seg, isolated = STRAY_SUSPENSION.subn(", ", seg)
    if repeated + isolated:
        warns.append(f"{label} : {repeated + isolated} point(s) de suspension "
                     "produit(s) par le modèle, retiré(s) — le marqueur est "
                     "réservé au glissement, que le code compose")
    seg, removed_count = STRAY_HEADER.subn("", seg)
    if removed_count:
        warns.append(f"{label} : {removed_count} en-tête(s) daté(s) produit(s) par le "
                     "modèle, retiré(s) — le code compose les en-têtes")
    return seg.strip(), warns


# THE ENTRY GUARD IS THE OUTPUT LINT. The detector that catches « Couperet » in
# the text is the one that should have forbidden serving it.
for _name, _, _, _instruction in SEGMENTS:
    _leaks = sorted({m.group(0).lower() for m in META_TERMS.finditer(_instruction)})
    assert not _leaks, (f"consigne du segment « {_name} » : termes d'atelier "
                         f"servis au modèle — {_leaks}")


# --- Assembly micro-nodes (stage C) ------------------------------------------
#
# The reproach SHOWS no example text. Session 3 measured that a shown reference
# gets copied character for character, and `validate_accumulation` detects it.
# The movement is described, the constraint is numbered, the sentence is
# anchored in the entry's objects (doctrine 6).
# THE FALL IS IMPOSED (session 6, §3.1). « celui qui cloche » let the model
# pick the anomaly, and it picked one of its own — a tap left running (C1).
# The chapter's anomaly is a fact of the novel, not a find at the end of a
# sentence: it is given, like the verdict and the imposed fact.
# The object the accumulation falls upon comes from the chapter spec
# (`state["accumulation_fall"]`); without one, « celui qui cloche ».

_ACC_INSTRUCTION = """Voici la partie d'une entrée de carnet où la narratrice \
rétablit sa soirée.

Écris UNE SEULE PHRASE qui reprenne, dans l'ordre, les faits de cette soirée : \
le retour, les gestes, les objets, les heures — jusqu'à celui qui cloche, sur \
lequel la phrase s'achève.

L'étape qui cloche, imposée : {fall}. La phrase finit sur elle.
Les objets de cette maison, les seuls : {objects}.

Contraintes, vérifiées :
- une seule phrase : AUCUN point, aucun point-virgule à l'intérieur ;
- **au moins DOUZE étapes**, chacune séparée par une simple virgule — l'heure \
du retour, un geste, un objet, une pièce, un autre geste, et ainsi de suite \
jusqu'au coucher ;
- pas de « et » ni de « puis » pour les relier : la virgule seule ;
- puis la rupture (« sauf une, une seule ») et l'étape qui cloche ;
- entre douze et vingt étapes : au-delà, c'est un emballement, pas une spirale ;
- uniquement des faits DE CE TEXTE, aucun objet ni lieu nouveau ;
- l'absente ne se qualifie JAMAIS au masculin — ni « mari », ni « lui », ni \
« il » : la maison a été partagée avec une femme. Mais la phrase n'a besoin \
que de SES gestes à elle ; l'absente n'a pas à y figurer ;
- des ÉTAPES, pas des états d'âme : ce qu'elle fait et ce qu'elle touche, \
jamais ce qu'elle ressent ni ce qu'elle conclut.

Rends la phrase seule, rien d'autre."""

# The drift instruction was REMOVED, not commented out: the gesture is no
# longer asked of the model, it is drawn from the bank (see `drift_node`). A
# dead instruction left in place reads one day as a live one.



def _gestures_allowed(state: ChapterState) -> bool:
    """Does this entry admit the signature gestures?

    Chapter 7 decides it per entry: entry 1 is two sentences long, with room
    for neither an accumulation nor a drift. In the previous draw the
    accumulation was spliced in anyway — 471 words instead of two sentences,
    and that is how « les courses » and « la télévision » entered the chapter.
    """
    spec = state.get("entry_specs") or []
    idx = len(state["scenes"]) - 1
    if idx < 0 or idx >= len(spec):
        return True
    return bool(spec[idx].gestures)


def accumulate_node(state: ChapterState) -> dict:
    """Produce the accumulation sentence. The CODE validates and will place it.

    Four sessions established that it comes neither from the sheet (three
    formulations) nor from a reproach loop (never an authentic one). So it is
    assembled: the model supplies the matter, the code the form (ADR-0018).
    """
    if not state.get("micro_nodes") or not state["scenes"]:
        return {}
    if not _gestures_allowed(state):
        return {}
    # THE CONTEXT IS THE RECONSTRUCTION SEGMENT, not the whole entry.
    # `accumulate` had become stage C's famine channel: it got only the entry
    # and a form instruction, so when the reconstruction was thin it invented
    # the missing steps from its priors — television and messages (C1),
    # « revenue du travail » (C3), handbag and tray (CC). nemo's generic world,
    # driven out of `write` by the RAG, came back in here (doctrine 7). The cut
    # of `write` makes this segment identifiable without guessing.
    entry = state.get("reconstruction") or state["scenes"][-1]
    instruction = _ACC_INSTRUCTION.format(
        objects=state.get("active_objects") or "le cahier, l'assiette, l'égouttoir",
        fall=state.get("accumulation_fall") or "celui qui cloche")
    metrics, warns, sentence = [], [], ""
    for try_no in range(1, MAX_GESTURE_ATTEMPTS + 1):
        progress.phase("Accumulation",
                       f"entrée {len(state['scenes'])} (essai {try_no})")
        txt, m = chat(instruction, entry, model=settings.effective_gesture_model,
                      temperature=settings.gesture_temperature, num_predict=300)
        metrics.append(m)
        candidate = " ".join(txt.strip().split())
        # The accumulation is ANOTHER node, run AFTER the write's `delint` —
        # glued tokens (« j'aiallumé ») survived there. Clean here, before
        # validation (so the word count bears upon the corrected text).
        candidate, _ = delint(candidate)
        # Counting STEPS is something the model can do; counting WORDS is not
        # — it returned 48 words for a floor of 60, twice in a row. The code
        # keeps checking in words: the instruction aims at what is reachable,
        # the guard measures what counts.
        ok, reason = validate_accumulation(
            candidate, last_attempt=(try_no == MAX_GESTURE_ATTEMPTS),
            chapter=state.get("chapter") or 0)
        if ok:
            sentence = candidate
            if reason:
                warns.append(f"accumulation entrée {len(state['scenes'])} : "
                             f"{reason}")
            break
        warns.append(f"accumulation entrée {len(state['scenes'])}, essai "
                     f"{try_no} : {reason}")
    if not sentence:
        warns.append(f"accumulation entrée {len(state['scenes'])} : ABANDONNÉE "
                     f"après {MAX_GESTURE_ATTEMPTS} essais")
    return {"accumulation": sentence,
            "metrics": state["metrics"] + _tag(metrics, "accumulate"),
            "warnings": state["warnings"] + warns}


def drift_node(state: ChapterState) -> dict:
    """Compose the drift FROM THE BANK, then set the gestures aside.

    THE GESTURE LEFT THE MODEL (session 6, §2). Eleven runs, three distinct
    failure modes, zero drift: the difficulty is not length but the NATURE of
    the request — approaching a subject then breaking off is a gesture of
    meaning, not of form. The matter is written by hand in the chapter's
    drift bank, and the code chooses, cuts and pastes (ADR-0018). The doctrine
    of the notebook quotations, extended: the most intimate part of the novel
    is already written.

    This node makes NO model call any more. It stays a node because the
    assembly must live after `accumulate`: both positions are computed against
    the ORIGINAL text, and had `accumulate` already inserted its sentence, the
    drift offsets would point into a shifted text.
    """
    if not state.get("micro_nodes") or not state["scenes"]:
        return {}
    if not _gestures_allowed(state):
        # The entry admits no gesture: push an EMPTY set so the indexing of
        # `gestures` stays aligned with the entries. Without it, the gestures
        # of entry 2 would be posed in entry 1.
        gestures = list(state.get("gestures") or [])
        gestures.append({})
        return {"gestures": gestures, "accumulation": ""}
    warns: list[str] = []
    spec = state.get("entry_specs") or []
    idx = len(state["scenes"]) - 1
    sheet: EntrySpec = spec[idx] if 0 <= idx < len(spec) else EMPTY_ENTRY

    # WRITTEN PASSAGE (movement method): the brief supplies it whole, with its
    # frontier. No more approach + « … » + fact suture — the interruption
    # carries the approach and the return to the material IS the next
    # discovery. Both forms coexist: the bank stays for the chapters not yet
    # migrated, and the presence of the field decides (ADR-0019).
    if sheet.drift and sheet.drift.text:
        passage = sheet.drift.text
        ok, reason = passage_valid(passage)
        if not ok:
            warns.append(f"glissement entrée {idx + 1} : passage REFUSÉ par "
                         f"son validateur — {reason}")
            passage = ""
        gestures = list(state.get("gestures") or [])
        gestures.append({"accumulation": state.get("accumulation") or "",
                       "glissement": passage,
                       "frontiere": sheet.drift.position,
                       "reconstruction": state.get("reconstruction") or "",
                       "entete": state.get("placed_header") or "",
                       "ancre": state.get("placed_anchor") or "",
                       "chute": state.get("placed_fall") or ""})
        return {"gestures": gestures, "accumulation": "",
                "warnings": state["warnings"] + warns}

    drawn = list(state.get("drawn_approaches") or [])
    approach, fact = draw_approach(state.get("drift_bank") or {}, drawn,
                                   state.get("seed") or 0)
    drift = ""
    if approach:
        progress.phase("Glissement", f"entrée {len(state['scenes'])} (banque)")
        # The material fact is taken from the active objects when the chapter
        # gives others than the bank's — variation stays possible without the
        # form depending upon the model.
        drift = compose_drift(approach, fact)
        drawn.append(approach)
    else:
        warns.append(f"glissement entrée {len(state['scenes'])} : aucune "
                     "approche disponible en banque pour ce chapitre — M1 se "
                     "lit « non prévu », pas « manqué »")

    # The fragments are SET ASIDE, not inserted here. Put into `scenes`, they
    # then went through `review` (« resserre la prose ») and `repair` — which
    # rewrite the whole entry and dissolved the accumulation: a sixty-word
    # sentence is precisely what a tightening instruction breaks. The gesture
    # is posed in the FINAL text, in `place_gestures_node`.
    gestures = list(state.get("gestures") or [])
    gestures.append({"accumulation": state.get("accumulation") or "",
                   "glissement": drift,
                   "reconstruction": state.get("reconstruction") or "",
                   "entete": state.get("placed_header") or "",
                   "ancre": state.get("placed_anchor") or "",
                   "chute": state.get("placed_fall") or ""})
    return {"gestures": gestures, "accumulation": "", "drawn_approaches": drawn,
            "warnings": state["warnings"] + warns}


# A dated header, even MALFORMED — comma instead of the period, lowercase
# weather. This is what the stamp must recognise in order to replace it rather
# than add a second one beside it.
NEAR_HEADER = re.compile(
    r"^\s*(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}"
    r"\s*[.,;:]?\s*\S", re.IGNORECASE)


def _restamp(entry: str, *, head: str, anchor: str) -> tuple[str, list[str]]:
    """Re-pose the header and the anchor, exactly, at the top of the entry.

    The code OWNS both markers. Prefixing by real concatenation (session 5)
    made them unalterable during writing — but `review` and `repair` get the
    WHOLE entry and rewrite it, anchor included. Measured: 0/3 verbatim at B′,
    2/3 at stage C, ✗ in S6-1, where the French guillemets had become straight.

    The stake is not typographic. The assembly places the audio switch at the
    normalised header (ADR-0013): a rewritten header is a switch lost onstage.

    The first block is replaced if it RESEMBLES what is re-posed (the model
    altered it); it is inserted if it vanished.
    """
    notes: list[str] = []
    paras = [p for p in entry.split("\n\n") if p.strip()]

    def place(expected: str, recognizes, what: str) -> None:
        if not expected:
            return
        for k, para in enumerate(paras[:3]):
            if para.strip() == expected.strip():
                return                          # already exact, nothing to do
            if recognizes(para):
                if difflib.SequenceMatcher(None, para.strip(),
                                           expected.strip()).ratio() > 0.55:
                    notes.append(f"{what} re-tamponné — le texte portait "
                                 f"« {' '.join(para.split())[:70]} »")
                    paras[k] = expected
                    return
        # Vanished: re-pose at the top, header first then anchor.
        notes.append(f"{what} ABSENT après réparation — reposé par le code")
        paras.insert(0 if what == "en-tête" else min(1, len(paras)), expected)

    # The header recogniser ALSO accepts the damaged form: `ENTRY_HEADER`
    # demands the period, and the comma is precisely what repair introduces
    # (B′C: « Lundi 2, nuageux. »). Recognising only the correct form INSERTED
    # the right header without removing the wrong one — two headers, the very
    # defect this stamp exists to put out.
    place(head,
          lambda p: bool(ENTRY_HEADER.match(p.strip()))
          or bool(NEAR_HEADER.match(p.strip())), "en-tête")
    place(anchor, lambda p: re.match(r'^\s*[«"“]', p.strip()), "ancre")
    # THE DOUBLED ANCHOR. The code poses it at the top; the model sometimes
    # copied it right after, opening its own text. The same quotation twice,
    # three lines apart, reads as a stutter — and in chapter 7 it is the most
    # loaded line of the novel.
    if anchor:
        core = " ".join(anchor.split()).strip('«»"“” ')
        guard, seen_flag = [], False
        for para in paras:
            flat = " ".join(para.split()).strip('«»"“” ')
            if flat and (flat in core or core in flat):
                # The FIRST is the anchor the code just posed; the following
                # ones are the model's copies. Keep the first, not « all but
                # the first paragraph »: the header already holds index 0, and
                # the naive version removed BOTH copies.
                if seen_flag:
                    notes.append("ancre recopiée par le modèle — doublon retiré")
                    continue
                seen_flag = True
            guard.append(para)
        paras = guard
    return "\n\n".join(paras), notes


def place_gestures_node(state: ChapterState) -> dict:
    """Insert the gestures into the FINAL text, after review and repair.

    The only place they survive: upstream, `review` and `repair` rewrite the
    entry and take the accumulation with the rest. The gestures are artefacts
    COMPOSED by the code — submitting them to a rewrite pass asked the model
    to undo what had just been built (ADR-0018).
    """
    if not state.get("micro_nodes"):
        return {}
    gestures = state.get("gestures") or []
    final_entries = state.get("repaired") or state.get("reviewed") or []
    if not gestures or not final_entries:
        return {}
    progress.phase("Pose des gestes", f"{len(gestures)} entrée(s)")
    outputs, warns = [], []
    for i, entry in enumerate(final_entries):
        g = gestures[i] if i < len(gestures) else {}
        # RECONSTRUCTION BOUNDS, found by SEARCH and not by offset counting:
        # between generation and here the text went through `review` then
        # `repair`, which rewrite it. Stored offsets would point beside; the
        # start of the segment survives well enough to be found — and if it
        # does not, the lexical fallback plays.
        recon = (g.get("reconstruction") or "").strip()
        bounds = None
        if recon:
            head = " ".join(recon.split()[:6])
            # `start`, NOT `i`: the previous version overwrote the loop index
            # with a character offset, so the assembly warnings announced
            # « entrée 26 » in a ONE-entry run (recorded as such in S6-2). A
            # message that names the wrong entry sends the reader to the wrong
            # text.
            start = entry.find(head)
            if start >= 0:
                bounds = (start, start + len(recon))

        # THE STAMP (session 7). The code OWNS the header and the anchor:
        # prefixing guaranteed them to the end of writing, but `review` and
        # `repair` go over the whole entry and rewrite them — French guillemets
        # turned straight, 0/3 verbatim at B′, ✗ in S6-1. This node is the last
        # to touch the text: it re-poses them.
        entry, buffered_notes = _restamp(
            entry, head=g.get("entete") or "", anchor=g.get("ancre") or "")

        # THE FALL, POSED BY THE CODE when the brief imposes it word for word.
        #
        # « Constat : anniversaire. » is the last line of chapter 7 and the
        # novel's tipping point: the day wins by entering her vocabulary. The
        # model missed it THREE times out of three — it closes with a body
        # line and stops there.
        #
        # Same reasoning as for the header and the anchor: what the stage
        # depends upon word for word is not asked, it is composed. And like
        # them it is posed LAST, after the repair that would rewrite it.
        fall = (g.get("chute") or "").strip()
        if fall and fall not in entry:
            entry = entry.rstrip() + "\n\n" + fall
            buffered_notes.append(f"chute imposée absente — posée par le code : "
                                f"« {fall} »")

        # THE DECLARED FRONTIER wins over the offset computation: it is a
        # place in the narrative, not a position in the text. If the anchor
        # cannot be found, SAY so and fall back to the offset — a gesture
        # placed at random is worse than an absent one, but a silent gesture
        # is worse still.
        frontier = None
        if g.get("frontiere") and g.get("glissement"):
            frontier = frontier_position(entry, g["frontiere"],
                                         state.get("drift_anchors") or {})
            if frontier is None:
                warns.append(f"assemblage entrée {i + 1} : frontière « "
                             f"{g['frontiere'][:60]} » introuvable dans le "
                             "texte — repli sur le placement par offset")
        text, notes = assemble(entry, g.get("accumulation") or "",
                                 g.get("glissement") or "",
                                 state.get("verdict") or "", bounds,
                                 frontier=frontier)

        # DEDUPLICATION last — after the gestures, so the composed paragraphs
        # are in the text and therefore explicitly protected. Falsified in
        # S6-C: without protection the three strongest similarities of the
        # chapter were the header, the anchor and the drift.
        protected = tuple(x for x in (g.get("accumulation"), g.get("glissement"),
                                     g.get("ancre"), g.get("entete")) if x)
        for _, j, ratio, _ in reversed(repeated_paragraphs(text,
                                                          protected=protected)):
            paras = [p for p in text.split("\n\n") if p.strip()]
            if j >= len(paras):
                continue
            removed = paras.pop(j)
            text = "\n\n".join(paras)
            # Say WHAT is removed: the rule of the cutting net since session
            # 4. A silent removal is indistinguishable from a model that wrote
            # nothing there.
            notes.append(f"paragraphe redit retiré ({ratio}) — « "
                         f"{' '.join(removed.split())[:90]}… »")

        outputs.append(text)
        warns += [f"assemblage entrée {i + 1} : {n}"
                  for n in notes + buffered_notes]
        if not (g.get("accumulation") or "").strip():
            warns.append(f"assemblage entrée {i + 1} : aucune accumulation à "
                         "poser")
    return {"repaired": outputs, "warnings": state["warnings"] + warns}


def route_after_write(state: ChapterState) -> str:
    """Loop while scenes remain to write, otherwise move to review."""
    return "write" if state["idx"] < len(state["plan"]) else "review"


def _entry_target(state: ChapterState, i: int) -> tuple[int, int]:
    """Word range of entry `i` — the brief's when it gives one."""
    spec = state.get("entry_specs") or []
    if i < len(spec) and spec[i].words:
        return tuple(spec[i].words)
    return WORDS_PER_ENTRY


def _acceptable_cut(before: int, after: int, target: tuple[int, int]) -> bool:
    """A cut that brings the text CLOSER to the target is good, however deep.

    The 60 % threshold exists against vanishing: a rewrite pass must not make
    the entry disappear. But it only looked at the DEPTH of the cut, never its
    DIRECTION — and it cost dearly.

    Measured in S6-C: `review` trimmed entry 1 from 1033 to 495 words and
    entry 3 from 1567 to 709. Both aimed at 450-600, both were rejected (48 %,
    45 %), and the chapter stayed at 1008 words per entry. Review did exactly
    the work asked of it — correcting excess mass — and the guard stopped it
    twice.

    The rule becomes: if the reviewed text lands IN the target, or approaches
    it without crossing the floor, accept whatever the depth. The threshold
    only applies to cuts that move away — those that go under the floor, the
    vanishing the guard really aimed at.
    """
    lo, hi = target
    if after >= lo:                 # in the target or still above
        return True
    if before < lo:                  # already too short: any cut moves away
        return after >= 0.6 * before
    # The cut went UNDER the floor: acceptable only if it moved away less than
    # it brought closer.
    return (lo - after) < (before - hi) and after >= 0.6 * before


def review_node(state: ChapterState) -> dict:
    """Prose review: tighten, fix repetitions, keep the voice.

    Scene by scene (the model reviews a short block better than a whole
    chapter — mitigation of the long-range coherence limit).

    Two protections against the truncation observed at the first milestone:
      1. `num_predict` adapts to the scene length (a rewrite cannot be shorter
         than the original without losing text).
      2. Guard: if the reviewed version is under 60 % of the original (the
         model « swallowed » the scene), the original is kept. A scene is
         never destroyed by review.
    """
    reviewed: list[str] = []
    metrics = list(state["metrics"])
    warns = list(state["warnings"])
    system = assemble_system_prompt(
        characters=state["characters"], scene_brief=state["brief"],
        include_scenes=False, rag=state.get("rag", True),
        chapter=state.get("chapter"),
        style=REVIEW_STYLE, epistemic=False,
    )
    for i, scene in enumerate(state["scenes"]):
        progress.phase("Relecture",
                       f"entrée {i + 1}/{len(state['scenes'])} (nemo)",
                       i=i + 1, n=len(state["scenes"]))
        # ~3.5 characters per token in French; aim at 1.6x the scene length,
        # bounded, to leave room for a complete rewrite.
        budget = min(2000, max(1200, int(len(scene) / 3) + 300))
        user = (
            "Relis et RÉÉCRIS INTÉGRALEMENT cette entrée de carnet pour "
            "resserrer la prose : supprime les répétitions, renforce les "
            "images, garde EXACTEMENT la voix et les faits, et conserve "
            "l'en-tête daté tel quel. Rends l'entrée ENTIÈRE corrigée, du "
            "début à la fin, et rien d'autre (pas de commentaire, pas de "
            "titre).\n\n"
            f"--- ENTRÉE À RÉÉCRIRE ---\n{scene}"
        )
        text, ms, wg = _generate_whole(system, user, num_predict=budget,
                                       temperature=0.5,
                                       label=f"relecture entrée {i + 1}")
        metrics.extend(_tag(ms, f"review/{i + 1}"))
        warns.extend(wg)
        # Anti-destruction guard: a review too short -> keep the original. It
        # was SILENT: a rewrite that tightened hard was cancelled wholesale
        # without a word, and style work aiming at concision vanished without
        # trace. Make it speak.
        before, after = len(scene.split()), len(text.split())
        # THIS ENTRY'S TARGET, not the chapter's. In ch. 7 entry 1 aims at
        # 25-60 words: review had brought it from 315 to 156 — towards the
        # brief — and the guard rejected it by comparing with 450-600. A
        # « target-aware » guard that reads the wrong target fights exactly
        # what it should serve.
        target = _entry_target(state, i)
        if not _acceptable_cut(before, after, target):
            warns.append(
                f"relecture entrée {i + 1}: garde-fou déclenché "
                f"({after} mots contre {before}, soit {after / max(before, 1):.0%} "
                f"— hors cible {target[0]}-{target[1]}) "
                "— relecture REJETÉE, original conservé"
            )
            text = scene
        elif after < 0.6 * before:
            warns.append(
                f"relecture entrée {i + 1}: coupe profonde ACCEPTÉE "
                f"({after} mots contre {before}) — elle rapproche de la cible")
        text, w = delint(text)
        warns.extend(f"relecture entrée {i + 1}: {x}" for x in w)
        reviewed.append(text)
    return {"reviewed": reviewed, "metrics": metrics, "warnings": warns}


def repair_node(state: ChapterState) -> dict:
    """Linguistic repair (Qwen): rewrites the English leaks left by nemo,
    sentence by sentence, without touching meaning or style.

    Here Ollama swaps from the author model (nemo) to the QA model (Qwen) —
    one swap for the whole QA phase that follows. nemo is unloaded FIRST: nemo
    (13 GB) + Qwen (4.8 GB) warm together is 17.8 GB of 19.3 GB, exactly the
    memory pressure that panicked the machine (ADR-0008). nemo has nothing
    left to produce at this point."""
    repaired: list[str] = []
    metrics = list(state["metrics"])
    warns = list(state["warnings"])
    progress.phase("Bascule des modèles", "nemo déchargé, Qwen prend la main")
    if not unload():
        warns.append("QA : déchargement de nemo refusé par Ollama (co-résidence "
                     "nemo + Qwen, pression mémoire)")
        progress.note("déchargement de nemo REFUSÉ — pression mémoire")
    for i, scene in enumerate(state["reviewed"]):
        progress.phase("Réparation linguistique",
                       f"entrée {i + 1}/{len(state['reviewed'])} (Qwen)",
                       i=i + 1, n=len(state["reviewed"]))
        text, m = repair(scene)
        metrics.extend(_tag([m], f"repair/{i + 1}"))
        # Guard: a repair must not make the entry vanish. Talkative for the
        # same reason as the review's.
        before, after = len(scene.split()), len(text.split())
        # THIS ENTRY'S TARGET, not the chapter's. In ch. 7 entry 1 aims at
        # 25-60 words: review had brought it from 315 to 156 — towards the
        # brief — and the guard rejected it by comparing with 450-600. A
        # « target-aware » guard that reads the wrong target fights exactly
        # what it should serve.
        target = _entry_target(state, i)
        if not _acceptable_cut(before, after, target):
            warns.append(
                f"réparation entrée {i + 1}: garde-fou déclenché "
                f"({after} mots contre {before}, soit {after / max(before, 1):.0%} "
                f"— hors cible {target[0]}-{target[1]}) "
                "— réparation REJETÉE, texte relu conservé"
            )
            text = scene
        elif after < 0.6 * before:
            warns.append(
                f"réparation entrée {i + 1}: coupe profonde ACCEPTÉE "
                f"({after} mots contre {before}) — elle rapproche de la cible")
        # Re-lint to trace what remains (stubborn English, glued tokens).
        text, w = delint(text)
        warns.extend(f"réparation entrée {i + 1}: {x}" for x in w)
        repaired.append(text)
    return {"repaired": repaired, "metrics": metrics, "warnings": warns}


def _protected_sentence(sentence: str) -> bool:
    """Sentences the removal NEVER touches, even if Qwen flags them: header,
    notebook quotation, drift fragments (« … »), fall."""
    n = sentence.strip()
    return bool(re.match(r"[A-ZÉÈ][a-zé]+ \d+\.", n)   # header « Samedi 14. »
                or "…" in n
                or n.startswith("Constat")
                or ("«" in n and "»" in n))            # quotation in guillemets


# DETERMINISTIC PRUNING of the diffuse residue. Qwen was falsified in both
# roles — editor (cuts the good) AND detector: « NON » to
# « le départ, la réunion, la départementale, le garage », it does not link an
# oblique reconstruction to an outing. Code matches the markers without
# ambiguity. A sentence touching ONE motif is removed whole. Whack-a-mole, but
# RELIABLE (ADR-0020).
_PRUNE_PATTERNS = {
    "sortie": re.compile(
        r"\b(r[ée]union|d[ée]partementale|au\s+travail|au\s+bureau|"
        r"le\s+garage|la\s+buanderie|le\s+d[ée]jeuner|le\s+trajet|"
        r"sept\s+heures\s+quarante|le\s+retour\s+par)\b", re.IGNORECASE),
    "présence": re.compile(
        r"\b(un\s+bruit|des\s+bruits|des\s+pas\b|une\s+sonnerie|quelqu'un|"
        r"une\s+voix|qui\s+rentrait|porter\s+mes\s+cl[ée]s|une?\s+invit[ée]e?)\b",
        re.IGNORECASE),
    # Same detection as the scorer: one regex, aligned by construction.
    "récursion": _BEAT_RECURSION,
    "résolution": re.compile(
        r"je\s+n'ai\s+pas\s+r[êe]v[ée]|ma\s+m[ée]moire\s+(?:m'a\s+jou|me\s+joue)"
        r"|je\s+me\s+souviens\s+(?:maintenant|soudain|enfin)"
        r"|tout\s+est\s+normal", re.IGNORECASE),
}


def _prune_residue(entry: str) -> tuple[str, list[str]]:
    """Code pruning of the diffuse residue (ADR-0020: the code, not Qwen).

    Removes the sentences touching a named motif (outing / presence /
    recursion / resolution), protects header/quotation/drift/fall, and
    refuses to remove more than half (safety guard — at worst, a no-op).
    """
    paras_out, removed_ones = [], []
    for para in entry.split("\n\n"):
        kept = []
        for ph in re.split(r"(?<=[.!?…»])\s+", para.strip()):
            if not ph.strip():
                continue
            pattern = next((k for k, rx in _PRUNE_PATTERNS.items() if rx.search(ph)),
                        None)
            if pattern and not _protected_sentence(ph):
                removed_ones.append(f"[{pattern}] " + " ".join(ph.split())[:45])
            else:
                kept.append(ph.strip())
        if kept:
            paras_out.append(" ".join(kept))
    output = "\n\n".join(paras_out).strip()

    if not removed_ones:
        return entry, ["pruning : rien à retirer"]
    if len(output) < 0.5 * len(entry):
        return entry, [f"pruning : suppression > 50 % ({len(removed_ones)} "
                        "phrases) — REJETÉ, original conservé"]
    return output, [f"pruning : {len(removed_ones)} phrase(s) retirée(s) — "
                    + " | ".join(removed_ones)]


def assemble_node(state: ChapterState) -> dict:
    """Deterministic pruning of the diffuse residue, for the beat entries.

    Placed BEFORE `place_gestures`, over the BODY alone (`repaired`): the
    gestures (drift, fall, accumulation) are not yet posed, so the pruning
    cannot touch them, and the code poses them clean over the cleaned body.
    """
    if not settings.pruning_enabled or not state.get("micro_nodes"):
        return {}
    entries = state.get("repaired") or []
    spec = state.get("entry_specs") or []
    if not entries:
        return {}
    outputs, warns = list(entries), []
    for i, entry in enumerate(entries):
        sheet = spec[i] if i < len(spec) else EMPTY_ENTRY
        if sheet.strategy != "beats":     # only the beat entry is cleaned
            continue
        progress.phase("Assemblage", f"entrée {i + 1}")
        outputs[i], w = _prune_residue(entry)
        warns += w
    return {"repaired": outputs, "warnings": state["warnings"] + warns}


def coherence_node(state: ChapterState) -> dict:
    """Coherence by FACTS (Qwen): derive the structuring facts from the sheets,
    then check them SCENE BY SCENE before aggregating.

    The per-scene cut is not cosmetic: over the whole chapter Qwen turns into
    a workshop critic (suggestions, rewriting) and stops returning verdicts.
    Over a short entry it holds the format. And a fact is violated only if a
    scene CONTRADICTS it — the unmentioned is not a fault (ADR-0010).
    The facts are those ALREADY derived by the plan node: the same invariants
    constrain the plan and judge the result, otherwise the final report would
    sanction a chapter in the name of rules the planning never received. Side
    saving: one Qwen call fewer.
    This is the final « strate 4 » shown onstage."""
    metrics = list(state["metrics"])
    progress.phase("Cohérence par faits", "(Qwen)")

    facts = state.get("facts") or []
    # Without RAG there is no bible to query: re-deriving here would reach for
    # Chroma and bring the whole run down against a stopped container. The
    # node is INERT in stage A, by construction — the second variable of the
    # A → B gap, and it must be read in the report rather than show up as a
    # call trace.
    if not facts and state.get("rag", True):
        # Plan short-circuited (unit test, resume): re-derive.
        facts, mf = derive_facts(state["characters"])
        metrics.extend(_tag([mf], "coherence/faits"))
    if not facts:
        return {
            "coherence": ("Aucun fait dérivé de la bible — cohérence inerte "
                          "(étage A, rag=False)." if not state.get("rag", True)
                          else "Aucun fait dérivé de la bible."),
            "metrics": metrics,
        }

    report, mc = check_facts(facts, state["repaired"])
    metrics.extend(_tag(mc, "coherence"))
    return {"coherence": report, "metrics": metrics}


# --- Graph assembly ----------------------------------------------------------

def build_graph():
    g = StateGraph(ChapterState)
    # The machine gate opens the graph (ADR-0002, item 5): a throttled machine
    # is refused before any model call, from the API and the CLI alike.
    g.add_node("preflight", preflight_node)
    # The narrative state of this chapter, generated from the author's table
    # and indexed before the first model call (ADR-0002, step 6).
    g.add_node("narrative_state", narrative_state_node)
    g.add_node("plan", plan_node)
    g.add_node("write", write_node)
    g.add_node("review", review_node)
    g.add_node("repair", repair_node)
    g.add_node("coherence", coherence_node)

    g.add_edge(START, "preflight")
    g.add_edge("preflight", "narrative_state")
    g.add_edge("narrative_state", "plan")
    g.add_node("accumulate", accumulate_node)
    g.add_node("drift", drift_node)
    g.add_edge("plan", "write")
    # The gestures are assembled INSIDE the loop, one pass per entry: they
    # work over a closed entry, not a chapter.
    g.add_edge("write", "accumulate")
    g.add_edge("accumulate", "drift")
    g.add_conditional_edges("drift", route_after_write, ["write", "review"])
    g.add_edge("review", "repair")
    # The gestures are posed AFTER the repair, in the final text — and so
    # BEFORE coherence, which must judge the chapter as it will be read.
    g.add_node("place_gestures", place_gestures_node)
    g.add_node("assemble", assemble_node)
    # BEFORE place_gestures: `repaired` is the BODY alone, the gestures (drift,
    # fall, accumulation) are not yet posed — the pruning cannot damage them,
    # and the code poses them CLEAN over the cleaned body. The pass makes no
    # model call: no extra swap.
    g.add_edge("repair", "assemble")
    g.add_edge("assemble", "place_gestures")
    g.add_edge("place_gestures", "coherence")
    # Assembly and voice close the graph: the chapter judged by coherence is
    # the chapter served, and the WAV is rendered from that same text.
    g.add_node("render", render_node)
    g.add_edge("coherence", "render")
    g.add_edge("render", END)
    return g.compile()
