"""The style scorer is falsified before it serves (doctrines 3 and 4).

It ranks register, not structure. The claims: every reference excerpt of the
style sheet outranks the drafts the owner read aloud as generic; the
references' mean outranks the journal's mean; the conforming fixtures score
high; a genre paragraph scores below a dry one; and it never decides against
a defect score in the best-of selection.
"""

from pathlib import Path

from factory.eval import style
from factory.eval.lint import _references
from factory.pipeline import graph
from fakes import fixtures as fx

REPO = Path(__file__).resolve().parents[2]
JOURNAL = sorted(p for p in (REPO / "experiments/journal").glob("*.md") if p.name != "README.md")

# Read aloud as generic by the owner (journal digest, ADR-0019, ADR-0020): the
# retained draw under the movement method (genre physiology, "alors" ×6), the
# inner novel, the eight-header chapter, the first stage-A draw.
GENERIC = (
    REPO / "experiments/runs/20260827-ch7-movement-method/run-MOUV.md",
    REPO / "experiments/journal/20260827T232014-mouvement-trois-arcs.md",
    REPO / "experiments/journal/20260826T014921-runs-ch7-run-CH7-plan-non-decoupe.md",
    REPO / "experiments/journal/20260818T012029-runs-s4-a-run-AC.md",
    REPO / "experiments/journal/20260818T010331-runs-s4-a-run-A1.md",
)

GENRE = ("Je me suis approchée, intriguée, et j'ai réalisé que quelque chose d'étrange "
         "se passait. Mon cœur s'est mis à battre la chamade, une sueur froide a coulé "
         "le long de mon dos. Est-ce que je perdais la tête ? Je me suis alors rendu "
         "compte que je n'étais pas seule.")
DRY = ("L'égouttoir, ce soir : deux assiettes. Je les compte deux fois. Je relis la "
       "ligne d'hier. Mes mains étaient froides.")


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_references_outrank_the_generic_drafts_and_the_journal_mean():
    refs = _references(REPO / "bible/style-auteur.md")
    assert len(refs) == 4
    ref_scores = [style.score(text) for _, text in refs]
    generic = [style.score(_read(p)) for p in GENERIC]
    assert min(ref_scores) > max(generic), (ref_scores, generic)
    journal = [style.score(_read(p)) for p in JOURNAL]
    assert len(journal) >= 30
    assert sum(ref_scores) / len(ref_scores) > sum(journal) / len(journal)


def test_fixtures_score_high_and_genre_scores_below_dry():
    assert style.score(fx.FULL_ENTRY) > 10 and style.score("\n\n".join(fx.BEATS)) > 10
    assert style.score(GENRE) < 0 < style.score(DRY)
    f = style.features(GENRE)
    assert f["genre_physiology"] > 0 and f["mental_states"] > 0 and f["questions"] > 0
    assert f["surprise"] > 0 and f["telling"] > 0
    assert style.features(DRY)["inventory_lines"] == 1


def test_body_drops_journal_header_and_quotations():
    text = _read(GENERIC[1])
    b = style.body(text)
    assert "JOURNAL DES MURS" not in b and "run: " not in b
    assert "Neuf ans aujourd'hui" not in b          # the anchor is the author's, blanked
    # The accumulation is exempt from the length regime.
    acc = fx.accumulation("la playlist qui tourne encore")
    assert style.features(acc)["long_share"] == 0.0


def test_style_breaks_ties_only_behind_the_defect_score():
    ranked = [{"score": 0, "style": 2.0, "k": 0}, {"score": 0, "style": 5.0, "k": 1},
              {"score": -10, "style": 9.0, "k": 2}]
    ranked.sort(key=lambda v: (-v["score"], -v["style"], v["k"]))
    assert [v["k"] for v in ranked] == [1, 0, 2]
    note = graph._style_tiebreak_note("entrée 2/relève", ranked)
    assert note == ["entrée 2/relève : départage par les marques de style — variant 2 (5.0) "
                    "devant #1 (2.0)"]
    assert graph._style_tiebreak_note("x", [{"score": 3, "style": 1.0, "k": 0},
                                            {"score": 3, "style": 1.0, "k": 1}]) == []
    assert graph._style_tiebreak_note("x", [{"score": 3, "style": 1.0, "k": 0},
                                            {"score": 0, "style": 9.0, "k": 1}]) == []


def test_tiebreak_reaches_the_beat_selection(fake_model, fake_chroma, quiet_progress):
    from factory.chapter_spec import load_chapter

    fake_model.responses["write.beat"] = [GENRE.replace("Mon cœur", "Le cœur"), DRY, DRY] * 3
    spec = load_chapter(7)
    state = {**spec.state(seed=1), "plan": list(spec.imposed_plan), "idx": 1,
             "scenes": [""], "metrics": [], "warnings": []}
    out = graph.write_node(state)
    # GENRE carries named defects (presence, dismissal): it loses on defects,
    # DRY wins; the two DRY variants tie on both counts, so no tie-break note.
    assert DRY.split(".")[0] in out["scenes"][-1]
    assert not any("départage" in w for w in out["warnings"])
