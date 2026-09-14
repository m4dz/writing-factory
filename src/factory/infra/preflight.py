#!/usr/bin/env python3
"""Machine safety gate before a long generation (ADR-0016).

Born from an incident: a test session panicked the MacBook (watchdog timeout,
`no checkins from watchdogd in 91 seconds`). Root cause: disk at 99 %, so the
swap could not grow under a 13 GB model in 18 GB of unified memory; the
kernel could not schedule watchdogd.

Onstage the generation runs ~20 min UNATTENDED, and a crash then cannot be
recovered. These checks cost milliseconds and refuse to start a machine that
is already choked. Signals, from the most decisive to the most indicative:

1. DISK: a full data volume means macOS cannot allocate a swapfile. The exact
   condition of the observed panic.
2. SWAP: a consumed swap blocks only in timer mode, and only when the pageout
   rate says the machine LIVES in its swap (see `_swap_cold`). It never
   crashed the machine; it makes durations uninterpretable.
3. macOS MAINTENANCE: two runs showed 5 to 18 MINUTE holes between two model
   calls with 0.8 s of CPU used in 49 minutes; `mediaanalysisd` at 197-227 %
   CPU after a reboot, against a generation process at `nice 5`. First
   blamed paging, until the second run reproduced it with a fresh machine
   and an empty swap: two simultaneous symptoms are not a cause.
4. MODEL CO-RESIDENCE: two warm LLMs (nemo 13 GB + small 14 GB) do not fit in
   18 GB. Without `OLLAMA_MAX_LOADED_MODELS=2` Ollama allows three; `/api/ps`
   reports the real state.

Memory pressure is reported as well, from macOS's own verdict
(`kern.memorystatus_vm_pressure_level`) and not a home-made page count; see
`_pressure_level` for the false alarm the first version raised.
"""

import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

from factory.settings import settings

# Thresholds: `settings.min_disk_gb` (the disk must absorb the swap's growth,
# up to ~2× physical RAM under macOS, and a working margin),
# `settings.min_swap_free_gb`, `settings.pageout_block_kb_s`,
# `settings.daemon_warn_cpu` / `daemon_block_cpu`, `settings.probe_model`.

# Swap: a WARNING by default, blocking only in timer mode (ADR-0016). The
# 2026-08-09 revision withdrew the blanket block: the panics came from a disk
# at 99 % (covered by `min_disk_gb`), the holes from `mediaanalysisd` (covered
# by `NOISY_DAEMONS`; run 4 reproduced them with swap at zero). Measured
# 2026-08-09, after Ollama's `keep_alive` expired and nothing else: free memory
# 11 % → 87 %, swap `used` −1.35 GB, `total` 4096 → 3072 MB. macOS DOES return
# swapfiles live; unloading the model suffices, a reboot is a last resort. What
# stays true: a machine living in its swap gives no reliable DURATIONS, hence
# timer mode.

# COLD SWAP, the 2026-08-22 fix: a LOGIC flaw, not an arbitration.
# `free = total - used`, and macOS SIZES `total` just above `used`, so `free`
# stays small while swapfiles are returned. Observed over an hour with models
# unloaded: total 10240 → 8192 → 4096 MB, `free` always 0.5-1.1 GB. The
# `free < 2 GB` threshold is the NORMAL STEADY STATE of a modest swap: it can
# never turn green by waiting, and it blocked runs S6-2, S6-3 and S6-C while
# direct measurement gave 85 % free memory and 88 pages out in twenty seconds
# (1.4 MB). What the rule NAMES is a machine living in its swap, and that is
# measurable: the pageout rate. A consumed but cold swap is dead memory nobody
# rereads; it costs durations nothing. Lesson (ADR-0016): a threshold that
# correlates is not a threshold that causes.
PAGEOUT_WINDOW_S = 4.0
# Apple Silicon memory page size. `vm_stat` prints it in its header; pinned
# rather than parsed, it does not vary for this platform.
PAGE_SIZE_BYTES = 16384

# Memory pressure: macOS's own verdict (see _pressure_level), not a home-made
# page count. 1 = normal, 2 = warn, 4 = critical.
PRESSURE_BLOCK = 4

# Above this size a loaded model is no embedder but a real LLM competing for
# memory with the author model. nomic-embed weighs 370 MB.
EMBED_SIZE_LIMIT_GB = 2.0

DATA_VOLUME = "/System/Volumes/Data"

