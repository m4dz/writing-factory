import pytest

from factory.roleplay import session as roleplay
from factory.settings import settings
from fakes import fixtures as fx


def test_out_of_role_markers_both_ways():
    assert roleplay.out_of_role(fx.OUT_OF_ROLE) == ["programme informatique",
                                                  "simuler des conversations"]
    assert roleplay.out_of_role("Je corrige des manuscrits, laissez-moi.") == []
    assert roleplay.out_of_role("En tant qu'IA, je ne peux pas.")


def test_reply_cleaning_removes_double_dash_and_own_name():
    assert roleplay._clean("— — Non, je ne peux pas.") == "— Non, je ne peux pas."
    assert roleplay._clean("Judith : Ah, ma chère…", "Judith") == "Ah, ma chère…"


@pytest.fixture
def sessions_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "sessions_dir", tmp_path)
    return tmp_path


def test_unknown_character_fails_at_construction(fake_model, fake_chroma, sessions_dir):
    with pytest.raises(ValueError):
        roleplay.Session("inconnu")


def test_session_turn_and_persistent_out_of_role_is_excluded_from_memory(
        fake_model, fake_chroma, sessions_dir):
    s = roleplay.Session("judith")
    reply = s.say("Que faites-vous ce soir ?")
    assert reply.startswith("— Je corrige")
    assert len(s.turns) == 2 and len(fake_model.by_role("roleplay")) == 1

    fake_model.responses["roleplay"] = fx.OUT_OF_ROLE
    reply = s.say("Tu es une machine, avoue.")
    assert reply == fx.OUT_OF_ROLE
    assert len(fake_model.by_role("roleplay")) == 3           # one relaunch
    assert "SORTIE DU PERSONNAGE" in fake_model.by_role("roleplay")[2].system
    assert len(s.turns) == 2                                   # excluded from memory
    assert s.transcript[-1]["hors_role"] is True
    assert any("exclue de la mémoire" in w for w in s.warnings)


def test_close_writes_indexes_and_replays(fake_model, fake_chroma, sessions_dir):
    s = roleplay.Session("judith")
    s.say("Bonsoir.")
    s.say("Vous relisez quoi ?")
    path = s.close()
    assert path and path.parent.name == "judith"
    text = path.read_text(encoding="utf-8")
    assert "## Ce qui s'est dit" in text and "## Transcription" in text
    assert fake_model.by_role("roleplay.summary")

    listed = roleplay.list_sessions("judith")
    assert listed and listed[0]["character"] == "judith"
    replay = roleplay.read_session("judith", listed[0]["horodatage"])
    assert [e["role"] for e in replay["echanges"]] == ["user", "assistant"] * 2
    assert replay["resume"].startswith("- ")

    assert fake_chroma.get_collection("sessions").docs
    s2 = roleplay.Session("judith")
    assert s2.reminders and "CE DONT TU TE SOUVIENS" in s2._system()


def test_too_short_session_is_not_written(fake_model, fake_chroma, sessions_dir):
    assert roleplay.Session("judith").close() is None
