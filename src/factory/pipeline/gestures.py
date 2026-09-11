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

import random
import re

from factory.eval.lint import (ACC_ABSTRACT_MAX, L3_WORDS,
                        L3_COMMAS, summarizing_accumulation,
                        accumulation_at_first_person, accumulations_l3,
                        material_forbidden, sentences, reference_copy)
from factory.text import delint

MAX_ATTEMPTS = 2

# PLAFOND de l'accumulation. La spec ne posait qu'un plancher (60 mots), et le
# modèle occupe l'espace offert : 214 mots sur C1, contre 90 pour l'étalon. Le
# raisonnement est celui qui avait fait écarter la montée de `num_predict` en
# session 1, pris par l'autre bout — un seuil sans borne haute ne cadre rien.
ACC_WORDS_MAX = 120

# Le terme de verdict est le REPÈRE PRIMAIRE de l'entrée, et ce n'est pas un
# détail d'implémentation : c'est le seul point garanti, parce qu'un autre
# contrôle l'exige en présence (lint du verdict, notes d'outillage §3).
#
# Les marqueurs de reconstruction ne servent qu'en repli. Ils sont dépendants du
# chapitre : « fatigue » est la marche du chapitre 2, mais la table de pilotage
# la fait migrer (automatisme, trouble, l'autre). S'appuyer sur eux en primaire
# aurait cassé EN SILENCE dès le chapitre 3.
RECONSTRUCTION_MARKERS = re.compile(
    r"\b(dans l'ordre|reprends? les faits|repass\w+|reconstitu\w+|"
    r"fatigue|automatisme|trouble|distraction|inattention)\b", re.IGNORECASE)

# LE PIVOT SUSPENDU — ce qui fait qu'une phrase est une approche.
#
# ⚠ Ce motif REMPLACE un `CHAMP_DEPART` qui exigeait un mot du départ (partie,
# absence, quittée…). Ce critère était FAUX, et il coûtait le geste :
#
#   · il rejette les TROIS approches écrites main livrées par le protocole
#     (« Je pourrais me demander ce qui, ce soir-là », « Si je savais seulement
#     pourquoi », « Il faudrait que je relise le jour où elle ») — aucune ne
#     contient de mot du départ ;
#   · et c'est littéralement lui qui a rejeté l'approche du modèle sur C2, deux
#     essais de suite : « approche rejetée — n'approche pas le départ (champ
#     lexical absent) ».
#
# Le geste est défini par l'interruption AVANT que le départ soit nommé. Exiger
# le mot du départ dans l'approche, c'est exiger que le geste n'ait pas lieu :
# le validateur qui devait garantir le glissement était ce qui l'empêchait.
#
# Ce qu'une approche porte vraiment, c'est un PIVOT resté ouvert — un mot
# interrogatif ou relatif après lequel la phrase se coupe.
# Le champ du départ, INTERDIT dans un passage rédigé : le geste s'arrête avant
# de nommer. Même liste que le lint L4, employée à l'envers.
FORBIDDEN_DEPARTURE_FIELD = re.compile(
    r"\b(partie|départ|absence|absente|quittée|plus là)\b", re.IGNORECASE)
SUSPENSION_PASSAGE = re.compile(r"…|\.\.\.")

SUSPENDED_PIVOT = re.compile(
    r"\b(ce qui|ce que|pourquoi|comment|où|quand|le jour où|si elle|"
    r"ce qu'|qui a|quelle|lequel)\b", re.IGNORECASE)


def paragraphs(text: str) -> list[tuple[int, int, str]]:
    """(début, fin, contenu) de chaque paragraphe, offsets sur le texte donné."""
    out, pos = [], 0
    for block in text.split("\n\n"):
        out.append((pos, pos + len(block), block))
        pos += len(block) + 2
    return [b for b in out if b[2].strip()]


def accumulation_position(text: str, verdict: str) -> int:
    """Offset d'insertion : juste AVANT le paragraphe du verdict.

    Repli sur le dernier paragraphe portant des marqueurs de reconstruction,
    puis sur l'avant-dernier paragraphe. Rend toujours une position valide : un
    geste qu'on renonce à placer est un geste perdu.
    """
    paras = paragraphs(text)
    if verdict:
        core = re.split(r"\s*\(", verdict)[0].strip()
        for start, _, content in paras:
            if core and core.lower() in content.lower():
                return start
    for start, _, content in reversed(paras):
        if RECONSTRUCTION_MARKERS.search(content):
            return start
    return paras[-1][0] if len(paras) > 1 else len(text)


