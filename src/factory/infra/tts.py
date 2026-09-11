#!/usr/bin/env python3
"""Rendu du chapitre en voix clonée (Qwen3-TTS via MLX), LOCAL.

Dernière étape du pipeline de démo : le clone reprend la lecture là où la voix
humaine s'arrête (cf. `chapitre.py` pour le marqueur de bascule).

## Pourquoi ce module existe alors que `../TTS/lire_chapitre.py` fait déjà le
## rendu

Parce que ce script est une CLI, pas une bibliothèque. Sa boucle de rendu vit
dans `main()`, collée à `argparse`, et son `charger_texte()` appelle
`sys.exit()` quand le marqueur manque. Dans un serveur, `SystemExit` est une
`BaseException` : elle traverse un `except Exception`, tue le thread en silence
et laisse le job bloqué en « generating » pour toujours. On ne l'importe donc
pas.

Ce que les deux dépôts partagent n'est pas du code mais **la voix** —
`voix/ma-voix.wav` et sa transcription — et l'identifiant du modèle. Leur script
comme ce module sont des clients minces de `mlx_audio` : quinze lignes autour de
`load_model().generate()`. `TTS/RUNBOOK.md` reste la référence des paramètres
(modèle, segments courts, pause, langue) ; si l'un bouge là-bas, il bouge ici.

L'import de `mlx_audio` est PARESSEUX, fait dans la fonction de rendu : ce module
est importé par un serveur qui vit des heures et ne synthétise qu'une fois, il
n'a pas à porter `mlx` + `transformers` en mémoire tout ce temps.
"""

import time
from pathlib import Path

from factory.infra import progress
from factory.pipeline.assembly import audio_excerpt
from factory.settings import settings

# Modèle, référence vocale (asset du dépôt TTS voisin : la SEULE dépendance
# inter-dépôts, en lecture seule), taille des segments (courts = prosodie
# stable, pas de dérive du clone) et pause : `settings.tts_*`, `settings.voice_dir`.
DEFAULT_SAMPLE_RATE = 24_000


class TTSUnavailable(RuntimeError):
    """Rendu impossible (référence vocale absente, mlx-audio non installé…).

    Exception ORDINAIRE, pas un `sys.exit` : l'appelant est un serveur, il doit
    pouvoir la rattraper, la journaliser et laisser le deck basculer en silence.
    """


def split_segments(text: str, *, max_chars: int | None = None) -> list[str]:
    """Découpe en segments courts, jamais au milieu d'une phrase."""
    from factory.text import sentence_ends

    if max_chars is None:
        max_chars = settings.tts_max_chars
    segments: list[str] = []
    for para in text.split("\n\n"):
        para = " ".join(para.split())
        if not para:
            continue
        if len(para) <= max_chars:
            segments.append(para)
            continue
        block, start = "", 0
        for end in sentence_ends(para) + [len(para)]:
            sentence = para[start:end].strip()
            start = end
            if not sentence:
                continue
            if block and len(block) + len(sentence) + 1 > max_chars:
                segments.append(block)
                block = sentence
            else:
                block = f"{block} {sentence}".strip()
        if block:
            segments.append(block)
    return segments


def _reference() -> tuple[str, str]:
    """Chemin du WAV de référence et sa transcription. Lève si absents."""
    voice_dir = settings.voice_dir
    wav, txt = voice_dir / "ma-voix.wav", voice_dir / "ma-voix.txt"
    if not wav.exists() or not txt.exists():
        raise TTSUnavailable(
            f"référence vocale manquante dans {voice_dir} "
            "(ma-voix.wav + ma-voix.txt attendus)"
        )
    return str(wav), txt.read_text(encoding="utf-8").strip()


def render(text: str, output: Path, *, model_id: str | None = None,
           pause_s: float | None = None) -> dict:
    """Synthétise `texte` dans la voix de référence, écrit un WAV, rend les
    métriques (durée d'audio, durée de calcul, facteur temps réel).

    Le facteur temps réel est LA mesure qui compte : il dit si la synthèse tient
    dans la queue du compte à rebours. Le RUNBOOK l'annonce à ~1×, à confirmer
    sur cette machine.
    """
    model_id = model_id or settings.tts_model
    pause_s = settings.tts_pause_s if pause_s is None else pause_s
    ref_audio, ref_text = _reference()
    segments = split_segments(text)
    if not segments:
        raise TTSUnavailable("aucun texte à lire après la bascule")

    try:
        import numpy as np
        import soundfile as sf
        from mlx_audio.tts.utils import load_model
    except ImportError as exc:
        raise TTSUnavailable(
            f"dépendances TTS absentes du venv ({exc}). "
            "pip install mlx-audio soundfile numpy"
        ) from exc

    progress.phase("Restitution", "préparation")
    model = load_model(model_id)

    sr = DEFAULT_SAMPLE_RATE
    tracks = []
    t0 = time.time()
    for i, segment in enumerate(segments, 1):
        progress.phase("Restitution",
                       f"segment {i}/{len(segments)}", i=i, n=len(segments))
        for result in model.generate(
            text=segment, ref_audio=ref_audio, ref_text=ref_text,
            lang_code="french",
        ):
            tracks.append(np.asarray(result.audio))
            sr = getattr(result, "sample_rate", sr)
        tracks.append(np.zeros(int(sr * pause_s), dtype=np.float32))

    audio = np.concatenate(tracks)
    output.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output, audio, sr)

    compute_s = time.time() - t0
    duration = len(audio) / sr
    # Rendre la mémoire du GPU : ce processus vit encore des heures après, et la
    # pression mémoire est l'ennemi numéro un de cette machine.
    try:
        import mlx.core as mx

        mx.clear_cache()
    except Exception:                                   # noqa: BLE001
        pass

    # Le débit du clone est une HYPOTHÈSE (190 mots/min, mesurés sur un seul
    # échantillon) qui sert à convertir la durée voulue par le deck en nombre de
    # mots. Si elle est fausse, l'extrait sort trop court ou trop long, et
    # personne ne s'en aperçoit avant la scène — sauf si on le dit ici.
    cible_s = settings.audio_seconds
    gap = duration - cible_s
    if abs(gap) > settings.audio_tolerance_s:
        progress.note(
            f"durée de lecture hors cible : {duration:.0f} s au lieu de "
            f"{cible_s:.0f} s ({gap:+.0f} s). Recalibrer "
            f"AUDIO_WORDS_PER_MINUTE (actuel {settings.audio_words_per_minute:.0f} mots/min, "
            f"réel {len(text.split()) / (duration / 60):.0f})."
        )

    return {
        "segments": len(segments),
        "audio_s": round(duration, 1),
        "cible_s": cible_s,
        "debit_mots_min": round(len(text.split()) / (duration / 60), 1),
        "calcul_s": round(compute_s, 1),
        "facteur_temps_reel": round(duration / compute_s, 2) if compute_s else 0.0,
        "sample_rate": sr,
        "sortie": str(output),
    }


def render_chapter(markdown: str, output: Path, **kwargs) -> dict:
    """Rend la portion post-bascule et bornée d'un chapitre Markdown."""
    return render(audio_excerpt(markdown), output, **kwargs)
