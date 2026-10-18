"""The progress gate of plan-state-beats: a beat variant that writes again
what the entry already holds is scored as a « recopie ». Falsified both ways
(doctrine 4) on the beats drawn in `20261018-beats-see-movement`: arm B's
doubt recopied the discovery whole; the quotation, read by the relève, is not
a recopy; R's beats share at most one sentence."""

from factory.pipeline.graph import _recopied, _score_beat

QUOTATION = ("« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès "
             "cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime toujours. »")

# Arm B, run 182926: the discovery as written, then the doubt variant that
# recopied it (4 of its 4 sentences).
DISCOVERY = (
    "Je relis la ligne que je viens de recopier. Autour de moi, la maison est dressée pour "
    "la fête que je n'ai pas préparée : les photos sont étalées sur la table du salon, la "
    "musique joue en boucle dans la cuisine, le plat des anniversaires est en train de cuire "
    "dans le four, et deux couverts sont mis sur la table. Je ne me souviens pas avoir fait "
    "tout ça. Je me suis peut-être perdue dans le temps, dans les souvenirs de notre amour "
    "qui ont envahi chaque coin de la maison.")
RECOPIED_DOUBT = DISCOVERY

# Arm B, run 180309: a doubt variant that recopies the quotation only.
QUOTED_DOUBT = ("« Neuf ans aujourd'hui que je t'ai dit oui. J'ai mis deux couverts, exprès "
                "cette fois, et j'ai redit oui tout haut dans la cuisine. Je t'aime "
                "toujours. »\n\nJ'ai mis deux couverts, exprès cette fois, et j'ai redit oui "
                "tout haut dans la cuisine.")

OPEN_DOUBT = ("Mes mains sont froides. Ma nuque est raide, je relis la page une troisième "
              "fois. Je ne me souviens pas avoir mis la table. Je repose le crayon.")


def test_a_recopied_beat_is_vetoed():
    assert _recopied(RECOPIED_DOUBT, DISCOVERY, QUOTATION) == 4
    score, defects = _score_beat(RECOPIED_DOUBT, False, 7, written=DISCOVERY,
                                 quotation=QUOTATION)
    assert "recopie (4 phrases déjà écrites)" in defects and score <= -7


def test_the_quotation_is_not_a_recopy():
    written = f"{QUOTATION}\n\n{DISCOVERY}"
    assert _recopied(QUOTED_DOUBT, written, QUOTATION) == 0


def test_a_moving_beat_passes():
    score, defects = _score_beat(OPEN_DOUBT, False, 7, written=DISCOVERY, quotation=QUOTATION)
    assert defects == [] and score == 3


def test_one_shared_sentence_is_not_a_recopy():
    doubt = "Je ne me souviens pas avoir fait tout ça. Mes mains sont froides sur la page."
    assert _recopied(doubt, DISCOVERY) == 1
    assert not any("recopie" in d for d in _score_beat(doubt, False, 7, written=DISCOVERY)[1])


def test_off_without_the_entry():
    """`blind` passes nothing written: the selection is production's."""
    assert _score_beat(RECOPIED_DOUBT, False, 7) == _score_beat(RECOPIED_DOUBT, False, 7,
                                                                  written="")
