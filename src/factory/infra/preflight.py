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
   les swapfiles à chaud). C'est BLOQUANT : un modèle de 13 GB sur 18 GB
   unifiés n'a aucune marge sur une machine qui vit déjà sur son swap. Ça ne
   l'a pas toujours été — j'avais d'abord raisonné que la saturation n'était
   dangereuse qu'avec un disque plein, puisque macOS peut sinon allouer un
   swapfile de plus. Il le fait, mais ce n'est pas une machine sur laquelle on
   chronomètre une démo.

3. ENTRETIEN macOS — le risque le plus concret, et le dernier trouvé. Deux runs
   ont montré des trous de cinq à dix-huit MINUTES entre deux appels au modèle,
   avec 0,8 s de CPU consommé en 49 minutes : le processus dormait. Cause :
   `mediaanalysisd` à 197-227 % de CPU, réveillé par le redémarrage, contre un
   processus de génération à `nice 5`. À noter, parce que je me suis trompé
   d'abord : j'ai attribué ces trous à la pagination avant que le second run,
   sur machine fraîche et swap vide, ne reproduise le même motif. Deux
   symptômes simultanés ne font pas une cause.
4. CO-RÉSIDENCE DE MODÈLES — deux LLM chauds (nemo 13 GB + small 14 GB) ne
   tiennent pas dans 18 GB. Sans `OLLAMA_MAX_LOADED_MODELS=2`, Ollama en
   autorise trois. L'API `/api/ps` dit l'état réel, elle ne ment pas.

