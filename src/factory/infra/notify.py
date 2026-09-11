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
import os
import re
import threading
import time
import urllib.error
import urllib.request

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
TIMEOUT_S = float(os.environ.get("TELEGRAM_TIMEOUT_S", "5"))

# Un message d'avancement au plus toutes les N secondes : sur une montre, une
# rafale de notifications est pire que pas de notification du tout.
PERIODE_MIN_S = float(os.environ.get("TELEGRAM_PERIODE_S", "300"))

# Tout ce qui est cité l'est parce que ça vient du modèle ou de la bible.
_CITATIONS = re.compile(r"[«\"“][^»\"”]*[»\"”]")
_LONGUEUR_MAX = 200

_dernier_envoi = 0.0
_verrou = threading.Lock()


def actif() -> bool:
    return bool(TOKEN and CHAT_ID)


def _assainir(texte: str) -> str:
    """Retire les citations et borne la longueur — second rideau.

    Le premier rideau est de ne composer les messages qu'à partir de champs
    structurés ; celui-ci protège le cas où une exception inattendue porterait
    du contenu dans son message.
    """
    sans_citation = _CITATIONS.sub("[…]", texte)
    sans_citation = " ".join(sans_citation.split())
    return sans_citation[:_LONGUEUR_MAX]


def _poster(texte: str) -> None:
    """Envoi réel, en tâche de fond. N'échoue jamais vers l'appelant."""
    charge = json.dumps({
        "chat_id": CHAT_ID, "text": texte, "disable_notification": False,
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data=charge, headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=TIMEOUT_S).read()
    except (urllib.error.URLError, OSError, ValueError):
        # Le bipeur qui tombe ne doit surtout pas emporter la génération : c'est
        # un confort d'opérateur, pas une dépendance du pipeline.
        pass


def _envoyer(texte: str, *, prioritaire: bool = False) -> None:
    """Poste un message, sauf si le débit est déjà atteint (hors priorité).

    L'envoi part dans un THREAD : une génération ne doit pas attendre cinq
    secondes de timeout réseau parce qu'un opérateur veut être prévenu.
    """
    global _dernier_envoi
    if not actif():
        return
    with _verrou:
        maintenant = time.time()
        if not prioritaire and maintenant - _dernier_envoi < PERIODE_MIN_S:
            return
        _dernier_envoi = maintenant
    threading.Thread(target=_poster, args=(_assainir(texte),),
                     daemon=True).start()


# --- Événements : la seule surface d'appel autorisée -------------------------
#
# Chaque fonction compose son message à partir de champs typés. Il n'existe
# volontairement PAS de `notify.texte(...)` générique : ce serait la porte par
# laquelle le contenu finirait par sortir.

def demarrage(scenes_prevues: str = "") -> None:
    _envoyer(f"▶️ Génération lancée{f' ({scenes_prevues})' if scenes_prevues else ''}",
             prioritaire=True)


def avancement(label: str, pourcentage: float, ecoule_s: int) -> None:
    """Battement de progression. `label` vient de nos PHASES, pas du modèle."""
    _envoyer(f"⏳ {int(pourcentage * 100)} % — {label} — {ecoule_s // 60} min écoulées")


def alerte(code: str) -> None:
    """Événement notable. `code` est un libellé COURT et fixe, pas une citation."""
    _envoyer(f"⚠️ {code}", prioritaire=True)


def pret(duree_s: int, scenes: int, audio_s: float | None) -> None:
    audio = f", audio {audio_s / 60:.1f} min" if audio_s else ", sans audio"
    _envoyer(f"✅ Chapitre prêt en {duree_s // 60} min {duree_s % 60} s "
             f"({scenes} scènes{audio})", prioritaire=True)


def echec(classe: str, raison: str) -> None:
    """Échec. `raison` passe par l'assainisseur : elle peut venir d'ailleurs."""
    _envoyer(f"❌ ÉCHEC ({classe}) — {raison} — PLAN B", prioritaire=True)


def annule() -> None:
    _envoyer("⏹️ Génération annulée par l'opérateur", prioritaire=True)
