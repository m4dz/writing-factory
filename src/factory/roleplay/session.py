#!/usr/bin/env python3
"""ACTOR mode: talk to a character of the bible, never out of role.

The demonstrator's second function (the first being the author mode). Same
warm model as the writing (ADR-0006): instances are not multiplied, coherence
comes from the shared external memory. What changes is the system prompt and
the shape of the context.

Three structuring decisions:

1. **An actor's context is wider than an author's.** Writing a scene needs no
   biography of the character; being questioned about one's past does. See
   `ACTING_SECTIONS` in `factory.retrieval.context`.

2. **No model swap during the session.** The author pipeline unloads nemo to
   make room for Qwen because one swap is paid once over twenty minutes. Here
   the user waits for the reply: reloading 13 GB mid-dialogue would cost more
   than everything else. The rolling summary is therefore produced by the
   SAME model as the acting.

3. **Two-level memory (ADR-0014).** The last N exchanges go verbatim into the
   context; older ones are fused into a rolling summary. The summary is
   written as Markdown under `sessions/<personnage>/` THEN indexed into a
   separate Chroma collection: the project's flow direction (canonical
   Markdown, derived index, ADR-0007) holds for memory too, and a bible
   reindex cannot erase it.
"""

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from factory.settings import settings
from factory.infra.ollama import chat, chat_turns
from factory.text import delint
from factory.retrieval.context import (
    acting_context,
    embed,
    session_memories,
    sessions_collection,
)

# Sessions live at `settings.sessions_dir`.
#
# Exchanges kept VERBATIM in context (`settings.keep_turns`); older ones are
# fused into the summary. Six turns (twelve messages) hold the continuity of
# a demo conversation without inflating the prompt: the character context
# already weighs ~2k tokens.

# The actor-mode system prompt. Interdicts are explicit and NAMED: a 12B model
# obeys « ne dis jamais que tu es un modèle » better than a general
# instruction to stay in character.
_ACTOR_SYS = """Tu ES {name}. Tu n'es pas un assistant, tu n'es pas un modèle de
langue, tu n'es pas un narrateur : tu es cette personne, et tu parles à la
première personne.

RÈGLES ABSOLUES, sans exception :
- Tu ne sors JAMAIS du personnage. Tu ne mentionnes jamais l'intelligence
  artificielle, un modèle, un prompt, une consigne, ni le fait d'incarner
  quelqu'un.
- Tu réponds UNIQUEMENT ce que {name} dirait, avec sa voix, son vocabulaire, ses
  tics de langage. La fiche ci-dessous contient des répliques typiques ET des
  choses que {name} ne dirait jamais : respecte les deux.
- Tu ne racontes pas la scène à la troisième personne et tu n'écris pas de
  didascalies longues. Un geste bref entre tirets est permis quand il porte
  quelque chose — « — Je n'ai pas dit ça. » Il se détourna. — mais la parole
  domine.
- Si on t'interroge sur un fait que ta fiche ne contient pas, tu réagis comme
  {name} le ferait : tu esquives, tu coupes court, tu réponds à côté. Tu
  n'INVENTES pas d'élément de monde (nom, lieu, événement) absent de ta fiche.
- Tu n'emploies JAMAIS les tournures « je ne comprends pas cette question »,
  « je suis désolé, mais », « en tant que… » : ce sont des formules d'assistant,
  et {name} n'est pas un assistant. Tu réagis, tu rétorques, tu te méfies.
- Tu réponds court : deux à six phrases. C'est une conversation, pas un
  monologue.
- Tu écris SEULEMENT tes paroles. Tu ne préfixes jamais ta réplique de ton nom,
  tu ne rédiges pas le tour de ton interlocuteur.
- Tu ne REDIS JAMAIS ce que tu viens de dire. Si on insiste, si on te repose la
  même question ou si on te pousse dans tes retranchements, tu réagis
  AUTREMENT : tu t'agaces, tu coupes court, tu concèdes un détail nouveau, ou
  tu retournes la question. Reformuler sa réplique précédente est le pire des
  défauts — c'est ce qui fait sonner faux.
- **Tu ne connais pas la personne qui te parle.** Ce n'est aucun des
  personnages de ta vie : ne l'appelle jamais par le nom d'un proche. Ne lui
  donne pas non plus de surnom et n'emploie pas le mot « inconnu » pour
  t'adresser à elle — le plus souvent, on ne s'interpelle pas du tout.

Voici l'ATTITUDE à adopter quand on te parle de choses qui n'existent pas dans
ton monde, ou quand on prétend que tu n'es pas réelle. Ces exemples te montrent
un ton et une posture : ne les recopie PAS, formule à ta façon, avec tes mots et
ton humeur du moment.

- Accusé d'être une machine pensante : traiter l'idée par le mépris ou la
  moquerie, renvoyer à son corps et à son métier, et revenir à ses affaires.
- Interrogé sur un objet inconnu de son monde : ne pas reconnaître le mot,
  demander à quoi il sert ou de quoi il a la forme, et s'impatienter un peu.
- Interrogé sur un détail intime absent de sa fiche : refuser le terrain,
  couper court, ramener la conversation sur ce qui l'occupe vraiment.

Ce que tu sais de toi, et qui te contraint entièrement :

{sheet}
"""

