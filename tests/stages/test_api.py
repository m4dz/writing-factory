"""The HTTP surface of ADR-0005, served in-process: the graph runs against the
fake model with the machine probes and the voice replaced, runs land in a
temporary registry.

Covers: mandatory payload, `202 {run_id}`, one worker with a queue, per-run
status / events / chapter / audio / prompts, `204` before artifacts exist,
`404` for an unknown run, `410` for the keynote's singleton routes, `409` for
chat during generation, the whitelist for session and run identifiers, the
traversal guard at the slides root.
"""

import http.client
import json
import threading
import time
from http.server import ThreadingHTTPServer

import pytest

from factory.api import server as api
from factory.pipeline import assembly
from factory.settings import settings


@pytest.fixture
def server(tmp_path, monkeypatch, fake_chroma, fake_model):
    from factory.pipeline.nodes import preflight as preflight_node
    from factory.pipeline.nodes import render as render_node

    monkeypatch.setattr(settings, "runs_dir", tmp_path / "runs")
    monkeypatch.setattr(settings, "generated_dir", tmp_path / "generated")
    monkeypatch.setattr(preflight_node, "preflight", lambda **k: ["avertissement machine"])
    monkeypatch.setattr(api, "report", lambda: "machine ok")
    monkeypatch.setattr(render_node, "render_chapter",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no voice")))
    slides = tmp_path / "slides"
    slides.mkdir()
    (slides / "index.html").write_text("<html>deck</html>", encoding="utf-8")
    monkeypatch.setattr(settings, "slides_dir", slides)
    monkeypatch.setattr(api, "WORKER", api.Worker())
    monkeypatch.setattr(api, "ROOM", api.ChatRoom())

    srv = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv.server_address
    srv.shutdown()
    srv.server_close()


def call(addr, method, path, body=None, raw=None):
    conn = http.client.HTTPConnection(*addr, timeout=10)
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    headers = {"Content-Type": "application/json"} if data else {}
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    payload = resp.read()
    conn.close()
    return resp.status, resp.getheader("Content-Type", ""), payload


def wait_terminal(addr, run_id, timeout=90.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        status, _, body = call(addr, "GET", f"/runs/{run_id}/status")
        snap = json.loads(body)
        if snap["state"] in ("ready", "error", "cancelled"):
            return snap
        time.sleep(0.05)
    raise AssertionError(f"run {run_id} still {snap}")


def test_generate_requires_a_payload_naming_a_chapter(server):
    status, _, body = call(server, "POST", "/generate")
    assert status == 400 and "charge utile" in json.loads(body)["error"]
    assert json.loads(body)["chapters"] == [2, 7]
    status, _, body = call(server, "POST", "/generate", {"chapter": 3})
    assert status == 400 and "chapitre 3" in json.loads(body)["error"]
    status, _, body = call(server, "POST", "/generate", {"chapter": 7, "seed": "x"})
    assert status == 400
    status, _, body = call(server, "POST", "/generate",
                           {"chapter": 7, "overrides": {"bible_dir": "/"}})
    assert status == 400 and "override refusé" in json.loads(body)["error"]


def test_a_run_goes_through_the_graph_and_its_artifacts_appear(server):
    status, _, body = call(server, "POST", "/generate", {"chapter": 7, "seed": 424242})
    assert status == 202
    accepted = json.loads(body)
    run_id = accepted["run_id"]
    assert accepted["seed"] == 424242 and accepted["position"] == 0
    assert run_id.endswith("-ch07-anniversaire")
    assert call(server, "GET", f"/runs/{run_id}/chapter")[0] in (204, 200)

    snap = wait_terminal(server, run_id)
    assert snap["state"] == "ready" and snap["phase"] == "ready" and snap["ready"] is True
    assert snap["progress"] == 1.0 and snap["chapter"] == 7 and snap["seed"] == 424242

    status, ctype, body = call(server, "GET", f"/runs/{run_id}/chapter")
    text = body.decode()
    assert status == 200 and ctype.startswith("text/markdown")
    assert assembly.SWITCH in text and assembly.AUDIO_END in text
    assert text.split(assembly.SWITCH)[1].lstrip().startswith("Samedi 14.")
    # TTS failed: the chapter is served, the audio alone is absent (per-resource fallback).
    assert call(server, "GET", f"/runs/{run_id}/audio")[0] == 204
    status, _, body = call(server, "GET", f"/runs/{run_id}/prompts")
    assert status == 200 and b"## appel 1" in body and b"### system" in body
    status, _, body = call(server, "GET", f"/runs/{run_id}/manifest")
    assert status == 200 and b"status: ready" in body and b"commit:" in body

    # /runs/latest aliases the newest run; the listing knows its state.
    status, _, body = call(server, "GET", "/runs/latest/status")
    assert status == 200 and json.loads(body)["run_id"] == run_id
    status, _, body = call(server, "GET", "/runs")
    assert [r["run_id"] for r in json.loads(body)["runs"]] == [run_id]
    # The narrative state of chapter 7 was generated and indexed for the run.
    assert (settings.generated_dir / "narrative-state" / "ch-07.md").is_file()
    # The manifest keeps the record: preflight warnings, no audio, the run's timings.
    manifest = (settings.runs_dir / run_id / "manifest.yaml").read_text(encoding="utf-8")
    assert "avertissement machine" in manifest and "audio: null" in manifest
    assert "wall_s:" in manifest and "collections:" in manifest


def test_a_second_post_is_queued_not_refused(server, monkeypatch):
    from factory.pipeline.nodes import preflight as preflight_node

    # Hold the first run in its preflight so the queue can be observed.
    gate = threading.Event()
    monkeypatch.setattr(preflight_node, "preflight", lambda **k: gate.wait(30) and [])
    status, _, body = call(server, "POST", "/generate", {"chapter": 7})
    first = json.loads(body)["run_id"]
    status, _, body = call(server, "POST", "/generate", {"chapter": 2, "seed": 1})
    second = json.loads(body)
    assert status == 202 and second["state"] == "queued" and second["position"] == 1
    status, _, body = call(server, "GET", f"/runs/{second['run_id']}/status")
    assert json.loads(body)["state"] == "queued"
    status, _, body = call(server, "GET", f"/runs/{first}/status")
    assert json.loads(body)["state"] == "generating"
    # Chat is refused while the worker generates.
    status, _, body = call(server, "POST", "/chat", {"character": "judith", "message": "x"})
    assert status == 409 and json.loads(body)["state"] == "generating"
    # Cancelling a queued run removes it without touching the running one.
    status, _, body = call(server, "POST", f"/runs/{second['run_id']}/cancel")
    assert status == 200 and json.loads(body)["cancelled"] is True
    assert wait_terminal(server, second["run_id"])["state"] == "cancelled"
    gate.set()
    assert wait_terminal(server, first)["state"] == "ready"
    status, _, body = call(server, "GET", "/runs")
    assert [r["state"] for r in json.loads(body)["runs"]] == ["cancelled", "ready"]


def test_unknown_and_invalid_run_ids(server):
    assert call(server, "GET", "/runs/20260912-000000-ch07-nope/status")[0] == 404
    assert call(server, "GET", "/runs/../etc/status")[0] == 400
    assert call(server, "GET", "/runs/latest/status")[0] == 404
    assert call(server, "POST", "/runs/20260912-000000-ch07-nope/cancel")[0] == 404


def test_keynote_routes_are_gone_with_a_pointer(server):
    for route in ("/status", "/events", "/chapter", "/audio"):
        status, _, body = call(server, "GET", route)
        assert status == 410 and "/runs/" in json.loads(body)["detail"]
    assert call(server, "POST", "/cancel")[0] == 410


def test_chat_validates_input_and_unknown_character_is_404(server, fake_model):
    assert call(server, "POST", "/chat", {"character": "judith"})[0] == 400
    assert call(server, "POST", "/chat", {"character": "inconnu", "message": "x"})[0] == 404


def test_chat_turn_then_close(server, fake_model, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "sessions_dir", tmp_path / "sessions")
    status, _, body = call(server, "POST", "/chat", {"character": "judith", "message": "Bonsoir"})
    assert status == 200
    reply = json.loads(body)
    assert reply["reply"].startswith("— Je corrige") and reply["turns"] == 1
    call(server, "POST", "/chat", {"character": "judith", "message": "Encore",
                                   "session": reply["session"]})
    status, _, body = call(server, "POST", "/chat", {"session": reply["session"], "close": True})
    assert status == 200 and json.loads(body)["closed"] is True
    assert json.loads(body)["fichier"].endswith(".md")


@pytest.mark.parametrize("path", [
    "/session/../x", "/session/..%2f..%2fetc/passwd", "/session/%2e%2e/x",
    "/session/judith/../../etc", "/session/Judith/2026",
])
def test_session_identifiers_are_whitelisted(server, path):
    assert call(server, "GET", path)[0] == 400


def test_unknown_session_is_404_and_listing_works(server, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "sessions_dir", tmp_path / "none")
    assert call(server, "GET", "/session/judith/2026-01-01T00-00-00Z")[0] == 404
    status, _, body = call(server, "GET", "/sessions?character=judith")
    assert status == 200 and json.loads(body) == {"sessions": []}


def test_slides_root_refuses_traversal_and_falls_back_to_index(server):
    assert call(server, "GET", "/assets/../../etc/passwd")[0] == 403
    status, ctype, body = call(server, "GET", "/2")
    assert status == 200 and ctype.startswith("text/html") and b"deck" in body


def test_events_stream_ends_on_a_terminal_state(server):
    status, _, body = call(server, "POST", "/generate", {"chapter": 7, "seed": 7})
    run_id = json.loads(body)["run_id"]
    wait_terminal(server, run_id)
    status, ctype, body = call(server, "GET", f"/runs/{run_id}/events")
    assert status == 200 and ctype.startswith("text/event-stream")
    events = [json.loads(ln[6:]) for ln in body.decode().splitlines() if ln.startswith("data: ")]
    assert len(events) == 1 and events[0]["state"] == "ready" and events[0]["run_id"] == run_id


def test_misc_routes(server):
    status, _, body = call(server, "GET", "/health")
    health = json.loads(body)
    assert status == 200 and health["machine"] == "machine ok" and health["chapters"] == [2, 7]
    status, _, body = call(server, "GET", "/characters")
    assert [c["id"] for c in json.loads(body)["characters"]] == ["judith"]
    assert call(server, "OPTIONS", "/generate")[0] == 204
    assert call(server, "POST", "/nope")[0] == 404
