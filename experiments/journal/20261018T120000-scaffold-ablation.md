# scaffold-ablation — lecture à l'aveugle rendue — 20261018T120000

Expérience : `experiments/runs/20261018-scaffold-ablation` (rapport complet :
`report.md`). Chapitre 7, entrée 2. Cinq bras × trois graines, lus à
l'aveugle par l'auteur.

| bras | oui / partiel / non |
|---|---|
| R — production | 0 / 1 / 2 |
| A1 — sans best-of | 0 / 2 / 1 |
| A2 — sans pruning | 0 / 1 / 2 |
| A3 — sans accumulation | 0 / 0 / 3 |
| A4 — entrée 2 en un appel | 2 / 0 / 1 |

## Causes des échecs, par les notes de l'auteur

- **Invention** (R ×2, A1, A2 ×2, A3) : narratifs inventés, externalités
  impossibles, « Huit couverts ce soir. ». Aucune sur A4. Hypothèse : beats
  servis seuls, sans le mouvement.
- **Densité absente** (A1, A3 ×2) : « pas de densité », « pas de
  profondeur ». A3 : 170 mots sans l'accumulation, 326 avec.
- **Contre-sens de rôle** (E04, A4, le plus dense, 624 mots) : « le ton sonne
  creux […] le personnage ne tient pas son rôle ».
- **Froideur** (E01, A4) : mouvement accompli, « froide énumération ».

## Erreurs de ma part, corrigées avant la lecture ou par elle

- A3 v1 coupait quatre pièces (`micro_nodes=false`) : rejoué avec
  `accumulation_enabled=false`.
- Graines non appariées : Ollama ne reçoit pas la graine.
- J'avais déclaré les beats porteurs sur la doctrine 8 avant la lecture ; la
  doctrine 8 n'était pas dans le véto écrit d'avance, et le meilleur tirage
  (E03) porte huit « je décide de ». Rétracté.
