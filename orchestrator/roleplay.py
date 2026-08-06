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

import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from llm import chat, chat_turns
from style import delint
from retrieval import (
    acting_context,
    embed,
    session_memories,
    sessions_collection,
)

SESSIONS_DIR = Path(
    os.environ.get("SESSIONS_DIR", Path(__file__).resolve().parent.parent / "sessions")
)

# Échanges gardés VERBATIM en contexte. Au-delà, on fond dans le résumé. Six
# tours (douze messages) tiennent la continuité d'une conversation de démo sans
# gonfler le prompt : le contexte de personnage pèse déjà ~2k tokens.
KEEP_TURNS = int(os.environ.get("RP_KEEP_TURNS", "6"))

# Le prompt système du mode acteur. Les interdits sont explicites et NOMMÉS :
# un modèle de 12B respecte mieux « ne dis jamais que tu es un modèle » qu'une
# consigne générale de rester dans le personnage.
_ACTOR_SYS = """Tu ES {nom}. Tu n'es pas un assistant, tu n'es pas un modèle de
langue, tu n'es pas un narrateur : tu es cette personne, et tu parles à la
première personne.

RÈGLES ABSOLUES, sans exception :
- Tu ne sors JAMAIS du personnage. Tu ne mentionnes jamais l'intelligence
  artificielle, un modèle, un prompt, une consigne, ni le fait d'incarner
  quelqu'un.
- Tu réponds UNIQUEMENT ce que {nom} dirait, avec sa voix, son vocabulaire, ses
  tics de langage. La fiche ci-dessous contient des répliques typiques ET des
  choses que {nom} ne dirait jamais : respecte les deux.
- Tu ne racontes pas la scène à la troisième personne et tu n'écris pas de
  didascalies longues. Un geste bref entre tirets est permis quand il porte
  quelque chose — « — Je n'ai pas dit ça. » Il se détourna. — mais la parole
  domine.
- Si on t'interroge sur un fait que ta fiche ne contient pas, tu réagis comme
  {nom} le ferait : tu esquives, tu coupes court, tu réponds à côté. Tu
  n'INVENTES pas d'élément de monde (nom, lieu, événement) absent de ta fiche.
- Tu n'emploies JAMAIS les tournures « je ne comprends pas cette question »,
  « je suis désolé, mais », « en tant que… » : ce sont des formules d'assistant,
  et {nom} n'est pas un assistant. Tu réagis, tu rétorques, tu te méfies.
- Tu réponds court : deux à six phrases. C'est une conversation, pas un
  monologue.

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

{fiche}
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
_HORS_ROLE = re.compile(
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
_TIRETS_DOUBLES = re.compile(r"^\s*[—–-]\s*[—–-]\s*")


def hors_role(texte: str) -> list[str]:
    """Marqueurs de sortie de personnage trouvés dans une réplique."""
    return sorted({m.group(0).lower() for m in _HORS_ROLE.finditer(texte)})


def _nettoyer(texte: str) -> str:
    """Retire les artefacts de forme d'une réplique (tirets doublés)."""
    return _TIRETS_DOUBLES.sub("— ", texte.strip())


def _slug(texte: str) -> str:
    """Slug ASCII pour un nom de fichier ou un id de chunk."""
    plat = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plat.lower()).strip("-")


def build_system(doc_id: str, *, nom: str | None = None,
                 rappels: list[str] | None = None) -> str:
    """Assemble le prompt système d'incarnation depuis la bible.

    `rappels` : résumés de sessions antérieures, injectés comme des SOUVENIRS du
    personnage. Ils sont présentés à part de la fiche : la fiche est la vérité
    durable, le souvenir est daté et révisable — les mélanger inviterait le
    modèle à traiter un épisode de conversation comme un fait de la bible.
    """
    fiche = acting_context(doc_id)
    if not fiche:
        raise ValueError(
            f"Aucune fiche indexée pour « {doc_id} ». Vérifier la bible et "
            "l'indexeur (ids attendus : {doc_id}::voix_et_expression, …)."
        )
    system = _ACTOR_SYS.format(nom=nom or doc_id, fiche=fiche)

    if rappels:
        bloc = "\n\n".join(rappels)
        system += (
            "\n\nCE DONT TU TE SOUVIENS de vos précédentes conversations (des "
            "souvenirs, pas des faits de ta fiche — tu peux t'en servir, les "
            "nuancer, ou refuser d'en parler) :\n" + bloc
        )
    return system


