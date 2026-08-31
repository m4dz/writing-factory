---
doc_id: passation-generale
type: passation
nom: "L'Involontaire — synthèse générale et passation à la session Code"
version: 1.0
date: 2026-08-27
layer: PROFOND — ce document contient la vérité de fin. Jamais indexé, jamais dans bible/, jamais servi. Racine du repo ou docs/.
statut: la session Code devient l'assistant de réflexion unique ; ce document transfère l'état, les doctrines, les décisions ouvertes et le rôle attendu.
---

# L'Involontaire — passation générale

## 1. Le projet

Deux objets couplés. **Une nouvelle**, *L'Involontaire* : Judith, correctrice, morte sans le savoir, relit chaque soir « son » cahier — qui est le journal de deuil de Romane, sa femme vivante — et le commente dans un carnet de relecture, qui est le texte du roman. Elle croit avoir été quittée ; elle est partie. Onze chapitres, trois régimes, révélation au 9 (la tierce), fin au 11 (le bon à tirer). **Une keynote**, « L'IA devant soi » : le chapitre 7 (l'anniversaire, deux entrées) généré en direct sur une stack 100 % locale (Ollama/mistral-nemo, LangGraph, ChromaDB, TTS mlx-audio voix clonée), avec protocole de secours silencieux. La thèse des deux objets est la même, et elle est désormais mesurée : **la chaleur ne se génère pas, elle se compose** — tout ce qui est chaud dans le roman est écrit main et injecté (citations, glissements, mouvements) ; le modèle fournit le relevé, le code tient les gestes.

## 2. État de la bible (complète, verrouillée)

`chronologie-partie-double.md` (règles 1–8, colonnes réel/perçu/fuites, table de pilotage 11 chapitres — régime, grade, verdict, marche, ratio, chaleur, séances, objets, événement payeur, fragments), `verite-de-surface.md` v2, fiches Judith (double couche, splitter [SURFACE]/[PROFOND])/Romane/thérapeute, `objets.md` (+ section du vide), `lexique-correction.md`, `citations-cahier.md` (neuf mini-entrées sources, versions injectables = lectures de Judith, double version veuve/vieille au ch. 3), `style-auteur.md` v3, `mouvements-chapitres.md` (nouveau, PROFOND, la ligne du chapitre courant seule transite au brief). Format : ch. 1–6 et 8–11 = trois entrées de 450–600 mots ; ch. 7 = deux entrées, 800–1000, entrée 1 en deux phrases. Le firewall : la collection auteur ne contient que la surface ; audit par inventaire contre manifeste, marqueurs profonds, canaris d'obsolescence (Élise/Anna), témoin positif — **l'étanchéité se re-prouve à chaque réindexation, jamais présumée**.

## 3. État de la machine (sept sessions de mesure)

Acquis, chiffré : zéro fuite lexicale sur tous les runs scorés depuis B′ ; ancre, en-têtes et chute **possédés par le code** (préfixage concaténé + tampon post-repair — le tampon a déjà sauvé un en-tête que `repair` supprimait) ; glissement composé 4/4 ; accumulation composée 6/6 (2–5 % de similarité étalon) ; masse 2/3 en cible au compteur officiel (entrée seule, accumulation déduite) ; méta-termes 0/4 (garde d'entrée alignée sur le lint de sortie) ; répétition chapitre 7 : **7,6 minutes bout à bout, 20,4 de marge sur 28**, audio 92,5 s pour 90 visées, débit 173,9 contre 177 calibrés, deux horloges coïncidentes. Non acquis : **la voix à l'oral** (verdict constant : la restitution chevrote — texture par endroits, jamais soutenue) ; **le mouvement** (le tirage comparatif de la méthode du mouvement est le test en cours) ; **le texte backup** (le tirage 6 du ch. 7 est structurellement complet, scéniquement fautif).

## 4. Les doctrines (l'acquis le plus précieux — les tenir)

1. **Le modèle fournit la matière, le code tient le geste.** Chute, ancre, en-têtes, glissement, assemblage : au code.
2. **La chaleur ne se génère pas, elle se compose.** Le firewall affame le modèle en matière chaude par construction : sa chaleur spontanée est confabulée (prénoms, fantômes, quatuor — toujours dans les passages chauds).
3. **Compter n'est pas lire.** La grille automatique est un véto (fuites, ancres, interdits, bornes) ; le juge est la lecture debout, désormais incarnée par la ligne manuelle « le mouvement déclaré est-il accompli ? ».
4. **Falsifier dans les deux sens.** Un contrôle doit échouer sur un cas connu ET accepter la référence. Quatre contrôles justes en apparence refusaient l'étalon ou la banque (CHAMP_DEPART, critère verbal, similarité de mots, filtre de longueur).
5. **Les instruments mentent** : lint fantôme (calculé, jamais câblé), message qui rapporte autre chose que ce que la porte mesure, chronomètre qui s'arrête en veille, ligne de grille absente. Aucun détecteur sans sa ligne ; aucun chiffre sans son horloge.
6. **Montré = récité.** Étalons, exemples, contre-exemples, mots du brief : tout ce qui est servi peut ressortir verbatim (« perplexe » était le contre-exemple ; « Couperet : » venait du squelette servi). Les instances vivent dans l'outillage, le contexte servi ne porte que des catégories et des attitudes.
7. **Un vide dans la matière servie se remplit toujours** — par le monde générique du modèle (travail, télévision, sac à main) ou par un emprunt (le verdict « coquille » au ch. 7 hors échelle). Le vide s'écrit : section « Ce que la maison n'a pas », « aucun verdict ne se rend ce soir ».
8. **Une consigne qui décrit ce que le personnage décide produit un personnage qui décrit ses décisions.** Les consignes énoncent des faits et des trajectoires, jamais des intentions.
9. **L'exception se déclare en données, jamais en assouplissement de règle** (`entrees_spec`). Corollaire : tout validateur écrit avant une structure la lit comme une anomalie — trois occurrences (glissement, garde-fou, en-têtes du 7).
10. **L'interdit seul déplace le défaut** : la fiche dit ce que le personnage fait *à la place* (elle inscrit ; le corps, une ligne).
11. **Toute fiction imbriquée est un tunnel sous le firewall lexical** (le roman intérieur de B′C).
12. **Chaque dispositif qui règle un défaut en crée un à l'endroit qu'il touche** — le chercher là, systématiquement.
13. **Une seule variable entre deux mesures ; les runs ratés sont de la matière** (`journal-des-murs/` : le coup de couteau, le roman intérieur, le dîner fabriqué, le sommaire nominal, « Finalement, j'ai compris », la saga des six tirages, « le clone disait tout sauf la phrase pour laquelle il parle »).

## 5. Le tournant en cours — la méthode du mouvement

Diagnostic acté après la répétition : la stack produisait de la conformité sans intention — un patchwork sans consistance globale, des chapitres tous écrits de la même manière. Le contexte servi décrivait des faits, des formes et des prohibitions ; jamais ce que l'entrée doit *faire*. La correction : ordre de service **intention → trajectoire → matière → vétos** ; la colonne « mouvement » écrite main (11 chapitres livrés, arbitrés) ; le glissement en passage rédigé entier ; les stations en matière disponible ; la ligne manuelle en juge. **Le test en cours : tirage comparatif de l'entrée 2 du chapitre 7 contre le tirage 6** (note d'implémentation livrée). Trois issues : le mouvement y est → généralisation aux scene briefs (~30 mouvements par entrée à rédiger, format départ/bascule/arrivée — écriture d'auteur, arbitrage requis) ; il n'y est pas → le dossier du rythme s'ouvre sur deux tirages comparables (options : passe de révision dédiée — risquée, `review` a toujours abîmé —, réserves lourdes LoRA/modèle, ou **passe humaine assumée**, qui est thématiquement le sujet même du roman) ; entre les deux → itérer sur la trajectoire, pas sur l'architecture.

## 6. Reste à faire

**Machine** : le tirage comparatif ; le lot chapitre-7 (8 items de la grille remplie) ; le lot bible différé — clôtures en fiche, symétrisation du prénom de celle qui est partie à l'indexation, réindexation, étanchéité en entier ; selon verdict, généralisation ou dossier du rythme. **Roman** : scene briefs des ch. 1, 3–6, 8–11 (mouvements par entrée + matière depuis la table) ; génération chapitre par chapitre avec lecture à chaque point d'arrêt ; le mode acteur (spécifié, jamais construit — collection propre, firewall identique) ; la passe finale (décision d'auteur ouverte, cf. §7). **Keynote** : second tirage ch. 7 → lecture debout → WAV de secours rendu et archivé ; répétition générale chronométrée complète (préchauffage TTS inclus — 0,60× à froid) ; sections 6–7 figées avec les chiffres ; placeholders des sections 5–6 (extraits du journal des murs, un échange verbatim en mode acteur) ; **la question locale/cloud à trancher dans le cadrage public** — les travaux fondateurs (bible, calibration, arbitrages) ont été menés en cloud, l'exécution est locale : Mads a flaggé le point, il mérite d'être dit plutôt que masqué ; assets pulp hi-res restants (Dumas, Vian, rue-pluie — `{SUJET}` corrigés dans la spec) ; validations projecteur (pseudo-texte Oulipo, plis) ; `CREDITS.md` (Sinzano, licence commerciale).

## 7. Décisions d'auteur — jamais prises par la session

Le canon (histoire, personnages, chronologie) ; toute phrase servie comme exemple ou injectée comme matière (citations, glissements, mouvements, fragments) ; les arbitrages de grille contestés ; la passe finale humaine ; le cadrage public de la keynote. La session **propose, rédige des variantes, argumente — et remonte l'arbitrage**. Le pattern éprouvé : « décisions que je prends, à contester si elles sont fausses » pour le technique ; « question qui vous revient » pour l'auteur.

## 8. Le rôle attendu de la session (le réalignement demandé)

De doer à assistant de réflexion. Concrètement, sur le modèle des meilleures séquences des sept sessions : **vérifier avant d'implémenter** (la préparation de session 7 a corrigé trois affirmations fausses du protocole, dont une des miennes — c'est le standard) ; **contester les specs reçues**, y compris celles de ce document ; **chercher le défaut créé par chaque correctif à l'endroit qu'il touche** ; tenir les doctrines du §4 et les enrichir quand une session en établit une nouvelle ; tenir le journal des murs ; produire des synthèses SURFACE (lintées aux marqueurs profonds avant toute sortie du repo) ; respecter les points d'arrêt — **la lecture debout de Mads est le juge, aucune généralisation sans elle** ; et adopter le style de collaboration établi : factuel, direct, sans images ni complaisance, prose dense, le désaccord argumenté préféré à l'accord confortable. Un « Go » vaut exécution complète du périmètre validé, rien de plus.
