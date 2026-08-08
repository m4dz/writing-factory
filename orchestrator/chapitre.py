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

from style import sentence_ends

BASCULE = "<!-- BASCULE -->"
FIN_AUDIO = "<!-- FIN AUDIO -->"

# Phrases lues à voix nue avant la bascule.
PHRASES_AVANT_BASCULE = int(os.environ.get("BASCULE_APRES_PHRASES", "2"))

# Budget de mots de la lecture clonée. Calé sur le BESOIN RÉEL du deck : la
# section 7 ne joue que 45 s à 1 min de voix clonée, la coupe se faisant en
# avançant d'une slide (session frontend, 2026-08-08). À 190 mots/min mesurés,
# 250 mots ≈ 79 s — une marge délibérée sur leur maximum : un audio trop long se
# coupe sans qu'on l'entende, un audio trop court laisse un trou sur scène.
# Le premier calibrage (550 mots, 2,9 min) rendait trois fois trop d'audio et
# coûtait 1,8 min de calcul au lieu de ~50 s.
MOTS_AUDIO = int(os.environ.get("AUDIO_MOTS_MAX", "250"))


def _fin_de_phrase_n(texte: str, n: int) -> int | None:
    """Position de fin de la n-ième phrase, ou None s'il n'y en a pas tant."""
    fins = sentence_ends(texte)
    return fins[n - 1] if len(fins) >= n else None


def inserer_bascule(texte: str, *, phrases: int = PHRASES_AVANT_BASCULE) -> str:
    """Insère le marqueur de bascule après les `phrases` premières phrases.

    Si le texte compte moins de phrases que demandé (scène très courte, ou
    découpage inattendu), le marqueur est posé en TÊTE plutôt qu'omis : mieux
    vaut que le clone lise tout que pas de marqueur du tout, car son absence
    ferait échouer le rendu et priverait la scène de son audio.
    """
    coupe = _fin_de_phrase_n(texte, phrases)
    if coupe is None:
        return f"{BASCULE}\n\n{texte.lstrip()}"
    tete, reste = texte[:coupe].rstrip(), texte[coupe:].lstrip()
    return f"{tete}\n\n{BASCULE}\n\n{reste}" if reste else f"{tete}\n\n{BASCULE}"


def extrait_audio(texte: str, *, mots_max: int = MOTS_AUDIO) -> str:
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

    for fin in fins:
        if len(apres[:fin].split()) >= mots_max:
            return apres[:fin].strip()
    return apres


def assembler(scenes: list[str], *, mots_max: int = MOTS_AUDIO,
              phrases: int = PHRASES_AVANT_BASCULE) -> str:
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
                            phrases=phrases)
    lu = extrait_audio(corps, mots_max=mots_max)
    if lu and lu in corps:
        pos = corps.index(lu) + len(lu)
        corps = f"{corps[:pos]}\n\n{FIN_AUDIO}\n\n{corps[pos:].lstrip()}".rstrip()
    else:
        corps = f"{corps.rstrip()}\n\n{FIN_AUDIO}"
    return corps
