from factory.infra import notify
from factory.settings import settings


def test_sanitiser_strips_quotes_and_bounds_length():
    assert notify._sanitize("PLAN REFUSÉ — contredit « Romane est partie il y a un an »") == \
        "PLAN REFUSÉ — contredit […]"
    assert notify._sanitize('fin coupée — "la lampe du couloir restée allumée"') == \
        "fin coupée — […]"
    assert len(notify._sanitize("x" * 500)) == 200
    assert notify._sanitize("a  b\n c") == "a b c"


def test_nothing_leaves_when_inactive(monkeypatch):
    monkeypatch.setattr(settings, "telegram_token", "")
    monkeypatch.setattr(settings, "telegram_chat_id", "")
    monkeypatch.setattr(notify, "_post", lambda text: (_ for _ in ()).throw(AssertionError))
    notify.startup()
    notify.failure("X", "raison « citée »")
    assert not notify.active()


def test_rate_limit_and_priority(monkeypatch):
    sent = []
    monkeypatch.setattr(settings, "telegram_token", "t")
    monkeypatch.setattr(settings, "telegram_chat_id", "c")
    monkeypatch.setattr(notify, "_last_sent", 0.0)
    monkeypatch.setattr(notify, "_post", sent.append)

    class Sync:
        def __init__(self, target, args, daemon):
            self.t, self.a = target, args

        def start(self):
            self.t(*self.a)

    monkeypatch.setattr(notify.threading, "Thread", Sync)
    notify.advancement("Écriture", 0.2, 120)
    notify.advancement("Écriture", 0.3, 180)       # within the period: dropped
    notify.ready(600, 2, 165.0)                     # priority: passes
    assert len(sent) == 2 and sent[0].startswith("⏳ 20 %") and sent[1].startswith("✅")
