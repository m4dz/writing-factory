import notify


def test_sanitiser_strips_quotes_and_bounds_length():
    assert notify._assainir("PLAN REFUSÉ — contredit « Romane est partie il y a un an »") == \
        "PLAN REFUSÉ — contredit […]"
    assert notify._assainir('fin coupée — "la lampe du couloir restée allumée"') == \
        "fin coupée — […]"
    assert len(notify._assainir("x" * 500)) == 200
    assert notify._assainir("a  b\n c") == "a b c"


def test_nothing_leaves_when_inactive(monkeypatch):
    monkeypatch.setattr(notify, "TOKEN", "")
    monkeypatch.setattr(notify, "CHAT_ID", "")
    monkeypatch.setattr(notify, "_poster", lambda texte: (_ for _ in ()).throw(AssertionError))
    notify.demarrage()
    notify.echec("X", "raison « citée »")
    assert not notify.actif()


def test_rate_limit_and_priority(monkeypatch):
    sent = []
    monkeypatch.setattr(notify, "TOKEN", "t")
    monkeypatch.setattr(notify, "CHAT_ID", "c")
    monkeypatch.setattr(notify, "_dernier_envoi", 0.0)
    monkeypatch.setattr(notify, "_poster", sent.append)

    class Sync:
        def __init__(self, target, args, daemon):
            self.t, self.a = target, args

        def start(self):
            self.t(*self.a)

    monkeypatch.setattr(notify.threading, "Thread", Sync)
    notify.avancement("Écriture", 0.2, 120)
    notify.avancement("Écriture", 0.3, 180)       # within the period: dropped
    notify.pret(600, 2, 165.0)                     # priority: passes
    assert len(sent) == 2 and sent[0].startswith("⏳ 20 %") and sent[1].startswith("✅")
