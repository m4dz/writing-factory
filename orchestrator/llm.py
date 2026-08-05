#!/usr/bin/env python3
"""Client LLM minimal vers Ollama (rôle « auteur »).

Un seul modèle chaud sert les deux rôles du projet (auteur / acteur) : on ne
multiplie pas les instances, la cohérence vient de la mémoire externe partagée.
Le modèle auteur a été tranché au benchmark : mistral-nemo Q8_0 (voir CLAUDE.md).

La garde française est PRÉPENDUE à chaque prompt système : le benchmark a
montré que nemo laisse fuir un mot anglais de temps à autre (« Suddenly »),
et une consigne explicite « exclusivement en français » suffit à le juguler.
"""

import json
import os
import time
import urllib.request

from style import FRENCH_GUARD

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
AUTHOR_MODEL = os.environ.get(
    "AUTHOR_MODEL", "mistral-nemo:12b-instruct-2407-q8_0"
)


def chat(
    system: str,
    user: str,
    *,
    model: str = AUTHOR_MODEL,
    temperature: float = 0.8,
    num_predict: int = 1200,
    timeout: float = 900.0,
) -> tuple[str, dict]:
    """Un tour de chat non-streamé. Retourne (texte, métriques de timing).

    Les métriques (tok/s génération, prefill, durée) servent le compte à
    rebours et le profilage de la contrainte des 35 minutes de scène.
    """
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "system", "content": f"{FRENCH_GUARD}\n\n{system}"},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": num_predict},
        }
    ).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    wall = time.time() - t0

    ec = data.get("eval_count", 0)
    ed = data.get("eval_duration", 1) / 1e9
    pc = data.get("prompt_eval_count", 0)
    pd = data.get("prompt_eval_duration", 1) / 1e9
    metrics = {
        "wall_s": round(wall, 1),
        "gen_toks": ec,
        "gen_tok_s": round(ec / ed, 1) if ed else 0.0,
        "prompt_toks": pc,
        "prefill_tok_s": round(pc / pd, 1) if pd else 0.0,
        "num_predict": num_predict,
        # « length » = coupé par num_predict ; « stop » = fin naturelle (EOS).
        "done_reason": data.get("done_reason", "?"),
    }
    return data["message"]["content"].strip(), metrics