# macOS maintenance daemons that wake after a reboot or a large copy and hog
# CPU, memory and disk for tens of minutes. Measured 2026-08-06:
# `mediaanalysisd` at 197 % CPU (two cores) during a run, with seventeen-minute
# holes between two model calls. A generation launched in the background runs
# at `nice 5` and loses every arbitration (ADR-0016). The most concrete stage
# risk: the machine decides to index the photo library during the keynote.
NOISY_DAEMONS = (
    "mediaanalysisd", "photoanalysisd", "photolibraryd", "mdworker",
    "mds_stores", "mds", "backupd", "cloudphotod", "corespotlightd",
    "spotlightknowledged", "knowledgeconstructiond",
    "IntelligencePlatformComputeService", "duetexpertd",
    "AssetCacheLocatorService", "syspolicyd",
)

# Generation probe model (`settings.probe_model`): the SMALLEST of the project.
# It checks that the server can start a llama-server, not that nemo fits in
# memory, and loading 4.8 GB takes ten seconds against about thirty for 13 GB.
# An empty value disables the probe.


class PreflightError(RuntimeError):
    """Machine condition incompatible with a long generation."""


def _disk_free_gb(path: str = DATA_VOLUME) -> float:
    """Free space of the data volume, in GB."""
    try:
        return shutil.disk_usage(path).free / 1e9
    except OSError:
        return shutil.disk_usage("/").free / 1e9


