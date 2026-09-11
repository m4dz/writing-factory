---
doc_id: synthese-session-7
type: retour de session
nom: "Retour d'implémentation — session 7, le lot correctif"
date: 2026-08-25
destinataire: conversation de style (rédaction de la fiche)
---

# Ce qui s'est passé — session 7

Retour d'implémentation du lot correctif : outillage (dédoublonnage, familles
d'attracteurs, seuils d'`accumulate`, garde-fou conscient de la cible, tampon
d'ancre), bible (substitutions de la fiche, section du vide dans les objets),
brief v4 corrigé (stations, consignes en faits). Trois runs de validation sur le
chapitre 2. La répétition du chapitre 7 est câblée mais pas jouée — elle attend
la lecture debout.

**Ce document est SURFACE.** Passé au lint des marqueurs profonds avant envoi,
comme les retours précédents.

---

## 1. Le résultat en trois lignes

**Les deux critères principaux sont atteints.** Masse 2 runs sur 3 en cible
(contre 1 sur 3 en session 6), ancre verbatim **3 sur 3** (contre 1 sur 3).

**« Je décide de » est éteint** : 3, 0, 0 contre 7, 1, 6. La correction était
dans nos consignes, pas dans la fiche.

**Les stations ont créé une litanie** — le défaut neuf de la session, et il est
de nature stylistique. C'est ce que la lecture doit trancher.

| | session 6 | session 7 |
|---|---|---|
| entrée seule, en cible 450-600 | 467 ✓ / 370 / 716 | 401 / **567 ✓** / **552 ✓** |
| ancre verbatim | 1/3 | **3/3** |
| « je décide de » | 7 / 1 / 6 | **3 / 0 / 0** |
| méta-termes en sortie | 0/4 | 0/3 |
| phrases reprises d'un ¶ à l'autre | 2 / 0 / 2 | 0 / 4 / 3 |

**Un run porte une fuite lexicale**, et je ne l'avais pas vue au premier compte
rendu — c'est le lint de l'archive, passé avant envoi, qui l'a rattrapée. Le
run 1 écrit *« cette deuxième assiette fantôme. Demain est un autre jour, et
j'ai un manuscrit à relire. »* Trois défauts dans une phrase et demie : le champ
interdit, l'attracteur du lendemain qui résout, et le manuscrit intérieur qu'on
croyait éteint depuis la session 5. C'est aussi la clôture de l'entrée — le
moment où le modèle apaise.

---

## 2. La litanie — ce que les stations ont coûté

Le plancher de masse est devenu mécanique : au lieu de demander « raconte
longuement », la consigne de reconstruction donne six lieux à traverser (la
table du séjour, la cuisine, le dîner, la vaisselle, la relecture, le coucher).

Ça marche : la reconstruction est enfin longue, six paragraphes au lieu de deux.

Et ça produit une **litanie**. Chaque station se referme sur le même refrain :

> *« Je me souviens distinctement d'avoir dîné seule, mais le texte raconte une
> autre histoire. Il faut vérifier. »*
> *« … mais le texte raconte une autre histoire. Il faut comprendre. »*
> *« … mais le texte raconte une autre histoire. Il faut vérifier. »*

Six fois dans la même entrée. C'est le détecteur de phrase reprise, écrit le
matin même, qui l'a attrapé — le dédoublonnage de paragraphes ne le voyait pas,
puisque chaque station est par ailleurs différente.

**C'est la troisième fois que ce motif se répète, et il vaut d'être nommé comme
régularité : un dispositif règle un défaut et en crée un autre, à l'endroit
exact qu'il touche.** L'étage C avait donné l'accumulation et fabriqué un canal
de famine ; la session 6 a donné la masse et multiplié les décisions ; la
session 7 donne la structure et fabrique un refrain.

**Question qui vous revient.** Une station traversée demande une clôture, et le
modèle prend la seule qu'il connaisse. La fiche pourrait dire comment une
station se ferme — ou dire qu'elle ne se ferme pas, que le relevé enchaîne sans
récapituler. C'est un choix de rythme, et il n'appartient pas au câblage.

---

## 3. Quatre fois, un contrôle visait ce qu'il devait protéger

