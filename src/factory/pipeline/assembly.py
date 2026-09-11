#!/usr/bin/env python3
"""Assemblage du chapitre livré : marqueur de bascule et extrait à lire.

Ce module ne génère rien. Il décide OÙ la voix humaine s'arrête et où la voix
clonée reprend — c'est la charnière du tour de magie de la keynote, et elle est
posée par du CODE, jamais par le modèle : un marqueur placé par nemo tomberait
ailleurs à chaque tirage, et le speaker ne saurait pas quoi lire à voix haute.

Deux décisions du propriétaire (2026-08-07) :

1. **La bascule tombe après la DEUXIÈME PHRASE.** Repère strictement
   reproductible : sur scène, il lit deux phrases, puis lance l'audio. Ma
   proposition initiale (« frontière de paragraphe ») dépendait du découpage de
   nemo, donc variait d'un run à l'autre — inutilisable comme repère de scène.

2. **L'extrait lu par le clone est BORNÉ** (~550 mots, ≈ 3-4 min). Le TTS tourne
   à ~1× temps réel : lire tout un chapitre de quatre scènes (~2400 mots)
   demanderait un quart d'heure d'audio ET un quart d'heure de calcul, soit
   32 min contre 28' au compteur du deck — sans parler d'une lecture de quinze
   minutes dans une keynote de cinquante.
"""

import re

from factory.settings import settings
from factory.text import sentence_ends

SWITCH = "<!-- BASCULE -->"
AUDIO_END = "<!-- FIN AUDIO -->"

# Phrases lues à voix nue avant la bascule : `settings.switch_after_sentences`.

# La borne se règle en SECONDES, pas en mots — parce que c'est une durée que le
# deck demande (« 2'30 à 3 min, extrait joué EN ENTIER », session frontend du
# 2026-08-08), et qu'une consigne exprimée dans l'unité du besoin ne se traduit
# pas de travers.
#
# La traduction en mots passe par le débit MESURÉ du clone. Attention : le deck
# raisonnait à ~150 mots/min (d'où leur estimation de 375-450 mots), alors que
# le rendu mesuré parle à 190. Leurs 450 mots auraient donné 2'22, soit SOUS
# leur propre plancher — un trou là où ils attendent du son.
#
# ⚠ Ce débit vient d'UN échantillon de 117 mots. Le premier run complet doit le
# confirmer : `tts.rendre` compare la durée obtenue à la cible et le signale.
# 177 mots/min : MESURÉ sur un vrai extrait de 540 mots (183 s d'audio) au run
# complet du 2026-08-09. Le premier chiffre (190) venait d'un échantillon de
# 117 mots et surestimait de 7 % — d'où un extrait rendu à 3'03 au lieu des 2'45
# visées. Un texte long porte proportionnellement plus de pauses : fins de
# phrase, plus 0,6 s entre chaque segment (13 segments = 7,8 s de silence).
#
# Marge d'acceptation autour de la cible. 15 s et non 20 : au run du 2026-08-09
# l'écart était de 18 s — donc sous l'ancien seuil, donc silencieux, alors qu'il
# suffisait à sortir de la fenêtre demandée par le deck (2'30-3'00).
#
# Les quatre réglages (`audio_words_per_minute`, `audio_seconds`,
# `audio_tolerance_s`, `audio_max_words`) vivent dans `factory.settings` ; la
# borne en mots est `settings.effective_audio_max_words`.


# L'en-tête normalisé en DÉBUT DE LIGNE — le repère de bascule du chapitre 7.
# Même format que `lint_style.ENTETE_ENTREE`, réécrit ici plutôt qu'importé :
# `chapitre.py` est servi par l'API et ne doit pas dépendre de l'outillage de
# calibration. Si le format bouge, il bouge aux deux endroits — c'est le prix,
# et il est explicite.
HEADER_LINE = re.compile(
    r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}\.\s+"
    r"\S[^\n]{0,40}\.\s*$", re.MULTILINE | re.IGNORECASE)


def _nth_sentence_end(text: str, n: int) -> int | None:
    """Position de fin de la n-ième phrase, ou None s'il n'y en a pas tant."""
    ends = sentence_ends(text)
    return ends[n - 1] if len(ends) >= n else None