def drift_position(text: str, acc_position: int,
                        reconstruction_bounds: tuple[int, int] | None = None
                        ) -> int:
    """Offset d'insertion du glissement, dans la reconstruction.

    RÈGLE 1 : jamais dans le paragraphe qui va recevoir l'accumulation. Si le
    seul candidat est celui-là, on recule d'un paragraphe.

    Quand `write` génère en trois segments, les BORNES de la reconstruction sont
    connues et font foi. C'est un gain de fond, pas de confort : le repli sur
    `MARQUEURS_RECONSTRUCTION` s'indexait sur *fatigue* et *automatisme*, qui
    sont des valeurs de la colonne « marche des explications » — la table de
    pilotage les fait migrer (fatigue → automatisme → trouble → l'autre), donc
    ce repli aurait cassé EN SILENCE dès le chapitre 3. Le découpage rend la
    reconstruction repérable par construction plutôt que par lexique.
    """
    paras = paragraphs(text)
    # LE DERNIER TIERS EST INTERDIT AU GLISSEMENT (micro-lot, item 3).
    #
    # Sur S7-2 il s'est posé en DERNIÈRE LIGNE de l'entrée, après le couperet et
    # la physiologie : là, une phrase suspendue ne suspend plus rien, elle
    # console. Le geste vit dans la reconstruction, où il interrompt une pensée
    # en cours ; en clôture, il défait la chute que la fermeture vient de poser.
    last_third = int(len(text) * 2 / 3)
    if reconstruction_bounds:
        a, b = reconstruction_bounds
        b = min(b, last_third) if a < last_third else b
        inner = [p for p in paras if a <= p[0] < b]
        # NON ADJACENT, et pas seulement « pas dans le même paragraphe ».
        # Le §2 du protocole dit « jamais adjacent à l'accumulation », et la
        # nuance compte : posé en fin du dernier paragraphe de la
        # reconstruction, le glissement tombe juste au-dessus de l'accumulation
        # — deux signatures collées, ce qui fait un tic et non un style. On
        # préfère donc un paragraphe qui ne touche pas le point d'épissure.
        # Mesuré sur un cas de test avant d'être écrit : la reconstruction à
        # deux paragraphes produisait exactement cette collision.
        distant = [p for p in inner if p[1] + 2 != acc_position]
        for start, end, _ in reversed(distant or inner):
            if start != acc_position:
                return end
    candidates = [p for p in paras if RECONSTRUCTION_MARKERS.search(p[2])
                 and p[0] < last_third]
    if not candidates:
        candidates = [p for p in paras[1:-1] if p[0] < last_third] or paras[1:-1] or paras
    for start, end, _ in reversed(candidates):
        if start != acc_position:
            return end
    previous_ones = [p for p in paras if p[0] < acc_position]
    return previous_ones[-1][1] if previous_ones else paras[0][1]


# ---------------------------------------------------------------------------
# LA BANQUE D'APPROCHES — le geste quitte le modèle (session 6, §2)
#
# Huit runs, puis trois de plus à l'étage C : le modèle n'a jamais fourni cette
# phrase. Trois modes d'échec distincts, ce qui dit que la difficulté n'est pas
# la longueur mais la NATURE de la demande — approcher un sujet puis
# s'interrompre est un geste de sens, pas de forme. La mesure a tranché.
#
# C'est la doctrine des citations du cahier, étendue : la matière la plus intime
# du roman est écrite main. Le code choisit, coupe et colle ; il n'invente rien.
# ---------------------------------------------------------------------------
DRIFT_BANK: dict[int, dict] = {
    2: {
        "approches": (
            "Je pourrais me demander ce qui, ce soir-là",
            "Si je savais seulement pourquoi",
            "Il faudrait que je relise le jour où elle",
        ),
        # Faits matériels de collage. Le retour au matériel est ce qui fait du
        # glissement un geste et non une plainte.
        #
        # PLUSIEURS, et tirés eux aussi : à l'étage C, les trois glissements de
        # CC partageaient le même fait, donc se ressemblaient par la queue —
        # 0,62 à 0,71 de similarité entre eux. Le geste variait, sa chute non.
        "faits": ("L'assiette est sèche. Je la range.",
                  "L'égouttoir est vide. Je ferme le placard.",
                  "La lampe du couloir est restée allumée. Je l'éteins."),
    },
    # CHAPITRE 7 — l'anniversaire. Banque livrée par le protocole de session 7,
    # pour l'ENTRÉE 2 seulement : l'entrée 1 tient en deux phrases, elle n'a pas
    # la place d'un geste. Les faits sont pris au matériau imposé du brief.
    7: {
        "approches": (
            "Neuf ans, et je ne sais toujours pas ce qui",
            "J'aurais dû demander, le jour où elle",
            "Je pourrais compter ce qui reste depuis qu'elle",
        ),
        "faits": ("Le plat est au four.",
                  "Les deux couverts sont mis."),
    },
}


