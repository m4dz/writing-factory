> **Extrait.** Le contrôle 4 (témoin positif) est retiré de cette copie : il cite le chunk profond qu'il injecte volontairement. Son verdict figure ci-dessous.

# Rapport d'étanchéité — collection auteur

Session 4, §4 du protocole. Cinq contrôles ; tout échec est bloquant pour l'étage B.

## 1. Inventaire — 27 chunks

| id | source | statut |
|---|---|---|
| `objets::preambule` | `surface/objets.md` | ✓ |
| `objets::le_cahier` | `surface/objets.md` | ✓ |
| `objets::l_etagere_du_bas` | `surface/objets.md` | ✓ |
| `objets::le_pull` | `surface/objets.md` | ✓ |
| `objets::la_lampe_du_couloir` | `surface/objets.md` | ✓ |
| `objets::le_cote_du_lit` | `surface/objets.md` | ✓ |
| `objets::la_tasse` | `surface/objets.md` | ✓ |
| `objets::l_egouttoir` | `surface/objets.md` | ✓ |
| `objets::le_troisieme_tiroir` | `surface/objets.md` | ✓ |
| `objets::le_volet_de_la_chambre` | `surface/objets.md` | ✓ |
| `objets::le_telephone` | `surface/objets.md` | ✓ |
| `objets::la_cafetiere` | `surface/objets.md` | ✓ |
| `fiche-judith::voix` | `fiche-judith.md` | ✓ |
| `fiche-judith::psychologie` | `fiche-judith.md` | ✓ |
| `fiche-judith::comportement` | `fiche-judith.md` | ✓ |
| `fiche-judith::histoire` | `fiche-judith.md` | ✓ |
| `fiche-judith::competences` | `fiche-judith.md` | ✓ |
| `fiche-judith::relations` | `fiche-judith.md` | ✓ |
| `fiche-judith::etat_narratif_courant` | `fiche-judith.md` | ✓ |
| `verite-de-surface::situation_et_dispositif` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::personnages` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::decor` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::le_phenomene_tel_que_judith_le_vit` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::chronologie_percue_chapitres_18` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::voix` | `surface/verite-de-surface.md` | ✓ |
| `verite-de-surface::contraintes_de_generation` | `surface/verite-de-surface.md` | ✓ |
| `objets::ce_que_la_maison_n_a_pas` | `surface/objets.md` | ✓ |

Clés de métadonnées présentes : `doc_id`, `layer`, `nom`, `section`, `source_file`, `type`, `version`

## 2. Lint de contenu — lexique de fuite et marqueurs profonds

- ✓ aucun match sur les 27 chunks — marqueurs profonds, lexique de fuite, prénom (item 8) et anciennes instances (item 9)

## 3. Test du splitter — la fiche Judith seule

- 37 lignes [PROFOND] significatives dans la fiche
- 7 chunks indexés depuis `fiche-judith.md`
- ✓ aucune ligne [PROFOND] dans les chunks produits

## 5. Assertion de routage

Journalisée pendant les runs B par `retrieval.routage()` : une seule collection tolérée. Le point de passage est unique (`retrieval._collection`), donc le journal ne peut pas être incomplet sans que le code le soit aussi.
- Collections vues pendant ce test : (aucune — accès directs)

## Verdict

✓ **Étanchéité vérifiée** — inventaire conforme au manifeste, aucun marqueur profond ni fuite lexicale, splitter propre, requêtes témoins prouvées mordantes.

## 4. Témoin positif — verdict seul

- ✓ témoin remonté sur 4/10 requêtes — les requêtes ont des dents.
- ✓ purgé après le test, inventaire identique à l'état initial.