C'est la continuité directe de la session 6, où le validateur du glissement
était ce qui empêchait le glissement. Le même piège s'est présenté quatre fois
en une journée, et à chaque fois la falsification l'a trouvé avant les runs.

**Le dédoublonnage, mesuré avant d'être écrit.** Un recouvrement de mots aurait
supprimé **l'accumulation** — qui re-narre la soirée par définition, c'est sa
raison d'être — avec 0,52 de recouvrement contre la reconstruction qu'elle
résume. On aurait tué le geste acquis à la session précédente, sur un contrôle
bloquant.

**Puis, en falsifiant l'assemblage entier**, les trois plus fortes similarités
d'un chapitre complet se sont révélées être **l'en-tête, l'ancre et le
glissement**. Retirer le premier supprimait la bascule audio ; retirer le
troisième supprimait le geste. Le détecteur ne juge donc que ce que le modèle a
écrit : ce que le code compose se répète parce que c'est sa fonction.

**Le ratio seul ne suffisait pas non plus.** Deux paragraphes courts et
entièrement différents montent à 0,51 par les mots-outils du français. Il faut
aussi une suite commune de trente caractères : la vraie redite en partage
quarante-deux, les fausses six.

**Et un diagnostic reposait sur un message qui mentait.** Le lot demandait de
symétriser les seuils d'`accumulate` parce qu'un run de la session 6 « avait
perdu son accumulation pour huit mots ». Or l'essai rapportait *60 mots,
10 virgules* pour un seuil de *60 et 6* — et il était refusé. Le message
comptait le candidat entier quand la porte mesure la plus longue phrase et
refuse un point-virgule. La vraie cause était un point interne. On corrige donc
le message avant le seuil : un contrôle qui rapporte autre chose que ce qu'il
mesure fait corriger la mauvaise pièce.

---

## 4. Ce que la bible cachait — deux fuites préexistantes

En écrivant les substitutions demandées, deux choses sont apparues qui ne
figuraient à aucun ordre du jour.

**Le matériau réservé du chapitre 7 était indexé.** Nommé comme interdit dans
deux chunks servis (« les photos, la playlist, le plat des anniversaires et les
couverts sont réservés : ne jamais les mentionner »). Le modèle recevait donc,
en écrivant le chapitre 2, la liste exacte de ce qu'il n'a pas le droit
d'écrire — et la grille de l'étage C avait relevé la fuite sans en voir la
cause. C'est la doctrine du lexique de fuite, jamais appliquée ici : les
instances vivent déjà dans l'outillage, où le lint les scope par chapitre. La
règle servie est devenue **close et positive** : n'écrire que les objets nommés
au matériau du brief et à la liste du programme ; ce qui n'y est pas n'existe
pas dans la scène.

**Le chunk de voix proposait comme jargon courant un terme qui est le
dénouement du roman**, réservé au dernier chapitre. Deux lignes du même fichier
se contredisaient : l'une l'offrait à faible dose, l'autre le réservait. Un
texte servi qui se contredit laisse le modèle choisir. Remplacé par du jargon
non réservé.

**Et j'ai écarté une formulation du lot.** Le §2 demandait de nommer les états
bannis dans le chunk de voix (« jamais *troublée*, *perplexe*, *intriguée* »).
Or ce chunk est **servi**, et c'est précisément ce que la session 6 en avait
retiré — les instances descendues dans l'outillage, les catégories seules
servies. La substitution est donc écrite en positif, sans les instances : l'état
se constate par le corps, en une ligne, sans cause. Résultat mesuré : **état
mental nommé, 0 sur 3** cette session, contre 4 sur 4 la précédente.

---

## 5. Le tampon d'ancre, et pourquoi il fallait plus qu'un rappel

Le préfixage garantissait l'ancre pendant l'écriture, mais la relecture et la
réparation repassent sur l'entrée entière et la réécrivent. L'ancre sortait
altérée — guillemets français devenus droits — 0 fois sur 3 en session 5, 1 fois
sur 3 en session 6.

Le code possède ce marqueur : il le repose en dernier, après réparation. Il a
mordu sur les trois runs, et sur l'un d'eux la réparation avait **supprimé
l'en-tête entier**. Sans le tampon, ce run n'aurait eu aucun en-tête — donc
aucune bascule audio, donc pas de démonstration.