def approach_valid(approach: str) -> tuple[bool, str]:
    """Une approche est-elle exploitable ? ASSERTION DE BANQUE.

    Depuis que la matière est écrite main, cette fonction ne filtre plus une
    sortie de modèle : elle vérifie que la banque est conforme. On la garde —
    « avant de faire confiance à un contrôle, exiger qu'il échoue sur un cas
    connu » suppose un contrôle, et une banque éditée à la main peut recevoir
    une ligne fautive comme n'importe quel fichier.

    Trois critères, et pas un de plus : assez longue pour être une phrase, pas
    un en-tête daté (le modèle avait rendu « Mardi 12. Pluie fine » comme
    approche, et le code en avait composé un faux en-tête au milieu de
    l'entrée), et un pivot resté ouvert.
    """
    a = approach.strip()
    if len(a.split()) < 5:
        return False, f"trop courte ({len(a.split())} mots)"
    if re.match(r"^(?:Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)\s+\d",
                a, re.IGNORECASE):
        return False, "c'est un en-tête daté, pas une approche"
    if not SUSPENDED_PIVOT.search(a):
        return False, "aucun pivot resté ouvert (ce qui, pourquoi, le jour où…)"
    return True, ""


# La banque se falsifie AU CHARGEMENT. C'est ainsi qu'on découvre qu'un critère
# d'entrée refuse la matière de référence : `CHAMP_DEPART` rejetait ces trois
# lignes, et l'assertion l'aurait dit au premier import au lieu de le laisser
# se découvrir en fin de run, dans les warnings.
for _ch, _bank in DRIFT_BANK.items():
    for _a in _bank["approches"]:
        _ok, _reason = approach_valid(_a)
        assert _ok, (f"banque du chapitre {_ch} : approche refusée par son "
                     f"propre validateur — « {_a} » ({_reason})")


def passage_valid(passage: str) -> tuple[bool, str]:
    """Le glissement RÉDIGÉ, livré entier par le brief. Validation symétrique.

    Deux conditions, et la seconde est neuve :
      · un PIVOT resté ouvert — la phrase s'approche puis se coupe ;
      · AUCUN mot du champ du départ — nommer le départ est un refus.

    La session 6 avait retiré l'exigence inverse : `CHAMP_DEPART` demandait un
    mot du départ DANS l'approche, ce qui rejetait les trois approches livrées
    et bloquait le geste. La règle se retourne ici et devient plus forte : le
    geste consiste à s'interrompre AVANT de nommer, donc nommer le disqualifie.

    Falsifiée dans les deux sens sur le passage livré et sur une variante qui
    nomme le départ — sans quoi ce ne serait qu'une préférence.
    """
    p = passage.strip()
    if len(p.split()) < 8:
        return False, f"trop court ({len(p.split())} mots)"
    if not SUSPENDED_PIVOT.search(p):
        return False, "aucun pivot resté ouvert (ce qui, pourquoi, quand…)"
    if FORBIDDEN_DEPARTURE_FIELD.search(p):
        m = FORBIDDEN_DEPARTURE_FIELD.search(p)
        return False, (f"nomme le départ (« {m.group(0)} ») — le geste "
                       "s'interrompt AVANT")
    if not SUSPENSION_PASSAGE.search(p):
        return False, "aucune interruption marquée par des points de suspension"
    if len(SUSPENSION_PASSAGE.findall(p)) > 1:
        return False, f"{len(SUSPENSION_PASSAGE.findall(p))} interruptions — une seule"
    return True, ""


