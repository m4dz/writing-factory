"""One settings object for the whole factory (ADR-0002).

Every knob the operator can turn lives here with its default, and the
environment overrides it once at import (`settings = Settings.from_env()`).
Modules read `settings.<field>` at call time, never at import, so a test or
a CLI can change a value and see it applied.

What is NOT here: chapter knowledge (`chapters/`, author-owned) and the
repository paths (`factory.paths`). Configuration says how the machine runs;
the chapter spec says what the chapter is.

Environment variable names are English. The well-known ones are unchanged
(`OLLAMA_URL`, `CHROMA_HOST`, `TELEGRAM_BOT_TOKEN`, `API_PORT`, …); the
formerly French ones map as follows:

| former | now |
|---|---|
| `AUDIO_SECONDES` | `AUDIO_SECONDS` |
| `AUDIO_DEBIT_MOTS_MIN` | `AUDIO_WORDS_PER_MINUTE` |
| `AUDIO_MOTS_MAX` | `AUDIO_MAX_WORDS` |
| `BASCULE_APRES_PHRASES` | `SWITCH_AFTER_SENTENCES` |
| `MODELE_GESTES` | `GESTURE_MODEL` |
| `TEMP_GESTES` | `GESTURE_TEMPERATURE` |
| `ASSEMBLAGE` | `PRUNING` |
| `TELEGRAM_PERIODE_S` | `TELEGRAM_PERIOD_S` |
| `TTS_MAX_CAR` | `TTS_MAX_CHARS` |
| `RP_KEEP_TURNS` | `ROLEPLAY_KEEP_TURNS` |
| `DEMO_BUDGET_MIN` | `STAGE_BUDGET_MIN` |
| `XP_TIRAGES`, `XP_TEMP` | `XP_DRAWS`, `XP_TEMPERATURE` |
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from factory import paths


def _flag(value: str) -> bool:
    return value.strip().lower() not in ("0", "false", "no", "off", "")


def _path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else paths.REPO_ROOT / p


@dataclass
class Settings:
    # --- Ollama and models ----------------------------------------------------
    ollama_url: str = "http://localhost:11434"
    author_model: str = "mistral-nemo:12b-instruct-2407-q8_0"
    qa_model: str = "qwen2.5:7b-instruct"
    embed_model: str = "nomic-embed-text"
    num_ctx: int = 8192
    gesture_model: str = ""                  # empty: the author model
    gesture_temperature: float = 0.3
    beats_n: int = 3
    pruning_enabled: bool = True
    # Sampling of the WRITING calls (single call, segments, beats, best-of
    # variants). The temperature was a constant 0.7 in node code until
    # ADR-0026 reopened the writer; the other three are sent to Ollama only
    # when set, so the default request is byte-identical to the measured one.
    write_temperature: float = 0.7
    min_p: float | None = None
    top_p: float | None = None
    repeat_penalty: float | None = None

    # --- vector store and bible -----------------------------------------------
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    author_collection: str = "auteur"
    sessions_collection: str = "sessions"
    bible_dir: Path = paths.BIBLE_DIR
    style_path: Path = paths.BIBLE_DIR / "style-auteur.md"
    generated_dir: Path = paths.BIBLE_DIR / "generated"   # derived bible files (narrative state)

    # --- runs -----------------------------------------------------------------
    runs_dir: Path = paths.EXPERIMENTS_DIR / "runs"

    # --- API and stage --------------------------------------------------------
    api_host: str = "0.0.0.0"
    api_port: int = 8420
    cors_origin: str = "*"
    output_dir: Path = paths.OUTPUT_DIR
    slides_dir: Path = paths.REPO_ROOT.parent / "talk" / "slides" / "dist"
    chat_ttl_s: float = 7200.0
    stage_budget_min: float = 25.0

    # --- assembly and render --------------------------------------------------
    switch_after_sentences: int = 2
    audio_seconds: float = 165.0
    audio_words_per_minute: float = 177.0
    audio_tolerance_s: float = 15.0
    audio_max_words: int = 0                 # 0: derived from seconds × rate
    tts_model: str = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
    voice_dir: Path = paths.REPO_ROOT.parent / "TTS" / "voix"
    tts_max_chars: int = 400
    tts_pause_s: float = 0.6

    # --- roleplay -------------------------------------------------------------
    keep_turns: int = 6
    sessions_dir: Path = paths.SESSIONS_DIR

    # --- notifications --------------------------------------------------------
    telegram_token: str = ""
    telegram_chat_id: str = ""
    telegram_timeout_s: float = 5.0
    telegram_period_s: float = 300.0

    # --- preflight ------------------------------------------------------------
    min_disk_gb: float = 20.0
    min_swap_free_gb: float = 2.0
    pageout_block_kb_s: float = 1024.0
    daemon_warn_cpu: float = 30.0
    daemon_block_cpu: float = 80.0
    probe_model: str = "qwen2.5:7b-instruct"  # empty: no generation probe

    # --- experiments ----------------------------------------------------------
    xp_draws: int = 3
    xp_temperature: float = 0.7
    xp_num_predict: int = 300

    def sampling_options(self) -> dict:
        """The optional Ollama sampling options, only those set."""
        return {k: v for k, v in (("min_p", self.min_p), ("top_p", self.top_p),
                                  ("repeat_penalty", self.repeat_penalty)) if v is not None}

    @property
    def effective_gesture_model(self) -> str:
        return self.gesture_model or self.author_model

    @property
    def effective_audio_max_words(self) -> int:
        return self.audio_max_words or int(self.audio_words_per_minute * self.audio_seconds / 60)

    ENV = {
        "ollama_url": ("OLLAMA_URL", str),
        "author_model": ("AUTHOR_MODEL", str),
        "qa_model": ("QA_MODEL", str),
        "embed_model": ("EMBED_MODEL", str),
        "num_ctx": ("NUM_CTX", int),
        "gesture_model": ("GESTURE_MODEL", str),
        "gesture_temperature": ("GESTURE_TEMPERATURE", float),
        "beats_n": ("BEATS_N", int),
        "pruning_enabled": ("PRUNING", _flag),
        "write_temperature": ("WRITE_TEMPERATURE", float),
        "min_p": ("MIN_P", float),
        "top_p": ("TOP_P", float),
        "repeat_penalty": ("REPEAT_PENALTY", float),
        "chroma_host": ("CHROMA_HOST", str),
        "chroma_port": ("CHROMA_PORT", int),
        "author_collection": ("CHROMA_COLLECTION", str),
        "sessions_collection": ("CHROMA_SESSIONS", str),
        "bible_dir": ("BIBLE_DIR", _path),
        "style_path": ("STYLE_PATH", _path),
        "generated_dir": ("GENERATED_DIR", _path),
        "runs_dir": ("RUNS_DIR", _path),
        "api_host": ("API_HOST", str),
        "api_port": ("API_PORT", int),
        "cors_origin": ("API_CORS_ORIGIN", str),
        "output_dir": ("API_OUTPUT_DIR", _path),
        "slides_dir": ("API_SLIDES_DIR", _path),
        "chat_ttl_s": ("CHAT_TTL_S", float),
        "stage_budget_min": ("STAGE_BUDGET_MIN", float),
        "switch_after_sentences": ("SWITCH_AFTER_SENTENCES", int),
        "audio_seconds": ("AUDIO_SECONDS", float),
        "audio_words_per_minute": ("AUDIO_WORDS_PER_MINUTE", float),
        "audio_tolerance_s": ("AUDIO_TOLERANCE_S", float),
        "audio_max_words": ("AUDIO_MAX_WORDS", int),
        "tts_model": ("TTS_MODEL", str),
        "voice_dir": ("TTS_VOICE_DIR", _path),
        "tts_max_chars": ("TTS_MAX_CHARS", int),
        "tts_pause_s": ("TTS_PAUSE_S", float),
        "keep_turns": ("ROLEPLAY_KEEP_TURNS", int),
        "sessions_dir": ("SESSIONS_DIR", _path),
        "telegram_token": ("TELEGRAM_BOT_TOKEN", str.strip),
        "telegram_chat_id": ("TELEGRAM_CHAT_ID", str.strip),
        "telegram_timeout_s": ("TELEGRAM_TIMEOUT_S", float),
        "telegram_period_s": ("TELEGRAM_PERIOD_S", float),
        "min_disk_gb": ("PREFLIGHT_MIN_DISK_GB", float),
        "min_swap_free_gb": ("PREFLIGHT_MIN_SWAP_FREE_GB", float),
        "pageout_block_kb_s": ("PREFLIGHT_PAGEOUT_KB_S", float),
        "daemon_warn_cpu": ("PREFLIGHT_DAEMON_WARN_CPU", float),
        "daemon_block_cpu": ("PREFLIGHT_DAEMON_BLOCK_CPU", float),
        "probe_model": ("PREFLIGHT_PROBE_MODEL", str),
        "xp_draws": ("XP_DRAWS", int),
        "xp_temperature": ("XP_TEMPERATURE", float),
        "xp_num_predict": ("XP_NUM_PREDICT", int),
    }

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "Settings":
        env = os.environ if env is None else env
        s = cls()
        for field, (key, cast) in cls.ENV.items():
            if key in env:
                setattr(s, field, cast(env[key]))
        return s


settings = Settings.from_env()
