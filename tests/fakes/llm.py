"""A fake model that answers every node of the pipeline with crafted French text.

The dispatcher recognises the node from the prompt it receives (system prompt
identity for the QA and gesture nodes, user prompt shape for plan, write,
review and continuation). Each node has a NOMINAL fixture, conforming to the
validators the real pipeline applies to the model's output, so the graph takes
its nominal path; tests that exercise a retry or a rejection override one role.

Every call is recorded in ``calls`` with the exact system and user text served:
that recording is what the snapshot suite compares to the golden files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from factory.pipeline import qa
from factory.roleplay import session as roleplay
from fakes import fixtures as fx

Response = str | list[str]

_BEAT_MARKER = "AUCUNE étiquette de section"          # from graph._BEAT_SUFFIXE
_TARGET_RE = re.compile(r"(?:Longueur visée : |\()(\d+)(?: à |-)(\d+) mots")


@dataclass
class Call:
    role: str
    system: str
    user: str
    model: str
    num_predict: int
    temperature: float
    reply: str


@dataclass
class FakeModel:
    """``chat``/``chat_turns`` drop-in. ``responses`` overrides a role's text
    (a string, or a list consumed in order and repeating its last item)."""

    responses: dict[str, Response] = field(default_factory=dict)
    beats_n: int = 3
    calls: list[Call] = field(default_factory=list)
    _counters: dict[str, int] = field(default_factory=dict)

    # --- public surface mirroring llm.py --------------------------------------

    def chat(self, system: str, user: str, *, model: str = "fake",
             temperature: float = 0.8, num_predict: int = 1200,
             num_ctx: int = 8192, timeout: float = 0.0, on_token=None):
        role = self.recognise(system, user)
        text = self._reply(role, system, user)
        self.calls.append(Call(role, system, user, model, num_predict,
                               temperature, text))
        self._record(model, system, user, num_predict, temperature)
        if on_token:
            on_token(text, 1)
        return text, self._metrics(text, num_predict, num_ctx)

    def chat_turns(self, system: str, turns: list[dict], *, model: str = "fake",
                   temperature: float = 0.8, num_predict: int = 1200,
                   num_ctx: int = 8192, timeout: float = 0.0, on_token=None):
        user = "\n".join(f"{t['role']}: {t['content']}" for t in turns)
        role = "roleplay" if system.startswith("Tu ES ") else self.recognise(system, user)
        text = self._reply(role, system, user)
        self.calls.append(Call(role, system, user, model, num_predict,
                               temperature, text))
        self._record(model, system, user, num_predict, temperature)
        return text, self._metrics(text, num_predict, num_ctx)

    @staticmethod
    def _record(model, system, user, num_predict, temperature) -> None:
        """Mirror the real client's `recording` (the run's prompts.md)."""
        from factory.infra.ollama import client

        if client.recording is not None:
            client.recording.append({"model": model, "system": system, "user": user,
                                     "turns": 1, "num_predict": num_predict,
                                     "temperature": temperature, "gen_toks": 0, "wall_s": 0.0})

    def by_role(self, role: str) -> list[Call]:
        return [c for c in self.calls if c.role == role]

    # --- recognition ----------------------------------------------------------

    @staticmethod
    def recognise(system: str, user: str) -> str:
        if system == qa._FACTS_SYS:
            return "qa.facts"
        if system == qa._QUESTIONS_SYS:
            return "qa.questions"
        if system in (qa._ANSWER_SYS, qa._PLAN_ANSWER_SYS):
            return "qa.answers"
        if system in (qa._CONFIRM_SYS, qa._CONFIRM_PLAN_SYS):
            return "qa.confirm"
        if system == qa._REPAIR_SYS:
            return "repair"
        if system == roleplay._SUMMARY_SYS:
            return "roleplay.summary"
        if system.startswith("Tu ES "):
            return "roleplay"
        if system.startswith("Voici la partie d'une entrée de carnet"):
            return "accumulate"
        if user.startswith("Tu es un PLANIFICATEUR"):
            return "plan"
        if "Ta génération a été coupée" in user:
            return "continuation"
        if "Relis et RÉÉCRIS INTÉGRALEMENT" in user:
            return "review"
        if _BEAT_MARKER in user:
            return "write.beat"
        if "Écris seulement le DÉBUT" in user or "Tu écris le DÉBUT" in user:
            return "write.opening"
        if "Écris maintenant le MILIEU" in user or "Tu écris la SUITE" in user:
            return "write.reconstruction"
        if "Écris la FIN de l'entrée" in user or "Tu écris la FIN" in user:
            return "write.closing"
        if "Écris UNIQUEMENT l'entrée" in user or "trajectoire ENTIÈRE" in user:
            return "write.entry"
        return "unknown"

    # --- replies --------------------------------------------------------------

    def _reply(self, role: str, system: str, user: str) -> str:
        if role in self.responses:
            return self._pick(role, self.responses[role])
        if role == "qa.facts":
            return fx.FACTS
        if role == "qa.questions":
            n = len(re.findall(r"^\s*\d+\.\s", user, re.M))
            return "\n".join(f"{i}. Le texte montre-t-il l'événement {i} ?"
                             for i in range(1, n + 1))
        if role == "qa.answers":
            nums = re.findall(r"^Q(\d+) :", user, re.M)
            return "\n".join(f"Q{n} : NON" for n in nums)
        if role == "qa.confirm":
            return "NON"
        if role == "repair":
            return user
        if role == "review":
            return user.split("--- ENTRÉE À RÉÉCRIRE ---\n", 1)[1]
        if role == "continuation":
            return fx.CONTINUATION
        if role == "accumulate":
            m = re.search(r"L'étape qui cloche, imposée : (.+?)\. La phrase", system)
            fall = m.group(1) if m else "l'assiette"
            return fx.accumulation(fall)
        if role == "plan":
            return fx.PLAN
        if role == "roleplay":
            return fx.ROLEPLAY_REPLY
        if role == "roleplay.summary":
            return fx.ROLEPLAY_SUMMARY
        if role == "write.beat":
            k = self._counters.get(role, 0)
            self._counters[role] = k + 1
            return fx.BEATS[(k // self.beats_n) % len(fx.BEATS)]
        if role == "write.opening":
            return fx.OPENING
        if role == "write.reconstruction":
            return fx.RECONSTRUCTION
        if role == "write.closing":
            return fx.CLOSING
        if role == "write.entry":
            m = _TARGET_RE.search(user)
            if m and int(m.group(2)) <= 80:
                return fx.SHORT_ENTRY
            return fx.FULL_ENTRY
        raise AssertionError(f"fake model: unrecognised prompt\n--- system ---\n"
                             f"{system[:300]}\n--- user ---\n{user[:300]}")

    def _pick(self, role: str, response: Response) -> str:
        if isinstance(response, str):
            return response
        k = self._counters.get(role, 0)
        self._counters[role] = k + 1
        return response[min(k, len(response) - 1)]

    @staticmethod
    def _metrics(text: str, num_predict: int, num_ctx: int) -> dict:
        toks = max(1, len(text.split()))
        return {
            "wall_s": 0.0, "gen_toks": toks, "gen_tok_s": 10.0,
            "prompt_toks": 100, "prefill_tok_s": 100.0,
            "num_predict": num_predict, "num_ctx": num_ctx,
            "ctx_fill": 0.1, "ctx_need": 0.2, "est_prompt_toks": 100,
            "ctx_truncated": False, "done_reason": "stop",
        }