L'enjeu n'est pas typographique : la bascule scénique se place sur l'en-tête
normalisé.

---

## 6. Deux défauts que je n'ai pas corrigés, et pourquoi

Les corriger en cours de série aurait ajouté une seconde variable à ce qu'on
mesurait. Ils sont documentés pour la suite.

**Le contrôle bloquant consomme l'unique relance.** `accumulate` a deux essais.
Sur un run, l'essai 1 a été refusé pour un terme de décor interdit ; l'essai 2 a
rendu une accumulation de 43 mots, tolérée au dernier tour par la symétrie
nouvelle. Elle existe dans le texte mais passe sous le seuil de comptage, donc
la grille la lit comme **absente**. Deux portes bloquantes pour deux essais : la
seconde n'a jamais de seconde chance.

**Une accumulation est sortie à la troisième personne** — « Elle est revenue à
vingt heures, a refermé le cahier… » — dans un carnet écrit à la première.
Aucun lint ne l'attrape. Candidat évident pour la prochaine passe d'outillage.

---

## 7. Une découverte de méthode : notre chronomètre excluait la veille

Un run a rapporté 374 secondes de calcul pendant que la somme de ses appels au
modèle en donnait 2682. La machine avait fait deux mises en veille de
maintenance, sur batterie, au milieu du run.

La cause est structurelle et vaut au-delà de l'incident : le lanceur mesure avec
une horloge qui **s'arrête pendant la veille**, les appels au modèle avec une
horloge qui continue. Or **le budget de scène est du temps de mur** — le
compteur tourne pendant que le public attend, veille comprise. Notre chiffre de
référence, celui qu'on compare aux vingt-huit minutes, était donc le mauvais :
sur scène, ce run aurait explosé le budget en affichant que tout allait bien.

C'est la même classe de défaut qu'une métrique plafonnée par construction : elle
se lit comme une mesure. Les deux horloges sont désormais relevées, l'écart est
au frontmatter, et au-delà de trente secondes le run se signale comme non
comparable.

Note d'exploitation : la commande qui empêche la veille **n'a pas suffi** sur
batterie — la veille de maintenance est passée outre. Machine branchée pour
toute mesure qui compte.

---

## 8. Ce qui vous revient

1. **La litanie des stations** (§2) — le seul vrai arbitrage de fiche de cette
   session. Comment une station se ferme, ou l'aveu qu'elle ne se ferme pas.

2. **La masse reste inégale** : 401, 567, 552. Le critère passe, mais l'écart
   entre le plus court et le plus long reste d'un tiers à brief constant. La
   variance est-elle un défaut, ou une entrée de carnet a-t-elle le droit de
   varier ? La fiche pourrait le dire.

3. **La troisième personne dans un carnet à la première** (§6) — défaut de voix,
   pas de câblage, et il vaut peut-être une ligne d'interdit.

4. **La clôture d'entrée est le point faible.** Les trois défauts du run 1
   tombent dans la même phrase et demie, à la toute fin : le champ interdit,
   l'attracteur, le manuscrit intérieur. Le modèle, arrivé au bout, cherche à
   apaiser — et c'est précisément ce que le style refuse. La fiche décrit ce que
   la dernière ligne doit faire ; elle pourrait dire ce qu'elle ne doit pas
   consoler.

5. **Le prénom de celle qui est partie est servi au modèle** — dix chunks
   indexés le portent, dont la fiche de comportement et deux fiches d'objet. Le
   texte généré est resté propre trois fois sur trois, et le lint des noms
   propres garde la sortie. Mais c'est le même schéma que le matériau réservé du
   §4 : la seule protection est en sortie. Le prénom de la narratrice, lui, est
   traduit à l'indexation. L'asymétrie est peut-être voulue — la vérité de
   surface nomme celle qui est partie — mais elle mérite d'être décidée plutôt
   que constatée.

Et la remarque de méthode, puisqu'elle a encore payé quatre fois : **un contrôle
se falsifie dans les deux sens.** Pas seulement « rate-t-il le défaut ? », mais
aussi « refuse-t-il la référence ? ». Les erreurs des deux dernières sessions
sont toutes du second type — des contrôles justes en apparence qui rejetaient
l'étalon, la banque, l'accumulation, ou la bascule elle-même.