La pression mémoire est rapportée en plus, d'après le verdict de macOS lui-même
(`kern.memorystatus_vm_pressure_level`) et non d'après un comptage de pages
maison — cf. `_pressure_level`, où la première version alertait sur une machine
parfaitement saine.
"""

import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

from factory.settings import settings

# Seuils : `settings.min_disk_gb` (le disque doit pouvoir absorber la
# croissance du swap, macOS va jusqu'à ~2× la RAM physique, plus une marge de
# travail), `settings.min_swap_free_gb`, `settings.pageout_block_kb_s`,
# `settings.daemon_warn_cpu` / `daemon_block_cpu`, `settings.probe_model`.

# Swap : AVERTISSEMENT par défaut, bloquant seulement en mode chrono
# (cf. `preflight(chrono=...)`). Révision du 2026-08-09, sur mesure.
#
# Ce seuil bloquait tout, et il le faisait sur un raisonnement que le dossier du
# projet contredit lui-même :
#   - Les kernel panics venaient d'un DISQUE À 99 % (macOS ne pouvait plus
#     agrandir le swap), pas d'un swap consommé. `MIN_DISK_GB` couvre ce cas
#     directement, et mieux.
#   - Les trous de 5 à 18 minutes venaient de `mediaanalysisd`, pas de la
#     pagination — le run 4 les a reproduits sur une machine fraîchement
#     redémarrée, swap à zéro. `NOISY_DAEMONS` couvre ce cas directement.
# Le swap libre n'était donc qu'un PROXY de deux signaux déjà mesurés, et il
# coûtait un redémarrage à chaque session de test.
#
# Mesuré le 2026-08-09, sans autre intervention que l'expiration de `keep_alive`
# d'Ollama : mémoire libre 11 % → 87 %, swap `used` −1,35 GB, et `total` passé de
# 4096 à 3072 MB. macOS REND donc les swapfiles à chaud, contrairement à ce que
# ce fichier affirmait. Décharger le modèle suffit ; redémarrer est un dernier
# recours.
#
# Ce qui reste vrai : une machine qui vit sur son swap ne donne pas des DURÉES
# fiables. D'où le mode chrono, pour les runs dont le chiffre est l'objet.

# SWAP FROID — la correction du 2026-08-22, et elle porte sur une faille de
# LOGIQUE, pas sur un arbitrage.
#
# `free = total - used`, et macOS DIMENSIONNE `total` juste au-dessus de `used` :
# à mesure qu'il rend les swapfiles, `free` reste petit. Observé en une heure sur
# cette machine, modèles déchargés : total 10240 → 8192 → 4096 MB, `free` toujours
# entre 0,5 et 1,1 GB. Le seuil `free < 2 GB` est donc l'ÉTAT STATIONNAIRE NORMAL
# d'une machine à swap modeste — il ne peut jamais redevenir vert par attente, et
# il a bloqué les runs S6-2, S6-3 et S6-C alors que la mesure directe donnait
# 85 % de mémoire libre et 88 pages sorties en vingt secondes (1,4 Mo).
#
# Ce que la règle NOMME, c'est « une machine qui vit sur son swap ». Ça se mesure :
# le débit de pageouts. Un swap consommé mais froid est de la mémoire morte que
# personne ne relit ; il ne coûte rien aux durées.
#
# C'est la leçon déjà gravée dans CLAUDE.md, appliquée une fois de plus : un
# seuil qui corrèle n'est pas un seuil qui cause, et avant d'imposer un rituel,
# vérifier que le signal bloquant n'est pas déjà couvert par un signal direct.
PAGEOUT_FENETRE_S = 4.0
# Taille de page mémoire d'Apple Silicon. `vm_stat` la rappelle en en-tête ;
# on la fixe plutôt que de la parser, elle ne varie pas sur cette plateforme.
PAGE_SIZE_BYTES = 16384

# Pression mémoire : on s'en remet au verdict de macOS (cf. _pressure_level),
# pas à un comptage de pages maison. 1 = normal, 2 = warn, 4 = critique.
PRESSURE_BLOCK = 4

# Au-delà, un modèle chargé n'est plus un embedder mais un vrai LLM qui
# dispute la mémoire au modèle auteur. nomic-embed pèse 370 MB.
EMBED_SIZE_LIMIT_GB = 2.0

DATA_VOLUME = "/System/Volumes/Data"

# Démons d'entretien macOS qui se réveillent après un redémarrage ou une grosse
# copie et monopolisent CPU, mémoire et disque pendant des dizaines de minutes.
# Mesuré le 2026-08-06 : `mediaanalysisd` à 197 % de CPU (deux cœurs) pendant un
# run, avec des trous de dix-sept minutes entre deux appels au modèle. Le
# processus de génération, lancé en tâche de fond, tourne à `nice 5` : il perd
# systématiquement l'arbitrage. C'est le risque de scène le plus concret —
# la machine décide d'indexer la photothèque pendant la keynote.
NOISY_DAEMONS = (
    "mediaanalysisd", "photoanalysisd", "photolibraryd", "mdworker",
    "mds_stores", "mds", "backupd", "cloudphotod", "corespotlightd",
    "spotlightknowledged", "knowledgeconstructiond",
    "IntelligencePlatformComputeService", "duetexpertd",
    "AssetCacheLocatorService", "syspolicyd",
)

# Modèle de la sonde de génération. Le PLUS PETIT du projet : on vérifie que le
# serveur sait lancer un llama-server, pas que nemo tient en mémoire — et
# charger 4,8 GB coûte dix secondes contre une trentaine pour 13 GB.
# Vider la variable désactive la sonde.


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


def _pageouts() -> int | None:
    """Compteur cumulé de pages sorties vers le swap, via `vm_stat`."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=5, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return None
    for ligne in out.splitlines():
        if ligne.startswith("Pageouts"):
            try:
                return int(ligne.split(":")[1].strip().rstrip("."))
            except (IndexError, ValueError):
                return None
    return None


def _swap_froid(fenetre: float = PAGEOUT_FENETRE_S) -> bool:
    """Le swap est-il consommé mais INERTE ?

    Coûte `fenetre` secondes, et seulement dans la branche où le swap paraît
    bas — le chemin normal est inchangé. En cas de lecture impossible on rend
    False : on retombe alors sur l'ancien comportement, plus sévère. Un garde
    qui échoue doit échouer du côté du refus.
    """
    a = _pageouts()
    if a is None:
        return False
    time.sleep(fenetre)
    b = _pageouts()
    if b is None or b < a:
        return False
    ko_par_s = (b - a) * PAGE_SIZE_BYTES / 1024 / fenetre
    return ko_par_s < settings.pageout_block_kb_s