def draw_approach(chapter: int, already_drawn: list[str],
                   seed: int) -> tuple[str, str]:
    """Tire une approche non encore utilisée dans ce chapitre, et le fait.

    Tirage ALÉATOIRE SANS REMISE, graine fournie par l'appelant et consignée au
    frontmatter du run. Le déterminisme par index d'entrée aurait remis la même
    phrase à la même place à chaque run : une liturgie de notre propre gabarit,
    exactement le défaut mesuré trois fois (l'étalon récité, les contre-exemples
    repris). La graine garde le run rejouable.

    Rend `("", "")` si le chapitre n'a pas de banque : un chapitre sans
    glissement prévu n'est pas une erreur, et M1 le lit comme « non prévu ».
    """
    bank = DRIFT_BANK.get(chapter)
    if not bank:
        return "", ""
    facts = bank["faits"]
    # Le fait tourne AVEC l'approche, sur son propre index : deux glissements
    # d'un même chapitre ne partagent ni leur tête ni leur queue.
    fact = facts[len(already_drawn) % len(facts)]
    remaining_ones = [a for a in bank["approches"] if a not in already_drawn]
    if not remaining_ones:
        # Plus d'approche neuve : on rend vide plutôt que de répéter. Deux fois
        # la même phrase dans un chapitre, c'est le tic qu'on cherche à éteindre.
        return "", fact
    return random.Random(seed + len(already_drawn)).choice(remaining_ones), fact


def compose_drift(approach: str, material_fact: str) -> str:
    """Coupe l'approche sur « … » et enchaîne le fait matériel.

    Le code COMPOSE : c'est ce qui rend le geste conforme par construction —
    au plus une occurrence, la coupe au bon endroit, le retour immédiat au
    matériel. Le modèle n'a fourni qu'une phrase.
    """
    a = approach.strip().rstrip(" .!?…")
    # Si le modèle a déjà mis des points de suspension, on coupe là.
    a = re.split(r"\s*(?:…|\.\.\.)", a)[0].rstrip(" ,;")
    return f"{a}… {material_fact.strip()}"


