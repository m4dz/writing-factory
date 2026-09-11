from factory import text as style


def test_sentence_ends_counts_french_punctuation_and_closing_quotes():
    assert len(style.sentence_ends("Une. Deux ! Trois ?")) == 3
    text = "Il a dit : « Va-t'en. » Puis rien."
    ends = style.sentence_ends(text)
    assert len(ends) == 2
    assert text[:ends[0]].endswith("»")


def test_ends_mid_sentence():
    assert style.ends_mid_sentence("Il marche")
    assert not style.ends_mid_sentence("Il marche.")
    assert not style.ends_mid_sentence("« Va-t'en. »")
    assert not style.ends_mid_sentence("Elle attend…  ")


def test_trim_to_sentence_only_removes_a_small_tail():
    long = "Première phrase complète, assez longue pour compter. " * 4 + "Puis un fragm"
    trimmed = style.trim_to_sentence(long)
    assert trimmed.endswith("compter.") and "fragm" not in trimmed
    short = "Une phrase. Puis un très long fragment qui pèse plus du quart du texte sans"
    assert style.trim_to_sentence(short) == short


def test_delint_replaces_known_franglais_and_reports_the_rest():
    text, warns = style.delint("Suddenly, il pleut. Slowly, la porte.")
    assert text == "Soudain, il pleut. Lentement, la porte."
    assert warns == []
    text, warns = style.delint("j'aiallumé la lampe et the door")
    assert text.startswith("j'ai allumé")
    assert any("anglais résiduel" in w and "the" in w for w in warns)
    _, warns = style.delint("nousWantons partir")
    assert any("tokens corrompus" in w and "nousWantons" in w for w in warns)


def test_delint_leaves_accented_lowercase_alone():
    _, warns = style.delint("L'égouttoir est vide, la lampe éteinte.")
    assert warns == []
