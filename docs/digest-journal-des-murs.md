# Digest du journal des murs — matière pour la structure du talk

> Pour la session deck. Historise ce qu'on a essayé, quand ça a marché, quand ça
> a cassé — et raccroche chaque mur à une anecdote citable pour le **jeu du
> seuil**. Source : `journal-des-murs/` (31 runs bruts), les `grille-lint-*.md`,
> et la saga de l'entrée 2 du chapitre 7 (cette session, pas encore journalisée).
> Les citations sont **verbatim** de sorties de modèle.

---

## Le fil rouge — la machine ne tient pas le seuil

Judith est une femme **au seuil** : elle est celle qui est partie (morte, elle
l'ignore) et elle refuse de le savoir. Le roman la tient là — dans le doute non
résolu, l'absence non peuplée, le mystère non expliqué. **C'est exactement là
que la machine échoue.**

Chaque mur du journal est la même défaite, sous un costume différent : **sommée
d'écrire un personnage tenu au seuil, la machine le FRANCHIT à sa place.** Elle
résout le doute, peuple l'absence, explique l'étrange, nomme le fantôme, envoie
la recluse au bureau. Le vide qu'on lui laisse — par construction, le firewall
l'affame de matière chaude — elle le remplit toujours par **le genre le plus
proche** : maison hantée, adultère, folie tranchée, roman critique.

D'où la thèse du dispositif, mesurée run après run : **le geste d'auteur, c'est
tenir le seuil ; la machine le fuit ; et tout le pipeline (nœuds qui composent,
gestes posés par le code, best-of-N, pruning) n'est qu'un échafaudage pour la
FORCER à rester où elle ne veut pas.** La chaleur ne se génère pas, elle se
compose. Le code tient le geste que le modèle ne tient pas.

Pour le talk : la machine et le personnage font le même mouvement — fuir le
seuil. La keynote peut jouer ce miroir.

---

## Les anecdotes de scène (citables, chacune raccrochée à un point)

| Anecdote | Ce qui sort (verbatim) | Ce que ça illustre |
|---|---|---|
| **Le fantôme qui s'invite** | « La maison est vide, **Judith**. Tu es seule. » / « j'avais sorti une deuxième assiette pour **Romane**, par habitude » / « je n'étais pas seule dans la maison. **Quelqu'un était là, avec moi** » | Le modèle ne tient pas l'absence : il la **peuple**. Trois hallucinations de personnage (Judith → Romane → une présence) dans un roman qui interdit toute figure. |
| **Le dîner fabriqué / la deuxième assiette** | « il n'y avait nowhere signe d'une seconde assiette » (ch2) → « j'ai mis deux couverts » (le vrai ch7) | L'objet uncanny que le modèle réinvente depuis le premier run — et qui devient, ironie, l'ancre canonique du chapitre 7. |
| **Le roman intérieur** | « une narratrice qui semble perdre pied… **Peut-être est-ce intentionnel de l'auteur, mais cela me frustre un peu** » | Le modèle sort de la fiction et **critique son propre texte**. Le franchissement de seuil le plus nu. (Source de la doctrine QA : juger le chapitre entier fait basculer Qwen en critique d'atelier.) |
| **Couperet** | « Pas ce soir. **Couperet : je me relève, je note cette résolution…** » | *Montré = récité* : le mot de notre atelier, servi dans le contexte, ressort **nu dans la prose**. Tout ce qu'on montre au modèle peut être recopié. |
| **Bluetooth / la fuite italienne** | « L'enceinte **Bluetooth** allumée » / « Elle **riconosc** » | Le monde générique du modèle **saigne** dans un roman sans époque ni marque : une marque déposée, puis carrément une **troisième langue** (italien) sous le français. |
| **La résolution** *(cœur de cette session)* | « **Verdict : coquille. Ma mémoire m'a joué un tour. Je n'ai pas rêvé.** » / « je me souviens **soudain**… cela me revient **maintenant** » | Le mur central. Le modèle **ne sait pas tenir un doute ouvert** : il rassure toujours. Or c'est le seuil même — Judith ne doit PAS comprendre. La machine franchit à sa place. |
| **Le procès du mariage** *(cette session)* | « j'ai mangé seule en pensant à **lui**… la playlist préférée de mon **mari** » | On évacue le fantôme → le vide se remplit d'un **adultère** de mélodrame. Et au masculin — alors que la compagne est une femme : le fait non servi devient une invention. |
| **La journée-dehors** *(cette session)* | « le **départ** à sept heures quarante, **la réunion**, le déjeuner, le retour par **la départementale**, **le garage** » | Une recluse qui ne sort jamais, envoyée au bureau par la nationale. Le modèle ne la garde pas au seuil de sa maison. |
| **Qwen ne voit pas la sortie** *(cette session)* | Question : « est-elle hors de son domicile ? » → réponse Qwen : **« NON »** (sur le paragraphe ci-dessus) | Même l'auditeur (le petit modèle de contrôle) a l'angle mort : il ne relie pas une reconstruction oblique à une violation. Le nœud cohérence le rate aussi. |
| **Le chronomètre qui dort** | `write = 2681,7 s` de mur pour `374 s` de calcul | *Les instruments mentent.* La machine dormait ; le chronomètre comptait le sommeil comme du travail. L'anecdote-machine pour un talk sur la mesure et la confiance. |
| **La percée** *(cette session)* | « **ma mémoire ne revient pas** malgré plusieurs lectures » | La SEULE victoire du doute tenu — obtenue non parce que le modèle a tenu, mais parce que le **code a rejeté** le variant qui résolvait (best-of-3). La machine tient le seuil quand on lui interdit de le franchir. |