class Session:
    """Une conversation avec un personnage, mémoire à deux niveaux comprise.

    Volontairement sans état caché côté modèle : tout ce que le modèle voit est
    reconstruit à chaque tour depuis la bible, le résumé et les N derniers
    échanges. C'est la thèse du projet appliquée au dialogue — le modèle est un
    lecteur d'une vérité stockée hors de lui, jamais son dépositaire.
    """

    def __init__(self, doc_id: str, *, nom: str | None = None,
                 keep_turns: int = KEEP_TURNS, rappeler: bool = True):
        self.doc_id = doc_id
        self.nom = nom or doc_id.split("-")[0].capitalize()
        self.keep_turns = keep_turns
        self.turns: list[dict] = []       # échanges verbatim (role/content)
        self.resume: str = ""             # résumé glissant des échanges sortis
        self.metrics: list[dict] = []
        self.warnings: list[str] = []     # sorties de rôle, fuites de langue
        self.rappels = session_memories(doc_id) if rappeler else []
        self.debut = datetime.now(timezone.utc)

    # --- contexte ------------------------------------------------------------

    def _system(self) -> str:
        system = build_system(self.doc_id, nom=self.nom, rappels=self.rappels)
        if self.resume:
            system += (
                "\n\nDÉBUT DE LA CONVERSATION EN COURS, résumé (la suite du "
                f"dialogue t'est donnée mot pour mot après) :\n{self.resume}"
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
        # num_predict serré : la consigne demande deux à six phrases, et un
        # plafond bas est une contrainte plus efficace qu'une prière dans le
        # prompt. Le mode acteur n'a pas besoin du filet de continuation du mode
        # auteur — une réplique coupée se relance d'un mot, une scène non.
        texte, m = chat_turns(self._system(), self._trimmed_turns(),
                              temperature=temperature, num_predict=320)
        self.metrics.append(m)
        fautes = hors_role(texte)

        if fautes:
            rappel = (
                "Ta réponse précédente est SORTIE DU PERSONNAGE : elle contient "
                f"{', '.join('« ' + f + ' »' for f in fautes)}. "
                f"{self.nom} ne sait pas ce qu'est un programme ni une machine "
                "pensante. Réponds de nouveau à la même question, uniquement "
                f"comme {self.nom}, en réagissant à l'insinuation ou en la "
                "balayant. Deux à quatre phrases, rien d'autre."
            )
            texte, m = chat_turns(
                self._system() + "\n\n" + rappel,
                self._trimmed_turns(),
                temperature=min(0.7, temperature), num_predict=320,
            )
            self.metrics.append(m)
            fautes = hors_role(texte)

        texte, fuites = delint(_nettoyer(texte))
        if fuites:
            self.warnings.append(f"tour {len(self.metrics)}: {'; '.join(fuites)}")

        if fautes:
            self.warnings.append(
                f"tour {len(self.metrics)} : SORTIE DE PERSONNAGE persistante "
                f"({', '.join(fautes)}) — réplique exclue de la mémoire"
            )
            # L'échange fautif reste visible à l'écran mais ne pollue ni la
            # fenêtre de contexte des tours suivants ni le résumé.
            self.turns.pop()
            return texte

        self.turns.append({"role": "assistant", "content": texte})
        self._roll()
        return texte

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
        sortants = self.turns[:surplus]
        dialogue = "\n".join(
            f"{'INTERLOCUTEUR' if t['role'] == 'user' else self.nom.upper()} : "
            f"{t['content']}"
            for t in sortants
        )
        entree = (f"RÉSUMÉ DÉJÀ ÉTABLI :\n{self.resume}\n\n" if self.resume else "")
        texte, m = chat(
            _SUMMARY_SYS,
            f"{entree}EXTRAIT À INTÉGRER :\n{dialogue}",
            temperature=0.2, num_predict=400,
        )
        self.metrics.append(m)
        self.resume = texte.strip()
        self.turns = self.turns[surplus:]

    # --- persistance ---------------------------------------------------------

    def close(self, *, indexer: bool = True) -> Path | None:
        """Écrit la mémoire de session en Markdown, puis l'indexe.

        Retourne le chemin du fichier, ou None si la session est trop courte pour
        valoir un souvenir. L'ordre compte : le Markdown est écrit d'ABORD, il
        est la source ; l'index n'en est qu'une projection.
        """
        if len(self.turns) < 2 and not self.resume:
            return None

        # Ce qui n'a pas encore été fondu doit l'être avant de fermer, sinon la
        # fin de conversation — souvent la plus chargée — serait perdue.
        garde = self.keep_turns
        self.keep_turns = 0
        self._roll()
        self.keep_turns = garde

        horodatage = self.debut.strftime("%Y-%m-%dT%H-%M-%SZ")
        chemin = SESSIONS_DIR / self.doc_id / f"{horodatage}.md"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        corps = (
            f"# Session de roleplay — {self.nom}\n\n"
            f"<!-- Généré par orchestrator/roleplay.py. Source canonique de la\n"
            f"     mémoire conversationnelle : éditable à la main, réindexable. -->\n\n"
            f"- personnage : `{self.doc_id}`\n"
            f"- début : {self.debut.isoformat(timespec='seconds')}\n"
            f"- tours : {len(self.metrics)}\n\n"
            f"## Ce qui s'est dit\n\n{self.resume}\n"
        )
        chemin.write_text(corps, encoding="utf-8")

        if indexer:
            self.index(chemin, horodatage)
        return chemin

    def index(self, chemin: Path, horodatage: str) -> None:
        """Indexe un souvenir de session dans la collection `sessions`.

        Même convention que l'indexeur de la bible : id déterministe, document
        préfixé de son origine, métadonnées scalaires uniquement.
        """
        doc = (
            f"[{self.doc_id} / souvenir de session {horodatage}]\n{self.resume}"
        )
        sessions_collection().upsert(
            ids=[f"{self.doc_id}::session-{_slug(horodatage)}"],
            embeddings=[embed(doc)],
            documents=[doc],
            metadatas=[{
                "type": "session",
                "doc_id": self.doc_id,
                "section": f"session-{_slug(horodatage)}",
                "horodatage": horodatage,
                "source": str(chemin.name),
            }],
        )
