#!/usr/bin/env python3
"""Micro-nœuds d'assemblage — les gestes signatures du style (étage C).

Deux gestes que huit runs n'ont jamais produits spontanément :

  `accumulate` — la phrase d'accumulation : une seule phrase longue, en
      propositions juxtaposées par des virgules, qui reprend les faits dans
      l'ordre jusqu'à celui qui cloche. Quatre sessions ont établi qu'elle ne
      s'obtient ni par la fiche (trois formulations essayées) ni par une boucle
      de reproche (jamais une seule authentique). Elle est donc ASSEMBLÉE.

  `glisse` — le glissement : une phrase d'approche du départ, coupée sur « … »,
      immédiatement suivie d'un fait matériel. Zéro occurrence en huit runs.

Le partage du travail est le même pour les deux : le modèle fournit la MATIÈRE
(une phrase), le code fait la FORME (la coupe, la place, le comptage). C'est la
doctrine du projet — le garde-fou qui tient est dans le code — appliquée non
plus à interdire mais à construire.

Deux règles d'assemblage, explicites parce qu'elles sont faciles à rater :

  1. **Jamais les deux gestes dans le même paragraphe.** Le glissement vit dans
     la reconstruction, l'accumulation se place avant le verdict. Adjacents, ils
     ne font pas un style : ils font un tic — exactement le défaut qu'on cherche
     à éteindre, et que l'étage C pourrait fabriquer lui-même.

  2. **Les positions se calculent sur le texte ORIGINAL, les insertions
     s'appliquent de la FIN vers le DÉBUT.** Sinon la première insertion décale
     les offsets de la seconde et le glissement atterrit à côté. Coût nul, et le
     genre d'erreur qui ne se voit qu'une fois sur trois.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "outillage"))
from lint_style import accumulations_l3, recopie_etalon  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from style import delint  # noqa: E402

MAX_TENTATIVES = 2

# PLAFOND de l'accumulation. La spec ne posait qu'un plancher (60 mots), et le
# modèle occupe l'espace offert : 214 mots sur C1, contre 90 pour l'étalon. Le
# raisonnement est celui qui avait fait écarter la montée de `num_predict` en
# session 1, pris par l'autre bout — un seuil sans borne haute ne cadre rien.
ACC_MOTS_MAX = 120

# Le terme de verdict est le REPÈRE PRIMAIRE de l'entrée, et ce n'est pas un
# détail d'implémentation : c'est le seul point garanti, parce qu'un autre
# contrôle l'exige en présence (lint du verdict, notes d'outillage §3).
#
# Les marqueurs de reconstruction ne servent qu'en repli. Ils sont dépendants du
# chapitre : « fatigue » est la marche du chapitre 2, mais la table de pilotage
# la fait migrer (automatisme, trouble, l'autre). S'appuyer sur eux en primaire
# aurait cassé EN SILENCE dès le chapitre 3.
MARQUEURS_RECONSTRUCTION = re.compile(
    r"\b(dans l'ordre|reprends? les faits|repass\w+|reconstitu\w+|"
    r"fatigue|automatisme|trouble|distraction|inattention)\b", re.IGNORECASE)

# Champ du départ — le glissement doit s'y approcher pour que L4 le reconnaisse.
CHAMP_DEPART = re.compile(
    r"\b(partie|départ|absence|absente|quittée|plus là)\b", re.IGNORECASE)


def paragraphes(texte: str) -> list[tuple[int, int, str]]:
    """(début, fin, contenu) de chaque paragraphe, offsets sur le texte donné."""
    out, pos = [], 0
    for bloc in texte.split("\n\n"):
        out.append((pos, pos + len(bloc), bloc))
        pos += len(bloc) + 2
    return [b for b in out if b[2].strip()]


def position_accumulation(texte: str, verdict: str) -> int:
    """Offset d'insertion : juste AVANT le paragraphe du verdict.

    Repli sur le dernier paragraphe portant des marqueurs de reconstruction,
    puis sur l'avant-dernier paragraphe. Rend toujours une position valide : un
    geste qu'on renonce à placer est un geste perdu.
    """
    paras = paragraphes(texte)
    if verdict:
        noyau = re.split(r"\s*\(", verdict)[0].strip()
        for debut, _, contenu in paras:
            if noyau and noyau.lower() in contenu.lower():
                return debut
    for debut, _, contenu in reversed(paras):
        if MARQUEURS_RECONSTRUCTION.search(contenu):
            return debut
    return paras[-1][0] if len(paras) > 1 else len(texte)


def position_glissement(texte: str, position_acc: int) -> int:
    """Offset d'insertion du glissement, dans la reconstruction.

    RÈGLE 1 : jamais dans le paragraphe qui va recevoir l'accumulation. Si le
    seul candidat est celui-là, on recule d'un paragraphe.
    """
    paras = paragraphes(texte)
    candidats = [p for p in paras if MARQUEURS_RECONSTRUCTION.search(p[2])]
    if not candidats:
        candidats = paras[1:-1] or paras
    for debut, fin, _ in reversed(candidats):
        if debut != position_acc:
            return fin
    precedents = [p for p in paras if p[0] < position_acc]
    return precedents[-1][1] if precedents else paras[0][1]


def approche_valide(approche: str) -> tuple[bool, str]:
    """La phrase d'approche doit approcher le DÉPART, et n'être pas un en-tête.

    Au premier run C, le modèle a rendu « Mardi 12. Pluie fine » comme phrase
    d'approche : le code a composé « Mardi 12. Pluie fine… » suivi d'une
    citation, soit un faux en-tête au milieu de l'entrée. Une transformation
    quasi déterministe doit valider son entrée, sinon elle produit du déterminé
    faux plutôt que de l'aléatoire vrai.
    """
    a = approche.strip()
    if len(a.split()) < 5:
        return False, f"trop courte ({len(a.split())} mots)"
    if re.match(r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d",
                a, re.IGNORECASE):
        return False, "c'est un en-tête daté, pas une approche"
    if not CHAMP_DEPART.search(a):
        return False, "n'approche pas le départ (champ lexical absent)"
    return True, ""


def composer_glissement(approche: str, fait_materiel: str) -> str:
    """Coupe l'approche sur « … » et enchaîne le fait matériel.

    Le code COMPOSE : c'est ce qui rend le geste conforme par construction —
    au plus une occurrence, la coupe au bon endroit, le retour immédiat au
    matériel. Le modèle n'a fourni qu'une phrase.
    """
    a = approche.strip().rstrip(" .!?…")
    # Si le modèle a déjà mis des points de suspension, on coupe là.
    a = re.split(r"\s*(?:…|\.\.\.)", a)[0].rstrip(" ,;")
    return f"{a}… {fait_materiel.strip()}"


def valider_accumulation(phrase: str,
                         dernier_essai: bool = False) -> tuple[bool, str]:
    """Vérification COMPTABLE, plus une garde anti-recopie.

    Une accumulation recopiée de l'étalon n'en est pas une : la session 3 a vu
    deux « réussites » qui étaient l'étalon au caractère près, dans une scène
    qui parlait d'autre chose.
    """
    if not accumulations_l3(phrase):
        mots = len(phrase.split())
        return False, (f"seuils non atteints ({mots} mots, "
                       f"{phrase.count(',')} virgules ; il faut 60 et 6)")
    if recopie_etalon(phrase):
        return False, "étalon recopié — ce n'est pas une accumulation"
    # Le plafond est STRICT au premier essai, TOLÉRÉ au dernier : une
    # accumulation trop longue est un défaut de style, une accumulation absente
    # est un échec bloquant. On refuse la démesure quand on peut encore
    # relancer, on l'accepte en la signalant quand c'est le dernier tour.
    if len(phrase.split()) > ACC_MOTS_MAX and not dernier_essai:
        return False, (f"trop longue ({len(phrase.split())} mots ; plafond "
                       f"{ACC_MOTS_MAX})")
    # LA LANGUE. Au premier run C, `accumulate` a rendu une phrase de 75 mots et
    # 7 virgules — en ANGLAIS (« Despite having dinner alone with one plate… »),
    # et la validation l'a acceptée : elle comptait des mots et des virgules,
    # pas une langue. Compter n'est pas lire. FRENCH_GUARD était pourtant dans
    # le prompt système : la garde ne suffit pas, il faut le contrôle en sortie.
    _, alertes = delint(phrase)
    fuites = [a for a in alertes if "anglais" in a]
    if fuites:
        return False, f"langue : {fuites[0]}"
    if len(phrase.split()) > ACC_MOTS_MAX:
        return True, (f"ACCEPTÉE malgré {len(phrase.split())} mots (plafond "
                      f"{ACC_MOTS_MAX}) — dernier essai")
    return True, ""


def assembler(texte: str, accumulation: str, glissement: str,
              verdict: str) -> tuple[str, list[str]]:
    """Insère les deux gestes. RÈGLE 2 : positions sur l'original, de la fin
    vers le début."""
    notes: list[str] = []
    pos_acc = position_accumulation(texte, verdict) if accumulation else -1
    pos_gli = position_glissement(texte, pos_acc) if glissement else -1

    inserts = []
    if accumulation:
        inserts.append((pos_acc, accumulation.strip() + "\n\n"))
    if glissement:
        inserts.append((pos_gli, "\n\n" + glissement.strip()))
    if accumulation and glissement and pos_acc == pos_gli:
        notes.append("les deux gestes visaient le même point — glissement "
                     "reculé (règle d'assemblage 1)")

    # De la FIN vers le DÉBUT : les offsets calculés sur l'original restent
    # valides pour les insertions qui les précèdent.
    for position, fragment in sorted(inserts, key=lambda x: -x[0]):
        texte = texte[:position] + fragment + texte[position:]
    return texte, notes
