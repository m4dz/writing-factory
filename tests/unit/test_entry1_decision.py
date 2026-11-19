"""Entry 1 keeps its decision: own line unquoted, decision scored, day's word
refused (entry1-decision).

Falsified both ways (doctrine 4) on raw draws of M, verbatim, from the pools
kept in `experiments/runs/20261119-entry1-decision/` (`raw-a.json`,
`raw-b.json`): served prompt of entry 1, chapter 7, as main served it.
"""

from dataclasses import replace

from test_notebook_checks import ACCEPTED, REJECTED

from factory.chapter_spec import load_chapter
from factory.chapter_spec.model import BestOf
from factory.pipeline import graph, scorers

# The narrator's own line, in the anchor's dress.
OWN_LINE = {
    # raw-a #2: never closed before the cut.
    "a2": ("« J’ai décidé de ne pas préparer le plat, ni d’allumer la musique, ni de "
           "regarder les photos du tiroir. Les couverts resteront dans le placard, les "
           "verres dans l’armoire.",
           "J’ai décidé de ne pas préparer le plat, ni d’allumer la musique, ni de "
           "regarder les photos du tiroir. Les couverts resteront dans le placard, les "
           "verres dans l’armoire."),
    # raw-a #3: emphasis inside the marks, narration after them.
    "a3": ("« *J’ai décidé qu’il ne serait pas question de l’anniversaire aujourd’hui. "
           "Pas de musique, pas de plat des grandes occasions.* » Le téléphone posé sur "
           "la table, je vérifie trois fois.",
           "J’ai décidé qu’il ne serait pas question de l’anniversaire aujourd’hui. "
           "Pas de musique, pas de plat des grandes occasions. Le téléphone posé sur "
           "la table, je vérifie trois fois."),
    # raw-b #9: one sentence quoted, then the list.
    "b9": ("« J’ai décidé que ce jour n’aurait pas lieu. » Les albums sont rentrés dans "
           "le placard, les cadres retournés contre le mur.",
           "J’ai décidé que ce jour n’aurait pas lieu. Les albums sont rentrés dans "
           "le placard, les cadres retournés contre le mur."),
}

# The decision terms proposed to the owner for chapter 7's `best_of.decision`.
DECISION = ("décidé", "décidée", "décision", "n'aura pas lieu", "n'aurait pas lieu",
            "ne se célébrera pas", "pas question")
CRITERION = BestOf(3, "names-erasure",
                   load_chapter(7).entries[0].best_of.names,
                   load_chapter(7).entries[0].best_of.drift, DECISION)


def test_own_line_loses_its_marks():
    for raw, own in OWN_LINE.values():
        assert scorers.unquote_own_line(raw) == own
        assert scorers.notebook(own, cites=False)[0] == 0


def test_a_quotation_keeps_its_marks():
    # Somebody else's words, an addressed line, a transposed matter, an
    # attribution: the notebook goes on rejecting them.
    for name in ("N-014804", "N-032210", "M-000344", "S-234809", "N-225918"):
        text = REJECTED[name][0]
        assert scorers.unquote_own_line(text) == text, name


def test_unquoted_text_is_left_alone():
    for text in ACCEPTED.values():
        assert scorers.unquote_own_line(text) == text


def test_the_decision_outranks_the_doorstep():
    # raw-a #1 won its group with today's rule: a key turned, a drawer.
    doorstep = ("J’ai tourné la clé dans la serrure après avoir vérifié trois fois que rien "
                "ne traînait sur la console. Les photos, encore dans leur enveloppe de "
                "plastique froissé, sont parties dans le premier tiroir du bureau.")
    decided = OWN_LINE["a2"][1]
    assert scorers.score(doorstep, CRITERION) == (-1, ["ne pose pas la décision"])
    assert scorers.score(decided, CRITERION) == (3, [])


def test_either_apostrophe_poses_the_decision():
    for text in ("Ce jour n'aura pas lieu. Les photos au tiroir.",
                 "Ce jour n’aura pas lieu. Les photos au tiroir."):
        assert scorers.score(text, CRITERION) == (3, [])


def test_no_decision_list_no_check():
    criterion = load_chapter(7).entries[0].best_of
    assert criterion.decision == ()
    assert "ne pose pas la décision" not in scorers.score(ACCEPTED["N-104812"], criterion)[1]


def test_the_day_word_is_refused_where_the_verdict_is_absent():
    score, defects = scorers.notebook(OWN_LINE["a3"][1], cites=False, day_word="anniversaire")
    assert score == -5 and defects == ["écrit le mot du jour (« anniversaire »)"]
    assert scorers.notebook(OWN_LINE["b9"][1], cites=False, day_word="anniversaire") == (0, [])
    # « anniversaires » is another word; the check is on the word.
    assert scorers.notebook("Les anniversaires passent.", cites=False,
                            day_word="anniversaire") == (0, [])


def test_best_of_serves_the_unquoted_decision(fake_model, fake_chroma, quiet_progress):
    doorstep = ("J'ai tourné la clé dans la serrure. Les photos sont parties dans le "
                "premier tiroir du bureau.")
    fake_model.responses["write.entry"] = [doorstep, OWN_LINE["a2"][0], doorstep]
    spec = load_chapter(7)
    state = {**spec.state(seed=1), "plan": list(spec.imposed_plan), "idx": 0,
             "scenes": [], "metrics": [], "warnings": []}
    sheets = list(state["entry_specs"])
    sheets[0] = replace(sheets[0], best_of=CRITERION)
    state["entry_specs"] = sheets
    out = graph.write_node(state)
    assert OWN_LINE["a2"][1][:40] in out["scenes"][0]
    assert "«" not in out["scenes"][0]
    assert any("variant 2 retenu" in w for w in out["warnings"])
    assert any("guillemets d'ouverture retirés" in w for w in out["warnings"])
    # Entry 1's draws are recorded, as served, winner marked.
    drawn = [v for v in out["beat_variants"] if v["beat"] == "entrée entière"]
    assert [(v["variant"], v["winner"]) for v in drawn] == [(1, False), (2, True), (3, False)]
    assert drawn[0]["defects"] == ["ne pose pas la décision"]
