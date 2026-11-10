"""Sampling knobs of the writing calls: configuration, run overrides, the request sent."""

import json
from dataclasses import replace

import pytest

from factory import runs
from factory.infra import ollama
from factory.pipeline import graph
from factory.settings import Settings


def test_optional_knobs_are_listed_only_when_set():
    s = Settings()
    assert s.sampling_options() == {}
    s = replace(s, min_p=0.05, repeat_penalty=1.1)
    assert s.sampling_options() == {"min_p": 0.05, "repeat_penalty": 1.1}
    s = Settings.from_env({"MIN_P": "0.1", "TOP_P": "0.9", "WRITE_TEMPERATURE": "0.9"})
    assert s.sampling_options() == {"min_p": 0.1, "top_p": 0.9} and s.write_temperature == 0.9


@pytest.fixture
def sent(monkeypatch):
    """The JSON body of the last request the real client sent."""
    body = {}

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
        body.clear()
        body.update(json.loads(req.data))
        return _Resp()

    monkeypatch.setattr(ollama.urllib.request, "urlopen", fake_urlopen)
    return body


def test_default_request_is_unchanged_even_with_knobs_set(sent):
    # The client never injects the knobs itself: a call that does not pass
    # them (plan, review, QA, gestures) keeps today's options.
    client = ollama.OllamaClient(replace(Settings(), min_p=0.05, top_p=0.9))
    client.chat("S", "U", temperature=0.5, num_predict=10)
    assert sent["options"] == {"temperature": 0.5, "num_predict": 10, "num_ctx": 8192}


def test_options_passed_are_sent_and_recorded(sent):
    client = ollama.OllamaClient(Settings())
    client.recording = []
    client.chat("S", "U", temperature=0.7, num_predict=10, options={"min_p": 0.05})
    assert sent["options"] == {"temperature": 0.7, "num_predict": 10, "num_ctx": 8192,
                               "min_p": 0.05}
    client.chat_continue("S", "U", "Début", temperature=0.7, num_predict=10,
                         options={"top_p": 0.9})
    assert sent["options"]["top_p"] == 0.9
    assert [c.get("options") for c in client.recording] == [{"min_p": 0.05}, {"top_p": 0.9}]
    assert "min_p=0.05" in runs.render_prompts(client.recording)


def test_knobs_are_run_overrides():
    out = runs.validate_overrides({"write_temperature": "0.9", "min_p": "0.05", "top_p": None})
    assert out == {"write_temperature": 0.9, "min_p": 0.05, "top_p": None}
    with pytest.raises(runs.RunError, match="valeur invalide"):
        runs.validate_overrides({"min_p": "bas"})
    conf = runs.resolved_config()
    assert {"write_temperature", "min_p", "top_p", "repeat_penalty"} <= conf.keys()


def test_write_calls_read_the_configured_sampling(fake_model, fake_chroma, quiet_progress,
                                                  monkeypatch):
    from factory.chapter_spec import load_chapter
    from factory.settings import settings

    monkeypatch.setattr(settings, "write_temperature", 0.93)
    monkeypatch.setattr(settings, "min_p", 0.05)
    monkeypatch.setattr(ollama.client, "recording", [])
    spec = load_chapter(7)
    state = {**spec.state(seed=1), "plan": list(spec.imposed_plan), "idx": 1,
             "scenes": [""], "metrics": [], "warnings": []}
    graph.write_node(state)
    beats = fake_model.by_role("write.beat")
    assert beats and {c.temperature for c in beats} == {0.93}
    assert ollama.client.recording
    assert all(c.get("options") == {"min_p": 0.05} for c in ollama.client.recording)
