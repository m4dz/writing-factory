#!/usr/bin/env python3
"""Progress notifications to a phone (Telegram), OFF BY DEFAULT (ADR-0015).

The one exception to the golden rule, and its exact limit. The project bans
every cloud API; this module is the OPERATOR'S BEEPER, not a link of the
factory. It says, from the stage, that a generation failed and plan B is due.
Its value is being OUT OF BAND: it goes through the cellular network, so it
survives the conference WiFi dropping, the very case it must signal.

What leaves the machine is strictly bounded:

    phase, percentage, durations, counters, error class.

What NEVER leaves: the chapter text, a bible excerpt, a character's line, a
prompt. Not a discipline but a mechanism: messages are composed from
STRUCTURED FIELDS, never free text, and a second filter strips what sits
between quotation marks before sending. Our own progress notes quote the bible
(« PLAN REFUSÉ — contredit … ») and the chapter (« fin coupée — … »); relaying
them verbatim would have exported the work.

Without `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, every call is a silent no-op.
"""

import json
import re
import threading
import time
import urllib.error
import urllib.request

from factory.settings import settings

# Token, chat, timeout and minimum period between two progress messages (at
# the wrist, a burst of notifications is worse than none): `settings.telegram_*`.

# Anything quoted is quoted because it comes from the model or the bible.
_QUOTATIONS = re.compile(r"[«\"“][^»\"”]*[»\"”]")
_MAX_LENGTH = 200

_last_sent = 0.0
_lock = threading.Lock()


def active() -> bool:
    return bool(settings.telegram_token and settings.telegram_chat_id)


def _sanitize(text: str) -> str:
    """Strip quotations and bound the length: the second curtain.

    The first curtain is composing messages from structured fields only;
    this one covers the case where an unexpected exception carries content
    in its message.
    """
    without_quotation = _QUOTATIONS.sub("[…]", text)
    without_quotation = " ".join(without_quotation.split())
    return without_quotation[:_MAX_LENGTH]


def _post(text: str) -> None:
    """The real send, in the background. Never fails towards the caller."""
    payload_dict = json.dumps({
        "chat_id": settings.telegram_chat_id, "text": text, "disable_notification": False,
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
        data=payload_dict, headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=settings.telegram_timeout_s).read()
    except (urllib.error.URLError, OSError, ValueError):
        # A falling beeper must never take the generation down: it is an
        # operator comfort, not a pipeline dependency.
        pass


def _send(text: str, *, priority: bool = False) -> None:
    """Post a message, unless the rate is already reached (priority excepted).

    The send runs in a THREAD: a generation must not wait five seconds of
    network timeout because an operator wants to be warned.
    """
    global _last_sent
    if not active():
        return
    with _lock:
        now = time.time()
        if not priority and now - _last_sent < settings.telegram_period_s:
            return
        _last_sent = now
    threading.Thread(target=_post, args=(_sanitize(text),),
                     daemon=True).start()


# --- Events: the only permitted call surface ---------------------------------
#
# Each function composes its message from typed fields. There is deliberately
# NO generic `notify.text(...)`: it would be the door through which content
# ends up leaving (ADR-0015).

def startup(planned_scenes: str = "") -> None:
    _send(f"▶️ Génération lancée{f' ({planned_scenes})' if planned_scenes else ''}",
             priority=True)


def advancement(label: str, percent: float, elapsed_s: int) -> None:
    """Progress beat. `label` comes from our PHASES, not from the model."""
    _send(f"⏳ {int(percent * 100)} % — {label} — {elapsed_s // 60} min écoulées")


def alert(code: str) -> None:
    """Notable event. `code` is a SHORT, fixed label, not a quotation."""
    _send(f"⚠️ {code}", priority=True)


def ready(duration_s: int, scenes: int, audio_s: float | None) -> None:
    audio = f", audio {audio_s / 60:.1f} min" if audio_s else ", sans audio"
    _send(f"✅ Chapitre prêt en {duration_s // 60} min {duration_s % 60} s "
             f"({scenes} scènes{audio})", priority=True)


def failure(kind: str, reason: str) -> None:
    """Failure. `reason` goes through the sanitizer: it may come from elsewhere."""
    _send(f"❌ ÉCHEC ({kind}) — {reason} — PLAN B", priority=True)


def cancelled() -> None:
    _send("⏹️ Génération annulée par l'opérateur", priority=True)
