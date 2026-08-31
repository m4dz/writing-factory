---
doc_id: notes-outillage-propagation
type: outillage
version: 1.0
date: 2026-08-16
statut: handoff pour la session d'implémentation — extensions d'outillage issues du lot de propagation
---

# Notes d'outillage — lot de propagation

## 1. En-tête normalisé — détection déterministe d'entrées

Format canonique : « Jeudi 7. Beau temps. » — jour de semaine, numéro, point, météo en deux mots, point. Jamais l'année.
Regex de départ : `^(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche) [0-9]{1,2}\. .{2,40}\.$`
Trois usages : (a) le comptage d'entrées de L3 (remplace l'heuristique), (b) le point de bascule de `lire_chapitre.py` = le second en-tête du chapitre 7, (c) la validation de structure en grille.

## 2. Ratio citation/commentaire — lintable

Par entrée : signes entre guillemets français « » contre signes hors guillemets. Cible par chapitre : colonne « Ratio » de la table de pilotage (`chronologie-partie-double.md`). Trois classes suffisent : commentaire dominant / équilibre / citation dominante.

## 3. Verdict imposé — lint en présence

Le verdict du chapitre (table de pilotage) doit apparaître dans l'entrée — mot exact, ou variante légère validée à la main. Jamais de lint en absence des autres termes du lexique (la dérive synonymique est tolérée, souhaitable à faible dose). Exception : les termes réservés (la tierce, l'errata, le bon à tirer) sont lintés **en absence** sur les chapitres 1–8.

## 4. Interdits scopés par chapitre

Générés depuis la table de pilotage : termes réservés + quatuor d'objets (photos, playlist, plat, couverts) hors chapitre 7 + ancres [CIT-x] hors de leur chapitre. À intégrer à `grille_session.py` comme paramètre de chapitre.

## 5. Corrections en attente sur l'existant

- `lexique-fuite.txt` : déplacer « tombe » en L2b, signalé non bloquant (faux positif verbe, constaté session 3, run 3).
- Détecteur de tics d'IA : couvrir les variantes de temps (« je ne peux m'empêcher » a échappé au présent, run 3).
- Détecteur passé simple : « mis », « pris » sont des participes — faux positifs confirmés.
- Template de grille : l'en-tête généré dit encore « session 1 » ; retirer la ligne « décalage dans le dialogue » (remplacée par M4).

## 6. `build_etat_narratif.py` — à créer

Génère le chunk 7 (état narratif) de la fiche Judith depuis la table de pilotage. Discipline canonique : la table est la source, le chunk est un artefact généré — jamais l'inverse, jamais d'édition à la main entre deux chapitres.

## 7. Deux couches de lint sur le texte final

Les lints de voix de la fiche Judith (tics d'IA, physiologie, état mental nommé, glissement) s'appliquent **hors guillemets** uniquement : le contenu cité est fabriqué main et porte la voix de Romane, pas celle de Judith. Le contrat prose-guard (tirets-séparateurs, clichés, passifs à sujet connu, variation des longueurs) s'applique **partout**, citations comprises. Implémentation : le découpage guillemets/hors-guillemets du §2 sert aux deux couches.

## 8. Test d'étanchéité — marqueurs profonds et manifeste

`marqueurs-profonds.txt` — chaînes n'existant que dans les documents firewallés, un marqueur par ligne, recherche insensible à la casse sur chaque chunk indexé (zéro match toléré) :

```
colonne réelle
vérité profonde
partie double
Morte à J0
confabul
firewall
lecture de Judith
hors-champ
citation-fenêtre
antagoniste involontaire
métronome
Élise
Anna
```

Les deux derniers sont des canaris d'obsolescence : les anciens prénoms ne doivent exister nulle part — leur présence signale une version périmée de fichier entrée dans l'index. **Règle de chunking associée : les frontmatters YAML ne sont jamais chunkés** (ils contiennent des références croisées vers le firewallé — `depends_on`, statuts RAG).

**Manifeste des sources autorisées (collection auteur)** : `verite-de-surface.md` ; `objets.md` ; `fiche-judith.md`, blocs [SURFACE], [GABARIT], [VALEURS] uniquement. L'inventaire du test d'étanchéité (session 4, §4) vérifie que chaque chunk trace vers ce manifeste — tout intrus est un échec, quel que soit son contenu.

## 9. Indexation — périmètres

**Collection auteur (ch. 1–8)** : `verite-de-surface.md` v2 + `objets.md` + blocs [SURFACE] de `fiche-judith.md` (splitter sur les marqueurs [SURFACE]/[PROFOND]/[GABARIT]/[VALEURS]). Jamais : chronologie, fiches Romane et thérapeute, `lexique-correction.md`, briefs.
**Collection acteur** : identique, plus les sections [SURFACE] de `lexique-correction.md`. Firewall identique à celui de l'auteur — l'acteur joue Judith, pas la vérité.