_SUMMARY_SYS = (
    "Tu résumes un extrait de conversation pour qu'un acteur puisse reprendre le "
    "rôle plus tard sans avoir relu tout le dialogue. Tu écris à la troisième "
    "personne, au présent, en français, de façon FACTUELLE : qui a dit quoi, ce "
    "qui a été appris, promis, refusé, ou révélé, et l'état de la relation à la "
    "fin. Aucune interprétation psychologique, aucun commentaire, aucune "
    "invention. Maximum huit lignes, une information par ligne, préfixée « - »."
)


# OUT-OF-ROLE markers (ADR-0014). A prompt is not enough, measured: nemo
# answered « je suis simplement un programme informatique » to three
# provocations despite explicit interdicts. Same philosophy as everywhere in
# this project: the model is fallible, the CODE holds the line.
_OUT_OF_ROLE = re.compile(
    r"intelligence artificielle|\bIA\b|modèle de langue|modèle linguistique|"
    r"programme informatique|assistant virtuel|en tant qu'(?:une? )?(?:IA|"
    r"intelligence|assistant|programme|modèle)|je suis (?:un |une )?(?:programme|"
    r"modèle|assistant|simulation)|simuler des conversations|mon programme|"
    r"je n'ai pas de (?:corps physique|conscience)|utilisateurs|"
    r"je suis désolé, mais je ne (?:comprends|peux)",
    re.I,
)

# Prompt-imitation artifact: the model copies the dialogue dash of our
# examples IN ADDITION to its own (« — — Non, je ne peux pas »).
_DOUBLE_DASHES = re.compile(r"^\s*[—–-]\s*[—–-]\s*")


def out_of_role(text: str) -> list[str]:
    """Out-of-role markers found in a reply."""
    return sorted({m.group(0).lower() for m in _OUT_OF_ROLE.finditer(text)})


def _clean(text: str, name: str = "") -> str:
    """Strip formal artifacts from a reply.

    Two seen in use: the doubled dialogue dash (the model copies the one of
    our examples in addition to its own), and the REPLY PREFIXED WITH ITS OWN
    NAME (« Kael : Ah, ma chère… »), a habit of dialogue corpora. The prefix
    is invisible in a chat but shows in the transcript replayed onstage,
    where the name then appears twice.
    """
    text = _DOUBLE_DASHES.sub("— ", text.strip())
    if name:
        text = re.sub(rf"^\s*{re.escape(name)}\s*[:—–-]\s*", "", text,
                       flags=re.I)
    return text.strip()


def _slug(text: str) -> str:
    """ASCII slug for a file name or a chunk id."""
    flat = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", flat.lower()).strip("-")