def _pressure_level() -> int | None:
    """Niveau de pression mémoire SELON macOS : 1 normal, 2 warn, 4 critique.

    C'est le verdict du système lui-même (celui qui pilote jetsam), et il vaut
    mieux que tout comptage de pages fait à la main. Première version de ce
    contrôle : je sommais les pages « free + speculative » de `vm_stat` en
    excluant « inactive », au motif que les récupérer suppose de la pagination.
    Faux — l'essentiel des pages inactives sont du cache fichier PROPRE, que le
    noyau libère sans rien écrire. Sur une machine fraîchement redémarrée et
    parfaitement saine, ce calcul annonçait 0,45 GB disponibles quand macOS
    rapportait 79 % de mémoire libre et une pression normale. Exactement le
    piège du contrôle de swap : alerter juste après un redémarrage.
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
    """Mémoire récupérable sans pagination, en Go — chiffre INDICATIF du log.

    Pages libres + spéculatives + inactives + purgeables. Sert à donner un ordre
    de grandeur dans le rapport, pas à décider : c'est `_pressure_level` qui
    tranche.
    """
    try:
        out = subprocess.run(
            ["vm_stat"], capture_output=True, text=True, timeout=5, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    taille = re.search(r"page size of (\d+) bytes", out)
    if not taille:
        return None
    total = 0
    for cle in ("Pages free", "Pages speculative", "Pages inactive",
                "Pages purgeable"):
        hit = re.search(rf"{cle}:\s+(\d+)", out)
        if hit:
            total += int(hit.group(1))
    return total * int(taille.group(1)) / 1e9


def _busy_daemons() -> list[tuple[str, float]] | None:
    """Démons d'entretien macOS actuellement gourmands. None si `ps` illisible.

    Retourne [(nom, %cpu)] trié décroissant, pour les seuls processus de
    `NOISY_DAEMONS` au-dessus du seuil d'avertissement. Le `%cpu` de `ps` est
    une moyenne sur la vie du processus, pas un instantané : un démon qui vient
    de se réveiller est donc sous-estimé — l'erreur va dans le bon sens pour un
    contrôle, jamais vers la fausse alerte.
    """
    try:
        out = subprocess.run(
            ["ps", "-Ao", "pcpu,comm", "-r"],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout
    except (subprocess.SubprocessError, OSError):
        return None

    trouves: list[tuple[str, float]] = []
    for line in out.splitlines()[1:]:
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        try:
            cpu = float(parts[0])
        except ValueError:
            continue
        if cpu < settings.daemon_warn_cpu:
            break  # `-r` trie par CPU décroissant : plus rien au-dessus du seuil
        nom = parts[1].rsplit("/", 1)[-1].strip()
        if nom in NOISY_DAEMONS:
            trouves.append((nom, cpu))
    return trouves


def _probe_generation(model: str, timeout: float = 120.0) -> str | None:
    """Fait RÉELLEMENT générer un token. Retourne None si tout va bien, sinon la
    raison de l'échec.

    Sans cette sonde, le contrôle d'Ollama se limitait à `/api/ps`, qui répond
    200 avec une liste vide quand rien n'est chargé — indiscernable d'une
    machine saine. Or après une MISE EN VEILLE, le démon Ollama survit mais ne
    parvient plus à lancer `llama-server` : « timed out waiting for llama-server
    to start », et TOUTES les requêtes rendent 500. Mesuré le 2026-08-07 après
    une nuit de veille. Un préflight qui ne fait pas générer un token ne dit rien
    de ce qui compte. Remède : `launchctl kickstart -k gui/$(id -u)/local.ollama`.
    """
    # `keep_alive: 0` : la sonde rend la mémoire qu'elle emprunte. Sans ça elle
    # laisserait le modèle chaud, et le run démarrerait avec deux modèles en
    # co-résidence — la pression mémoire que ce préflight existe pour empêcher.
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
    """Modèles actuellement chauds, embedders exclus. None si Ollama muet.

    On filtre sur la taille : `/api/ps` ne distingue pas un embedder d'un
    LLM, mais 370 MB contre 13 GB, l'écart tranche tout seul.
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


