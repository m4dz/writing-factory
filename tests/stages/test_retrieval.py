from factory.retrieval import context as retrieval


def test_system_prompt_without_rag_is_style_and_rules_only(fake_chroma):
    prompt = retrieval.assemble_system_prompt(characters=["judith"], scene_brief="x", rag=False)
    assert prompt.startswith(retrieval.PREAMBLE)
    assert "=== CONTRAT DE STYLE" in prompt and "## Narration" in prompt
    assert "=== RÈGLE DU RÉCIT ===" in prompt and retrieval.EPISTEMIC_LINE in prompt
    assert "NARRATRICE" not in prompt
    assert retrieval.routing() == []


def test_system_prompt_with_rag_serves_the_writing_chunks_by_id(fake_chroma):
    prompt = retrieval.assemble_system_prompt(characters=["judith"], scene_brief="x", rag=True,
                                              include_scenes=False)
    assert "=== NARRATRICE : judith ===" in prompt
    assert "[la narratrice / Voix]" in prompt
    assert "[la narratrice / État narratif courant]" in prompt
    assert "[la narratrice / Histoire]" not in prompt          # world chunk, not a writing chunk
    assert "Judith" not in prompt                              # translated at index time
    assert retrieval.routing() == ["auteur"]


def test_planner_and_reviewer_get_their_own_sections(fake_chroma):
    plan = retrieval.assemble_system_prompt(characters=["judith"], scene_brief="x", rag=True,
                                            style=(), include_scenes=False)
    assert "CONTRAT DE STYLE" not in plan
    review = retrieval.assemble_system_prompt(characters=["judith"], scene_brief="x", rag=True,
                                              style=retrieval.REVIEW_STYLE,
                                              include_scenes=False, epistemic=False)
    assert "## Phrase et rythme" in review and "RÈGLE DU RÉCIT" not in review


def test_examples_are_stripped_from_served_style_sections():
    section = ("- Règle prescriptive.\n**Écrire :** un exemple à ne pas montrer.\n"
               "**Ne pas écrire :** perplexe, je repose le cahier.\n- Autre règle.")
    served = retrieval._without_examples(section)
    assert "Règle prescriptive" in served and "Autre règle" in served
    assert "exemple à ne pas montrer" not in served and "perplexe" not in served
    served = retrieval.style_sections(retrieval.WRITING_STYLE)
    assert "**Écrire" not in served and "**Ne pas écrire" not in served


def test_world_and_acting_contexts(fake_chroma):
    world = retrieval.world_context("judith")
    assert "[la narratrice / Psychologie]" in world and "[la narratrice / Relations]" in world
    acting = retrieval.acting_context("judith")
    assert "[la narratrice / Comportement]" in acting and "[la narratrice / Voix]" in acting
    assert retrieval.character_context("personne") == ""


def test_character_listing_reads_metadata(fake_chroma):
    assert retrieval.list_characters() == [{"id": "judith", "rank": "", "nom": "Judith"}]
