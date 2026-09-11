import chapitre
from chapitre import BASCULE, FIN_AUDIO

HEADER = "Samedi 14. Beau temps."


def test_switch_after_the_second_sentence():
    out = chapitre.inserer_bascule("Une. Deux. Trois. Quatre.", phrases=2)
    assert out == f"Une. Deux.\n\n{BASCULE}\n\nTrois. Quatre."


def test_switch_goes_to_the_head_when_the_text_is_too_short():
    out = chapitre.inserer_bascule("Une seule phrase.", phrases=2)
    assert out.startswith(BASCULE)


def test_switch_on_second_header_when_two_headers_exist():
    text = f"{HEADER}\n\nA. B. C.\n\n{HEADER}\n\nD. E."
    out = chapitre.inserer_bascule(text, sur_second_entete=True)
    before, after = out.split(BASCULE)
    assert before.count(HEADER) == 1 and after.lstrip().startswith(HEADER)


def test_switch_on_second_header_falls_back_to_sentences_with_one_header():
    text = f"{HEADER}\n\nA. B. C."
    out = chapitre.inserer_bascule(text, sur_second_entete=True, phrases=2)
    # The header itself is two sentences: the sentence fallback lands after it.
    assert out.split(BASCULE)[0].rstrip() == HEADER
    assert out.split(BASCULE)[1].lstrip() == "A. B. C."


def test_extract_stops_on_a_sentence_end_after_the_word_budget():
    text = f"X.\n\n{BASCULE}\n\n" + "Mot mot mot mot. " * 10
    out = chapitre.extrait_audio(text, mots_max=10)
    assert out.endswith(".") and 10 <= len(out.split()) <= 13


def test_extract_always_includes_the_fall_when_named():
    body = "Une. " * 40 + "Constat : anniversaire. Après."
    text = f"{BASCULE}\n\n{body}"
    out = chapitre.extrait_audio(text, mots_max=5, jusqu_a="Constat : anniversaire.")
    assert out.endswith("Constat : anniversaire.")


def test_assembler_guarantees_both_markers_in_order():
    for scenes in (["A. B. C. D."], ["A."], [""]):
        out = chapitre.assembler(scenes)
        assert BASCULE in out and FIN_AUDIO in out
        assert out.index(BASCULE) < out.index(FIN_AUDIO)


def test_assembler_ch7_mode_ends_audio_on_the_fall():
    scenes = [f"{HEADER}\n\nA. B.", f"{HEADER}\n\n« Cit. »\n\nC. D.\n\nConstat : anniversaire."]
    out = chapitre.assembler(scenes, sur_second_entete=True, chute="Constat : anniversaire.")
    audio = out.split(BASCULE)[1].split(FIN_AUDIO)[0]
    assert audio.rstrip().endswith("Constat : anniversaire.")
