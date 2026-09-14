#!/usr/bin/env python3
"""Minimal LLM client for Ollama (the author role).

One warm model serves both roles of the project (author / actor): instances
are not multiplied, coherence comes from the shared external memory
(ADR-0006). The author model was settled by benchmark: mistral-nemo Q8_0
(ADR-0008).

The French guard is PREPENDED to every system prompt: the benchmark showed
nemo leaking an English word now and then (« Suddenly »), and an explicit
« exclusivement en français » instruction is enough to curb it.

ONE client object. The module-level functions ``chat``, ``chat_turns`` and
``unload`` delegate to ``client`` at call time, so swapping the client (a fake
in tests, another backend later) happens in one place whatever a module
imported.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from factory.settings import Settings, settings
from factory.text import FRENCH_GUARD


class OllamaClient:
    def __init__(self, config: Settings | None = None):
        self.settings = config or settings
        # When a list, every call appends {model, system, user, ...}: the run
        # writes it as its `prompts.md` (the served prompt is a deliverable).
        self.recording: list[dict] | None = None

    # --- lifecycle ------------------------------------------------------------

    def unload(self, model: str | None = None, timeout: float = 60.0) -> bool:
        """Unload a model from Ollama (`keep_alive: 0`). Return success.

        Called at the writing → QA swap (ADR-0008). Without it nemo (13 GB)
        stays warm while Qwen (4.8 GB) loads: 17.8 GB requested of 19.3 GB of
        unified memory, the exact pressure that panicked the machine.
        `OLLAMA_MAX_LOADED_MODELS=2` ALLOWS this co-residence, it does not
        prevent it: the limit counts models, not gigabytes.
        """
        model = model or self.settings.author_model
        payload = json.dumps({"model": model, "keep_alive": 0}).encode()
        req = urllib.request.Request(
            f"{self.settings.ollama_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                json.loads(resp.read())
            return True
        except (urllib.error.URLError, OSError, json.JSONDecodeError):
            return False

    # --- generation -----------------------------------------------------------

    @staticmethod
    def _read_stream(req: urllib.request.Request, timeout: float, on_token) -> dict:
        """Consume an Ollama NDJSON stream and return a final object in the
        non-streamed format (last fragment + full content glued back).

        Ollama sends newline-delimited JSON: one object per token, then a last
        `done: true` object carrying ALL the counters. The text is glued back
        and that last object returned enriched, so the downstream metrics
        computation is identical in both modes; otherwise streaming would have
        its own figures, hence its own bugs.
        """
        pieces: list[str] = []
        final: dict = {}
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for line in resp:
                line = line.strip()
                if not line:
                    continue
                try:
                    block = json.loads(line)
                except json.JSONDecodeError:
                    continue
                fragment = (block.get("message") or {}).get("content", "")
                if fragment:
                    pieces.append(fragment)
                    on_token(fragment, len(pieces))
                if block.get("done"):
                    final = block
        final["message"] = {"content": "".join(pieces)}
        return final

    def chat(
        self,
        system: str,
        user: str,
        *,
        model: str | None = None,
        temperature: float = 0.8,
        num_predict: int = 1200,
        num_ctx: int | None = None,
        timeout: float = 900.0,
        on_token=None,
    ) -> tuple[str, dict]:
        """One chat turn. Return (text, timing metrics).

        The metrics (generation tok/s, prefill, duration) feed the countdown
        and the profiling of the 25-minute stage constraint.
        """
        return self.chat_turns(
            system, [{"role": "user", "content": user}],
            model=model, temperature=temperature, num_predict=num_predict,
            num_ctx=num_ctx, timeout=timeout, on_token=on_token,
        )

    def chat_turns(
        self,
        system: str,
        turns: list[dict],
        *,
        model: str | None = None,
        temperature: float = 0.8,
        num_predict: int = 1200,
        num_ctx: int | None = None,
        timeout: float = 900.0,
        on_token=None,
    ) -> tuple[str, dict]:
        """MULTI-TURN chat: `turns` is an already ordered list of {role, content}.

        Needed by the actor mode, where the model must see the exchange as a
        dialogue and not as a reformatted block of prose. The French guard is
        prepended to the system prompt, as everywhere else.

        `on_token(fragment, cumulative)` enables STREAMING. Without a callback
        the request stays non-streamed, byte for byte as before: the author
        pipeline was measured and validated in that mode, and the demo
        dressing must not replay that validation. Streaming only shows the
        work in progress; the final metrics are identical, Ollama sends them
        in its last fragment.

        EXPLICIT context window (`num_ctx`, 8192 by default). Without it
        Ollama applies 4096, while a writing call weighs 2-3k tokens of system
        prompt + up to 1400 generated tokens. At overflow Ollama raises no
        error: it SLIDES the window and cuts the HEAD of the prompt, that is
        FRENCH_GUARD then the bible facts (ADR-0008).
        """
        model = model or self.settings.author_model
        num_ctx = num_ctx or self.settings.num_ctx
        payload = json.dumps(
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": f"{FRENCH_GUARD}\n\n{system}"},
                    *turns,
                ],
                "stream": on_token is not None,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                    "num_ctx": num_ctx,
                    **self.settings.sampling_options(),
                },
            }
        ).encode()
        req = urllib.request.Request(
            f"{self.settings.ollama_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        t0 = time.time()
        if on_token is None:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
        else:
            data = self._read_stream(req, timeout, on_token)
        wall = time.time() - t0

        ec = data.get("eval_count", 0)
        ed = data.get("eval_duration", 1) / 1e9
        pc = data.get("prompt_eval_count", 0)
        pd = data.get("prompt_eval_duration", 1) / 1e9

        # CLIENT-SIDE estimate of the prompt size. Indispensable: Ollama
        # truncates silently, then reports ONLY what it evaluated. Checked by
        # hand: a ~2400-token prompt sent with num_ctx=512 answered
        # `prompt_eval_count: 258`. So `prompt_eval_count / num_ctx` NEVER
        # exceeds 1 and detects nothing; the only reliable alarm is the gap
        # between what was sent and what Ollama says it read (ADR-0008).
        # 3.3 characters per token: calibrated against Ollama's real count for a
        # 4065-token French prompt (chars/3.5 underestimated it by 6 %, and a
        # low estimate is the wrong direction of error for an alarm).
        # ~8 characters of role markup per message (`<|im_start|>user\n`…).
        body = sum(len(t.get("content", "")) + 8 for t in turns)
        est = int((len(FRENCH_GUARD) + len(system) + body + 8) / 3.3)
        metrics = {
            "wall_s": round(wall, 1),
            "gen_toks": ec,
            "gen_tok_s": round(ec / ed, 1) if ed else 0.0,
            "prompt_toks": pc,
            "prefill_tok_s": round(pc / pd, 1) if pd else 0.0,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
            # Window occupancy AS OLLAMA SEES IT. Useful for sizing, useless as
            # an alarm: capped at 1 by construction.
            "ctx_fill": round((pc + ec) / num_ctx, 2) if num_ctx else 0.0,
            # ESTIMATED occupancy before sending, generation included. This one
            # says whether the window is close: > 1.0 = the end of generation
            # will be clipped, or the head of the prompt cut.
            "ctx_need": round((est + num_predict) / num_ctx, 2) if num_ctx else 0.0,
            "est_prompt_toks": est,
            # Truncation alarm: Ollama says it read markedly less than what was
            # sent. The 25 % margin absorbs the imprecision of the character
            # estimate; below it, this is a truncation.
            "ctx_truncated": bool(est > 200 and pc < 0.75 * est),
            # « length » = cut by num_predict; « stop » = natural end (EOS).
            "done_reason": data.get("done_reason", "?"),
        }
        if self.recording is not None:
            self.recording.append({
                "model": model, "system": system,
                "user": turns[-1].get("content", "") if turns else "",
                "turns": len(turns), "num_predict": num_predict,
                "temperature": temperature, "gen_toks": ec, "wall_s": metrics["wall_s"],
            })
        return data["message"]["content"].strip(), metrics


client = OllamaClient()


def chat(*args, **kwargs) -> tuple[str, dict]:
    return client.chat(*args, **kwargs)


def chat_turns(*args, **kwargs) -> tuple[str, dict]:
    return client.chat_turns(*args, **kwargs)


def unload(*args, **kwargs) -> bool:
    return client.unload(*args, **kwargs)