def validate_accumulation(sentence: str, last_attempt: bool = False,
                         chapter: int = 2) -> tuple[bool, str]:
    """Vérification COMPTABLE, plus une garde anti-recopie.

    Une accumulation recopiée de l'étalon n'en est pas une : la session 3 a vu
    deux « réussites » qui étaient l'étalon au caractère près, dans une scène
    qui parlait d'autre chose.
    """
    if not accumulations_l3(sentence):
        # LE MESSAGE DIT CE QUE LA PORTE A MESURÉ, pas ce que le candidat pèse.
        #
        # L'ancienne version comptait la phrase ENTIÈRE (`len(split())`) alors
        # que `accumulations_l3` mesure la plus longue PHRASE et refuse tout
        # point-virgule. D'où le message impossible de S6-2 : « 60 mots,
        # 10 virgules ; il faut 60 et 6 » — et refusé. Le candidat portait un
        # point interne ou un `;`, pas huit mots de moins.
        #
        # Ce n'est pas un détail de confort : c'est sur ce message que le
        # protocole de session 7 a diagnostiqué « perdue pour huit mots » et
        # demandé de symétriser les seuils. Un contrôle qui rapporte autre chose
        # que ce qu'il mesure fait corriger la mauvaise pièce.
        segments = sentences(sentence)
        longest = max(segments, key=lambda p: len(p.split()), default=sentence)
        cause = []
        if len(segments) > 1:
            cause.append(f"{len(segments)} phrases (un point à l'intérieur)")
        if ";" in sentence:
            cause.append("un point-virgule")
        m, v = len(longest.split()), longest.count(",")
        if m < L3_WORDS:
            cause.append(f"{m} mots au lieu de {L3_WORDS}")
        if v < L3_COMMAS:
            cause.append(f"{v} virgules au lieu de {L3_COMMAS}")
        detail = ", ".join(cause) + f" (candidat entier : {len(sentence.split())} mots)"
        # SYMÉTRIE DU SEUIL (session 7). Le plafond était toléré au dernier
        # essai, le plancher non : S6-2 a rendu une accumulation à huit mots du
        # compte et l'a perdue, pendant que S6-1 en gardait une de 215. Une
        # accumulation un peu courte est un défaut de style ; une accumulation
        # absente est un échec bloquant — l'asymétrie punissait le moindre mal.
        #
        # La tolérance ne vaut QUE pour le compte. Une phrase coupée en deux ou
        # portant un point-virgule n'est pas une accumulation trop courte, c'est
        # autre chose : la forme reste refusée jusqu'au bout.
        broken_form = len(segments) > 1 or ";" in sentence
        if not last_attempt or broken_form:
            return False, "seuils non atteints — " + detail
        return True, f"ACCEPTÉE malgré des seuils non atteints — {detail} — dernier essai"
    if reference_copy(sentence):
        return False, "étalon recopié — ce n'est pas une accumulation"
    # Le plafond est STRICT au premier essai, TOLÉRÉ au dernier : une
    # accumulation trop longue est un défaut de style, une accumulation absente
    # est un échec bloquant. On refuse la démesure quand on peut encore
    # relancer, on l'accepte en la signalant quand c'est le dernier tour.
    n = len(sentence.split())
    # PLAFOND DUR (1,4× le plafond souple). La tolérance du dernier essai n'avait
    # PAS de limite : un tirage a rendu 190 mots (~30 étapes), accepté « malgré
    # 190 mots — dernier essai », et coupé en plein mot au service. Au-delà de
    # ~1,5× le plafond, ce n'est plus « un peu longue », c'est un emballement.
    # L'accumulation est optionnelle : mieux vaut aucune qu'une litanie tronquée.
    if n > int(ACC_WORDS_MAX * 1.4):
        return False, (f"emballement ({n} mots ; plafond dur "
                       f"{int(ACC_WORDS_MAX * 1.4)}) — rejetée même au dernier "
                       "essai, l'accumulation est droppée")
    if n > ACC_WORDS_MAX and not last_attempt:
        return False, (f"trop longue ({n} mots ; plafond {ACC_WORDS_MAX})")
    # LA LANGUE. Au premier run C, `accumulate` a rendu une phrase de 75 mots et
    # 7 virgules — en ANGLAIS (« Despite having dinner alone with one plate… »),
    # et la validation l'a acceptée : elle comptait des mots et des virgules,
    # pas une langue. Compter n'est pas lire. FRENCH_GUARD était pourtant dans
    # le prompt système : la garde ne suffit pas, il faut le contrôle en sortie.
    _, alerts = delint(sentence)
    leaks = [a for a in alerts if "anglais" in a]
    if leaks:
        return False, f"langue : {leaks[0]}"
    # L'ACCUMULATION QUI SE RÉSUME (session 6). C2 a rendu 131 mots de table des
    # matières — « perplexité, concentration sur les détails, rappel des faits,
    # fatigue, panique… » — et les compteurs l'ont acceptée. C'est *compter n'est
    # pas lire* pour la deuxième fois, après l'anglais.
    #
    # ⚠ Le protocole prescrivait « propositions verbales exigées ». Mesuré :
    # ce critère REJETTE L'ÉTALON, dont l'accumulation est nominale à 88 % de
    # ses items (« le café de sept heures, le départ de sept heures quarante,
    # la réunion, le déjeuner, le garage… »). Le vrai discriminant est
    # l'ABSTRACTION — l'étalon énumère des choses et des moments, C2 énumérait
    # les beats de l'entrée. Étalon : 0 %. Six accumulations de l'étage C : 0 %.
    # C2 : 47 %.
    # LA PERSONNE. Le carnet n'a qu'un sujet. S7-3 a rendu « Elle est revenue à
    # vingt heures, a refermé le cahier… » au milieu d'une entrée entièrement à
    # la première personne — un basculement que seule la lecture debout voyait.
    # Rejet à la porte : c'est mécanique, et une accumulation à la mauvaise
    # personne n'est pas réparable en aval.
    person_ok, person_reason = accumulation_at_first_person(sentence)
    if not person_ok:
        return False, person_reason
    part, abstract_items = summarizing_accumulation(sentence)
    if part > ACC_ABSTRACT_MAX:
        return False, (f"elle se résume au lieu de compter : {part:.0%} d'items "
                       f"abstraits ({', '.join(abstract_items[:4])})")
    # LE DÉCOR GÉNÉRIQUE, bloquant ICI et nulle part ailleurs. `accumulate` est
    # devenu le canal de famine de l'étage C : ne recevant que l'entrée et une
    # consigne de forme, le nœud inventait les étapes manquantes depuis ses
    # priors — télévision et messages (C1), « revenue du travail » alors qu'elle
    # travaille chez elle (C3), sac à main et barquette (CC). Le monde générique
    # de nemo, chassé de `write` par le RAG, rentrait par ici.
    #
    # Bloquant sur ce nœud, simple drapeau sur le texte d'écriture : automatiser
    # un contrôle et le rendre bloquant sont deux décisions distinctes, et le
    # §4.2 exige « zéro terme » dans les accumulations PRODUITES.
    scenery = material_forbidden(sentence, chapter)
    if scenery and not last_attempt:
        return False, (f"décor hors du monde : "
                       f"{'; '.join(d.split(' : ')[0] for d in scenery[:3])}")
    if len(sentence.split()) > ACC_WORDS_MAX:
        return True, (f"ACCEPTÉE malgré {len(sentence.split())} mots (plafond "
                      f"{ACC_WORDS_MAX}) — dernier essai")
    return True, ""


