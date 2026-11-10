"""Notebook checks on the entry best-of: third person, quotation (entry1-notebook-checks).

Falsified both ways (doctrine 4) on retained entry-1 texts of chapter 7,
verbatim from the runs named in each case: every one below was SERVED, none
was seen by the selection.
"""

import pytest

from factory.pipeline import graph, scorers

REJECTED = {
    # xp-author-models-2, M, 487914: third person inside an invented quotation.
    "M-000344": ("« Elle a posé le stylo, pointe vers le sol, comme une aiguille prête à "
                 "percer. L’album est resté ouvert sur les dernières photos, mais elle l’a "
                 "refermé d’un geste sec, les clichés glissés dans l’enveloppe sans un "
                 "regard. »", {"troisième personne", "cite"}),
    # xp-author-models-2, S, 731667: the served matter transposed, after a rule.
    "S-232653": ("---\nElle a effacé l'anniversaire, rangé les photos, supprimé la musique, "
                 "écarté le plat — et rien d'autre. La boîte à souvenirs contient les "
                 "photos, le placard du haut, le plat.", {"troisième personne"}),
    # xp-author-models-2, S, 139026: the matter quoted, then commented.
    "S-234809": ("« Elle efface l'anniversaire — range les photos, supprime la musique, "
                 "écarte le plat — et rien d'autre. » Le texte dit vrai : j'ai effacé "
                 "l'anniversaire.", {"cite"}),
    # xp-author-models-2, S, 487914: one « Elle », opening the entry, no « je ».
    "S-000951": ("Elle a posé les photos face contre le mur, empilé les albums dans le "
                 "tiroir du bas, effacé le répertoire de musique. La maison se tait.",
                 {"troisième personne"}),
    # nemo, 2026-10-18: an invented line opens the entry.
    "N-014804": ("\"Je ne veux pas que tu partes, mais je ne veux pas non plus que tu "
                 "restes.\" Ces mots résonnent dans ma tête, encore et encore.", {"cite"}),
    # nemo, 2026-10-18: a short line, but opening the entry.
    "N-032210": ("\"Nous sommes invincibles\", disait-elle, en riant, sur la photo. Je l'ai "
                 "rangée avec les autres, dans le tiroir du bas.", {"cite"}),
    # nemo, 2026-10-19: the quotation in the second sentence.
    "N-225918": ("Ce matin, en relisant le manuscrit de l'auteur, j'ai trouvé une phrase qui "
                 "m'a interpellée : \"Elle effaça l'anniversaire de son calendrier, comme on "
                 "efface une erreur.\"", {"cite"}),
}

ACCEPTED = {
    "N-104812": ("J'ai décidé cet après-midi d'effacer l'anniversaire de son départ. Je "
                 "rangerai les photos, je supprimerai la musique qu'elle aimait, je ne "
                 "sortirai pas le plat des grandes occasions."),
    # « elle » is Romane here, three times, next to the narrator's « je ».
    "N-184557": ("J'ai décidé cet après-midi d'effacer ce jour. Les photos où elle rit, où "
                 "elle est belle, où elle est encore là, je les range dans le tiroir du bas."),
    "N-021344": ("J'ai décidé aujourd'hui de supprimer cette journée de ma vie. J'ai rangé "
                 "les photos d'elle dans un tiroir, supprimé les chansons qu'on écoutait "
                 "ensemble de ma playlist."),
    # A quoted word, not a quotation.
    # Nominal, no « je », « elle » is Romane and opens no sentence.
    "nominal-romane": ("Ce jour n'aura pas lieu. Les photos d'elle au tiroir, la musique "
                       "coupée, le plat laissé au placard."),
    "short-word": ("J'ai décidé que ce jour n'aurait pas lieu. Je n'écrirai pas « oui », "
                   "je range les photos et la musique se tait."),
}


@pytest.mark.parametrize("name", sorted(REJECTED))
def test_rejected(name):
    text, expected = REJECTED[name]
    score, defects = scorers.notebook(text, cites=False)
    assert score < 0
    assert {d.split(" (")[0] for d in defects} == expected


@pytest.mark.parametrize("name", sorted(ACCEPTED))
def test_accepted(name):
    assert scorers.notebook(ACCEPTED[name], cites=False) == (0, [])


def test_an_anchored_entry_may_quote():
    text, _ = REJECTED["N-014804"]
    assert scorers.notebook(text, cites=True) == (0, [])


def test_best_of_skips_the_quoting_variant(fake_model, fake_chroma, quiet_progress):
    from factory.chapter_spec import load_chapter

    quoting = REJECTED["N-014804"][0]
    clean = ACCEPTED["N-104812"]
    fake_model.responses["write.entry"] = [quoting, clean, quoting]
    spec = load_chapter(7)
    state = {**spec.state(seed=1), "plan": list(spec.imposed_plan), "idx": 0,
             "scenes": [], "metrics": [], "warnings": []}
    out = graph.write_node(state)
    assert "J'ai décidé cet après-midi" in out["scenes"][0]
    assert not out["scenes"][0].lstrip().startswith('"')
    assert any("variant 2 retenu" in w for w in out["warnings"])
