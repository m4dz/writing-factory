#!/usr/bin/env python3
"""Notifications de progression vers un téléphone (Telegram), COUPÉES PAR DÉFAUT.

## L'exception à la règle d'or, et sa limite exacte

Le projet interdit toute API cloud : « la fabrique reste à notre main ». Ce
module est la seule exception, et elle est assumée pour une raison précise —
c'est le BIPEUR DE L'OPÉRATEUR, pas un maillon de la fabrique. Il sert à savoir,
depuis la scène, qu'une génération a échoué et qu'il faut basculer sur le plan B.
Son intérêt tient justement à ce qu'il est HORS BANDE : il passe par le réseau
cellulaire, donc il survit à la panne du wifi de la conférence — c'est-à-dire au
cas même qu'il doit signaler.

Ce qui sort de la machine est strictement borné :

    phase, pourcentage, durées, compteurs, classe d'erreur.

Ce qui ne sort JAMAIS : le texte du chapitre, un extrait de la bible, une
réplique de personnage, un prompt. Ce n'est pas une discipline, c'est une
mécanique — les messages sont composés à partir de CHAMPS STRUCTURÉS, jamais de
texte libre, et un second filtre retire ce qui est entre guillemets avant
l'envoi. Nos propres notes de progression citent la bible (« PLAN REFUSÉ —
contredit « … » ») et le chapitre (« fin coupée — « … » ») : les relayer
verbatim aurait exporté l'œuvre.

Sans `TELEGRAM_BOT_TOKEN` ni `TELEGRAM_CHAT_ID`, tout appel est un no-op silencieux.
"""

import json
import re
import threading
import time
import urllib.error
import urllib.request

from factory.settings import settings

# Jeton, chat, délai et période minimale entre deux messages d'avancement
# (sur une montre, une rafale de notifications est pire que pas de
# notification du tout) : `settings.telegram_*`.

# Tout ce qui est cité l'est parce que ça vient du modèle ou de la bible.
_QUOTATIONS = re.compile(r"[«\"“][^»\"”]*[»\"”]")
_MAX_LENGTH = 200

_last_sent = 0.0
_lock = threading.Lock()


def active() -> bool:
    return bool(settings.telegram_token and settings.telegram_chat_id)


def _sanitize(text: str) -> str:
    """Retire les citations et borne la longueur — second rideau.

    Le premier rideau est de ne composer les messages qu'à partir de champs
    structurés ; celui-ci protège le cas où une exception inattendue porterait
    du contenu dans son message.
    """
    without_quotation = _QUOTATIONS.sub("[…]", text)
    without_quotation = " ".join(without_quotation.split())
    return without_quotation[:_MAX_LENGTH]


def _post(text: str) -> None:
    """Envoi réel, en tâche de fond. N'échoue jamais vers l'appelant."""
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
        # Le bipeur qui tombe ne doit surtout pas emporter la génération : c'est
        # un confort d'opérateur, pas une dépendance du pipeline.
        pass


def _send(text: str, *, priority: bool = False) -> None:
    """Poste un message, sauf si le débit est déjà atteint (hors priorité).

    L'envoi part dans un THREAD : une génération ne doit pas attendre cinq
    secondes de timeout réseau parce qu'un opérateur veut être prévenu.
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


# --- Événements : la seule surface d'appel autorisée -------------------------
#
# Chaque fonction compose son message à partir de champs typés. Il n'existe
# volontairement PAS de `notify.texte(...)` générique : ce serait la porte par
# laquelle le contenu finirait par sortir.

def startup(planned_scenes: str = "") -> None:
    _send(f"▶️ Génération lancée{f' ({planned_scenes})' if planned_scenes else ''}",
             priority=True)


def advancement(label: str, percent: float, elapsed_s: int) -> None:
    """Battement de progression. `label` vient de nos PHASES, pas du modèle."""
    _send(f"⏳ {int(percent * 100)} % — {label} — {elapsed_s // 60} min écoulées")


def alert(code: str) -> None:
    """Événement notable. `code` est un libellé COURT et fixe, pas une citation."""
    _send(f"⚠️ {code}", priority=True)


def ready(duration_s: int, scenes: int, audio_s: float | None) -> None:
    audio = f", audio {audio_s / 60:.1f} min" if audio_s else ", sans audio"
    _send(f"✅ Chapitre prêt en {duration_s // 60} min {duration_s % 60} s "
             f"({scenes} scènes{audio})", priority=True)


def failure(kind: str, reason: str) -> None:
    """Échec. `raison` passe par l'assainisseur : elle peut venir d'ailleurs."""
    _send(f"❌ ÉCHEC ({kind}) — {reason} — PLAN B", priority=True)


def cancelled() -> None:
    _send("⏹️ Génération annulée par l'opérateur", priority=True)
