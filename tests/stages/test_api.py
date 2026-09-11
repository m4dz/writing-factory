"""The HTTP surface, served in-process with the pipeline replaced by a fake.

Covers the current (keynote) contract: idempotent ``POST /generate``, ``204``
for absent artifacts, ``409`` on chat during generation, the whitelist on
session identifiers, the traversal guard on the slides root, the SSE terminal
event. ADR-0005 replaces this surface in step 6; these tests are rewritten then.
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

FINAL = {
    "repaired": ["Samedi 14. Beau temps.\n\nUne. Deux. Trois.",
                 "Samedi 14. Beau temps.\n\n« Cit. »\n\nQuatre.\n\nConstat : anniversaire."],
    "warnings": ["w1"], "coherence": "FAIT 1 : tenu", "plan_report": "plan fourni",
}


class FakeGraph:
    def invoke(self, state, config=None):
        return dict(FINAL)


@pytest.fixture
def server(tmp_path, monkeypatch, fake_chroma):
    monkeypatch.setattr(settings, "output_dir", tmp_path / "out")
    monkeypatch.setattr(api, "preflight", lambda **k: ["avertissement machine"])
    monkeypatch.setattr(api, "report", lambda: "machine ok")
    monkeypatch.setattr(api, "build_graph", lambda: FakeGraph())
    monkeypatch.setattr(api, "unload", lambda *a, **k: True)
    monkeypatch.setattr(api, "render_chapter",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no voice")))
    slides = tmp_path / "slides"
    slides.mkdir()
    (slides / "index.html").write_text("<html>deck</html>", encoding="utf-8")
    monkeypatch.setattr(settings, "slides_dir", slides)
    monkeypatch.setattr(api, "JOB", api.Job())
    monkeypatch.setattr(api, "ROOM", api.ChatRoom())

    srv = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield srv.server_address
    srv.shutdown()
    srv.server_close()


def call(addr, method, path, body=None):
    conn = http.client.HTTPConnection(*addr, timeout=10)
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    conn.request(method, path, body=data, headers=headers)
    resp = conn.getresponse()
    payload = resp.read()
    conn.close()
    return resp.status, resp.getheader("Content-Type", ""), payload


def wait_ready(timeout=10.0):
    t0 = time.time()
    while api.JOB.status not in ("ready", "error") and time.time() - t0 < timeout:
        time.sleep(0.05)
    assert api.JOB.status == "ready", api.JOB.error


def test_generate_is_idempotent_and_artifacts_appear_on_disk(server):
    status, _, body = call(server, "GET", "/chapter")
    assert status == 204 and body == b""

    status, _, body = call(server, "POST", "/generate")
    assert status == 202 and json.loads(body)["started"] is True
    status, _, body = call(server, "POST", "/generate")
    assert status == 202 and json.loads(body)["started"] is False
    wait_ready()

    status, _, body = call(server, "GET", "/status")
    snap = json.loads(body)
    assert snap["phase"] == "ready" and snap["ready"] is True and snap["progress"] == 1.0
    assert "préflight : avertissement machine" in snap["notes"]
    assert any("lecture indisponible" in n for n in snap["notes"])

    status, ctype, body = call(server, "GET", "/chapter")
    text = body.decode()
    assert status == 200 and ctype.startswith("text/markdown")
    assert assembly.SWITCH in text and assembly.AUDIO_END in text
    assert text.split(assembly.SWITCH)[1].lstrip().startswith("Samedi 14.")
    # TTS failed: the chapter is served, the audio alone is absent (per-resource fallback).
    assert call(server, "GET", "/audio")[0] == 204
    assert api.chapter_path().exists() and not api.audio_path().exists()


def test_chat_is_refused_while_generating(server):
    api.JOB.status = "generating"
    status, _, body = call(server, "POST", "/chat", {"character": "judith", "message": "x"})
    assert status == 409 and json.loads(body)["state"] == "generating"
    api.JOB.status = "idle"


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
    status, ctype, body = call(server, "GET", "/events")
    assert status == 200 and ctype.startswith("text/event-stream")
    lines = body.decode().splitlines()
    events = [json.loads(ln[6:]) for ln in lines if ln.startswith("data: ")]
    assert len(events) == 1 and events[0]["state"] == "idle"


def test_misc_routes(server):
    status, _, body = call(server, "GET", "/health")
    assert status == 200 and json.loads(body)["machine"] == "machine ok"
    status, _, body = call(server, "GET", "/characters")
    assert [c["id"] for c in json.loads(body)["characters"]] == ["judith"]
    status, _, body = call(server, "POST", "/cancel")
    assert status == 200 and json.loads(body)["cancelled"] is False
    assert call(server, "OPTIONS", "/generate")[0] == 204
    assert call(server, "POST", "/nope")[0] == 404
