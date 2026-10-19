# plan-state-beats — lecture à l'aveugle rendue — 20261019T110000

Expérience : `experiments/runs/20261019-plan-state-beats` (rapport complet :
`report.md`). Chapitre 7, entrée 2. R × 3 (production, jamais lu) contre
P × 3 (chaque beat voit l'entrée avec l'état de chaque temps, fait, en cours,
à venir, sa condition de fin, et sa réponse commencée par le dernier
paragraphe écrit), lus à l'aveugle par l'auteur.

| bras | oui / partiel / non |
|---|---|
| R — production | 1 / 2 / 0 |
| P — plan d'état | 2 / 1 / 0 |

Règle écrite d'avance : non concluant (P meilleur sur une graine, égal sur
deux, pire sur aucune).

## Ce qui a appris quelque chose

- Servir à nemo le texte déjà écrit comme un bloc à ne pas réécrire le fait
  recopier dès que le prompt s'allonge (essai v1 : 6/6 variantes).
- Lui donner ce texte comme début de sa propre réponse arrête la recopie ;
  mais une réponse commencée qui finit sur un point final est close aussitôt
  (essai v2 : 6/9 vides). Une ligne blanche après suffit.
- Le gabarit de nemo jette le prompt système quand le dernier message est
  celui de l'assistant : il faut le replier dans la question.
- Défaut nouveau de P : le beat écrit à la troisième personne en
  transposant sa consigne (E06).

## Erreurs de ma part

- Le premier essai v2 a été lancé avec la mémoire déjà sous pression ; il a
  été tué par l'hôte. Exclu, rejoué.
