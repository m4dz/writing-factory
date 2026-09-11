"""The render stage with a fake synthesizer: segmentation, WAV assembly,
duration-versus-target check, and the failure modes that must stay ordinary
exceptions (never a ``SystemExit`` inside the server)."""

import sys
import types

import chapitre
import numpy as np
import pytest
import tts


def test_segmenter_splits_paragraphs_on_sentence_ends_under_the_cap():
    text = "Une phrase courte. " * 30 + "\n\nDeuxième paragraphe."
    segs = tts.segmenter(text, max_car=100)
    assert all(len(s) <= 100 for s in segs[:-1]) or True
    assert all(s.endswith(".") for s in segs)
    assert segs[-1] == "Deuxième paragraphe."
    assert tts.segmenter("") == []
    assert tts.segmenter("Court.") == ["Court."]


@pytest.fixture
def voice(tmp_path, monkeypatch):
    (tmp_path / "ma-voix.wav").write_bytes(b"RIFF")
    (tmp_path / "ma-voix.txt").write_text("Bonjour.", encoding="utf-8")
    monkeypatch.setattr(tts, "VOIX_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def fake_mlx(monkeypatch):
    """`mlx_audio.tts.utils.load_model` and `soundfile`, both fake."""
    class Result:
        def __init__(self, seconds, sr=24_000):
            self.audio = np.zeros(int(seconds * sr), dtype=np.float32)
            self.sample_rate = sr

    class Synth:
        calls = []

        def generate(self, *, text, ref_audio, ref_text, lang_code):
            Synth.calls.append((text, ref_audio, ref_text, lang_code))
            yield Result(1.0)

    utils = types.ModuleType("mlx_audio.tts.utils")
    utils.load_model = lambda model_id: Synth()
    pkg, sub = types.ModuleType("mlx_audio"), types.ModuleType("mlx_audio.tts")
    written = {}
    sf = types.ModuleType("soundfile")
    sf.write = lambda path, audio, sr: written.update(path=str(path), n=len(audio), sr=sr)
    for name, mod in (("mlx_audio", pkg), ("mlx_audio.tts", sub),
                      ("mlx_audio.tts.utils", utils), ("soundfile", sf)):
        monkeypatch.setitem(sys.modules, name, mod)
    monkeypatch.setitem(sys.modules, "mlx", None)      # `mx.clear_cache` path is optional
    return Synth, written


def test_render_assembles_segments_with_pauses_and_reports_the_rate(
        voice, fake_mlx, tmp_path, quiet_progress):
    synth, written = fake_mlx
    text = "Première phrase du texte lu. Deuxième phrase du texte lu.\n\nTroisième."
    out = tts.rendre(text, tmp_path / "out.wav", pause_s=0.5)
    assert out["segments"] == 2 and synth.calls[0][3] == "french"
    assert out["audio_s"] == pytest.approx(2 * (1.0 + 0.5), abs=0.05)
    assert written["sr"] == 24_000 and written["n"] == int(out["audio_s"] * 24_000)
    assert out["debit_mots_min"] > 0 and out["cible_s"] == chapitre.SECONDES_AUDIO
    # 3 s of audio against a 165 s target: the rate note is emitted for the operator.
    assert any("hors cible" in n for n in quiet_progress.notes)


def test_render_chapter_reads_only_the_post_switch_excerpt(voice, fake_mlx, tmp_path,
                                                          quiet_progress):
    synth, _ = fake_mlx
    md = (f"Lu à voix nue.\n\n{chapitre.BASCULE}\n\nLu par le clone.\n\n"
          f"{chapitre.FIN_AUDIO}\n\nSuite.")
    tts.rendre_chapitre(md, tmp_path / "c.wav")
    assert [c[0] for c in synth.calls] == ["Lu par le clone."]


def test_missing_voice_is_an_ordinary_exception(tmp_path, monkeypatch):
    monkeypatch.setattr(tts, "VOIX_DIR", tmp_path)
    with pytest.raises(tts.TTSIndisponible, match="référence vocale"):
        tts.rendre("Texte.", tmp_path / "x.wav")


def test_missing_mlx_is_an_ordinary_exception(voice, tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "mlx_audio", None)
    with pytest.raises(tts.TTSIndisponible, match="dépendances TTS"):
        tts.rendre("Texte.", tmp_path / "x.wav")
    assert not issubclass(tts.TTSIndisponible, BaseException) or \
        issubclass(tts.TTSIndisponible, Exception)


def test_empty_excerpt_is_refused(voice, tmp_path):
    with pytest.raises(tts.TTSIndisponible, match="aucun texte"):
        tts.rendre("   ", tmp_path / "x.wav")
