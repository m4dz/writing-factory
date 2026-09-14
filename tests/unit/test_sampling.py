"""Sampling knobs (ADR-0026): configuration, run overrides, the request sent."""

import json
from dataclasses import replace

import pytest

from factory import runs
from factory.infra import ollama
from factory.pipeline import graph
from factory.settings import Settings


def test_optional_knobs_are_sent_only_when_set():
    s = Settings()
    assert s.sampling_options() == {}
    s = replace(s, min_p=0.05, repeat_penalty=1.1)
    assert s.sampling_options() == {"min_p": 0.05, "repeat_penalty": 1.1}
    s = Settings.from_env({"MIN_P": "0.1", "TOP_P": "0.9", "WRITE_TEMPERATURE": "0.9"})
    assert s.sampling_options() == {"min_p": 0.1, "top_p": 0.9} and s.write_temperature == 0.9


def test_request_payload_carries_the_knobs(monkeypatch):
    sent = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"message": {"content": "Ligne."}, "eval_count": 1,
                               "eval_duration": 1, "prompt_eval_count": 1,
                               "prompt_eval_duration": 1, "done_reason": "stop"}).encode()

    def fake_urlopen(req, timeout=0):
        sent.update(json.loads(req.data))
        return _Resp()

    monkeypatch.setattr(ollama.urllib.request, "urlopen", fake_urlopen)
    client = ollama.OllamaClient(Settings())
    client.chat("S", "U", temperature=0.7, num_predict=10)
    assert sent["options"] == {"temperature": 0.7, "num_predict": 10, "num_ctx": 8192}
    client = ollama.OllamaClient(replace(Settings(), min_p=0.05, top_p=0.9))
    client.chat("S", "U", temperature=0.7, num_predict=10)
    assert sent["options"] == {"temperature": 0.7, "num_predict": 10, "num_ctx": 8192,
                               "min_p": 0.05, "top_p": 0.9}


def test_knobs_are_run_overrides():
    out = runs.validate_overrides({"write_temperature": "0.9", "min_p": "0.05", "top_p": None})
    assert out == {"write_temperature": 0.9, "min_p": 0.05, "top_p": None}
    with pytest.raises(runs.RunError, match="valeur invalide"):
        runs.validate_overrides({"min_p": "bas"})
    assert "write_temperature" in runs.resolved_config()


def test_write_calls_read_the_configured_temperature(fake_model, fake_chroma, quiet_progress,
                                                     monkeypatch):
    from factory.chapter_spec import load_chapter
    from factory.settings import settings

    monkeypatch.setattr(settings, "write_temperature", 0.93)
    spec = load_chapter(7)
    state = {**spec.state(seed=1), "plan": list(spec.imposed_plan), "idx": 1,
             "scenes": [""], "metrics": [], "warnings": []}
    graph.write_node(state)
    beats = fake_model.by_role("write.beat")
    assert beats and {c.temperature for c in beats} == {0.93}
