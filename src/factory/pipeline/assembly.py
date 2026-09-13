#!/usr/bin/env python3
"""Assembly of the delivered chapter: switch marker and excerpt to read.

This module generates nothing. It decides WHERE the human voice stops and the
cloned voice takes over — the hinge of the keynote's magic trick, set by
CODE, never by the model: a marker placed by nemo would land elsewhere at
every draw, and the speaker would not know what to read aloud.

Two owner decisions (2026-08-07), recorded in ADR-0013:

1. **The switch falls after the SECOND SENTENCE.** A strictly reproducible
   landmark: onstage he reads two sentences, then starts the audio. A
   paragraph boundary depended upon nemo's paragraphing, so varied from run
   to run — unusable as a stage cue.

2. **The excerpt read by the clone is BOUNDED** (~550 words, ≈ 3-4 min). TTS
   runs at ~1× real time: a whole four-scene chapter (~2400 words) would need
   a quarter hour of audio AND a quarter hour of compute, 32 min against the
   deck's 28' — and a fifteen-minute reading in a fifty-minute keynote.
"""

import re

from factory.settings import settings
from factory.text import sentence_ends

SWITCH = "<!-- BASCULE -->"
AUDIO_END = "<!-- FIN AUDIO -->"

# Sentences read aloud before the switch: `settings.switch_after_sentences`.

# The bound is set in SECONDS, not words — the deck asks for a duration
# (« 2'30 à 3 min, extrait joué EN ENTIER », frontend session of 2026-08-08),
# and an instruction expressed in the unit of the need does not get
# mistranslated.
#
# Conversion to words uses the clone's MEASURED rate: 177 words/min, measured
# over a real 540-word excerpt (183 s of audio) at the full run of 2026-08-09.
# The first figure (190) came from a 117-word sample and overestimated by 7 %
# — an excerpt rendered at 3'03 instead of the 2'45 aimed for. A long text
# carries proportionally more pauses: sentence ends, and 0.6 s between
# segments (13 segments = 7.8 s of silence). The deck reasoned at ~150
# words/min (hence its 375-450 words estimate): its 450 words would have given
# 2'22, UNDER its own floor — a hole where sound is expected.
#
# Acceptance margin around the target: 15 s, not 20. At the 2026-08-09 run the
# gap was 18 s — under the old threshold, hence silent, yet enough to leave
# the window the deck asks for (2'30-3'00).
#
# The four knobs (`audio_words_per_minute`, `audio_seconds`,
# `audio_tolerance_s`, `audio_max_words`) live in `factory.settings`; the
# bound in words is `settings.effective_audio_max_words`.


# The normalised header at LINE START — chapter 7's switch landmark. Same
# format as `ENTRY_HEADER` in `factory.eval.lint`, rewritten here rather than
# imported: this module is served by the API and must not depend upon the
# evaluation tooling. If the format moves, it moves in both places — the
# price, and it is explicit.
HEADER_LINE = re.compile(
    r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}\.\s+"
    r"\S[^\n]{0,40}\.\s*$", re.MULTILINE | re.IGNORECASE)


def _nth_sentence_end(text: str, n: int) -> int | None:
    """End position of the n-th sentence, or None if there are not that many."""
    ends = sentence_ends(text)
    return ends[n - 1] if len(ends) >= n else None


def insert_switch(text: str, *, sentences: int | None = None,
                    on_second_header: bool = False) -> str:
    """Insert the switch marker after the first `sentences` sentences.

    If the text has fewer sentences than asked (very short scene, unexpected
    segmentation), the marker goes at the HEAD rather than being omitted:
    better the clone reads everything than no marker at all, since its
    absence would fail the render and deprive the scene of its audio.

    `on_second_header` — CHAPTER 7 MODE. There the landmark is not a sentence
    count but the structure: two entries of the same day, the speaker reads
    the one where she resists, the cloned voice the one where the day has won.
    The switch goes just BEFORE the second header, and the stage coincidence
    is exact instead of approximate (ADR-0013). Brief 7 §7:
    « détection déterministe, plus d'heuristique ».
    """
    if sentences is None:
        sentences = settings.switch_after_sentences
    if on_second_header:
        heads = list(HEADER_LINE.finditer(text))
        if len(heads) >= 2:
            cut = heads[1].start()
            return (f"{text[:cut].rstrip()}\n\n{SWITCH}\n\n"
                    f"{text[cut:].lstrip()}")
        # A single header: the chapter lacks the expected structure. Fall back
        # to the sentence count rather than omit the marker — the deck treats
        # a chapter without a switch as not ready, so a failed structure would
        # make the demo vanish instead of degrading it.
        pass
    cut = _nth_sentence_end(text, sentences)
    if cut is None:
        return f"{SWITCH}\n\n{text.lstrip()}"
    head, rest = text[:cut].rstrip(), text[cut:].lstrip()
    return f"{head}\n\n{SWITCH}\n\n{rest}" if rest else f"{head}\n\n{SWITCH}"


def audio_excerpt(text: str, *, max_words: int | None = None,
                  until: str = "") -> str:
    """Text the cloned voice must read: after the switch, bounded in words.

    The cut always falls at a SENTENCE END: a WAV stopping mid-sentence is
    heard at once, where a complete sentence passes for an intended ending.
    So the budget is slightly exceeded rather than cut short — the sentence in
    progress is always included.
    """
    if max_words is None:
        max_words = settings.effective_audio_max_words
    after = text.split(SWITCH, 1)[1] if SWITCH in text else text
    after = after.split(AUDIO_END, 1)[0].strip()

    ends = sentence_ends(after)
    if not ends:
        return after

    # THE FALL IS ALWAYS READ. The word bound exists against over-long audio;
    # it must not amputate THE LINE THAT MAKES THE SCENE. At chapter 7's first
    # render the cut fell at 268 words, six lines before
    # « Constat : anniversaire. » — the cloned voice said everything except
    # the sentence it speaks for. The stage coincidence wants the speaker to
    # read the entry where she resists and the clone the one where the day has
    # won: without the fall, the clone wins nothing (ADR-0013).
    if until and until in after:
        bound = after.index(until) + len(until)
        return after[:bound].strip()

    for end in ends:
        if len(after[:end].split()) >= max_words:
            return after[:end].strip()
    return after


def assemble(scenes: list[str], *, max_words: int | None = None,
              sentences: int | None = None,
              on_second_header: bool = False, fall: str = "") -> str:
    """Whole chapter in Markdown, with switch and end of reading marked.

    BOTH MARKERS ARE GUARANTEED PRESENT. Deck requirement (frontend session
    message, 2026-08-08): a chapter missing either marker is treated as not
    ready and falls back to the embedded one. A missing marker would not
    degrade the display, it would make the live chapter vanish — silently.
    Hence the fallback at the end of the text rather than an omission when the
    excerpt bound cannot be computed (very short chapter, text without final
    punctuation).

    The served chapter stays WHOLE: it is the demo's exhibit, not truncated
    because the audio is bounded.
    """
    body = insert_switch("\n\n".join(s.strip() for s in scenes if s.strip()),
                            sentences=sentences,
                            on_second_header=on_second_header)
    read_part = audio_excerpt(body, max_words=max_words, until=fall)
    if read_part and read_part in body:
        pos = body.index(read_part) + len(read_part)
        body = f"{body[:pos]}\n\n{AUDIO_END}\n\n{body[pos:].lstrip()}".rstrip()
    else:
        body = f"{body.rstrip()}\n\n{AUDIO_END}"
    return body
