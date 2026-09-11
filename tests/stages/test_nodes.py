"""The two machine nodes of the graph: preflight opens it, render closes it.

Both are driven by state fields and skip when not asked, so the snapshot
scenarios never probe the machine. The probes and the voice are replaced.
"""

import pytest

from factory.infra.preflight import PreflightError
from factory.pipeline import assembly
from factory.pipeline.nodes import preflight as pf
from factory.pipeline.nodes import render as rd
from factory.settings import settings

SCENES = ["Samedi 14. Beau temps.\n\nUne. Deux. Trois.",
          "Samedi 14. Beau temps.\n\n« Cit. »\n\nQuatre.\n\nConstat : anniversaire."]


def test_preflight_node_skips_unless_asked(monkeypatch):
    monkeypatch.setattr(pf, "preflight", lambda **k: pytest.fail("probed"))
    assert pf.preflight_node({}) == {}
    assert pf.preflight_node({"preflight": False}) == {}


def test_preflight_node_runs_the_requested_mode_and_notes_warnings(monkeypatch, quiet_progress):
    seen = {}
    monkeypatch.setattr(pf, "preflight", lambda **k: seen.update(k) or ["swap tiède"])
    out = pf.preflight_node({"preflight": True})
    assert seen == {"strict": True, "timer": True}
    assert out == {"preflight_warnings": ["swap tiède"]}
    assert "préflight : swap tiède" in quiet_progress.notes
    pf.preflight_node({"preflight": {"strict": False, "timer": False}})
    assert seen == {"strict": False, "timer": False}


def test_preflight_refusal_propagates(monkeypatch, quiet_progress):
    def refuse(**k):
        raise PreflightError("Disque : 5 GB")
    monkeypatch.setattr(pf, "preflight", refuse)
    with pytest.raises(PreflightError, match="Disque"):
        pf.preflight_node({"preflight": True})


def test_render_node_always_assembles_and_writes_nothing_unless_asked(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "output_dir", tmp_path / "out")
    monkeypatch.setattr(rd, "render_chapter", lambda *a, **k: pytest.fail("rendered"))
    out = rd.render_node({"repaired": SCENES, "assembly": {"on_second_header": True}})
    assert out == {"chapter_md": assembly.assemble(SCENES, on_second_header=True)}
    assert assembly.SWITCH in out["chapter_md"] and assembly.AUDIO_END in out["chapter_md"]
    assert not (tmp_path / "out").exists()


def test_render_node_writes_the_chapter_and_keeps_it_when_the_voice_fails(
        tmp_path, monkeypatch, quiet_progress, fake_model):
    monkeypatch.setattr(settings, "output_dir", tmp_path / "out")
    monkeypatch.setattr(rd, "render_chapter",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no voice")))
    out = rd.render_node({"repaired": SCENES, "render": True})
    assert out["audio"] is None
    assert rd.chapter_path().read_text(encoding="utf-8") == out["chapter_md"]
    assert not rd.audio_path().exists()
    assert any("lecture indisponible" in n for n in quiet_progress.notes)
    assert quiet_progress.current_phase == "Restitution"


def test_render_node_returns_the_voice_metrics(tmp_path, monkeypatch, quiet_progress, fake_model):
    monkeypatch.setattr(settings, "output_dir", tmp_path / "out")
    calls = []
    def fake_render(markdown, output, **k):
        calls.append((markdown, output))
        output.write_bytes(b"RIFF")
        return {"audio_s": 165.0, "calcul_s": 100.0, "facteur_temps_reel": 1.65}
    monkeypatch.setattr(rd, "render_chapter", fake_render)
    out = rd.render_node({"scenes": SCENES, "render": True})
    assert out["audio"]["audio_s"] == 165.0
    assert calls == [(out["chapter_md"], rd.audio_path())]
    assert rd.audio_path().exists()
    assert any("lecture prête" in n for n in quiet_progress.notes)
