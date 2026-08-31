---
doc_id: synthese-session-6
type: retour de session
nom: "Retour d'implémentation — session 6, l'entrée en deux temps"
date: 2026-08-22
destinataire: conversation de style (rédaction de la fiche)
---

# Ce qui s'est passé — session 6

Retour d'implémentation de la session 6 : `write` décomposé en trois appels
(ouverture / reconstruction / fermeture), le glissement sorti du modèle et pris
dans une banque écrite main, plus le lot de corrections nées de l'étage C.
Quatre runs, série jouée d'un trait en 39 minutes.

**Ce document est SURFACE.** Il a été passé au lint des marqueurs profonds avant
envoi, comme le retour précédent — une archive qui alimente la rédaction de la
fiche ne doit rien porter de la couche cachée, sans quoi elle contaminerait la
fiche, puis le contexte servi au modèle.

---

## 1. Le résultat en trois lignes

**Ce qui est gagné.** Le glissement s'assemble : **quatre runs sur quatre**, un
par entrée, unique, conforme à L4. Il était à zéro sur onze runs. Et il ne
manquait pas au modèle — il était **refusé par nos propres validateurs**.

**Ce qui a bougé sans être acquis.** La masse. Le découpage produit de la
matière, mais il ne la cadre pas : 1 run sur 3 dans la cible, il en fallait 2.

**Ce qui est nouveau, et attendu.** Trois défauts nés du nœud lui-même, comme à
l'étage C. Le principal est de notre main : nos consignes de segment ont
multiplié « je décide de » par trois.

---

## 2. Le glissement — le geste ne manquait pas au modèle

C'est le fait marquant, et il vaut d'être lu en entier parce qu'il change ce
qu'on croyait savoir depuis trois sessions.

La banque de trois approches que vous avez livrée a été branchée telle quelle.
Avant de l'utiliser, le code la valide — et **le validateur a refusé les trois**.

`CHAMP_DEPART` exigeait qu'une approche contienne un mot du départ (*partie*,
*absence*, *quittée*). Or aucune des trois n'en contient :

> « Je pourrais me demander ce qui, ce soir-là »
> « Si je savais seulement pourquoi »
> « Il faudrait que je relise le jour où elle »

C'est tout l'objet du geste : la phrase s'interrompt **avant** que le départ
soit nommé. Exiger le mot du départ dans l'approche, c'est exiger que le geste
n'ait pas lieu.

Et ce n'est pas une hypothèse : c'est littéralement ce motif qui a rejeté
l'approche du modèle sur C2, deux essais de suite, avec le message *« approche
rejetée — n'approche pas le départ (champ lexical absent) »*. Le validateur
censé garantir le glissement était **ce qui l'empêchait**.

La même hypothèse fausse était logée à quatre endroits, dont deux qui auraient
menti sur le résultat :

- le validateur d'entrée du nœud (celui qui a rejeté C2) ;
- **le contrôle L4 de la grille** — il classait les trois glissements écrits
  main « hors champ du départ ». Sans cette correction, la grille aurait affiché
  trois croix sur le geste enfin correct, et nous aurions conclu que le
  glissement ne marchait toujours pas ;
- la ligne M1, qui en dépend ;
- le critère de composition du code.

Remplacé par le **pivot resté ouvert** — un mot interrogatif ou relatif après
lequel la phrase se coupe (*ce qui*, *pourquoi*, *le jour où*). La banque se
falsifie désormais au chargement du module : si une ligne future est refusée par
son propre validateur, ça échoue à l'import, pas dans les warnings d'un run.

**Ce que ça dit pour la fiche :** la conclusion de la session précédente — « ce
geste-là ne s'assemble pas » — était trop sévère. On ne sait toujours pas si le
modèle *pouvait* le produire, parce qu'on ne l'a jamais laissé passer. Ce qu'on
sait, c'est que la composition depuis une banque écrite main donne un geste
conforme à tous les coups, et que le tirage aléatoire sans remise (graine
consignée au frontmatter) évite la liturgie qu'on redoutait.

---

## 3. La masse — déplacée, pas cadrée

Le compteur est l'**entrée seule**, accumulation déduite : l'accumulation est un
artefact composé par le code, l'inclure ferait passer un run pour dans la cible
grâce à une phrase que le modèle n'a pas décidé d'écrire.