def preflight(*, strict: bool = True, chrono: bool = False) -> list[str]:
    """Vérifie la machine. Retourne les avertissements non bloquants.

    Lève PreflightError sur une condition qui a déjà fait planter la machine.
    `strict=False` dégrade tout en avertissement (itération de dev).

    `chrono=True` ajoute les conditions qui ne menacent pas la machine mais
    faussent les DURÉES : c'est le mode des runs dont le chiffre est l'objet
    (run de référence, répétition, génération de scène). Un test de style, lui,
    juge de la prose et se moque des secondes — il n'a pas à exiger un
    redémarrage.
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
        pass  # Aucun swapfile alloué : machine fraîche, rien à signaler.
    elif swap["free"] < settings.min_swap_free_gb and _swap_froid():
        warnings.append(
            f"Swap : {swap['free']:.2f} GB libres sur {swap['total']:.1f} GB "
            f"alloués, mais FROID (moins de "
            f"{settings.pageout_block_kb_s:.0f} Ko/s de pageouts sur "
            f"{PAGEOUT_FENETRE_S:.0f} s). Ce sont des pages froides que personne "
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
        # Bloquant seulement quand on chronomètre : un swap consommé ne casse
        # pas la machine (le disque, lui, si — cf. min_disk_gb), il rend les
        # durées ininterprétables.
        if chrono:
            blocking.append(
                msg + " Mesure de temps refusée dans cet état : les durées "
                "seraient ininterprétables."
            )
        else:
            warnings.append(msg)

    niveau = _pressure_level()
    if niveau is None:
        warnings.append("Pression mémoire : état illisible (sysctl).")
    elif niveau >= PRESSURE_BLOCK:
        blocking.append(
            "Pression mémoire CRITIQUE selon macOS "
            f"(kern.memorystatus_vm_pressure_level = {niveau}). Le système est "
            "déjà en train de récupérer de la mémoire de force ; une génération "
            "de vingt minutes va paginer au lieu de générer. Remède : décharger "
            "le modèle (`ollama stop <modèle>`) et fermer les gros consommateurs "
            "— c'est ce qui rend la mémoire, pas le redémarrage. Redémarrer "
            "seulement si la pression ne retombe pas."
        )
    elif niveau >= 2:
        warnings.append(
            f"Pression mémoire élevée selon macOS (niveau {niveau}). Fermer ce "
            "qui n'est pas nécessaire avant de lancer."
        )

    demons = _busy_daemons()
    if demons is None:
        warnings.append("Démons d'entretien : état illisible (ps).")
    elif demons:
        detail = ", ".join(f"{nom} {cpu:.0f} %" for nom, cpu in demons)
        pire = max(cpu for _, cpu in demons)
        if pire >= settings.daemon_block_cpu:
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
        echec = _probe_generation(settings.probe_model)
        if echec:
            blocking.append(
                f"Ollama ne GÉNÈRE pas : {echec}. Le démon écoute mais ne peut "
                "plus lancer llama-server — typiquement après une mise en veille. "
                "Remède : `launchctl kickstart -k gui/$(id -u)/local.ollama`. "
                "Et empêcher la veille avant la scène (`caffeinate -is`)."
            )

    llms = _loaded_llms()
    if llms is None:
        warnings.append(f"Ollama injoignable sur {settings.ollama_url} — état inconnu.")
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
    ram = _ram_available_gb()
    niveau = _pressure_level()
    demons = _busy_daemons()
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
    niveau_txt = {1: "normale", 2: "élevée", 4: "critique"}.get(niveau, "?")
    demons_txt = (
        ", ".join(f"{n} {c:.0f} %" for n, c in demons) if demons
        else ("aucun" if demons is not None else "?")
    )
    return (
        f"disque {disk:.1f} GB libres | swap {swap_txt} | "
        f"mémoire récupérable {ram_txt}, pression {niveau_txt} | "
        f"entretien macOS : {demons_txt} | LLM chauds : {llm_txt}"
    )


if __name__ == "__main__":
    print(report())
    try:
        for w in preflight():
            print(f"  ⚠ {w}")
    except PreflightError as exc:
        raise SystemExit(str(exc))
