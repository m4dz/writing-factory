---
doc_id: note-implementation-mouvement
type: protocole
nom: "Note d'intention d'implémentation — la méthode du mouvement"
version: 1.0
date: 2026-08-27
statut: artefact de transmission — accompagne brief-ch7-entree2-v2.md et mouvements-chapitres.md
---

# Note d'intention — implémentation de la méthode du mouvement

## Ce qui change, en une phrase

Le prompt d'écriture cesse de décrire des cases à traverser ; il déclare un mouvement à accomplir, des directives de prose, et une matière disponible — dans cet ordre. La mesure automatique passe du rôle de juge au rôle de véto ; le juge est une ligne manuelle unique : le mouvement déclaré est-il accompli ?

## Périmètre de ce lot

**Entrée 2 du chapitre 7, seule.** L'entrée 1, `entrees_spec`, la bascule, la chute posée, le tampon d'ancre : inchangés. Le lot chapitre-7 déjà transmis (scrub de l'imitation d'en-tête, borne en phrases de l'entrée 1, interdits matériels bloquants sur texte de scène, marque effacée, attracteurs « je n'ai pas rêvé » et images d'arme) s'applique avant ou avec ce lot, au choix de l'implémentation — il est orthogonal.

## 1. Structure du prompt d'écriture (le cœur du lot)

Ordre de service, strict : **intention → trajectoire → matière → vétos.**

- `entrees_spec` gagne quatre champs par entrée : `mouvement` (une phrase, servie en première ligne), `trajectoire` (liste de directives de prose), `matiere` (liste — remplace les stations-consignes), `forme` (accumulation : exigée / autorisée / absente ; verdict : présent / absent).
- Les stations et objets passent au statut de matière disponible : ils ne sont plus des étapes à traverser ni des cases à remplir. Les bornes de mots demeurent, comme bornes.
- Les slots disparaissent du prompt : la physiologie n'est plus une case mais une directive de trajectoire (« le corps la porte une fois, au contact d'un objet ») ; le squelette n'est pas servi pour cette entrée.
- Contenu exact : `brief-ch7-entree2-v2.md`, §1 à §3 et §5.

## 2. Le glissement change de mécanisme

Plus de suture fragment + « … » + fait. Le composeur insère un **passage rédigé entier** (2–3 phrases, livré au brief §4) à une frontière de segment déclarée (`glissement: {texte, position}`). Validation à l'import, dans les deux sens : le passage livré doit être ACCEPTÉ (pivot resté ouvert, aucun mot du champ du départ, les « … » du passage restent les seuls de l'entrée — L4 inchangé) ; un passage qui nomme le départ doit être refusé. La banque d'approches courtes est retirée du chemin du chapitre 7 ; elle reste en place pour les chapitres non migrés.

## 3. Couche cachée — règle de service de la colonne « mouvement »

`mouvements-chapitres.md` est PROFOND : les lignes des chapitres 9–11 énoncent la vérité de fin. **Seule la ligne du chapitre en cours transite vers le brief**, extraite à la construction ; la garde d'entrée existante (assertion méta-termes + marqueurs profonds sur tout brief servi) doit passer sur le brief v2 — c'est le contrôle qui a attrapé « matériau » il y a deux sessions, il est déjà en place. Rien ne se réindexe dans ce lot.

## 4. Grille

- Nouvelle ligne MANUELLE, unique et en tête : « Le mouvement déclaré est-il accompli ? » — c'est le juge.
- La grille automatique est requalifiée en véto (fuites, ancre, interdits, bornes) — aucune mécanique ne change, seule la note de rôle en tête de grille.
- L3 exempté par la table pour le chapitre 7 (hors échelle) ; accumulation « autorisée, non exigée » pour cette entrée.

## 5. Le tirage comparatif

Même chaîne, mêmes deux horloges, machine branchée. Tirages jusqu'à structure valide, écarts archivés avec cause, comme toujours. Livrables : le run, la grille (véto + la ligne du juge vide), le chronométrage, le dump du prompt servi. **Comparaison au tirage 6 : même véto, et la question manuelle.** La lecture debout tranche — si le mouvement y est, la méthode se généralise aux scene briefs ; s'il n'y est pas, le dossier du rythme s'ouvre sur un fait établi, avec deux tirages comparables pour le documenter.

## 6. Vérifications

1. Dump du prompt de l'entrée 2 : l'intention en première ligne, l'ordre intention → trajectoire → matière → vétos respecté, aucun mot d'atelier (assertion existante).
2. Le glissement rédigé accepté par son validateur ; sa variante nommant le départ refusée (falsification dans les deux sens).
3. Non-régression : la grille inchangée rejouée sur le tirage 6 rend le même résultat.
4. La ligne mouvement des chapitres 9–11 n'apparaît dans aucun brief 1–8 (contrôle d'extraction).
5. Chronométrage comparable : deux horloges, veille nulle ou consignée.
