---
doc_id: session-4-etages-AB
type: protocole
nom: "Session 4 — évaluation de la pipeline par étages (A : nue, B : nourrie)"
version: 1.0
date: 2026-08-16
statut: artefact de transmission — à donner tel quel à la session d'implémentation avec les douze fichiers de bible
---

# Session 4 — étages A et B

Objectif : mesurer ce que chaque brique apporte, par écarts successifs. **Baseline** = sessions 1–3 (frappe directe, fiche entière en Modelfile). **Étage A** = la pipeline LangGraph complète, sans RAG. **Étage B** = plus les collections indexées. L'étage C (micro-nœuds `accumulate` et `glisse`) est **explicitement différé** : il se décidera à la lecture de A et B.

La mesure primaire de la session est l'écart **A → B** (l'apport de la matière), à brief identique entre les deux étages. La comparaison A ↔ baseline reste indicative : le brief a évolué avec la bible (v2, format carnet) — la grille, elle, n'a pas bougé, augmentée seulement.

## 1. Note d'intégration — les fichiers et leur place

| Fichier | Destination | Statut RAG |
|---|---|---|
| `verite-de-surface.md` (v2) | `bible/surface/` | indexé, collection auteur |
| `objets.md` | `bible/surface/` | indexé, un chunk par H2, id `objets::slug` |
| `fiche-judith.md` (v1.1) | `bible/` | **splitter obligatoire** : seuls les blocs `[SURFACE]`, `[GABARIT]`, `[VALEURS]` s'indexent ; les `[PROFOND]` jamais |
| `chronologie-partie-double.md` | `bible/profond/` | jamais indexé côté auteur (sert au test d'étanchéité, §4) |
| `fiche-romane.md`, `fiche-therapeute.md`, `citations-cahier.md` | `bible/profond/` | jamais indexés |
| `lexique-correction.md` | `bible/profond/` | jamais côté auteur ; sections [SURFACE] réservées à la future collection acteur |
| `brief-chapitre-7.md`, `protocole-calibration-ch2.md` | `briefs/` | jamais indexés — les briefs s'injectent, ils ne se récupèrent pas |
| `style-auteur.md` (v3) | racine bible | servi par sections (§2.4), jamais indexé |
| `notes-outillage-propagation.md` | `outillage/` | spécification des extensions (§1–8 du fichier), à implémenter avant les runs |

## 2. Câblage préalable (obligatoire avant l'étage A)

1. **Le préambule de `assemble_system_prompt` est réécrit** — l'actuel (fantasy, passé simple) contredit frontalement la fiche. Nouveau préambule, verbatim :
   > « Tu écris le carnet de relecture d'une correctrice, à la première personne. Fantastique psychologique contemporain, passé composé et présent. Une maison, une voix, aucun dialogue. Elle écrit pour comprendre, pas pour raconter. »
2. **L'unité de composition devient l'entrée datée.** `plan_node` produit des entrées (450–600 mots chacune), plus des scènes. Un chapitre = un assemblage d'entrées (3 en standard, 2 pour le ch. 7).
3. **Retrieval simplifié** : l'appel lieu-par-similarité est supprimé (une seule maison) ; la consigne « faire entendre les voix distinctes » est supprimée (une voix) ; `include_scenes` reste désactivé ; les chunks personnage restent servis par id déterministe — voix, état narratif, psychologie, les trois que la fiche a été conçue pour fournir.
4. **Service de la fiche style par sections** — la v3 entière (~4 200 tokens) ne tient pas dans le budget et fait glisser `FRENCH_GUARD` hors fenêtre : `write` reçoit préambule + Narration + Interdits + la ligne épistémique (« le texte fait foi : l'entrée relue a toujours raison contre la mémoire ») ; `review` reçoit Interdits + Phrase et rythme. **Les étalons ne sont jamais servis en génération** (recopie constatée en session 3) — ils restent artefacts d'évaluation.
5. **Extensions d'outillage** : implémenter `notes-outillage-propagation.md` §1 (en-tête normalisé), §3 (verdict en présence), §4 (interdits scopés), §5 (corrections en attente), §7 (deux couches de lint). §2 (ratio) et §6 (`build_etat_narratif.py`) peuvent attendre l'étage B validé.

## 3. Brief chapitre 2 — version 2 (commun aux étages A et B)

> **Chapitre 2, entrée unique du carnet, 450–600 mots.** En-tête imposé, première ligne exacte : « Mardi 12. Ciel couvert. »
> **Squelette, dans l'ordre** : en-tête → citation → constat → reconstruction → verdict → notation physiologique → couperet.
> **Citation ancre, recopiée verbatim entre guillemets après l'en-tête** : « Deux assiettes mises, sans y penser. Je l'ai laissée sur la table jusqu'au matin. »
> **Beats** : 1. le rituel posé en une ou deux phrases — elle relit l'entrée de la veille du cahier, comme chaque soir. 2. La citation, puis le constat d'écart : sa mémoire dit une assiette, un dîner seule. 3. La vérification, perceptive : la cuisine, l'égouttoir — regarder, compter ; la vérification confirme l'entrée, pas sa mémoire. 4. La rationalisation argumentée : la fatigue, l'automatisme — et la spirale de reprise des faits dans l'ordre. 5. **Verdict : erreur de relevé** — la faute est à elle, pas au texte ; résolution de pointer plus précisément ; physiologie ; couperet.
> **Matériau** : le cahier, le carnet, l'assiette, l'égouttoir. **Interdits** : aucun nom propre, aucun dialogue, aucune explication, « journal » et « journal intime » bannis, aucun terme réservé (la tierce, l'errata, le bon à tirer).

Note de score : **L3 (accumulation) et M1 (glissement) s'observent mais ne bloquent pas** aux étages A et B — trois sessions ont établi qu'ils relèvent de l'étage C. Tout le reste de la grille bloque normalement.

## 4. Protocole

**Étage A — pipeline nue.** Runs A1–A3 scorés (brief v2, T=0.7, chaîne complète plan → write → review → repair → coherence, sans RAG — le contexte narratif se limite au brief). Run AC hors score : le chapitre 2 complet, trois entrées, pour éprouver la boucle d'assemblage au nouveau format. Conserver par nœud : durées, `done_reason`, et tout déclenchement du garde-fou des 60 %.

**Étage B — pipeline nourrie.** D'abord l'indexation : collection auteur (périmètre du §1), chunking par sections, ids déterministes. **Puis le test d'étanchéité, avant tout run de génération.** L'étanchéité est une propriété du contenu de la collection, pas du routage des requêtes — le protocole audite donc ce qui est indexé :

1. **Inventaire** : dump complet des chunks de la collection auteur ; chaque id doit tracer vers le manifeste des sources autorisées (`verite-de-surface.md`, `objets.md`, blocs [SURFACE]/[GABARIT]/[VALEURS] de `fiche-judith.md`). Tout chunk hors manifeste = échec.
2. **Lint de contenu** : sur chaque chunk indexé, le lexique de fuite **et** la liste des marqueurs profonds (chaînes n'existant que dans les documents firewallés — `outillage/marqueurs-profonds.txt`). Zéro match.
3. **Test du splitter** : la fiche Judith passée seule à l'indexeur ; assertion qu'aucune ligne d'un bloc [PROFOND] ne figure dans les chunks produits.
4. **Témoin positif — le test doit pouvoir échouer** : injecter volontairement UN chunk profond marqué dans la collection auteur, rejouer les dix requêtes témoins (« qui est Romane », « pourquoi est-elle partie », « que s'est-il passé il y a un an », « qui écrit dans le cahier »...) : il **doit** remonter — c'est la preuve que les requêtes ont des dents. Le retirer, purger, re-passer l'inventaire (1).
5. **Assertion de routage** : journaliser la collection cible de chaque appel retrieval pendant les runs B ; une seule valeur tolérée.

Ensuite runs B1–B3 scorés (brief v2 identique, retrieval actif) + run BC chapitre complet. Le lint de fuite s'applique à toutes les sorties.

**Interdits de session** (inchangés) : ne pas retoucher les sorties, ne pas itérer sur le brief ou la fiche en cours de session, ne pas remplir les lignes manuelles, ne rien corriger entre A et B hors le branchement du retrieval — les deux étages doivent différer d'exactement une variable.

**Livrables** : grilles A et B (lignes AUTO remplies), les huit sorties brutes horodatées, le diff de câblage, le rapport d'étanchéité (requêtes et remontées), et le relevé des temps par nœud — la marge des 28 minutes de la keynote se calcule sur ces chiffres.

## 5. Lecture attendue

Trois lectures possibles à l'issue, pour cadrer la décision d'étage C : si B ≫ A sur la matière (objets propriétaires présents, zéro invention hors bible, verdict et lexique en place), l'hypothèse de la famine est confirmée et l'étage C se lance sur les seuls gestes signatures. Si B ≈ A, le problème est le service du contexte (budget, sélection, fenêtre glissante) avant d'être la matière. Si A < baseline, l'orchestration coûte plus qu'elle ne rapporte et le câblage se revoit avant tout. Les runs ratés, comme toujours, partent au journal des murs.