| | étage C | session 6 |
|---|---|---|
| run 1 | 292 | **467** ✓ |
| run 2 | 439 | 370 ↓ |
| run 3 | 146 | 716 ↑ |
| chapitre complet | 422/entrée | 1008/entrée ↑↑ |

**1 run sur 3 dans la cible 450-600 ; le critère de session en demandait 2.**

Mais la distribution s'est déplacée franchement : 146-439 devient 370-716. Le
diagnostic « un seul appel traite cinq beats, le modèle écrit un paragraphe par
beat et s'arrête » était juste, et le découpage l'a traité.

Ce qui reste est un problème de **variance, pas de niveau**. Un facteur deux
entre le run le plus court et le plus long, sur trois tirages du même brief.
Le levier « monter le plancher de la reconstruction » ne suffira pas seul : il
déplacerait les trois runs vers le haut, dont celui qui est déjà à 716.

---

## 4. Trois défauts nouveaux, tous nés du nœud

C'est le même schéma qu'à l'étage C, et il mérite d'être noté comme régularité :
**un dispositif qui règle un défaut en crée un autre, à l'endroit qu'il touche.**

**« Je décide de » explose, et c'est notre consigne.** Sept occurrences sur le
run 1, six sur le run 3, contre deux au plus auparavant. La cause est la forme
de la consigne de segment : elle nomme une intention — « elle rétablit sa
soirée », « elle cherche où elle a pu se tromper » — et le modèle la rend en
texte : *« Je décide de rétablir ma soirée »*, *« Je décide de refaire le fil de
ma soirée »*, *« Je décide de reconstruire ma soirée étape par étape »*.

Vérifié avant de conclure : les occurrences sont **dispersées dans l'entrée**,
pas concentrées aux frontières de segments. Ce n'est donc pas un artefact de
couture — c'est bien la consigne, qui autorise la décision narrée partout où
elle porte. Une consigne qui décrit ce que le personnage *décide de faire*
produit un personnage qui décrit ce qu'il décide de faire.

**Un état mental nommé par run, quatre sur quatre** — *intriguée*, *troublée*,
*perplexe*. À noter : c'est exactement la session où les instances ont été
retirées du contexte servi (la section *Interdits* ne garde plus que les
catégories). Le retrait n'a donc pas suffi à éteindre le réflexe ; il a
seulement cessé de le nourrir par l'exemple.

**Le run 2 n'a produit aucune accumulation.** Deux essais, deux rejets, et le
run continue sans elle — d'où son L3 à zéro et, sans doute, une part de ses 370
mots.

---

## 5. Les interdits matériels — le décor générique persiste

La liste des interdits matériels (le monde générique du modèle, documenté sur
six runs) est désormais outillée et scopée par chapitre. Résultat :

- **bloquante dans le nœud d'accumulation** : elle a mordu et forcé une
  relance dès le premier run (« travail hors du domicile ») ;
- **drapeau sur le texte d'écriture** : elle y signale sur les quatre runs.
  « Travail hors du domicile » partout, plus lave-vaisselle, sac à main et
  télévision sur le chapitre complet.

Autrement dit : le validateur tient les accumulations propres, mais rien ne
relance le texte d'écriture. Le décor générique n'est pas éteint, il est
seulement chassé de l'endroit où on l'avait mesuré.

**Question qui vous revient :** la maison de ce roman n'a ni télévision, ni
lave-vaisselle, ni sac à main, et la narratrice ne revient pas du travail — mais
rien dans les fiches ne le dit, puisqu'une fiche décrit ce qui *est*, pas ce qui
n'est pas. La consigne de reconstruction porte maintenant une ligne négative
(« il n'y a aucun écran dans cette maison, et rien qui vienne d'un magasin »).
Est-ce à la fiche de porter ce vide, et sous quelle forme ?

---

## 6. Le brief traduit — la garde d'entrée est le lint de sortie

« Couperet : » sortait en texte parce que notre propre squelette servi le
nommait. Le brief est traduit en langue du monde, et surtout : **une assertion
vérifie désormais qu'aucun terme d'atelier ne figure dans un brief servi**, avec
le détecteur qui les traque en sortie.

