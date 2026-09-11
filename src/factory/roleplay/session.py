#!/usr/bin/env python3
"""Mode ACTEUR : dialoguer avec un personnage de la bible, sans sortie de rôle.

Deuxième fonction du démonstrateur (la première étant le mode auteur). Même
modèle chaud que l'écriture — on ne multiplie pas les instances, la cohérence
vient de la mémoire externe partagée. Ce qui change, c'est le prompt système et
la forme du contexte.

Trois décisions structurantes :

1. **Le contexte d'un acteur est plus large que celui d'un auteur.** Écrire une
   scène n'exige pas la biographie du personnage ; se faire interroger sur son
   passé, si. Cf. `ACTING_SECTIONS` dans retrieval.py.

2. **Aucun swap de modèle pendant la session.** Le pipeline auteur décharge nemo
   pour laisser la place à Qwen, parce qu'un swap unique se paie une fois sur
   vingt minutes. Ici, l'utilisateur attend sa réponse : recharger 13 GB au
   milieu d'un dialogue coûterait plus que tout le reste. Le résumé glissant est
   donc produit par le MÊME modèle que le jeu d'acteur.

3. **Mémoire à deux niveaux.** Les N derniers échanges passent en contexte
   verbatim ; au-delà, les plus anciens sont fondus dans un résumé glissant. Le
   résumé est écrit en Markdown sous `sessions/<personnage>/` PUIS indexé dans
   une collection Chroma séparée — le sens du flux du projet (Markdown
   canonique, index dérivé) vaut aussi pour la mémoire, et une réindexation de
   la bible ne peut pas l'effacer.
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

# Sessions sur disque : `settings.sessions_dir`.
#
# Échanges gardés VERBATIM en contexte (`settings.keep_turns`). Au-delà, on
# fond dans le résumé. Six tours (douze messages) tiennent la continuité d'une
# conversation de démo sans gonfler le prompt : le contexte de personnage pèse
# déjà ~2k tokens.

# Le prompt système du mode acteur. Les interdits sont explicites et NOMMÉS :
# un modèle de 12B respecte mieux « ne dis jamais que tu es un modèle » qu'une
# consigne générale de rester dans le personnage.
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


# Marqueurs de SORTIE DE PERSONNAGE. Un prompt ne suffit pas — mesuré : nemo a
# répondu « je suis simplement un programme informatique conçu pour simuler des
# conversations » à trois questions de provocation, malgré des interdits
# explicites. Même philosophie que partout ailleurs dans ce projet : le modèle
# est faillible, c'est le CODE qui tient la ligne.
_OUT_OF_ROLE = re.compile(
    r"intelligence artificielle|\bIA\b|modèle de langue|modèle linguistique|"
    r"programme informatique|assistant virtuel|en tant qu'(?:une? )?(?:IA|"
    r"intelligence|assistant|programme|modèle)|je suis (?:un |une )?(?:programme|"
    r"modèle|assistant|simulation)|simuler des conversations|mon programme|"
    r"je n'ai pas de (?:corps physique|conscience)|utilisateurs|"
    r"je suis désolé, mais je ne (?:comprends|peux)",
    re.I,
)

# Artefact d'imitation du prompt : le modèle recopie le tiret de dialogue de nos
# exemples EN PLUS du sien (« — — Non, je ne peux pas »).
_DOUBLE_DASHES = re.compile(r"^\s*[—–-]\s*[—–-]\s*")


def out_of_role(text: str) -> list[str]:
    """Marqueurs de sortie de personnage trouvés dans une réplique."""
    return sorted({m.group(0).lower() for m in _OUT_OF_ROLE.finditer(text)})


def _clean(text: str, name: str = "") -> str:
    """Retire les artefacts de forme d'une réplique.

    Deux constatés à l'usage : le tiret de dialogue doublé (le modèle recopie
    celui de nos exemples en plus du sien), et la RÉPLIQUE PRÉFIXÉE DE SON
    PROPRE NOM (« Kael : Ah, ma chère… »), qui vient de l'habitude des corpus de
    dialogue. Ce préfixe est invisible dans un chat, mais il ressort dans la
    transcription rejouée sur scène, où le nom apparaît alors deux fois.
    """
    text = _DOUBLE_DASHES.sub("— ", text.strip())
    if name:
        text = re.sub(rf"^\s*{re.escape(name)}\s*[:—–-]\s*", "", text,
                       flags=re.I)
    return text.strip()


def _slug(text: str) -> str:
    """Slug ASCII pour un nom de fichier ou un id de chunk."""
    flat = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", flat.lower()).strip("-")


def build_system(doc_id: str, *, name: str | None = None,
                 reminders: list[str] | None = None) -> str:
    """Assemble le prompt système d'incarnation depuis la bible.

    `rappels` : résumés de sessions antérieures, injectés comme des SOUVENIRS du
    personnage. Ils sont présentés à part de la fiche : la fiche est la vérité
    durable, le souvenir est daté et révisable — les mélanger inviterait le
    modèle à traiter un épisode de conversation comme un fait de la bible.
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
    """Sessions enregistrées sur disque, les plus récentes d'abord."""
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
    """Relit une session enregistrée : métadonnées, résumé, transcription.

    Le parseur est volontairement tolérant : ces fichiers sont faits pour être
    ÉDITÉS À LA MAIN avant la scène (élaguer une réplique ratée, resserrer un
    échange). Un format qui casserait à la première retouche manquerait son but.
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
    """Une conversation avec un personnage, mémoire à deux niveaux comprise.

    Volontairement sans état caché côté modèle : tout ce que le modèle voit est
    reconstruit à chaque tour depuis la bible, le résumé et les N derniers
    échanges. C'est la thèse du projet appliquée au dialogue — le modèle est un
    lecteur d'une vérité stockée hors de lui, jamais son dépositaire.
    """

    def __init__(self, doc_id: str, *, name: str | None = None,
                 keep_turns: int | None = None, remind: bool = True):
        self.doc_id = doc_id
        self.name = name or doc_id.split("-")[0].capitalize()
        self.keep_turns = settings.keep_turns if keep_turns is None else keep_turns
        self.turns: list[dict] = []       # échanges verbatim (role/content)
        self.summary: str = ""             # résumé glissant des échanges sortis
        self.metrics: list[dict] = []
        self.warnings: list[str] = []     # sorties de rôle, fuites de langue
        # Transcription INTÉGRALE, distincte de `turns`. `turns` est la mémoire
        # de travail du modèle : le résumé glissant y fond les échanges anciens
        # puis les retire, ce qui est juste pour un acteur (il se souvient de ce
        # qui s'est joué, pas des mots exacts) mais détruit la trace. Or c'est
        # cette trace qu'on rejoue sur scène — les sessions sont pré-générées.
        self.transcript: list[dict] = []
        self.reminders = session_memories(doc_id) if remind else []
        self.start = datetime.now(timezone.utc)
        # Valider la fiche À LA CONSTRUCTION, pas au premier tour. Sans ça
        # l'absence de personnage ne se voyait qu'après le premier message :
        # côté CLI le `except ValueError` de chat_character.py ne se déclenchait
        # jamais, et côté HTTP un personnage inconnu rendait 503 (« la machine
        # a un problème ») au lieu de 404 (« ce personnage n'existe pas »).
        build_system(doc_id, name=self.name, reminders=self.reminders)

    # --- contexte ------------------------------------------------------------

    def _system(self) -> str:
        system = build_system(self.doc_id, name=self.name, reminders=self.reminders)
        if self.summary:
            system += (
                "\n\nDÉBUT DE LA CONVERSATION EN COURS, résumé (la suite du "
                f"dialogue t'est donnée mot pour mot après) :\n{self.summary}"
            )
        return system

    # --- tour de parole ------------------------------------------------------

    def say(self, question: str, *, temperature: float = 0.85) -> str:
        """Un tour : la réplique du personnage à `question`.

        Une sortie de personnage déclenche UNE reprise, avec la faute citée au
        modèle. Si la reprise échoue aussi, la réplique est rendue mais marquée :
        elle n'entrera pas dans la mémoire de session, sinon l'aveu (« je suis un
        programme informatique ») deviendrait un souvenir du personnage et
        empoisonnerait toutes les sessions suivantes. Mesuré au premier test.
        """
        self.turns.append({"role": "user", "content": question})
        self.transcript.append({"role": "user", "texte": question})
        # num_predict serré : la consigne demande deux à six phrases, et un
        # plafond bas est une contrainte plus efficace qu'une prière dans le
        # prompt. Le mode acteur n'a pas besoin du filet de continuation du mode
        # auteur — une réplique coupée se relance d'un mot, une scène non.
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

        # La transcription enregistre ce qui a RÉELLEMENT été dit, y compris une
        # réplique fautive : elle sert à relire et à élaguer à la main avant la
        # scène, pas à nourrir le modèle. Le drapeau permet de la repérer d'un
        # coup d'œil dans le Markdown.
        self.transcript.append({
            "role": "assistant", "texte": text,
            **({"hors_role": True} if faults else {}),
        })

        if faults:
            self.warnings.append(
                f"tour {len(self.metrics)} : SORTIE DE PERSONNAGE persistante "
                f"({', '.join(faults)}) — réplique exclue de la mémoire"
            )
            # L'échange fautif reste visible à l'écran mais ne pollue ni la
            # fenêtre de contexte des tours suivants ni le résumé.
            self.turns.pop()
            return text

        self.turns.append({"role": "assistant", "content": text})
        self._roll()
        return text

    def _trimmed_turns(self) -> list[dict]:
        """Les 2 × keep_turns derniers messages (un tour = question + réponse)."""
        return self.turns[-2 * self.keep_turns:]

    def _roll(self) -> None:
        """Fond les échanges sortis de la fenêtre dans le résumé glissant.

        Appelé après chaque tour, ne travaille que lorsque la fenêtre débordera
        au tour suivant : résumer coûte un appel au modèle, autant ne le payer
        qu'une fois par tranche.
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

    # --- persistance ---------------------------------------------------------

    def close(self, *, indexer: bool = True) -> Path | None:
        """Écrit la mémoire de session en Markdown, puis l'indexe.

        Retourne le chemin du fichier, ou None si la session est trop courte pour
        valoir un souvenir. L'ordre compte : le Markdown est écrit d'ABORD, il
        est la source ; l'index n'en est qu'une projection.
        """
        if len(self.turns) < 2 and not self.summary:
            return None

        # Ce qui n'a pas encore été fondu doit l'être avant de fermer, sinon la
        # fin de conversation — souvent la plus chargée — serait perdue.
        guard = self.keep_turns
        self.keep_turns = 0
        self._roll()
        self.keep_turns = guard

        timestamp = self.start.strftime("%Y-%m-%dT%H-%M-%SZ")
        path = settings.sessions_dir / self.doc_id / f"{timestamp}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        body = (
            f"# Session de roleplay — {self.name}\n\n"
            f"<!-- Généré par orchestrator/roleplay.py. Source canonique de la\n"
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
        """Échanges verbatim, dans un format relisible ET éditable à la main.

        Une réplique se supprime en effaçant son paragraphe ; rien d'autre à
        maintenir cohérent. C'est le format qui décide si le contenu de démo est
        curable, et il doit rester du Markdown que l'œil lit.
        """
        lines = []
        for turn in self.transcript:
            who = "Vous" if turn["role"] == "user" else self.name
            mark = "  <!-- hors-rôle, à élaguer -->" if turn.get("hors_role") else ""
            lines.append(f"**{who}** — {turn['texte']}{mark}")
        return "\n\n".join(lines)

    def index(self, path: Path, timestamp: str) -> None:
        """Indexe un souvenir de session dans la collection `sessions`.

        Même convention que l'indexeur de la bible : id déterministe, document
        préfixé de son origine, métadonnées scalaires uniquement.
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
