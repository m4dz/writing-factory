# Design: beats-see-movement

## One variable

B differs from R by the movement map only: same beats, best-of-3, pruning,
verdict-free voice, beat suffix, sentence caps, old selection (branch
`xp-ablation-storyboard`). R is re-drawn rather than reused: the owner has
read the first R entries with the key open.

## Arms

| arm | command |
|---|---|
| R | `--chapter 7` |
| B | `--chapter 7 --override beats_see_movement=true` |

Seeds 395959, 528559, 781771 (scaffold-ablation's), interleaved R, B.
`--no-voice`, preflight strict. Seeds drive only the drift draw.

## Decision rule (written before the runs)

B replaces blind beats as the reference for `storyboard-density` when, on
the owner's blind reading: B is better than R on at least 2 seeds of 3,
AND B's entries carry fewer "invents" notes than R's, AND no veto defect
(resolves, dismisses, restarts, presence, recursion, forbidden decor —
old checks, as drawn) appears in B that R does not have, AND B's mean entry-2
length is not below R's (density: the criterion scaffold-ablation lacked).
B is rejected when it is worse than R on 2 seeds of 3 or more, or shows
« trois arcs » (a beat that writes the whole arc) on 2 of 3. Otherwise
inconclusive.

## Measures

`factory eval ablation` (table, `--blind`), plus per run the arc check by
reading: does a beat other than the last reach the doubt or the fall?
