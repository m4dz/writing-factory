"""R4: serve the best pair of consecutive sentences, not the first pair (offline)."""
import json, sys
from pathlib import Path
from factory.chapter_spec.loader import load_variant
from factory.pipeline import scorers
from factory.pipeline.graph import STRAY_HEADER
from factory.text import sentence_ends

here = Path(__file__).parent
sheet = load_variant(here / "spec.yaml").entries[0]

def sentences(t):
    out, p = [], 0
    for e in sentence_ends(t):
        out.append(t[p:e].strip()); p = e
    return out  # the cut tail is dropped, as the bounding does

def score(two):
    sc, d = scorers.score(two, sheet.best_of)
    nb, nd = scorers.notebook(two, cites=False, day_word="anniversaire")
    return sc + nb, d + nd

def best(t, window):
    ss = sentences(scorers.unquote_own_line(t))
    starts = range(max(1, len(ss) - 1)) if window else [0]
    cands = [(score(" ".join(ss[i:i + 2])), -i, " ".join(ss[i:i + 2])) for i in starts]
    (s, d), i, two = max(cands, key=lambda c: (c[0][0], c[1]))
    return s, d, -i, two

pool = [STRAY_HEADER.sub("", r["text"]).strip()
        for f in ("raw-a.json", "raw-b.json") for r in json.load(open(here / f))]
for window in (False, True):
    print("===== fenêtre" if window else "===== deux premières")
    ok = 0
    for g in range(0, len(pool), 3):
        cands = [(*best(t, window), g + k) for k, t in enumerate(pool[g:g + 3])]
        s, d, i, two, k = max(cands, key=lambda c: (c[0], -c[4]))
        ok += not d
        print(f"  groupe {g // 3} -> #{k} phrase {i + 1} ({s:>3}) {d} | {' '.join(two.split())[:200]}")
    print(f"  propres : {ok}/8")
