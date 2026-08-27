---
doc_id: note-micro-lot-repetition
type: protocole
nom: "Micro-lot pré-répétition — quatre corrections sans réindexation, puis le chapitre 7"
version: 1.0
date: 2026-08-26
statut: artefact de transmission — feu vert conditionnel du point d'arrêt S7, arbitrages du 2026-08-26
---

# Micro-lot pré-répétition

**Périmètre strict : consignes et lints seuls. La bible ne bouge pas, rien ne se réindexe, l'étanchéité acquise reste valide.** Les corrections de fiche validées sur le principe (clôture de station, dernière ligne, symétrisation du prénom de celle qui est partie) sont différées au lot post-répétition — on ne rouvre pas la bible la veille de monter sur scène.

## 1. Consignes (graph)

1. **Clôture de station** (`_SEG_RECONSTRUCTION`) : « chaque station se ferme sur un fait, jamais sur un commentaire ni une question — le relevé enchaîne sans récapituler. » Parade à la litanie (le refrain ×6 de S7-3).
2. **Clôture d'entrée** (segment fermeture) : « la dernière ligne referme, elle ne console pas — aucune promesse au lendemain, aucune adresse. » Parade à la phrase et demie fautive de S7-1 (fuite + attracteur + manuscrit + « Bonne nuit. »).

## 2. Composeur

3. **Position du glissement verrouillée** : il s'insère dans la reconstruction, jamais dans le dernier tiers de l'entrée — S7-2 l'avait en dernière ligne, où il console au lieu de suspendre. La règle d'espacement avec l'accumulation (jamais adjacents) demeure.

## 3. Lints (avec leurs lignes de grille — aucun détecteur sans sa ligne)

4. **Première personne exigée dans l'accumulation** — « Elle est revenue à vingt heures… » (S7-3) : items en troisième personne = rejet à la porte du nœud, ligne AUTO en grille.
5. **Couple M3 étendu au participe** — « Je me lève, décidée à vérifier » → vérification racontée : troisième forme après le présent et le passé composé. Reste CANDIDAT non bloquant, M3 tranche.
6. **Guillemets hors ancre en drapeau** — toute séquence entre guillemets qui n'est ni l'ancre ni le verdict final est signalée : la citation inventée de S7-3 (« "Les deux assiettes étaient bien là…" ») est une fuite de règle 8, le modèle fabrique du cahier.
7. **« Bonne nuit »** rejoint les attracteurs (famille de l'adresse consolante).

## 4. Test du test — bloquant, avant la répétition

La grille régénérée sur les runs S7 doit afficher : la troisième personne de l'accumulation S7-3, le couple au participe de S7-1, la citation inventée de S7-3. Falsification par le haut : l'ancre et le verdict final cités ne déclenchent pas le drapeau des guillemets ; l'étalon reste propre partout.

## 5. Puis : la répétition du chapitre 7

Telle que câblée et validée à sec (session 7, §5) : `entrees_spec` à deux entrées du même jour, entrée 1 en deux phrases sans découpage, [CIT-2] en ouverture d'entrée 2, banque du 7 (tirage sans remise), accumulation à chute quatuor, lint de fuite en ligne de grille du chapitre, voix `ma-voix.wav`, **chronométrage aux deux horloges, machine branchée**, coupe `trim_to_sentence` à ~1 min 30. Livrables : le run, la grille du chapitre 7, la fiche de chronométrage (génération + TTS + total contre la marge des 28 minutes), l'audio de l'entrée 2, `ctx_need`. Le run devient candidat backup s'il passe la lecture debout.