def insert_switch(text: str, *, sentences: int | None = None,
                    on_second_header: bool = False) -> str:
    """Insère le marqueur de bascule après les `phrases` premières phrases.

    Si le texte compte moins de phrases que demandé (scène très courte, ou
    découpage inattendu), le marqueur est posé en TÊTE plutôt qu'omis : mieux
    vaut que le clone lise tout que pas de marqueur du tout, car son absence
    ferait échouer le rendu et priverait la scène de son audio.

    `sur_second_entete` — LE MODE DU CHAPITRE 7. Là, le repère n'est pas un
    compte de phrases mais la structure : deux entrées du même jour, le speaker
    lit celle où elle résiste, la voix clonée celle où la journée a gagné. La
    bascule se pose donc juste AVANT le second en-tête, et la coïncidence
    scénique est exacte au lieu d'être approchée. C'est ce que décrit le §7 du
    brief 7 : « détection déterministe, plus d'heuristique ».
    """
    if sentences is None:
        sentences = settings.switch_after_sentences
    if on_second_header:
        heads = list(HEADER_LINE.finditer(text))
        if len(heads) >= 2:
            cut = heads[1].start()
            return (f"{text[:cut].rstrip()}\n\n{SWITCH}\n\n"
                    f"{text[cut:].lstrip()}")
        # Un seul en-tête : le chapitre n'a pas la structure attendue. On
        # retombe sur le compte de phrases plutôt que d'omettre le marqueur —
        # un chapitre sans bascule est traité comme non prêt par le deck, donc
        # une structure ratée ferait disparaître la démo au lieu de la dégrader.
        pass
    cut = _nth_sentence_end(text, sentences)
    if cut is None:
        return f"{SWITCH}\n\n{text.lstrip()}"
    head, rest = text[:cut].rstrip(), text[cut:].lstrip()
    return f"{head}\n\n{SWITCH}\n\n{rest}" if rest else f"{head}\n\n{SWITCH}"


def audio_excerpt(text: str, *, max_words: int | None = None,
                  until: str = "") -> str:
    """Texte que la voix clonée doit lire : après la bascule, borné en mots.

    La coupe tombe toujours sur une FIN DE PHRASE : un WAV qui s'arrête au
    milieu d'une phrase s'entend immédiatement, là où une phrase complète passe
    pour une fin voulue. On dépasse donc légèrement le budget plutôt que de
    couper net — la phrase en cours est toujours incluse.
    """
    if max_words is None:
        max_words = settings.effective_audio_max_words
    after = text.split(SWITCH, 1)[1] if SWITCH in text else text
    after = after.split(AUDIO_END, 1)[0].strip()

    ends = sentence_ends(after)
    if not ends:
        return after

    # LA CHUTE EST TOUJOURS LUE. La borne en mots existe contre un audio trop
    # long ; elle ne doit pas amputer la LIGNE QUI FAIT LA SCÈNE. Au premier
    # rendu du chapitre 7, la coupe est tombée à 268 mots, six lignes avant
    # « Constat : anniversaire. » — la voix clonée disait tout sauf la phrase
    # pour laquelle elle parle. La coïncidence scénique veut que le locuteur
    # lise l'entrée où elle résiste et le clone celle où la journée a gagné :
    # sans la chute, le clone ne gagne rien.
    if until and until in after:
        bound = after.index(until) + len(until)
        return after[:bound].strip()

    for end in ends:
        if len(after[:end].split()) >= max_words:
            return after[:end].strip()
    return after


def assemble(scenes: list[str], *, max_words: int | None = None,
              sentences: int | None = None,
              on_second_header: bool = False, fall: str = "") -> str:
    """Chapitre complet en Markdown, avec bascule et fin de lecture marquées.

    LES DEUX MARQUEURS SONT GARANTIS PRÉSENTS. Exigence du deck (message de la
    session frontend, 2026-08-08) : « un chapitre sans les deux marqueurs est
    traité comme non prêt et bascule sur l'embarqué ». Un marqueur manquant ne
    dégraderait donc pas l'affichage, il ferait disparaître le chapitre live —
    en silence. D'où le repli en fin de texte plutôt qu'une omission quand la
    borne d'extrait ne peut pas être calculée (chapitre très court, texte sans
    ponctuation finale).

    Le chapitre servi reste ENTIER : c'est la pièce à conviction de la démo, on
    ne la tronque pas parce que l'audio, lui, est borné.
    """
    body = insert_switch("\n\n".join(s.strip() for s in scenes if s.strip()),
                            sentences=sentences,
                            on_second_header=on_second_header)
    read_part = audio_excerpt(body, max_words=max_words, until=fall)
    if read_part and read_part in body:
        pos = body.index(read_part) + len(read_part)
        body = f"{body[:pos]}\n\n{AUDIO_END}\n\n{body[pos:].lstrip()}".rstrip()
    else:
        body = f"{body.rstrip()}\n\n{AUDIO_END}"
    return body
