"""Compare selection rules on raw entry-1 variants (offline)."""
import json, re, sys
from factory.chapter_spec.loader import load_chapter
from factory.pipeline import scorers
from factory.pipeline.graph import STRAY_HEADER, _bound_sentences

sheet = load_chapter(7).entries[0]
OPEN = re.compile(r"^[\s*_]*[«\"“]\s*[*_]*")
CLOSE = re.compile(r"[*_]*\s*[»\"”]")
DECISION = re.compile(r"d[ée]cid|n['’]aura pas lieu|ne se c[ée]l[ée]brera|pas question|ne passera", re.I)

def unwrap(t):
    m = OPEN.match(t)
    if not m:
        return t
    rest = t[m.end():]
    c = CLOSE.search(rest)
    inner, tail = (rest[:c.start()], rest[c.end():]) if c else (rest, "")
    inner = re.sub(r"\*+|_{1,2}", "", inner).strip()
    return (inner + " " + tail.strip()).strip()

def evaluate(t):
    first2 = _bound_sentences(t, 2, 0, "")[0]
    sc, d = scorers.score(first2, sheet.best_of)
    nb, nd = scorers.notebook(first2, cites=False)
    flags = []
    if DECISION.search(first2): flags.append("DÉCISION")
    if re.search(r"anniversaire", first2, re.I): flags.append("mot-du-jour")
    if re.search(r"\d", first2): flags.append("chiffres")
    if "*" in first2: flags.append("italiques")
    return sc + nb, d + nd, flags, " ".join(first2.split())

for f in sys.argv[1:]:
    for r in json.load(open(f)):
        t = STRAY_HEADER.sub("", r["text"]).strip()
        a, b = evaluate(t), evaluate(unwrap(t))
        print(f"## {f[-10:-5]} #{r['k']}")
        print(f"  cur {a[0]:>4} {a[1]} {a[2]} | {a[3][:230]}")
        if b[3] != a[3]:
            print(f"  unw {b[0]:>4} {b[1]} {b[2]} | {b[3][:230]}")

def rule(t, *, unw, dec, day):
    t = unwrap(t) if unw else t
    first2 = _bound_sentences(t, 2, 0, "")[0]
    sc = scorers.score(first2, sheet.best_of)[0] + scorers.notebook(first2, cites=False)[0]
    if dec and DECISION.search(first2): sc += 4
    if day and re.search(r"anniversaire", first2, re.I): sc -= 5
    return sc, " ".join(first2.split())

if __name__ == "__main__":
    pool = [STRAY_HEADER.sub("", r["text"]).strip() for f in sys.argv[1:] for r in json.load(open(f))]
    rules = {"R0 actuel": dict(unw=0, dec=0, day=0), "R1 +déballage": dict(unw=1, dec=0, day=0),
             "R2 +décision": dict(unw=1, dec=1, day=0), "R3 +mot du jour": dict(unw=1, dec=1, day=1)}
    for name, kw in rules.items():
        print("=====", name)
        for g in range(0, len(pool), 3):
            cands = [(*rule(t, **kw), k) for k, t in enumerate(pool[g:g + 3])]
            cands.sort(key=lambda c: (-c[0], c[2]))
            s, txt, k = cands[0]
            print(f"  groupe {g//3} -> #{g + k} ({s:>3}) {txt[:170]}")
