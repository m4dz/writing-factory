#!/usr/bin/env python3
"""Lance les runs du test de style contre Ollama.

Chaque run est une requête /api/chat indépendante (contexte neuf : le modèle
ne s'auto-imite jamais). Le brief est extrait de la section `## Brief` de la
scène test. Le mode --control retire les lignes « Régime : … » du brief pour
isoler ce qui vit dans la fiche de ce qui n'est qu'obéissance à l'instruction.

Usage :
  python outillage/run_scene.py                    # 3 runs : 0.7 / 0.7 / 0.9
  python outillage/run_scene.py --control          # 1 run de contrôle
  python outillage/run_scene.py --runs 1           # run unique de reprise

Sorties : runs/run-1.md, run-2.md, run-3.md, run-controle.md
Stdlib uniquement : aucun pip install requis sur la machine hôte.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from factory.eval.lint import analyse, mots, normalise, phrases
from factory.paths import BIBLE_DIR, EXPERIMENTS_DIR
from factory.text import ends_mid_sentence

OLLAMA_URL = "http://localhost:11434"

# Protocole de `_scene-test-style.md` : 0.7 pour les runs 1-2 (température de
# production, cf. write_node), 0.9 pour le run 3 — celui-ci mesure si le style
# survit à la variance. La température est envoyée par APPEL et non figée dans
# le Modelfile : un `options` de requête écrase le `PARAMETER` du modèle, ce qui
# évite de construire un second modèle pour un seul scalaire (deux noms de
# modèle désaligneraient les colonnes de la grille).
TEMPERATURES = [0.7, 0.7, 0.9]
TEMP_CONTROLE = 0.7

# --- Boucle de renvoi ---------------------------------------------------------
#
# L'accumulation manquait sur 7 tirages sur 7 en session 1, y compris sur le run
# de 673 mots : nemo ne construit pas de propositions juxtaposées, quelle que
# soit la longueur qu'on lui laisse. Une fiche mieux écrite ne suffira pas —
# c'est la leçon déjà payée trois fois dans ce projet (`repair()` pour l'anglais,
# `hors_role()` pour le roleplay, la vérification du plan pour les faits) : le
# garde-fou qui tient est dans le CODE, le prompt ne fait que le préparer.
#
# UN SEUL renvoi. J'étais passé à DEUX en croyant lire une convergence : au
# premier renvoi, un run était monté de 23 mots / 2 virgules à 42 / 3, soit la
# moitié du chemin. Mesuré ensuite sur le vrai modèle, le second renvoi rend
# 40 mots / 3 virgules — le MÊME point. Ce n'est pas une convergence lente,
# c'est un plateau : nemo donne sa meilleure réponse au premier reproche et n'en
# bouge plus. Le second tour coûte une génération entière et n'achète rien.
#
# Le renvoi est CHIRURGICAL — on ne redemande pas la scène entière. Une
# régénération complète perdrait les couperets et la vérification matérielle,
# qui, eux, sont tenus. On cible le seul paragraphe fautif.
MAX_RENVOIS = 1
REGIME_LINE = re.compile(
    # Coupe depuis « Régime » (début OU milieu de ligne, gras ou non)
    # jusqu'à la fin de la ligne.
    r"\*{0,2}r[ée]gime\b\s*:?\*{0,2}[^\n]*",
    re.IGNORECASE,
)


def extract_brief(scene_path: Path) -> str:
    """Extrait la section `## Brief …` (jusqu'au prochain `## `)."""
    text = scene_path.read_text(encoding="utf-8")
    match = re.search(r"^## Brief.*?$(.*?)(?=^## |\Z)", text,
                      re.MULTILINE | re.DOTALL)
    if not match:
        print(f"ERREUR : pas de section '## Brief' dans {scene_path}",
              file=sys.stderr)
        sys.exit(1)
    return match.group(1).strip()


def strip_regime_lines(brief: str) -> tuple[str, int]:
    stripped, count = REGIME_LINE.subn("", brief)
    stripped = re.sub(r"\n{3,}", "\n\n", stripped)
    return stripped.strip(), count


# Le reproche ne MONTRE aucun texte d'exemple, et c'est tout le sujet.
#
# Première version : elle donnait l'étalon en disant « forme exacte à
# reproduire ». nemo l'a recopié CARACTÈRE POUR CARACTÈRE, deux fois sur deux
# réussites apparentes — insérant dans une scène de cafetière un paragraphe qui
# parle de clés et d'une coupelle. La forme était juste, le sens absurde, et le
# lint applaudissait.
#
# C'est la leçon déjà payée sur le mode acteur, mot pour mot : « donner des
# exemples de répliques les fait RECOPIER ; les exemples sont désormais formulés
# comme des attitudes, pas comme du texte. » On décrit donc le MOUVEMENT, on
# chiffre la contrainte, et on force l'ancrage dans les éléments de CETTE scène.
ACCUMULATION_ATTENDUE = """Ta scène ne contient aucune phrase d'accumulation. \
Sa phrase la plus longue fait {mots} mots et {virgules} virgule(s) — il en faut \
au moins 60 et au moins 6.

La phrase d'accumulation est le marqueur signature de ce style, et il en faut \
exactement une par scène. Réécris le paragraphe où le narrateur reprend sa \
journée pour en faire UNE SEULE phrase, sans aucun point ni point-virgule à \
l'intérieur, qui enchaîne :

1. le narrateur qui s'assoit et reprend les faits dans l'ordre ;
2. puis les étapes de SA journée, égrenées une par une, séparées par de \
simples virgules, sans aucun verbe conjugué — juste les choses et les heures ;
3. puis une rupture (« sauf une, une seule ») ;
4. puis l'étape qui cloche, étirée sur une dernière proposition.

CONTRAINTE ABSOLUE : n'utilise QUE les éléments déjà présents dans ta scène — \
la cafetière, le paquet de café, la poubelle, les horaires que tu as toi-même \
donnés, les personnes que tu as nommées. N'introduis aucun objet, aucun lieu et \
aucun nom nouveau. Si tu écris des clés, une coupelle ou une buanderie, tu as \
échoué : ce sont les objets d'une autre scène.

Rends la scène ENTIÈRE, à l'identique, en ne remplaçant QUE ce paragraphe. Ne \
touche à aucun autre paragraphe. Aucun commentaire, aucun titre."""


def chat_messages(model: str, messages: list[dict], timeout: int,
                  temperature: float) -> dict:
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        # Écrase le PARAMETER du Modelfile. num_ctx et num_predict, eux, sont
        # laissés au modèle : ils ne varient pas d'un run à l'autre.
        "options": {"temperature": temperature},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def generer_avec_renvoi(model: str, prompt: str, timeout: int,
                        temperature: float) -> tuple[str, dict]:
    """Génère la scène, puis la renvoie UNE fois si l'accumulation manque.

    Rend (texte, journal). Le journal note ce qui s'est passé — un renvoi qui
    échoue doit rester visible dans le run : sur scène comme à la relecture, un
    dispositif silencieux se lit comme un dispositif qui a marché.
    """
    messages = [{"role": "user", "content": prompt}]
    resultat = chat_messages(model, messages, timeout, temperature)
    texte = resultat["message"]["content"].strip()
    journal = {"renvois": 0, "renvoi_verdict": "non déclenché",
               "duree_s": resultat.get("total_duration", 0) / 1e9,
               "done_reason": resultat.get("done_reason", "?")}

    for _ in range(MAX_RENVOIS):
        lint = analyse(texte)
        if len(lint["accumulations"]) == 1:
            break
        # Chiffrer la faute plutôt que la nommer : « ta phrase la plus longue
        # fait 38 mots » est vérifiable par le modèle, « fais plus long » ne
        # l'est pas.
        plus_longue = max(phrases(normalise(texte)), key=mots, default="")
        reproche = ACCUMULATION_ATTENDUE.format(
            mots=mots(plus_longue), virgules=plus_longue.count(","))
        avant = texte
        messages += [{"role": "assistant", "content": texte},
                     {"role": "user", "content": reproche}]
        suite = chat_messages(model, messages, timeout, temperature)
        texte = suite["message"]["content"].strip()
        journal["renvois"] += 1
        journal["duree_s"] += suite.get("total_duration", 0) / 1e9
        journal["done_reason"] = suite.get("done_reason", "?")

        apres = analyse(texte)
        n = len(apres["accumulations"])
        journal["renvoi_verdict"] = (
            f"accumulation obtenue en {journal['renvois']} renvoi(s)" if n == 1
            else f"ÉCHEC — {n} accumulation(s) après {journal['renvois']} renvoi(s)")
        # Le renvoi demandait de ne changer QUE le paragraphe fautif. S'il a
        # tout réécrit, les acquis du premier jet (couperets, vérification
        # matérielle) ont pu partir avec : il faut que ça se voie.
        ecart = abs(len(texte) - len(avant)) / max(len(avant), 1)
        if ecart > 0.4:
            journal["renvoi_verdict"] += f" · scène réécrite à {ecart:.0%}"
        # Pas de `break` ici : c'est le test en tête de boucle qui sort, une
        # fois l'accumulation obtenue. Un break inconditionnel rendrait
        # MAX_RENVOIS sans effet — il l'a été le temps d'une version.

    return texte, journal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", default=str(BIBLE_DIR / "scenes" / "_scene-test-style.md"))
    parser.add_argument("--model", default="auteur-test")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--control", action="store_true",
                        help="Run de contrôle : brief sans les lignes régime")
    parser.add_argument("--out-dir", default=str(EXPERIMENTS_DIR / "runs" / "style-test"))
    parser.add_argument("--timeout", type=int, default=600,
                        help="Timeout par run en secondes")
    parser.add_argument("--temperatures", type=float, nargs="+",
                        default=TEMPERATURES,
                        help="Température par run (défaut : 0.7 0.7 0.9)")
    # Sans suffixe, un second run de contrôle écrase le premier — et la règle
    # « ne jamais conclure sur un seul tirage » deviendrait impossible à suivre
    # pour le bras qui en a le plus besoin.
    parser.add_argument("--suffixe", default="",
                        help="Suffixe de nom de fichier (ex. : 2 → run-controle-2.md)")
    # Le bras témoin de la boucle : sans lui, on ne saurait pas si c'est la
    # fiche v2 ou le renvoi qui a produit l'accumulation.
    parser.add_argument("--sans-renvoi", action="store_true",
                        help="Désactive la boucle de renvoi (mesure la fiche seule)")
    args = parser.parse_args()

    brief = extract_brief(Path(args.scene))
    label = "controle"
    if args.control:
        brief, removed = strip_regime_lines(brief)
        if removed == 0:
            print("ATTENTION : aucune ligne régime trouvée dans le brief — "
                  "le run de contrôle est identique au run standard.",
                  file=sys.stderr)
        else:
            print(f"Run de contrôle : {removed} lignes régime retirées.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True)

    prompt = (
        "Rédige la scène décrite dans le brief ci-dessous, en respectant "
        "les beats dans l'ordre. Rends uniquement le texte de la scène, "
        "sans titre ni commentaire.\n\n" + brief
    )

    runs = [0] if args.control else list(range(1, args.runs + 1))
    for n in runs:
        suffixe = f"-{args.suffixe}" if args.suffixe else ""
        name = (f"run-{label}{suffixe}" if args.control
                else f"run-{n}{suffixe}")
        # Au-delà de la liste fournie, on reconduit la dernière valeur plutôt
        # que d'échouer : `--runs 5` reste utilisable pour lever une zone grise.
        temp = (TEMP_CONTROLE if args.control
                else args.temperatures[min(n - 1, len(args.temperatures) - 1)])
        print(f"[{name}] génération en cours ({args.model}, temp={temp})…",
              flush=True)
        if args.sans_renvoi:
            result = chat_messages(
                args.model, [{"role": "user", "content": prompt}],
                args.timeout, temp)
            text = result["message"]["content"].strip()
            journal = {"renvois": 0, "renvoi_verdict": "désactivé",
                       "duree_s": result.get("total_duration", 0) / 1e9,
                       "done_reason": result.get("done_reason", "?")}
        else:
            text, journal = generer_avec_renvoi(
                args.model, prompt, args.timeout, temp)
        words = len(text.split())
        duration_s = journal["duree_s"]
        done_reason = journal["done_reason"]

        # Deux façons pour une scène de finir amputée, et une seule est
        # annoncée par Ollama. `length` = plafond de num_predict atteint ; une
        # fin pendante SANS `length` = nemo a émis son EOS en pleine phrase
        # (constaté au run de référence du chapitre). Dans les deux cas, les
        # lignes « clôture » et « phrase-couperet » de la grille échouent pour
        # une raison MÉCANIQUE : le run n'est pas scorable tel quel.
        alertes = []
        if done_reason == "length":
            alertes.append("TRONQUÉ par num_predict (done_reason=length)")
        if ends_mid_sentence(text):
            alertes.append("fin pendante (pas de ponctuation finale)")

        lint = analyse(text)
        avert = list(lint["delint"])

        out_path = out_dir / f"{name}.md"
        out_path.write_text(
            f"---\n"
            f"run: {name}\n"
            f"model: {args.model}\n"
            f"control: {args.control}\n"
            f"temperature: {temp}\n"
            f"date: {datetime.now().isoformat(timespec='seconds')}\n"
            f"mots: {words}\n"
            f"duree_s: {duration_s:.0f}\n"
            f"done_reason: {done_reason}\n"
            f"renvois: {journal['renvois']}\n"
            f"renvoi_verdict: {journal['renvoi_verdict']}\n"
            f"accumulations: {len(lint['accumulations'])}\n"
            f"alertes: {alertes if alertes else '[]'}\n"
            f"lint_delint: {avert if avert else '[]'}\n"
            f"---\n\n{text}\n",
            encoding="utf-8",
        )
        target = "OK" if 400 <= words <= 550 else "HORS CIBLE (400-550)"
        print(f"[{name}] {words} mots [{target}], {duration_s:.0f}s, "
              f"done={done_reason}, renvois={journal['renvois']} "
              f"({journal['renvoi_verdict']}) → {out_path}")
        for a in alertes:
            print(f"  ⚠ {a} — run NON scorable sur les lignes de clôture",
                  file=sys.stderr)
        for a in avert:
            print(f"  ⚠ {a}", file=sys.stderr)

    print("\nRuns terminés.")
    print("  Lint mécanique : python3 outillage/lint_style.py runs/*.md")
    print("  Grille détaillée : bible/scenes/_scene-test-style.md")
    print("  Grille de synthèse : outillage/grille-lint.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
