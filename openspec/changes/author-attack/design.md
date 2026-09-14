# Design: author-attack

## Spec and loader

`BeatSpec(name, num_predict, sentences_max, instruction, attack="")`. In
`read_entry_brief`, §7 beats split each heading's lines into plain lines
(the instruction) and `> ` lines (the attack). `_entry` fills
`attack` from the cap literal or the brief, strips it, and asserts no `.md`
name and no workshop term (`ChapterSpecError`).

## Write node

In the beats loop, when `attack` is set: `already` gets `\n\n{attack}`
appended; `model_cap = max(1, sentences_max - sentence_ends(attack))`; after
`_clean_segment`, `_strip_attack_echo(attack, seg)` drops an exact copy or a
first sentence above 0.70 similarity to the attack; `_bound_sentences` uses
`model_cap`; `_score_beat` reads the model's segment; the winner becomes
`f"{attack} {seg}"`; a warning records the posed attack and the cap.

## What the fixtures and snapshots show

`tests/unit/test_attack.py` runs `write_node` on chapter 7 entry 2 with an
attack on the first beat: the entry carries the attack once, the served
prompt of that beat ends its "already written" block with it, the next beat
sees it once inside the text already written, the four-sentence fixture
loses its last sentence (cap 4 minus 1), a resolving variant still loses to
the fixture, and the loader accepts a clean attack and refuses a file name
or a workshop term. `tests/snapshots/*` are byte-identical.
