"""The review answers for the prose, not for the entry's bounds.

Texts are the measured ones (chapter 7 with M, 2026-11-11,
`experiments/runs/20261111-measure-prepared-plan/`), cut where noted.
"""

from factory.chapter_spec.model import EntrySpec
from factory.pipeline.graph import _review_guard

HEAD = "Samedi 14. Beau temps.\n\n"
ENTRY1 = EntrySpec(weekday="Samedi", number=14, weather="Beau temps", words=(25, 60),
                   sentences_max=2, citation="")
ENTRY2 = EntrySpec(weekday="Samedi", number=14, weather="Beau temps", words=(300, 400),
                   citation="« Neuf ans aujourd'hui que je t'ai dit oui. »")
STATE = {"entry_specs": [ENTRY1, ENTRY2]}

SELECTED = (HEAD + "J’ai retiré le cadre du miroir du salon avant le déjeuner, les deux "
            "photos fixées au dos avec du ruban adhésif depuis le printemps dernier. Elles "
            "sont maintenant dans le troisième tiroir de la commode, sous les chaussettes "
            "de laine, pliées en quatre avec leur bord déchiré par le scotch.")


def test_a_review_that_grows_the_entry_is_rejected():
    reviewed = (HEAD + "« J’ai retiré le cadre du miroir avant le déjeuner. »\n\n"
                "Le miroir du salon est nu depuis hier. Les photos ne sont plus "
                "accrochées.\n\nJe n’ai pas touché au scotch. La colle a jauni.\n\n"
                "Les photos ne sont pas dans le tiroir. Elles sont toujours sur la "
                "table de nuit.")
    text, warns = _review_guard(STATE, 0, SELECTED, reviewed)
    assert text == SELECTED
    assert "REJETÉE" in warns[-1] and "plus de 2 phrase(s)" in warns[-1]
    assert "cite" in warns[-1]


def test_a_review_that_quotes_is_rejected_even_within_two_sentences():
    reviewed = (HEAD + "*« Ce jour n’aura pas lieu. »* La phrase est venue, droite, "
                "sans retour possible.")
    selected = (HEAD + "J’ai noté l’après-midi : *ce jour n’aura pas lieu*. La décision "
                "s’est posée comme une évidence, sans hésitation.")
    text, warns = _review_guard(STATE, 0, selected, reviewed)
    assert text == selected and "cite" in warns[-1]


def test_the_header_is_the_codes():
    selected = HEAD + "J’ai rangé les photos. La journée sera ordinaire."
    reviewed = "Samedi 14. Ciel blanc.\n\nJ’ai rangé les photos. La journée sera simple."
    text, warns = _review_guard(STATE, 0, selected, reviewed)
    assert text == HEAD + "J’ai rangé les photos. La journée sera simple."
    assert "« Samedi 14. Beau temps. » rétabli" in warns[0]
    text, warns = _review_guard(STATE, 0, selected, "J’ai rangé les photos. Rien d’autre.")
    assert text == HEAD + "J’ai rangé les photos. Rien d’autre."


def test_a_defect_already_there_is_not_the_reviews():
    selected = HEAD + "« Je n’ai pas sorti le service. » La vaisselle de tous les jours."
    reviewed = HEAD + "« Je n’ai pas sorti le service. » La vaisselle ordinaire."
    text, warns = _review_guard(STATE, 0, selected, reviewed)
    assert text == reviewed and warns == []


def test_an_entry_without_sheet_only_gets_its_header_back():
    text, warns = _review_guard({"entry_specs": []}, 0, HEAD + "Un. Deux.",
                                "Samedi 14. Pluie.\n\nUn. Deux. Trois. Quatre.")
    assert text == HEAD + "Un. Deux. Trois. Quatre." and len(warns) == 1


def test_a_citing_entry_may_quote_but_not_lose_its_person():
    selected = (HEAD + ENTRY2.citation + "\n\nJ’ai relu la ligne deux fois. "
                "Je n’ai rien corrigé.")
    reviewed = (HEAD + ENTRY2.citation + "\n\nElle a relu la ligne deux fois. Elle "
                "n’a rien corrigé.")
    text, warns = _review_guard(STATE, 1, selected, reviewed)
    assert text == selected and "troisième personne" in warns[-1]
    fine = HEAD + ENTRY2.citation + "\n\nJ’ai relu la ligne. Je n’ai rien corrigé."
    assert _review_guard(STATE, 1, selected, fine) == (fine, [])
