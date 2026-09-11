#!/usr/bin/env python3
"""Client LLM minimal vers Ollama (rôle « auteur »).

Un seul modèle chaud sert les deux rôles du projet (auteur / acteur) : on ne
multiplie pas les instances, la cohérence vient de la mémoire externe partagée.
Le modèle auteur a été tranché au benchmark : mistral-nemo Q8_0 (ADR-0008).

La garde française est PRÉPENDUE à chaque prompt système : le benchmark a
montré que nemo laisse fuir un mot anglais de temps à autre (« Suddenly »),
et une consigne explicite « exclusivement en français » suffit à le juguler.

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

    # --- lifecycle ------------------------------------------------------------

    def unload(self, model: str | None = None, timeout: float = 60.0) -> bool:
        """Décharge un modèle d'Ollama (`keep_alive: 0`). Retourne le succès.

        Appelé au passage écriture → QA. Sans ça, nemo (13 GB) reste chaud pendant
        que Qwen (4,8 GB) se charge : 17,8 GB demandés sur 19,3 GB de mémoire
        unifiée, c'est-à-dire la pression exacte qui a fait paniquer la machine.
        `OLLAMA_MAX_LOADED_MODELS=2` AUTORISE cette co-résidence, il ne la prévient
        pas — la limite compte les modèles, pas les gigaoctets.
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
        """Consomme un flux NDJSON d'Ollama et rend un objet final au format
        non-streamé (dernier fragment + contenu complet recollé).

        Ollama envoie du JSON délimité par des sauts de ligne : un objet par token,
        puis un dernier objet `done: true` qui porte TOUS les compteurs. On recolle
        le texte et on rend ce dernier objet enrichi, pour que le calcul de
        métriques en aval soit identique dans les deux modes — sans quoi le
        streaming aurait ses propres chiffres, donc ses propres bugs.
        """
        morceaux: list[str] = []
        final: dict = {}
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for ligne in resp:
                ligne = ligne.strip()
                if not ligne:
                    continue
                try:
                    bloc = json.loads(ligne)
                except json.JSONDecodeError:
                    continue
                fragment = (bloc.get("message") or {}).get("content", "")
                if fragment:
                    morceaux.append(fragment)
                    on_token(fragment, len(morceaux))
                if bloc.get("done"):
                    final = bloc
        final["message"] = {"content": "".join(morceaux)}
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
        """Un tour de chat. Retourne (texte, métriques de timing).

        Les métriques (tok/s génération, prefill, durée) servent le compte à
        rebours et le profilage de la contrainte des 25 minutes de scène.
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
        """Chat MULTI-TOURS : `turns` est une liste de {role, content} déjà ordonnée.

        Nécessaire pour le mode acteur, où le modèle doit voir l'échange en cours
        comme un dialogue et non comme un bloc de texte reformaté. La garde
        française est prépendue au système, comme partout ailleurs.

        `on_token(fragment, cumul)` active le STREAMING. Sans callback, la requête
        reste non-streamée, à l'octet près comme avant : le pipeline auteur a été
        mesuré et validé dans ce mode, et l'habillage de démo ne doit pas rejouer
        cette validation. Le streaming ne sert qu'à montrer le travail en cours —
        les métriques finales sont identiques, Ollama les envoie dans son dernier
        fragment.

        Fenêtre de contexte EXPLICITE (`num_ctx`, 8192 par défaut). Sans ce
        réglage, Ollama applique 4096, or un appel d'écriture pèse 2-3k tokens
        de prompt système + jusqu'à 1400 tokens générés. Au dépassement, Ollama
        ne lève pas d'erreur : il fait GLISSER la fenêtre et ampute le DÉBUT du
        prompt, c'est-à-dire FRENCH_GUARD puis les faits de la bible.
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

        # Estimation CÔTÉ CLIENT de la taille du prompt. Indispensable : Ollama
        # tronque silencieusement puis ne rapporte QUE ce qu'il a évalué. Vérifié
        # à la main — prompt de ~2400 tokens envoyé avec num_ctx=512 : réponse
        # `prompt_eval_count: 258`. Autrement dit `prompt_eval_count / num_ctx` ne
        # dépasse JAMAIS 1 et ne détecte donc rien. La seule alarme fiable est
        # l'écart entre ce qu'on a envoyé et ce qu'Ollama dit avoir lu.
        # 3,3 caractères par token : calibré contre le compte réel d'Ollama sur un
        # prompt français de 4065 tokens (chars/3.5 le sous-estimait de 6 %, et
        # une estimation basse est le mauvais sens de l'erreur pour une alarme).
        # ~8 caractères de balisage de rôle par message (`<|im_start|>user\n`…).
        corps = sum(len(t.get("content", "")) + 8 for t in turns)
        est = int((len(FRENCH_GUARD) + len(system) + corps + 8) / 3.3)
        metrics = {
            "wall_s": round(wall, 1),
            "gen_toks": ec,
            "gen_tok_s": round(ec / ed, 1) if ed else 0.0,
            "prompt_toks": pc,
            "prefill_tok_s": round(pc / pd, 1) if pd else 0.0,
            "num_predict": num_predict,
            "num_ctx": num_ctx,
            # Occupation de la fenêtre TELLE QU'OLLAMA LA VOIT. Utile pour dimen-
            # sionner, inutile comme alarme : plafonnée à 1 par construction.
            "ctx_fill": round((pc + ec) / num_ctx, 2) if num_ctx else 0.0,
            # Occupation ESTIMÉE avant envoi, génération comprise. C'est elle qui
            # dit si on frôle la fenêtre : > 1.0 = la fin de génération sera
            # rognée, ou le début du prompt amputé.
            "ctx_need": round((est + num_predict) / num_ctx, 2) if num_ctx else 0.0,
            "est_prompt_toks": est,
            # Alarme d'amputation : Ollama dit avoir lu nettement moins que ce
            # qu'on a envoyé. La marge de 25 % absorbe l'imprécision de
            # l'estimation en caractères ; en dessous, c'est une troncature.
            "ctx_truncated": bool(est > 200 and pc < 0.75 * est),
            # « length » = coupé par num_predict ; « stop » = fin naturelle (EOS).
            "done_reason": data.get("done_reason", "?"),
        }
        return data["message"]["content"].strip(), metrics


client = OllamaClient()


def chat(*args, **kwargs) -> tuple[str, dict]:
    return client.chat(*args, **kwargs)


def chat_turns(*args, **kwargs) -> tuple[str, dict]:
    return client.chat_turns(*args, **kwargs)


def unload(*args, **kwargs) -> bool:
    return client.unload(*args, **kwargs)