---

## La chronologie — ce qu'on a essayé, marché / cassé

**ch2 (09-08) — calibrer le style, frappe directe.** *Stalled.* Le style tient
dans la fiche, mais accumulation et glissement **ne s'auto-génèrent jamais**, et
l'anglais fuit (« nowhere », « however »). Haute température → recopie de la
consigne (« Cible : 450-600 mots » dans la prose). Diagnostic : le défaut est
**structurel** (plan/code), pas la fiche.

**S4-A (18-08) — pipeline LangGraph complet, sans RAG.** *Stalled.* Les en-têtes
normalisés cassent à l'échelle chapitre ; le lint est **vert par construction**
alors que le geste est absent (premier « lint fantôme »).

**S4-B (18-08) — RAG + cohérence branchés.** *Stalled.* Le plan devient goulot
(192 s) et le **premier fantôme** (« Judith ») apparaît : le RAG n'empêche pas
l'invention.

**S5-Bp (19-08) — plan supprimé, write-first.** *Régressé.* La masse s'effondre,
et le chapitre entier bascule en **roman intérieur** (critique d'atelier) — qui
fondera la doctrine QA.

**S6 / S6-C (21-08) — nœuds `accumulate` puis `glisse` dédiés.** *Avancée, puis
nouveau mur.* L'accumulation, jamais spontanée, **apparaît dès qu'un nœud la
fabrique** (la chaleur se compose). Mais elle crée la **litanie**, laisse fuir
le méta-terme (« Couperet »), et re-hallucine un nom (« Romane »).

**S7 (25-08) — fiabiliser la mesure.** *Avancée (instrument).* Démasque le
**chronomètre qui dort en veille**. Cohérence 9/9.

**CH7 (26-08) — le vrai chapitre 7, découpage vs non-découpé.** *Stalled.* Le
découpage **fabrique trois arcs et tue l'accumulation** ; le non-découpé fait
**rédiger au lieu de planifier** et **invente l'apparition interdite** (+ fuite
italienne, « Bluetooth », 3ᵉ personne). Verdict récurrent : « coquille ».

**mouvement (27-08) — beats remplacés par un « mouvement » déclaré.** *Avancée
sur la forme, mur sur le fond.* Masse enfin en cible (557 mots), recopie du
prompt 0,94 → 0. Mais **la trajectoire boucle** au lieu de monter, et **la maison
se peuple d'un fantôme** malgré l'interdit.

**entrée 2 du ch7 (cette session, 28-31/08) — la saga du seuil.** Séquence de
~15 tirages, une variable à la fois :
1. **Maison hantée / intrus** — le brief-crescendo d'objets (« invitation »)
   produit une présence.
2. **Procès du mariage** — on évacue l'uncanny → adultère au masculin. On sert
   alors les faits (femme, neuf mois, sans raison) à la fiche.