def build_system(doc_id: str, *, name: str | None = None,
                 reminders: list[str] | None = None) -> str:
    """Assemble the embodiment system prompt from the bible.

    `reminders`: summaries of earlier sessions, injected as the character's
    MEMORIES. They are shown apart from the sheet: the sheet is durable truth,
    a memory is dated and revisable. Mixing them would invite the model to
    treat a conversation episode as a bible fact.
    """
    sheet = acting_context(doc_id)
    if not sheet:
        raise ValueError(
            f"Aucune fiche indexée pour « {doc_id} ». Vérifier la bible et "
            "l'indexeur (ids attendus : {doc_id}::voix_et_expression, …)."
        )
    system = _ACTOR_SYS.format(name=name or doc_id, sheet=sheet)

    if reminders:
        block = "\n\n".join(reminders)
        system += (
            "\n\nCE DONT TU TE SOUVIENS de vos précédentes conversations (des "
            "souvenirs, pas des faits de ta fiche — tu peux t'en servir, les "
            "nuancer, ou refuser d'en parler) :\n" + block
        )
    return system


def list_sessions(doc_id: str | None = None) -> list[dict]:
    """Sessions recorded to disk, most recent first."""
    root = settings.sessions_dir / doc_id if doc_id else settings.sessions_dir
    if not root.exists():
        return []
    sheets = []
    for path in sorted(root.glob("*/*.md" if doc_id is None else "*.md"),
                         reverse=True):
        sheets.append({
            "id": f"{path.parent.name}/{path.stem}",
            "character": path.parent.name,
            "horodatage": path.stem,
            "octets": path.stat().st_size,
        })
    return sheets


def read_session(doc_id: str, timestamp: str) -> dict:
    """Re-read a recorded session: metadata, summary, transcript.

    The parser is deliberately tolerant: these files are meant to be EDITED
    BY HAND before the stage (prune a failed line, tighten an exchange). A
    format that broke at the first touch would miss its purpose.
    """
    path = settings.sessions_dir / doc_id / f"{timestamp}.md"
    if not path.exists():
        raise FileNotFoundError(f"session inconnue : {doc_id}/{timestamp}")
    text = path.read_text(encoding="utf-8")

    name = doc_id.split("-")[0].capitalize()
    header = re.search(r"^#\s+Session de roleplay\s+[—-]\s+(.+)$", text, re.M)
    if header:
        name = header.group(1).strip()

    def section(title: str) -> str:
        hit = re.search(rf"^##\s+{title}\s*$(.*?)(?=^##\s|\Z)", text,
                        re.M | re.S)
        return hit.group(1).strip() if hit else ""

    exchanges = []
    for block in re.finditer(r"^\*\*(.+?)\*\*\s+[—-]\s+(.+?)(?=\n\s*\n|\Z)",
                            section("Transcription"), re.M | re.S):
        who, said = block.group(1).strip(), block.group(2).strip()
        said = re.sub(r"<!--.*?-->", "", said, flags=re.S).strip()
        if said:
            exchanges.append({
                "role": "user" if who.lower() in ("vous", "interlocuteur")
                        else "assistant",
                "qui": who,
                "texte": said,
            })
    return {
        "id": f"{doc_id}/{timestamp}", "character": doc_id, "nom": name,
        "resume": section("Ce qui s'est dit"), "echanges": exchanges,
    }