Elle a immédiatement trouvé un cas qu'on ne cherchait pas : l'objectif du
chapitre complet servait « Fait imposé, **au matériau** », et *matériau* est dans
la liste des méta-termes. Le chapitre complet recevait un mot d'atelier depuis
deux sessions sans que personne le remarque.

Résultat mesuré : **méta-termes 0/4** sur cette session, là où le run de voix de
l'étage C portait un « Couperet. » parasite venu de nous.

Leçon générale, réutilisable : on lintait la sortie contre un vocabulaire qu'on
injectait à l'entrée. Le détecteur qui attrape un mot dans le texte est
exactement celui qui aurait dû interdire de le servir.

---

## 7. Le critère « propositions verbales » rejetait l'étalon

Le lot de corrections demandait de rejeter le style nominal dans l'accumulation,
« ratio de verbes conjugués par item ». Implémenté au mot, ce critère **rejette
l'accumulation de l'étalon** : elle est nominale à 88 % de ses items —

> « …le café de sept heures, le départ de sept heures quarante, la réunion, le
> déjeuner, le retour par la départementale à cause des travaux, le garage, la
> porte du garage, la porte de la buanderie… »

— soit un ratio verbal de 12 %, plus bas que les six accumulations que l'étage C
avait produites. C'est l'auto-test sur les étalons qui l'a dit, avant le premier
run.

Le vrai discriminant est l'**abstraction**, ce que votre grille nommait déjà en
parlant de méta-beats : l'étalon énumère des choses et des moments de la soirée,
le sommaire du run C2 énumérait les beats de l'entrée (*perplexité*,
*corps qui parle*, *verdict d'erreur de relevé*).

| | étalon | les 6 accumulations de l'étage C | le sommaire de C2 |
|---|---|---|---|
| items abstraits | **0 %** | **0 %** | **47 %** |

Séparation totale, seuil posé à 20 %. Sur cette session : 0 % partout sauf une
accumulation du chapitre complet à 17 %.

---

## 8. Ce qui reste ouvert, et ce qui vous revient

**L'ancre n'est pas verbatim, et ce n'est pas nouveau.** Les guillemets français
de la citation ancre deviennent parfois droits dans le texte final. Le préfixage
par le code garantit l'ancre jusqu'à la fin de l'écriture — mais la relecture et
la réparation repassent sur l'entrée entière et la réécrivent. Mesuré :
0/3 à B′, 2/3 à l'étage C, ✗ sur le run 1 de cette session. Pas corrigé pendant
la série, pour ne pas ajouter une seconde variable à ce qu'on mesurait.

**Le coût du découpage, pour information.** Sur le chapitre complet, trois
appels au lieu d'un : ×2,2 sur l'écriture, ×1,6 sur le total. Le budget de scène
tient, mais la marge se resserre. Un signal à surveiller : la saturation de
fenêtre monte à 0,88 sur le chapitre complet (contre 0,63 sur une entrée seule)
— le préfixe croît sur trois segments *et* sur trois entrées.

**Trois questions qui relèvent de la fiche :**

1. **La variance de la masse.** Un facteur deux entre deux tirages du même
   brief. Est-ce une affaire de consigne, ou faut-il accepter qu'une entrée de
   carnet varie et le dire dans la fiche ?

2. **« Je décide de » et l'état mental nommé.** Les deux résistent à ce qui les
   vise. Le premier est nourri par nos consignes, qu'on va reformuler ; mais la
   fiche pourrait dire ce que la narratrice fait *à la place* de décider —
   l'interdit seul déplace le défaut, comme le mode acteur l'a montré trois
   fois.

3. **Le vide matériel du monde.** Cf. §5 : ce que la maison n'a pas n'est écrit
   nulle part, et c'est par là que le monde générique du modèle entre.

Et une remarque de méthode, puisqu'elle a encore payé quatre fois aujourd'hui :
**avant de faire confiance à un contrôle, exiger qu'il échoue sur un cas connu —
et exiger aussi qu'il ACCEPTE la référence.** Les quatre erreurs de cette
session sont du second type : des contrôles justes en apparence qui refusaient
l'étalon, la banque, ou les deux. Un détecteur ne se falsifie pas seulement par
le bas.
