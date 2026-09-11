"""Crafted French replies, one per node, conforming to the pipeline's validators.

Conformance is not a wish: ``tests/unit/test_fixtures.py`` runs each text
through the validator the pipeline applies to it (sentence bounds, gesture
validators, beat scorer, lint). A fixture that stops conforming fails there,
not silently inside the snapshot run.

Nothing here is prose the project would publish; the point is to make the
graph walk its nominal path deterministically.
"""

FACTS = (
    "- La femme qu'elle aimait est partie il y a un an, sans un mot.\n"
    "- Elle est correctrice et travaille chez elle, sur le manuscrit en cours.\n"
    "- Elle relit chaque soir l'entrée de la veille de son cahier.\n"
    "- Le verdict imposé du chapitre est une erreur de relevé.\n"
)

PLAN = (
    "1. [Ciel couvert] elle relit l'entrée de la veille, compte deux assiettes "
    "là où sa mémoire en dit une, va vérifier à la cuisine.\n"
    "2. [Pluie fine] elle relit l'entrée du soir précédent, retrouve le mot "
    "qu'elle n'a pas écrit, refait sa soirée heure par heure.\n"
    "3. [Vent] elle relit, constate une troisième divergence, rend son verdict "
    "et résout de pointer plus précisément.\n"
)

CONTINUATION = "Je referme le cahier et j'éteins la lampe."

# Chapter 7, entry 1 — two sentences naming the erasure of the anniversary.
SHORT_ENTRY = (
    "J'ai rangé les photos dans la boîte, supprimé la playlist et laissé le "
    "plat des grandes occasions au fond du placard. Une journée ordinaire, "
    "rien de plus, et je n'ai pas mis le couvert."
)

# Chapter 7, entry 2 — three bounded beats. No resolution, no presence, no
# restart, no recursion, no forbidden decor; an open doubt in each.
BEATS = (
    "Je rentre et la maison est allumée. Sur la table du séjour, la boîte est "
    "ouverte, les photos étalées en éventail. Je les ai rangées cet après-midi, "
    "la boîte fermée, l'étagère du bas. Je reste debout avec mon manteau.",
    "Dans le salon, l'enceinte est allumée et la musique tourne, la liste que "
    "j'ai effacée ce matin, titre après titre. À la cuisine, le plat est au "
    "four, l'odeur remplit la pièce. Sur la table, les deux couverts sont mis, les "
    "verres alignés. Je compte les assiettes deux fois. Je ne me souviens pas "
    "d'avoir sorti le plat.",
    "Le cahier est ouvert sur la table, à la page d'hier, la ligne relue trois "
    "fois. Rien n'est écrit de ma main entre midi et ce soir. Je ne sais pas si "
    "c'est moi qui ai mis la table sans le savoir. La lampe reste allumée.",
)

# Chapter 2 — the three segments of an entry (opening, reconstruction, closing).
OPENING = (
    "Le cahier est ouvert à la page d'hier, comme chaque soir, la lampe basse, "
    "le manuscrit repoussé sur le coin de la table. Je relis la phrase, deux "
    "fois. Ma mémoire dit une assiette, un dîner pris seule, debout, et la "
    "phrase en compte deux. Je repousse la chaise, je me lève, la main encore "
    "sur le cahier. Le couloir est sombre. Je m'arrête à la porte de la "
    "cuisine, sans allumer."
)

RECONSTRUCTION = (
    "Dix-huit heures trente. La table du séjour, le manuscrit ouvert au "
    "chapitre onze, le crayon rouge, la marge pleine de mes signes. Je "
    "corrige jusqu'à la dernière ligne de la page, je note l'heure dans la "
    "marge.\n\n"
    "Dix-neuf heures quinze. La cuisine, l'égouttoir vide, l'eau qui chauffe. "
    "Une casserole, du sel, le pain coupé en deux tranches. L'assiette sortie "
    "du placard, la fourchette, le verre.\n\n"
    "Dix-neuf heures quarante. Le dîner, l'assiette sur la table, le pain à "
    "gauche, le verre à droite. Je mange debout près de la fenêtre, le "
    "torchon sur l'épaule. La nuit tombe sur le jardin.\n\n"
    "Vingt heures cinq. La vaisselle, l'eau chaude, l'assiette rincée, "
    "retournée sur l'égouttoir. Le verre à côté. Le torchon plié sur le "
    "rebord.\n\n"
    "Vingt heures vingt. Le retour au séjour, le cahier rouvert, l'entrée de "
    "la veille relue une fois, le crayon posé. La phrase d'hier, mot à mot, "
    "les deux assiettes écrites de ma main.\n\n"
    "Vingt-deux heures. La lampe du couloir éteinte, la porte de la chambre, "
    "le volet tiré. Le pull sur la chaise. La maison silencieuse."
)

CLOSING = (
    "Erreur de relevé. J'ai compté une assiette là où il y en avait deux, "
    "et c'est le texte qui a raison, pas moi. Je pointerai plus précisément, "
    "chaque objet, chaque heure, à la ligne. La nuque raide, les doigts "
    "froids. Deux assiettes."
)

# Chapter 2 — a whole entry in one call (single strategy, 450-600 words).
FULL_ENTRY = "\n\n".join((OPENING, RECONSTRUCTION, CLOSING))


def accumulation(fall: str) -> str:
    """One sentence, twelve to twenty comma-separated steps, ending on the fall.

    Conforms to ``gestes.valider_accumulation``: at least 60 words and 6
    commas, no inner period or semicolon, under 120 words, first person or
    nominal, under 20 % abstract items, no forbidden decor, not the reference.
    """
    return (
        "Dix-neuf heures quinze, la clé dans la serrure, la lumière du couloir "
        "déjà allumée, le manteau sur la chaise, la table du séjour, le "
        "manuscrit refermé, la cuisine, l'eau du robinet, la casserole sur le "
        "feu, le sel, le pain coupé, l'assiette posée sur la table, la "
        "fourchette, le verre rempli, le repas pris debout près de la fenêtre, "
        "l'eau chaude, le torchon, l'égouttoir essuyé, le couloir, la lampe "
        "éteinte, le cahier rouvert sur la table, la page relue une fois, "
        f"chaque chose à sa place, sauf une, une seule, {fall}."
    )


ROLEPLAY_REPLY = (
    "— Je corrige des manuscrits, c'est tout. Si vous avez une question sur une "
    "virgule, je vous écoute. Sinon, laissez-moi finir ma page."
)

ROLEPLAY_SUMMARY = (
    "- L'interlocuteur demande ce qu'elle fait de ses soirées.\n"
    "- Elle répond qu'elle corrige et qu'elle relit son cahier.\n"
    "- Elle refuse de parler de la personne qui a partagé la maison.\n"
)

# Failing variants, for the tests that exercise retries and rejections.
OUT_OF_ROLE = ("Je suis simplement un programme informatique conçu pour "
               "simuler des conversations.")
BEAT_RESOLVING = ("Je me souviens soudain de tout : j'ai bien mis les deux "
                  "couverts ce matin. Tout est normal.")
ACCUMULATION_ENGLISH = ("The evening, the plate, the sink, the towel, the lamp, "
                        "the notebook, the page, the pencil, the door, the "
                        "bed, the window, the plate.")
ACCUMULATION_SHORT = "Le retour, l'assiette, le verre, sauf une, l'assiette."