# La frontière déclarée du brief est une phrase en français (« à la frontière
# entre la découverte de la musique et celle du plat »). Le composeur en tire
# l'ANCRE d'aval : le passage s'insère juste avant ce qui suit la frontière.
_FRONTIER_ANCHORS = {
    "plat": re.compile(r"\b(le plat|le four|au four)\b", re.IGNORECASE),
    "musique": re.compile(r"\b(la musique|la playlist|l'enceinte)\b", re.IGNORECASE),
    "photos": re.compile(r"\b(les photos|la boîte)\b", re.IGNORECASE),
    "couverts": re.compile(r"\b(les? (?:deux )?couverts?)\b", re.IGNORECASE),
    # CH7 e2 v3 : le moteur uncanny (objets qui se découvrent) est évacué, ses
    # ancres d'aval avec. Le glissement lexical revient au geste de correction —
    # « la marge » est de la matière servie, donc présente de façon fiable ; le
    # verdict/constat en secours si la marge n'est pas nommée.
    "marge": re.compile(r"\b(la marge|dans la marge|en marge)\b", re.IGNORECASE),
    "verdict": re.compile(r"\b(le verdict|un verdict|le constat)\b", re.IGNORECASE),
}


def frontier_position(text: str, position: str) -> int | None:
    """Offset d'insertion d'un passage à une frontière déclarée en français.

    On cherche l'ancre d'AVAL — « la frontière entre la musique et le plat »
    place le passage juste avant le paragraphe du plat. La position est ainsi
    un lieu du RÉCIT, pas un offset : le retour au matériel qui clôt le passage
    EST la découverte suivante, et le geste devient la charnière au lieu d'être
    une pièce rapportée.

    Rend None si l'ancre est introuvable — un geste placé au hasard est pire
    qu'un geste absent, et l'appelant doit pouvoir le dire.
    """
    words = position.lower()
    # L'AVAL est le dernier terme nommé DANS LA PHRASE, pas dans le
    # dictionnaire. « entre la découverte de la musique et celle du plat » :
    # l'aval est le plat. La première version itérait sur les clés et retenait
    # « musique » — le passage atterrissait un paragraphe trop tôt, à une
    # frontière qui n'était pas la bonne.
    named = [(words.rindex(key), pattern)
              for key, pattern in _FRONTIER_ANCHORS.items() if key in words]
    if not named:
        return None
    downstream = max(named)[1]
    for start, _, content in paragraphs(text):
        if downstream.search(content):
            return start
    return None


def assemble(text: str, accumulation: str, drift: str, verdict: str,
              reconstruction_bounds: tuple[int, int] | None = None,
              frontier: int | None = None) -> tuple[str, list[str]]:
    """Insère les deux gestes. RÈGLE 2 : positions sur l'original, de la fin
    vers le début."""
    notes: list[str] = []
    pos_acc = accumulation_position(text, verdict) if accumulation else -1
    pos_gli = (frontier if frontier is not None else
               drift_position(text, pos_acc, reconstruction_bounds)
               ) if drift else -1

    inserts = []
    if accumulation:
        inserts.append((pos_acc, accumulation.strip() + "\n\n"))
    if drift:
        # LA FORME DU FRAGMENT DÉPEND DU REPÈRE, et c'est facile à rater :
        # `position_glissement` rend une FIN de paragraphe (le geste se colle
        # après, donc « \n\n » devant), `position_frontiere` rend un DÉBUT (le
        # geste se pose avant, donc « \n\n » derrière). Confondre les deux
        # produit une ligne vide en trop d'un côté et un collage de l'autre —
        # exactement ce qu'a rendu le premier essai.
        inserts.append((pos_gli, drift.strip() + "\n\n"
                        if frontier is not None
                        else "\n\n" + drift.strip()))
    if accumulation and drift and pos_acc == pos_gli:
        notes.append("les deux gestes visaient le même point — glissement "
                     "reculé (règle d'assemblage 1)")

    # De la FIN vers le DÉBUT : les offsets calculés sur l'original restent
    # valides pour les insertions qui les précèdent.
    for position, fragment in sorted(inserts, key=lambda x: -x[0]):
        text = text[:position] + fragment + text[position:]
    return text, notes