def _swap_gb() -> dict[str, float] | None:
    """Swap state in GB, via `sysctl vm.swapusage`. None when unreadable.

    Expected format:
        vm.swapusage: total = 9216.00M  used = 8515.12M  free = 700.88M
    Units may be M or G according to size; normalised here.

    `total` is read as well as `free`: a freshly rebooted macOS has allocated
    NO swapfile yet, so `total = free = 0`. Looking at `free` alone concludes
    "swap saturated, reboot" right after a reboot, the exact opposite of the
    truth.
    """
    try:
        out = subprocess.run(
            ["sysctl", "-n", "vm.swapusage"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    # « total = 9216.00M  used = ...  free = 700.88M » → token after each key.
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


def _pageouts() -> int | None:
    """Cumulative count of pages written out to swap, via `vm_stat`."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=5, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return None
    for line in out.splitlines():
        if line.startswith("Pageouts"):
            try:
                return int(line.split(":")[1].strip().rstrip("."))
            except (IndexError, ValueError):
                return None
    return None


def _swap_cold(window: float = PAGEOUT_WINDOW_S) -> bool:
    """Is the swap consumed but INERT?

    Costs `window` seconds, and only in the branch where the swap looks low;
    the normal path is unchanged. When the counter cannot be read, return
    False and fall back to the older, stricter behaviour: a guard that fails
    must fail towards refusal.
    """
    a = _pageouts()
    if a is None:
        return False
    time.sleep(window)
    b = _pageouts()
    if b is None or b < a:
        return False
    ko_par_s = (b - a) * PAGE_SIZE_BYTES / 1024 / window
    return ko_par_s < settings.pageout_block_kb_s


def _pressure_level() -> int | None:
    """Memory pressure level ACCORDING TO macOS: 1 normal, 2 warn, 4 critical.

    The system's own verdict (the one driving jetsam) beats any hand count
    of pages. The first version of this check summed `vm_stat`'s "free +
    speculative" pages and excluded "inactive", reasoning that reclaiming
    them means paging. Wrong: most inactive pages are CLEAN file cache the
    kernel drops without writing anything. With a fresh, healthy machine
    that count announced 0.45 GB available while macOS reported 79 % free
    memory and normal pressure: the swap check's trap again, alerting right
    after a reboot.
    """
    try:
        out = subprocess.run(
            ["sysctl", "-n", "kern.memorystatus_vm_pressure_level"],
            capture_output=True, text=True, timeout=5, check=True,
        ).stdout
        return int(out.strip())
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


def _ram_available_gb() -> float | None:
    """Memory reclaimable without paging, in GB; an INDICATIVE figure for the log.

    Free + speculative + inactive + purgeable pages. Gives an order of
    magnitude in the report, decides nothing: `_pressure_level` rules.
    """
    try:
        out = subprocess.run(
            ["vm_stat"], capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    size = re.search(r"page size of (\d+) bytes", out)
    if not size:
        return None
    total = 0
    for key in ("Pages free", "Pages speculative", "Pages inactive",
                "Pages purgeable"):
        hit = re.search(rf"{key}:\s+(\d+)", out)
        if hit:
            total += int(hit.group(1))
    return total * int(size.group(1)) / 1e9


def _busy_daemons() -> list[tuple[str, float]] | None:
    """macOS maintenance daemons currently greedy. None when `ps` is unreadable.

    Returns [(name, %cpu)] sorted descending, for the `NOISY_DAEMONS`
    processes above the warning threshold only. The `%cpu` of `ps` is an
    average over the process lifetime, not an instant: a daemon that just
    woke is underestimated, which errs the right way for a gate, never
    towards a false alarm.
    """
    try:
        out = subprocess.run(
            ["ps", "-Ao", "pcpu,comm", "-r"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    found_list: list[tuple[str, float]] = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        try:
            cpu = float(parts[0])
        except ValueError:
            continue
        if cpu < settings.daemon_warn_cpu:
            break  # `-r` sorts by CPU descending: nothing above the threshold remains
        name = parts[1].rsplit("/", 1)[-1].strip()
        if name in NOISY_DAEMONS:
            found_list.append((name, cpu))
    return found_list


def _probe_generation(model: str, timeout: float = 120.0) -> str | None:
    """REALLY generate one token. Return None when all is well, else the reason
    of the failure.

    Without this probe the Ollama check stopped at `/api/ps`, which answers
    200 with an empty list when nothing is loaded, indistinguishable from a
    healthy machine. After SLEEP the Ollama daemon survives but can no longer
    start `llama-server` (« timed out waiting for llama-server to start »)
    and EVERY request returns 500; measured 2026-08-07 after a night of
    sleep. A preflight that does not generate a token says nothing of what
    counts. Remedy: `launchctl kickstart -k gui/$(id -u)/local.ollama`
    (ADR-0009).
    """
    # `keep_alive: 0`: the probe returns the memory it borrows. Otherwise it
    # would leave the model warm and the run would start with two co-resident
    # models, the memory pressure this preflight exists to prevent.
    payload = json.dumps({
        "model": model, "prompt": "1", "stream": False, "keep_alive": 0,
        "options": {"num_predict": 1},
    }).encode()
    req = urllib.request.Request(
        f"{settings.ollama_url}/api/generate", data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            json.loads(resp.read())
        return None
    except urllib.error.HTTPError as exc:
        return f"HTTP {exc.code} sur /api/generate ({model})"
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        return f"{type(exc).__name__} sur /api/generate ({model}) : {exc}"


def _loaded_llms() -> list[dict] | None:
    """Models currently warm, embedders excluded. None when Ollama is silent.

    Filtered by size: `/api/ps` does not tell an embedder from an LLM, but
    370 MB against 13 GB settles it alone.
    """
    try:
        with urllib.request.urlopen(f"{settings.ollama_url}/api/ps", timeout=5) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return None

    return [
        m for m in data.get("models", [])
        if m.get("size", 0) / 1e9 > EMBED_SIZE_LIMIT_GB
    ]


def preflight(*, strict: bool = True, timer: bool = False) -> list[str]:
    """Check the machine. Return the non-blocking warnings.

    Raises PreflightError for a condition that has already crashed the
    machine. `strict=False` degrades everything to a warning (dev iteration).

    `timer=True` adds the conditions that do not threaten the machine but
    distort DURATIONS: the mode of runs whose figure is the object (reference
    run, rehearsal, stage generation). A style test judges prose and does not
    care about seconds; it has no reason to demand a reboot (ADR-0016).
    """
    blocking: list[str] = []
    warnings: list[str] = []

    disk = _disk_free_gb()
    if disk < settings.min_disk_gb:
        blocking.append(
            f"Disque : {disk:.1f} GB libres (< {settings.min_disk_gb:.0f} GB). "
            "macOS ne pourra pas agrandir le swap → risque de panic "
            "watchdog. Libérer de l'espace avant de lancer."
        )

    swap = _swap_gb()
    if swap is None:
        warnings.append("Swap : état illisible (sysctl vm.swapusage).")
    elif swap["total"] == 0:
        pass  # No swapfile allocated: fresh machine, nothing to report.
    elif swap["free"] < settings.min_swap_free_gb and _swap_cold():
        warnings.append(
            f"Swap : {swap['free']:.2f} GB libres sur {swap['total']:.1f} GB "
            f"alloués, mais FROID (moins de "
            f"{settings.pageout_block_kb_s:.0f} Ko/s de pageouts sur "
            f"{PAGEOUT_WINDOW_S:.0f} s). Ce sont des pages froides que personne "
            "ne relit : macOS dimensionne `total` au-dessus de `used`, donc "
            "`free` reste petit même quand la machine va bien. Les durées "
            "restent interprétables."
        )
    elif swap["free"] < settings.min_swap_free_gb:
        msg = (
            f"Swap : {swap['free']:.2f} GB libres sur {swap['total']:.1f} GB "
            f"alloués (< {settings.min_swap_free_gb:.0f} GB). La machine porte encore la "
            "session précédente. Remède : DÉCHARGER le modèle "
            "(`ollama stop <modèle>`, ou attendre l'expiration de keep_alive) — "
            "macOS rend alors les pages ET rétrécit les swapfiles. Redémarrer "
            "n'est qu'un dernier recours."
        )
        # Blocking only when timing: a consumed swap does not break the
        # machine (the disk does, see min_disk_gb), it makes durations
        # uninterpretable.
        if timer:
            blocking.append(
                msg + " Mesure de temps refusée dans cet état : les durées "
                "seraient ininterprétables."
            )
        else:
            warnings.append(msg)

    level = _pressure_level()
    if level is None:
        warnings.append("Pression mémoire : état illisible (sysctl).")
    elif level >= PRESSURE_BLOCK:
        blocking.append(
            "Pression mémoire CRITIQUE selon macOS "
            f"(kern.memorystatus_vm_pressure_level = {level}). Le système est "
            "déjà en train de récupérer de la mémoire de force ; une génération "
            "de vingt minutes va paginer au lieu de générer. Remède : décharger "
            "le modèle (`ollama stop <modèle>`) et fermer les gros consommateurs "
            "— c'est ce qui rend la mémoire, pas le redémarrage. Redémarrer "
            "seulement si la pression ne retombe pas."
        )
    elif level >= 2:
        warnings.append(
            f"Pression mémoire élevée selon macOS (niveau {level}). Fermer ce "
            "qui n'est pas nécessaire avant de lancer."
        )

    daemons = _busy_daemons()
    if daemons is None:
        warnings.append("Démons d'entretien : état illisible (ps).")
    elif daemons:
        detail = ", ".join(f"{name} {cpu:.0f} %" for name, cpu in daemons)
        worst = max(cpu for _, cpu in daemons)
        if worst >= settings.daemon_block_cpu:
            blocking.append(
                f"Entretien macOS en cours : {detail}. Le processus de "
                "génération tourne à nice 5 et perdra l'arbitrage : trous de "
                "plusieurs minutes entre deux appels au modèle, budget de scène "
                "explosé. ATTENDRE que ça retombe (`ps -Ao %cpu,comm -r | head`) "
                "— après un redémarrage, l'analyse média peut tourner longtemps."
            )
        else:
            warnings.append(
                f"Entretien macOS actif : {detail}. Surveiller — au-delà de "
                f"{settings.daemon_block_cpu:.0f} % ça fausse toute mesure de temps."
            )

    if settings.probe_model:
        failure = _probe_generation(settings.probe_model)
        if failure:
            blocking.append(
                f"Ollama ne GÉNÈRE pas : {failure}. Le démon écoute mais ne peut "
                "plus lancer llama-server — typiquement après une mise en veille. "
                "Remède : `launchctl kickstart -k gui/$(id -u)/local.ollama`. "
                "Et empêcher la veille avant la scène (`caffeinate -is`)."
            )

    llms = _loaded_llms()
    if llms is None:
        warnings.append(f"Ollama injoignable sur {settings.ollama_url} — état inconnu.")
    elif len(llms) > 1:
        names = ", ".join(
            f"{m.get('name', '?')} ({m.get('size', 0) / 1e9:.1f} GB)"
            for m in llms
        )
        blocking.append(
            f"Co-résidence : {len(llms)} LLM chauds simultanément — {names}. "
            "Ils ne tiennent pas ensemble en mémoire unifiée. Décharger "
            "(`ollama stop <modèle>`) et régler OLLAMA_MAX_LOADED_MODELS=2."
        )

    if blocking and strict:
        raise PreflightError(
            "Préflight refusé :\n  - " + "\n  - ".join(blocking)
        )
    return warnings + blocking


def report() -> str:
    """Readable summary of the machine state, for the demo log."""
    disk = _disk_free_gb()
    swap = _swap_gb()
    ram = _ram_available_gb()
    level = _pressure_level()
    daemons = _busy_daemons()
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
    ram_txt = f"{ram:.1f} GB" if ram is not None else "?"
    level_txt = {1: "normale", 2: "élevée", 4: "critique"}.get(level, "?")
    daemons_txt = (
        ", ".join(f"{n} {c:.0f} %" for n, c in daemons) if daemons
        else ("aucun" if daemons is not None else "?")
    )
    return (
        f"disque {disk:.1f} GB libres | swap {swap_txt} | "
        f"mémoire récupérable {ram_txt}, pression {level_txt} | "
        f"entretien macOS : {daemons_txt} | LLM chauds : {llm_txt}"
    )


if __name__ == "__main__":
    print(report())
    try:
        for w in preflight():
            print(f"  ⚠ {w}")
    except PreflightError as exc:
        raise SystemExit(str(exc))
