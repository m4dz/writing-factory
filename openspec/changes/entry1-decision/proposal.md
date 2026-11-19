# Proposal: entry1-decision

## Why

After `review-guard` and `repair-english-only`, entry 1 of chapter 7 holds
its form on 3 runs of 3, and its matter on 1 (owner's reading, 2026-11-16:
171197 « poor and unmeaningful », 174597 « good enough », 424242 « fuzzy
and invented »). The brief asks two sentences: she has decided that the day
will not take place; the erasure list. Neither run of 171197 or 424242 says
the decision.

24 raw draws of M on the served prompt of entry 1, kept whole
(`experiments/runs/20261119-entry1-decision/raw-*.json`, before any
bounding):

- **M never writes two sentences.** 4 to 7 sentences, 70 to 99 words, one
  erasure gesture per sentence. `num_predict` (136) ends 16 of 24. The code
  keeps the first two: a door, a key, a drawer — the doorstep, not the
  decision.
- **The decision is dressed as a quotation.** 9 draws of 24 open on
  « « J'ai décidé … » », the narrator's own line in the anchor's dress; 7
  of those carry the decision. `scorers.notebook` (entry1-notebook-checks)
  rejects every one as a quotation.
- **The selection does not discriminate.** `names-erasure` scores +3 any
  text naming the photos: 7 of 12 in the first pool tie at « propre », the
  first drawn wins.
- **The day's word.** 1 draw in 24 writes « anniversaire », which the brief
  forbids in entry 1 (« Le mot du jour n'est jamais écrit dans l'entrée
  1. ») and which `best_of.names` lists as a positive term.

Offline, on the same 24 draws grouped by three as the pipeline draws them
(`sim.py`): today's rule serves the decision in 0 groups of 8. Unquoting
the own line: 3 of 8. Adding the decision to the score: 5 of 8. With 6
draws a group: 4 of 4.

## What changes

- **Own line unquoted.** For an entry without anchor, an opening quotation
  that is the narrator's own line loses its marks (and the emphasis inside
  them) before scoring, and the unquoted variant is the one served: first
  person, nobody addressed (no « tu »: a voice, and the entry has none),
  closed on a sentence end (« "…", disait-elle » keeps its marks). Every
  other quotation is left to `notebook`, which goes on rejecting it — the
  five quoting fixtures of `entry1-notebook-checks` are unchanged.
- **Decision scored.** `best_of.decision` (optional list of terms, spec
  data): a variant whose served sentences hold none scores −4, defect « ne
  pose pas la décision ». Absent list, no check: no chapter moves unless its
  spec asks.
- **Day's word refused.** An entry whose `form.verdict` is `absent` must
  not write the chapter's `verdict` word: −5 at selection, and a review
  that adds it is rejected (`review-guard`).
- **Terms accept both apostrophes** (the spec types « ' », M writes « ’ »).
- **Entry 1's draws are recorded** in `variants.md` (beat « entrée
  entière »), as served — until now the selection of entry 1 left no trace.

## Variable moved

The selection of entry 1. No served prompt moves (snapshots unchanged). The
chapter 7 spec does not move: `best_of.decision` is the OWNER's list, and
`n` the owner's number; the measure uses a variant spec under the
experiment directory.

## Owner's decisions (2026-11-19)

All four adopted, plus the movement line:

1. `best_of.decision` = the measured list.
2. « anniversaire » removed from `best_of.names`.
3. `album`, `albums`, `cadre`, `cadres` added to `best_of.names` (`drift`
   unchanged: « dans un album » still costs 5).
4. `n: 6`.
5. Movement of entry 1 (`bible/profond/mouvements-chapitres.md`, owner's
   wording): « Deux phrases, la porte fermée : la première décide que ce jour
   n'aura pas lieu ; la seconde l'efface — les photos rangées, la musique
   supprimée, le plat écarté. Rien d'autre. » The day's word leaves the
   served prompt; the decision enters it.

**Served prompt moved:** the MOUVEMENT line of entry 1 (snapshot `ch7`),
and six `write.entry` calls instead of three. The fake entry 1
(`tests/fakes/fixtures.py` `SHORT_ENTRY`) now poses the decision, as the
spec asks; `ch7/chapter.md` moves with it.

Entry 1 prepared the day before (the owner picks among 6) is its own change:
`prepared-entry1`.

## For the owner (asked 2026-11-19)

1. `best_of.decision` for chapter 7, entry 1 — measured with: `[décidé,
   décidée, décision, "n'aura pas lieu", "n'aurait pas lieu", ne se
   célébrera pas, pas question]`.
2. `best_of.names` lists « anniversaire », the word entry 1 must not write:
   remove it? (The selection now penalises it anyway.)
3. `best_of.names` misses « album(s) », « cadre(s) »: the best raw draw of
   24 (« J'ai décidé que ce jour n'aurait pas lieu. Les albums sont rentrés
   dans le placard, les cadres retournés contre le mur. ») names neither and
   loses — but « dans un album » is in `drift`.
4. `n: 3` → 6? About +100 s on the stage run (35 s a draw).

## Measure

Chapter 7, M, the three seeds of the owner's last reading (424242, 171197,
174597), variant spec = canonical spec + the decision list. Read by the
owner: entry 1 of `chapitre.md` against 2026-11-16's.