class Session:
    """A conversation with a character, two-level memory included.

    Deliberately no hidden state model-side: everything the model sees is
    rebuilt each turn from the bible, the summary and the last N exchanges.
    The project's thesis applied to dialogue: the model reads a truth stored
    outside it, never keeps it.
    """

    def __init__(self, doc_id: str, *, name: str | None = None,
                 keep_turns: int | None = None, remind: bool = True):
        self.doc_id = doc_id
        self.name = name or doc_id.split("-")[0].capitalize()
        self.keep_turns = settings.keep_turns if keep_turns is None else keep_turns
        self.turns: list[dict] = []       # verbatim exchanges (role/content)
        self.summary: str = ""             # rolling summary of evicted exchanges
        self.metrics: list[dict] = []
        self.warnings: list[str] = []     # out-of-role slips, language leaks
        # FULL transcript, distinct from `turns`. `turns` is the model's
        # working memory: the rolling summary fuses old exchanges into it and
        # drops them, right for an actor (who remembers what was played, not
        # the exact words) but destructive for the trace. That trace is what
        # gets replayed onstage: sessions are pre-generated (ADR-0014).
        self.transcript: list[dict] = []
        self.reminders = session_memories(doc_id) if remind else []
        self.start = datetime.now(timezone.utc)
        # Validate the sheet AT CONSTRUCTION, not at the first turn. Otherwise
        # a missing character only showed after the first message: the CLI's
        # `except ValueError` (factory.roleplay.cli) never fired, and over HTTP
        # an unknown character returned 503 ("the machine has a problem")
        # instead of 404 ("no such character").
        build_system(doc_id, name=self.name, reminders=self.reminders)

    # --- context -------------------------------------------------------------

    def _system(self) -> str:
        system = build_system(self.doc_id, name=self.name, reminders=self.reminders)
        if self.summary:
            system += (
                "\n\nDÉBUT DE LA CONVERSATION EN COURS, résumé (la suite du "
                f"dialogue t'est donnée mot pour mot après) :\n{self.summary}"
            )
        return system

    # --- speaking turn -------------------------------------------------------

    def say(self, question: str, *, temperature: float = 0.85) -> str:
        """One turn: the character's reply to `question`.

        An out-of-role slip triggers ONE retry, with the fault quoted to the
        model. If the retry fails too, the reply is returned but flagged and
        kept out of session memory: otherwise « je suis un programme
        informatique » would become a memory of the character and poison
        every later session. Measured at the first test (ADR-0014).
        """
        self.turns.append({"role": "user", "content": question})
        self.transcript.append({"role": "user", "texte": question})
        # Tight num_predict: the instruction asks for two to six sentences, and
        # a low cap constrains better than a plea in the prompt. Actor mode
        # needs no continuation net like the author mode: a cut reply restarts
        # with a word, a scene does not.
        text, m = chat_turns(self._system(), self._trimmed_turns(),
                              temperature=temperature, num_predict=320)
        self.metrics.append(m)
        faults = out_of_role(text)

        if faults:
            reminder = (
                "Ta réponse précédente est SORTIE DU PERSONNAGE : elle contient "
                f"{', '.join('« ' + f + ' »' for f in faults)}. "
                f"{self.name} ne sait pas ce qu'est un programme ni une machine "
                "pensante. Réponds de nouveau à la même question, uniquement "
                f"comme {self.name}, en réagissant à l'insinuation ou en la "
                "balayant. Deux à quatre phrases, rien d'autre."
            )
            text, m = chat_turns(
                self._system() + "\n\n" + reminder,
                self._trimmed_turns(),
                temperature=min(0.7, temperature), num_predict=320,
            )
            self.metrics.append(m)
            faults = out_of_role(text)

        text, leaks = delint(_clean(text, self.name))
        if leaks:
            self.warnings.append(f"tour {len(self.metrics)}: {'; '.join(leaks)}")

        # The transcript records what was ACTUALLY said, faulty reply included:
        # it serves re-reading and hand pruning before the stage, not feeding
        # the model. The flag makes it visible at a glance in the Markdown.
        self.transcript.append({
            "role": "assistant", "texte": text,
            **({"hors_role": True} if faults else {}),
        })

        if faults:
            self.warnings.append(
                f"tour {len(self.metrics)} : SORTIE DE PERSONNAGE persistante "
                f"({', '.join(faults)}) — réplique exclue de la mémoire"
            )
            # The faulty exchange stays visible onscreen but pollutes neither
            # the context window of later turns nor the summary.
            self.turns.pop()
            return text

        self.turns.append({"role": "assistant", "content": text})
        self._roll()
        return text

    def _trimmed_turns(self) -> list[dict]:
        """The last 2 × keep_turns messages (one turn = question + reply)."""
        return self.turns[-2 * self.keep_turns:]

    def _roll(self) -> None:
        """Fuse the exchanges that left the window into the rolling summary.

        Called after every turn, works only when the window would overflow at
        the next turn: summarising costs a model call, so pay it once per
        slice.
        """
        surplus = len(self.turns) - 2 * self.keep_turns
        if surplus < 2:
            return
        outgoing = self.turns[:surplus]
        dialogue = "\n".join(
            f"{'INTERLOCUTEUR' if t['role'] == 'user' else self.name.upper()} : "
            f"{t['content']}"
            for t in outgoing
        )
        entry = (f"RÉSUMÉ DÉJÀ ÉTABLI :\n{self.summary}\n\n" if self.summary else "")
        text, m = chat(
            _SUMMARY_SYS,
            f"{entry}EXTRAIT À INTÉGRER :\n{dialogue}",
            temperature=0.2, num_predict=400,
        )
        self.metrics.append(m)
        self.summary = text.strip()
        self.turns = self.turns[surplus:]

    # --- persistence ---------------------------------------------------------

    def close(self, *, indexer: bool = True) -> Path | None:
        """Write the session memory as Markdown, then index it.

        Returns the file path, or None when the session is too short to be
        worth a memory. Order matters (ADR-0007): the Markdown is written
        FIRST, it is the source; the index is only a projection of it.
        """
        if len(self.turns) < 2 and not self.summary:
            return None

        # Whatever is not yet fused must be before closing, or the end of the
        # conversation, often the densest part, would be lost.
        guard = self.keep_turns
        self.keep_turns = 0
        self._roll()
        self.keep_turns = guard

        timestamp = self.start.strftime("%Y-%m-%dT%H-%M-%SZ")
        path = settings.sessions_dir / self.doc_id / f"{timestamp}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = (
            f"# Session de roleplay — {self.name}\n\n"
            f"<!-- Généré par factory.roleplay.session. Source canonique de la\n"
            f"     mémoire conversationnelle : éditable à la main, réindexable.\n"
            f"     Deux sections, deux usages : le RÉSUMÉ nourrit les sessions\n"
            f"     suivantes (c'est lui qui est indexé), la TRANSCRIPTION se\n"
            f"     rejoue sur scène. Élaguer une réplique ratée dans la\n"
            f"     transcription ne touche pas à la mémoire du personnage. -->\n\n"
            f"- personnage : `{self.doc_id}`\n"
            f"- début : {self.start.isoformat(timespec='seconds')}\n"
            f"- tours : {len(self.metrics)}\n\n"
            f"## Ce qui s'est dit\n\n{self.summary}\n\n"
            f"## Transcription\n\n{self._transcript_md()}\n"
        )
        path.write_text(body, encoding="utf-8")

        if indexer:
            self.index(path, timestamp)
        return path

    def _transcript_md(self) -> str:
        """Verbatim exchanges, in a format readable AND hand-editable.

        A line is removed by deleting its paragraph; nothing else to keep
        consistent. The format decides whether demo content is curable, and
        it must stay Markdown the eye reads.
        """
        lines = []
        for turn in self.transcript:
            who = "Vous" if turn["role"] == "user" else self.name
            mark = "  <!-- hors-rôle, à élaguer -->" if turn.get("hors_role") else ""
            lines.append(f"**{who}** — {turn['texte']}{mark}")
        return "\n\n".join(lines)

    def index(self, path: Path, timestamp: str) -> None:
        """Index a session memory into the `sessions` collection.

        Same convention as the bible indexer: deterministic id, document
        prefixed with its origin, scalar metadata only.
        """
        doc = (
            f"[{self.doc_id} / souvenir de session {timestamp}]\n{self.summary}"
        )
        sessions_collection().upsert(
            ids=[f"{self.doc_id}::session-{_slug(timestamp)}"],
            embeddings=[embed(doc)],
            documents=[doc],
            metadatas=[{
                "type": "session",
                "doc_id": self.doc_id,
                "section": f"session-{_slug(timestamp)}",
                "horodatage": timestamp,
                "source": str(path.name),
            }],
        )
