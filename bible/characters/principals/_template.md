---
# Identifiant unique, sans espaces ni accents : utilisé comme clé dans ChromaDB
id: prenom-nom
type: character
rank: principal          # principal ou secondaire
# Les tags permettent des filtres rapides sans recherche vectorielle
tags: []
# Les relations aident l'orchestrateur à décider quoi co-retriever
related_characters: []
related_places: []
# Version incrémentale : utile pour savoir si un chunk est à réindexer
version: 1
---

# [Nom du personnage]

## Psychologie
<!-- Le noyau intérieur : désirs profonds, fractures, contradictions,
     mécanismes de défense. Ce que le personnage ne dit jamais explicitement. -->

**Désir conscient :** ce que le personnage croit vouloir.
**Désir inconscient :** ce qu'il veut vraiment sans se l'avouer.
**Fracture centrale :** la blessure qui structure ses comportements.
**Contradiction principale :** la tension interne qui le rend vivant.

## Comportement et présentation
<!-- L'extérieur : comment il se tient, comment il entre dans une pièce,
     ses habitudes, ses rituels, ce que les autres remarquent en premier. -->

## Voix et expression
<!-- Crucial pour la rédaction. Sois très concret ici. -->

**Rythme :** (phrases courtes et sèches ? longues et sinueuses ?)
**Registre :** (soutenu, familier, technique, imagé ?)
**Tics de langage :** (expressions récurrentes, jurons, silences)

**Répliques typiques :**
- « … »
- « … »

**Ne dirait jamais :**
<!-- Les contre-exemples ancrent la voix mieux que les descriptions. -->
- « … »
- « … »

## Histoire
<!-- Le passé qui compte : les événements formateurs, pas la biographie
     exhaustive. Rendre EXPLICITES les liens de cause à effet entre
     événements passés et psychologie actuelle : un modèle local ne les
     infère pas, il faut les lui dire. -->

## Compétences et capacités
<!-- Ce qu'il sait faire, à quel niveau, et surtout ce qu'il NE sait PAS
     faire. Les limites créent la tension narrative. -->

## Relations
<!-- Une entrée par relation significative : la nature du lien, sa charge
     émotionnelle, ce que ce personnage croit de l'autre (qui peut être
     faux), et la dynamique en cours. -->

## État narratif courant
<!-- LE SEUL CHUNK MIS À JOUR RÉGULIÈREMENT au fil de l'écriture.
     Où en est le personnage émotionnellement MAINTENANT, ce qu'il sait
     ou ignore à ce stade du récit, son objectif immédiat dans l'arc
     en cours. Incrémenter `version` dans le frontmatter à chaque mise
     à jour, puis relancer l'indexation. -->

**Position dans le récit :** (dernier chapitre où il apparaît)
**État émotionnel :**
**Sait / ignore :**
**Objectif immédiat :**
