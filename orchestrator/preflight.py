#!/usr/bin/env python3
"""Contrôle de sécurité machine avant une génération longue.

Motivation : une session de tests a fait paniquer le MacBook (watchdog
timeout, `no checkins from watchdogd in 91 seconds`). Cause racine : disque à
99 %, donc swap incapable de grandir, sous la pression d'un modèle de 13 GB
sur 18 GB de mémoire unifiée. Le kernel n'a pas pu ordonnancer watchdogd.

Sur scène, la génération tourne ~20 min SANS surveillance. Un plantage à ce
moment-là n'est pas rattrapable. Ces vérifications coûtent quelques
millisecondes et refusent de démarrer sur une machine déjà étranglée.

Trois signaux, du plus déterminant au plus indicatif :

1. DISQUE — si le volume de données est plein, macOS ne peut plus allouer de
   swapfile. C'est la condition exacte du panic observé.
2. SWAP — un swap déjà saturé signale une machine qui n'a pas digéré la
   session précédente. Un redémarrage est le seul remède (macOS ne rend pas
   les swapfiles à chaud). Attention : saturé ne veut dire « bloquant » que
   si le disque ne permet plus d'agrandir le swap — c'est la CONJONCTION des
   deux qui a fait paniquer la machine, pas le swap plein tout seul.
3. CO-RÉSIDENCE DE MODÈLES — deux LLM chauds (nemo 13 GB + small 14 GB) ne
   tiennent pas dans 18 GB. Sans `OLLAMA_MAX_LOADED_MODELS=2`, Ollama en
   autorise trois. L'API `/api/ps` dit l'état réel, elle ne ment pas.
"""

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Seuils. Le disque doit pouvoir absorber la croissance du swap (macOS va
# jusqu'à ~2× la RAM physique) plus une marge de travail.
MIN_DISK_GB = float(os.environ.get("PREFLIGHT_MIN_DISK_GB", "20"))
MIN_SWAP_FREE_GB = float(os.environ.get("PREFLIGHT_MIN_SWAP_FREE_GB", "2"))

# Un swap saturé n'est mortel que si macOS ne peut plus l'agrandir. Au-dessus
# de cette marge de disque, la saturation est un simple avertissement : le
# système allouera un swapfile de plus. En dessous, c'est la configuration
# exacte du panic (« 13 swapfiles and LOW swap space », disque à 99 %).
SWAP_GROWTH_MARGIN_GB = float(os.environ.get("PREFLIGHT_SWAP_MARGIN_GB", "40"))

# Au-delà, un modèle chargé n'est plus un embedder mais un vrai LLM qui
# dispute la mémoire au modèle auteur. nomic-embed pèse 370 MB.
EMBED_SIZE_LIMIT_GB = 2.0

DATA_VOLUME = "/System/Volumes/Data"


class PreflightError(RuntimeError):
    """Condition machine incompatible avec une génération longue."""


def _disk_free_gb(path: str = DATA_VOLUME) -> float:
    """Espace libre du volume de données, en Go."""
    try:
        return shutil.disk_usage(path).free / 1e9
    except OSError:
        return shutil.disk_usage("/").free / 1e9


def _swap_gb() -> dict[str, float] | None:
    """État du swap en Go, via `sysctl vm.swapusage`. None si illisible.

    Format attendu :
        vm.swapusage: total = 9216.00M  used = 8515.12M  free = 700.88M
    Les unités peuvent être M ou G selon la taille — on normalise.

    On lit `total` autant que `free` : sur une machine fraîchement redémarrée
    macOS n'a encore alloué AUCUN swapfile, donc `total = free = 0`. Ne
    regarder que `free` conclut « swap saturé, redémarrez » juste après un
    redémarrage — exactement l'inverse de la vérité.
    """
    try:
        out = subprocess.run(
            ["sysctl", "-n", "vm.swapusage"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    # « total = 9216.00M  used = ...  free = 700.88M » → jeton après chaque clé.
    tokens = out.replace("=", " = ").split()
    values: dict[str, float] = {}
    for i, tok in enumerate(tokens):
        if tok not in ("total", "used", "free") or i + 2 >= len(tokens):
            continue
        raw = tokens[i + 2]
        try:
            value = float(raw[:-1])
        except ValueError:
            return None
        unit = raw[-1].upper()
        factor = {"G": 1.0, "M": 1 / 1024, "K": 1 / 1024 / 1024}.get(unit)
        if factor is None:
            return None
        values[tok] = value * factor

    return values if {"total", "used", "free"} <= values.keys() else None


def _loaded_llms() -> list[dict] | None:
    """Modèles actuellement chauds, embedders exclus. None si Ollama muet.

    On filtre sur la taille : `/api/ps` ne distingue pas un embedder d'un
    LLM, mais 370 MB contre 13 GB, l'écart tranche tout seul.
    """
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/ps", timeout=5) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return None

    return [
        m for m in data.get("models", [])
        if m.get("size", 0) / 1e9 > EMBED_SIZE_LIMIT_GB
    ]


def preflight(*, strict: bool = True) -> list[str]:
    """Vérifie la machine. Retourne les avertissements non bloquants.

    Lève PreflightError sur une condition qui a déjà fait planter la machine.
    `strict=False` dégrade tout en avertissement (itération de dev).
    """
    blocking: list[str] = []
    warnings: list[str] = []

    disk = _disk_free_gb()
    if disk < MIN_DISK_GB:
        blocking.append(
            f"Disque : {disk:.1f} GB libres (< {MIN_DISK_GB:.0f} GB). "
            "macOS ne pourra pas agrandir le swap → risque de panic "
            "watchdog. Libérer de l'espace avant de lancer."
        )

    swap = _swap_gb()
    if swap is None:
        warnings.append("Swap : état illisible (sysctl vm.swapusage).")
    elif swap["total"] == 0:
        pass  # Aucun swapfile alloué : machine fraîche, rien à signaler.
    elif swap["free"] < MIN_SWAP_FREE_GB:
        detail = (
            f"Swap : {swap['free']:.2f} GB libres sur {swap['total']:.1f} GB "
            f"alloués (< {MIN_SWAP_FREE_GB:.0f} GB)."
        )
        if disk < SWAP_GROWTH_MARGIN_GB:
            blocking.append(
                f"{detail} Et le disque ({disk:.1f} GB) ne laisse plus de quoi "
                "l'agrandir — c'est la configuration exacte du panic watchdog. "
                "REDÉMARRER avant de générer (macOS ne rend pas les swapfiles "
                "à chaud)."
            )
        else:
            warnings.append(
                f"{detail} Le disque a de la marge, macOS pourra allouer un "
                "swapfile de plus — mais la machine n'a pas digéré la session "
                "précédente. Redémarrer avant la scène."
            )

    llms = _loaded_llms()
    if llms is None:
        warnings.append(f"Ollama injoignable sur {OLLAMA_URL} — état inconnu.")
    elif len(llms) > 1:
        noms = ", ".join(
            f"{m.get('name', '?')} ({m.get('size', 0) / 1e9:.1f} GB)"
            for m in llms
        )
        blocking.append(
            f"Co-résidence : {len(llms)} LLM chauds simultanément — {noms}. "
            "Ils ne tiennent pas ensemble en mémoire unifiée. Décharger "
            "(`ollama stop <modèle>`) et régler OLLAMA_MAX_LOADED_MODELS=2."
        )

    if blocking and strict:
        raise PreflightError(
            "Préflight refusé :\n  - " + "\n  - ".join(blocking)
        )
    return warnings + blocking


def report() -> str:
    """Résumé lisible de l'état machine, pour le log de démo."""
    disk = _disk_free_gb()
    swap = _swap_gb()
    llms = _loaded_llms()
    if swap is None:
        swap_txt = "?"
    elif swap["total"] == 0:
        swap_txt = "aucun swapfile (machine fraîche)"
    else:
        swap_txt = f"{swap['free']:.2f} / {swap['total']:.1f} GB"
    llm_txt = (
        ", ".join(m.get("name", "?") for m in llms) if llms
        else ("aucun" if llms is not None else "?")
    )
    return (
        f"disque {disk:.1f} GB libres | swap {swap_txt} | "
        f"LLM chauds : {llm_txt}"
    )


if __name__ == "__main__":
    print(report())
    try:
        for w in preflight():
            print(f"  ⚠ {w}")
    except PreflightError as exc:
        raise SystemExit(str(exc))