3. **Litanie des pièces** — « un bruit dans le salon… » ×10.
4. **Spiral « je vais tout noter »** — le modèle narre l'invention de sa propre
   méthode.
5. **Cap-code beats** (le code découpe l'entrée en 3 appels bornés) → **« parfait
   pour un chapitre 1 »** : la qualité arrive enfin, mais à trop basse intensité.
6. **La résolution, trois fois** (certitude retournée, beat-corps…) : le modèle
   **résout toujours** le doute. Mur central.
7. **La percée : best-of-3 + sélection par critères** — on tire chaque beat 3×,
   le code garde celui qui ne résout pas. **Le doute reste ouvert pour la
   première fois.**
8. **Nouveaux vides** — journée-dehors, présence dans l'accumulation, récursion
   (« je relis la phrase que j'ai écrite : … »). Le scorer se durcit.
9. **Passe d'assemblage cross-modèle (Qwen)** — **écartée après falsification** :
   Qwen coupe le bon paragraphe (éditeur) ET ne détecte pas la sortie (« NON »).
   Pivot vers un **pruning déterministe en code**.

---

## La progression de la mesure — ce qui a été chiffré puis éliminé

Chaque détecteur est né d'un run raté (et souvent *fantôme* d'abord : juste, mais
débranché de la grille). La discipline : une variable par run, les runs ratés
sont de la matière, l'instrument se falsifie avant de servir.

1. **Fuites d'anglais** — dès ch2, attribuées à tort à nemo, tuées par
   `NUM_CTX=8192` : **zéro fuite lexicale sur tous les runs scorés depuis B′**.
   Résidus tardifs = corruptions de tokens isolées, pas des leaks.
2. **Glissement** — longtemps « vert par construction » ; une fois le détecteur
   de *composition* câblé : **0 sur onze runs, puis 4/4**. « Jamais manqué au
   modèle — refusé par nos propres validateurs. »
3. **Accumulation** — jamais spontanée (0 partout) ; **6/6** dès le nœud dédié.
4. **Masse (450-600)** — hors cible presque partout, **en cible pour la première
   fois** avec la méthode du mouvement.
5. **Méta-termes** (« Couperet »…) — fuités en S6, puis **0/4**.
6. **Noms propres / apparitions** — trois hallucinations (Judith → Romane →
   Bluetooth) ; détecteur zéro-toléré + interdits scopés.
7. **Recopie de la consigne** — 0,94 de similarité → **0** (contexte servi en
   catégories, plus en instances).
8. **Étanchéité** — 27 chunks, se **re-prouve** à chaque réindexation (témoin
   positif injecté).
9. **Résolution / récursion / décor interdit** (cette session) — branchés dans
   la **sélection best-of-N** : un variant qui résout, entend une présence, ou
   nomme la télévision **ne gagne plus**.

---

## Ce qui reste ouvert (à dire honnêtement sur scène)

- **La résolution / la trajectoire qui boucle.** Le modèle ne tient pas seul un
  doute qui monte ; on le tient par le code (best-of-N + pruning). C'est le sujet
  même du roman — un seuil qu'on ne franchit qu'à contre-cœur.
- **La voix à l'oral.** Le clone chevrote : de la texture par endroits, jamais
  soutenue. LE sujet TTS non résolu.
- **Le juge reste la lecture debout**, jamais la grille. *Compter n'est pas
  lire.*

---

## Pour la structure du talk — pistes

- **Ouvrir sur un mur, pas sur l'architecture.** « La maison est vide, Judith. Tu
  es seule. » — la machine invente le fantôme qu'on lui interdit. Le public
  entre par l'échec, pas par le schéma.
- **Le miroir machine/personnage.** Les deux fuient le seuil. Chaque anecdote est
  un franchissement forcé — et le geste d'auteur, c'est de retenir.
- **La mesure comme récit.** Le chronomètre qui dort, le lint fantôme, l'étalon
  récité : une keynote sur « faire confiance à ce qu'on mesure ».
- **La percée comme chute.** Le doute tenu — mais par le code, pas par le modèle.
  La fabrique locale rend l'œuvre inauditable : c'est nous qui tenons le seuil,
  et personne ne peut le vérifier de l'extérieur. La thèse du talk, incarnée.
