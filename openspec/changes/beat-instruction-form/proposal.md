# Proposal: beat-instruction-form

## Why

The beats of chapter 7 entry 2 are served as prose in « elle » (brief §7).
`xp-author-models` measured what nemo does with them, over every drawn
variant (`experiments/runs/20261020-beat-instruction-form/recital.py`,
sentence-to-sentence similarity against the instruction, threshold 0.50 as
`lint.prompt_copy`):

| run (nemo, plan) | variants reciting | relève | découverte | doute |
|---|---|---|---|---|
| 20261019-223328 | 6/9 | 1.0 / 0.75 / 1.0 | 0.79 / 0.75 / 0.72 | ≤ 0.40 |
| 20261019-224615 | 6/9 | 0.92 / 0.92 / 0.86 | 0.97 / 1.0 / 1.0 | ≤ 0.45 |
| 20261019-225918 | 7/9 | 0.92 / 0.76 / 1.0 | 0.83 / 0.72 / 1.0 | 0.50 |

Ministral, same prompts: 1/9 and 2/9.

Two outcomes of one cause (doctrine 6, « shown is recited »):

- **verbatim, third person**: the variant IS the instruction (1.0); the
  selection flags it « troisième personne (la consigne transposée) »;
- **transposed, first person**: the instruction with its pronouns swapped
  (« Je relis la ligne que je viens de recopier. Je relève un écart… »,
  0.75–0.92); the selection keeps it, it reaches the chapter, and it reads
  well because the sentence is the owner's.

The third-person defect is the visible half of the recital. Rewriting the
instructions in the first person would remove the visible half and make the
invisible half perfect. Doctrine 6 asks for categories, not sentences: a
person-less, nominal form leaves no sentence to transpose. « tu » is excluded:
in this journal it is the husband (« je t'ai dit oui »).

The doute beat, already short and corporeal, barely recites (≤ 0.50). Its
nominal form is kept for symmetry, one variable for the whole entry.

## What changes

- **Code (done on this branch):** optional lines per beat in brief §7,
  `Nominal :` and `Finit quand (nominal) :`, read apart from the prose
  instruction (`BeatSpec.nominal`, `.ends_nominal`); override `beat_form` ∈
  `prose` (default) | `nominal`. Under `nominal`, the instruction, the
  time labels of the plan state and the end condition are the nominal ones;
  a beat without a nominal form refuses the run (doctrine 9). Prose
  unchanged: ch7 snapshot identical.
- **Owner material (to validate):** the three nominal forms below, written
  into `brief-entree-2.md` §7 under each beat, at the owner's word. The prose
  instructions stay as they are.
- **Experiment** `20261020-beat-instruction-form`: arms R (prose) and F
  (nominal), both nemo, `beat_context=plan`, 3 fresh seeds.

## Drafts of the nominal forms (owner canon, to correct)

The first sentence is the time's label in the plan state, so it is the
time's name.

**Beat A — la relève**

> Nominal : La relève. La ligne tout juste recopiée, relue. Un écart relevé
> entre la ligne et la mémoire : les deux couverts mis, décrits par la ligne,
> sous les yeux ; aucun souvenir de les avoir mis.
>
> Finit quand (nominal) : l'écart nommé — la ligne dit les couverts mis, la
> mémoire n'en garde rien.

**Beat B — la découverte**

> Nominal : La découverte. Autour, la maison dressée pour la fête non-désirée :
> photos étalées, musique qui joue, plat au four, deux couverts.
> Aucun souvenir d'avoir rien préparé. Le rangement commence : chaque chose
> remise à sa place. Chaque objet trouvé une seule fois ; pas de tour de la
> maison.
>
> Finit quand (nominal) : le rangement commencé ; les quatre objets trouvés,
> chacun une fois.

**Beat C — le doute (le corps, pas la pensée)**

> Nominal : Le doute, dans le corps. Plus de verdict cherché. Mains froides,
> nuque raide, la page relue trois fois. Le crayon reposé.
>
> Finit quand (nominal) : le crayon reposé.

Points the owner decides: « la fête décidée annulée » for « la fête qu'elle
avait décidé de ne pas tenir » (no person, but heavier); « un métier » for
« c'est son métier » (the possessive carries the person); whether the doute
needs a nominal form at all.

## Risks (doctrine 12: the defect the fix creates)

- **Telegraphic contamination.** A nominal instruction may be recited as
  nominal prose: verbless sentences, a list of states. The narrator's
  fragments (« Beau temps. ») are style; a litany of noun phrases is not.
  Measured: share of short sentences (≤ 6 words) in entry 2, and the grid's
  litany.
- **Person lost.** With no « elle » and no « je », the model takes the person
  from the begun answer (first person) and the system voice. If it drifts to
  « on » or impersonal prose, the selection does not catch it; the reading
  does.
- **Recital of the nominal form** is still recital: `recital.py` measures
  each variant against both forms in both arms.

## Out of scope

The movement, matter and vetos of the plan state (prose, not in « elle »
sentences to copy, and owner canon); the person line in the suffix (a
second variable, next if F fails on person); the models (`xp-author-models`
follow-up, on the winning form).
