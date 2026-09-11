from factory.pipeline import assembly
from factory.pipeline.assembly import AUDIO_END, SWITCH

HEADER = "Samedi 14. Beau temps."


def test_switch_after_the_second_sentence():
    out = assembly.insert_switch("Une. Deux. Trois. Quatre.", sentences=2)
    assert out == f"Une. Deux.\n\n{SWITCH}\n\nTrois. Quatre."


def test_switch_goes_to_the_head_when_the_text_is_too_short():
    out = assembly.insert_switch("Une seule phrase.", sentences=2)
    assert out.startswith(SWITCH)


def test_switch_on_second_header_when_two_headers_exist():
    text = f"{HEADER}\n\nA. B. C.\n\n{HEADER}\n\nD. E."
    out = assembly.insert_switch(text, on_second_header=True)
    before, after = out.split(SWITCH)
    assert before.count(HEADER) == 1 and after.lstrip().startswith(HEADER)


def test_switch_on_second_header_falls_back_to_sentences_with_one_header():
    text = f"{HEADER}\n\nA. B. C."
    out = assembly.insert_switch(text, on_second_header=True, sentences=2)
    # The header itself is two sentences: the sentence fallback lands after it.
    assert out.split(SWITCH)[0].rstrip() == HEADER
    assert out.split(SWITCH)[1].lstrip() == "A. B. C."


def test_extract_stops_on_a_sentence_end_after_the_word_budget():
    text = f"X.\n\n{SWITCH}\n\n" + "Mot mot mot mot. " * 10
    out = assembly.audio_excerpt(text, max_words=10)
    assert out.endswith(".") and 10 <= len(out.split()) <= 13


def test_extract_always_includes_the_fall_when_named():
    body = "Une. " * 40 + "Constat : anniversaire. Après."
    text = f"{SWITCH}\n\n{body}"
    out = assembly.audio_excerpt(text, max_words=5, until="Constat : anniversaire.")
    assert out.endswith("Constat : anniversaire.")


def test_assembler_guarantees_both_markers_in_order():
    for scenes in (["A. B. C. D."], ["A."], [""]):
        out = assembly.assemble(scenes)
        assert SWITCH in out and AUDIO_END in out
        assert out.index(SWITCH) < out.index(AUDIO_END)


def test_assembler_ch7_mode_ends_audio_on_the_fall():
    scenes = [f"{HEADER}\n\nA. B.", f"{HEADER}\n\n« Cit. »\n\nC. D.\n\nConstat : anniversaire."]
    out = assembly.assemble(scenes, on_second_header=True, fall="Constat : anniversaire.")
    audio = out.split(SWITCH)[1].split(AUDIO_END)[0]
    assert audio.rstrip().endswith("Constat : anniversaire.")
