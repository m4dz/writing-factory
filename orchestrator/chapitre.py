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

import os
import re

from style import sentence_ends

BASCULE = "<!-- BASCULE -->"
FIN_AUDIO = "<!-- FIN AUDIO -->"

# Phrases lues à voix nue avant la bascule.
PHRASES_AVANT_BASCULE = int(os.environ.get("BASCULE_APRES_PHRASES", "2"))

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
DEBIT_MOTS_MIN = float(os.environ.get("AUDIO_DEBIT_MOTS_MIN", "177"))
SECONDES_AUDIO = float(os.environ.get("AUDIO_SECONDES", "165"))   # 2 min 45

# Marge d'acceptation autour de la cible. 15 s et non 20 : au run du 2026-08-09
# l'écart était de 18 s — donc sous l'ancien seuil, donc silencieux, alors qu'il
# suffisait à sortir de la fenêtre demandée par le deck (2'30-3'00).
TOLERANCE_AUDIO_S = float(os.environ.get("AUDIO_TOLERANCE_S", "15"))

MOTS_AUDIO = int(os.environ.get(
    "AUDIO_MOTS_MAX", str(int(DEBIT_MOTS_MIN * SECONDES_AUDIO / 60))
))


# L'en-tête normalisé en DÉBUT DE LIGNE — le repère de bascule du chapitre 7.
# Même format que `lint_style.ENTETE_ENTREE`, réécrit ici plutôt qu'importé :
# `chapitre.py` est servi par l'API et ne doit pas dépendre de l'outillage de
# calibration. Si le format bouge, il bouge aux deux endroits — c'est le prix,
# et il est explicite.
ENTETE_LIGNE = re.compile(
    r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d{1,2}\.\s+"
    r"\S[^\n]{0,40}\.\s*$", re.MULTILINE | re.IGNORECASE)


def _fin_de_phrase_n(texte: str, n: int) -> int | None:
    """Position de fin de la n-ième phrase, ou None s'il n'y en a pas tant."""
    fins = sentence_ends(texte)
    return fins[n - 1] if len(fins) >= n else None


def inserer_bascule(texte: str, *, phrases: int = PHRASES_AVANT_BASCULE,
                    sur_second_entete: bool = False) -> str:
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
    if sur_second_entete:
        tetes = list(ENTETE_LIGNE.finditer(texte))
        if len(tetes) >= 2:
            coupe = tetes[1].start()
            return (f"{texte[:coupe].rstrip()}\n\n{BASCULE}\n\n"
                    f"{texte[coupe:].lstrip()}")
        # Un seul en-tête : le chapitre n'a pas la structure attendue. On
        # retombe sur le compte de phrases plutôt que d'omettre le marqueur —
        # un chapitre sans bascule est traité comme non prêt par le deck, donc
        # une structure ratée ferait disparaître la démo au lieu de la dégrader.
        pass
    coupe = _fin_de_phrase_n(texte, phrases)
    if coupe is None:
        return f"{BASCULE}\n\n{texte.lstrip()}"
    tete, reste = texte[:coupe].rstrip(), texte[coupe:].lstrip()
    return f"{tete}\n\n{BASCULE}\n\n{reste}" if reste else f"{tete}\n\n{BASCULE}"


def extrait_audio(texte: str, *, mots_max: int = MOTS_AUDIO,
                  jusqu_a: str = "") -> str:
    """Texte que la voix clonée doit lire : après la bascule, borné en mots.

    La coupe tombe toujours sur une FIN DE PHRASE : un WAV qui s'arrête au
    milieu d'une phrase s'entend immédiatement, là où une phrase complète passe
    pour une fin voulue. On dépasse donc légèrement le budget plutôt que de
    couper net — la phrase en cours est toujours incluse.
    """
    apres = texte.split(BASCULE, 1)[1] if BASCULE in texte else texte
    apres = apres.split(FIN_AUDIO, 1)[0].strip()

    fins = sentence_ends(apres)
    if not fins:
        return apres

    # LA CHUTE EST TOUJOURS LUE. La borne en mots existe contre un audio trop
    # long ; elle ne doit pas amputer la LIGNE QUI FAIT LA SCÈNE. Au premier
    # rendu du chapitre 7, la coupe est tombée à 268 mots, six lignes avant
    # « Constat : anniversaire. » — la voix clonée disait tout sauf la phrase
    # pour laquelle elle parle. La coïncidence scénique veut que le locuteur
    # lise l'entrée où elle résiste et le clone celle où la journée a gagné :
    # sans la chute, le clone ne gagne rien.
    if jusqu_a and jusqu_a in apres:
        borne = apres.index(jusqu_a) + len(jusqu_a)
        return apres[:borne].strip()

    for fin in fins:
        if len(apres[:fin].split()) >= mots_max:
            return apres[:fin].strip()
    return apres


def assembler(scenes: list[str], *, mots_max: int = MOTS_AUDIO,
              phrases: int = PHRASES_AVANT_BASCULE,
              sur_second_entete: bool = False, chute: str = "") -> str:
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
    corps = inserer_bascule("\n\n".join(s.strip() for s in scenes if s.strip()),
                            phrases=phrases,
                            sur_second_entete=sur_second_entete)
    lu = extrait_audio(corps, mots_max=mots_max, jusqu_a=chute)
    if lu and lu in corps:
        pos = corps.index(lu) + len(lu)
        corps = f"{corps[:pos]}\n\n{FIN_AUDIO}\n\n{corps[pos:].lstrip()}".rstrip()
    else:
        corps = f"{corps.rstrip()}\n\n{FIN_AUDIO}"
    return corps
