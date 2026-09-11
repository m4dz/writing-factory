from factory.pipeline import qa
from fakes import fixtures as fx

SCENE = ("Elle a ouvert la porte et la femme qu'elle aimait était là, dans le couloir, "
         "avec sa valise. Elles ont dîné ensemble et ri jusqu'à minuit.")


def test_answer_regex_accepts_the_formats_the_model_produces():
    for line, n, verdict in [("Q1 : OUI — « citation »", 1, "OUI"),
                             ("Q2: NON", 2, "NON"),
                             ("Q 3 - oui, « x »", 3, "OUI")]:
        m = qa._ANSWER_RE.search(line)
        assert m and int(m.group(1)) == n and m.group(2).upper() == verdict


def test_citation_must_be_found_in_the_scene():
    assert qa._sourced("OUI — « Elles ont dîné ensemble et ri »", SCENE) == \
        "Elles ont dîné ensemble et ri"
    assert qa._sourced("OUI — « Elles ont partagé un repas joyeux »", SCENE) is None
    assert qa._sourced("OUI — « la femme »", SCENE) is None       # too short
    assert qa._sourced("OUI sans citation", SCENE) is None


def test_questions_are_mapped_back_to_their_fact_indices():
    questions = ["", "", ""]
    qa._parse_questions("1. Q pour le fait 3 ?\n2. Q pour le fait 1 ?", questions, [2, 0])
    assert questions == ["Q pour le fait 1 ?", "", "Q pour le fait 3 ?"]


def test_derive_facts_filters_pilot_vocabulary_and_adds_negative_facts(fake_model, fake_chroma):
    fake_model.responses["qa.facts"] = ("- Elle relit son cahier chaque soir.\n"
                                        "- Le verdict imposé est une erreur de relevé.\n"
                                        "- Grade 1, ratio commentaire dominant.\n")
    facts, _ = fake_model and qa.derive_facts(["judith"])
    assert facts[0] == "Elle relit son cahier chaque soir."
    assert not any("verdict imposé" in f or "Grade" in f for f in facts)
    assert facts[-len(qa.FAITS_NEGATIFS):] == qa.FAITS_NEGATIFS
    assert "[la narratrice / Psychologie]" in fake_model.by_role("qa.facts")[0].user


def test_check_facts_counts_only_sourced_and_confirmed_violations(fake_model):
    facts = ["Personne d'autre n'entre dans la maison.", "Elle ne sort pas."]
    fake_model.responses["qa.questions"] = ("1. Le texte montre-t-il quelqu'un entrant ?\n"
                                            "2. Le texte montre-t-il la narratrice sortant ?")
    fake_model.responses["qa.answers"] = ("Q1 : OUI — « la femme qu'elle aimait était là, "
                                          "dans le couloir »\nQ2 : OUI — « elle sort en ville »")
    fake_model.responses["qa.confirm"] = "OUI"
    report, _ = qa.check_facts(facts, [SCENE])
    assert "FAIT 1 : CONTREDIT (scène 1)" in report
    assert "FAIT 2 : tenu" in report and "citation introuvable" in report

    fake_model.responses["qa.confirm"] = "NON"
    report, _ = qa.check_facts(facts, [SCENE])
    assert "CONTREDIT" not in report and "non confirmé au contre-appel" in report


def test_check_plan_reports_a_violation_with_its_line(fake_model):
    facts = ["Elle ne sort pas."]
    beats = ["[Pluie] elle relit", "[Vent] elle sort en ville et rencontre un homme"]
    fake_model.responses["qa.questions"] = "1. Le plan prévoit-il qu'elle sorte ?"
    fake_model.responses["qa.answers"] = "Q1 : OUI — « elle sort en ville et rencontre »"
    fake_model.responses["qa.confirm"] = "OUI"
    violations, report, _ = qa.check_plan(facts, beats)
    assert violations == [(1, "Elle ne sort pas.", "elle sort en ville et rencontre")]
    assert "PLAN CONTREDIT le fait 1" in report
    assert qa.check_plan([], beats)[0] == []


def test_fact_fixture_is_the_default(fake_model, fake_chroma):
    facts, _ = qa.derive_facts(["judith"])
    assert facts[0].startswith("La femme qu'elle aimait") and fx.FACTS
