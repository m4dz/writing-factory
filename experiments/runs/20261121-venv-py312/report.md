# venv Python 3.12 — la voix revient

> 2026-11-21, main c9aa1b0 (`.python-version` 3.12.13, scipy 1.18.1, tout le
> reste à la même version). `factory generate --chapter 7`, voix active,
> sans préparation.

Le run écrit `chapitre.wav` lui-même : 12 segments, 94 s restituées en 75 s
(×1,25), 217 mots/min. Premier run voix réussi depuis macOS 27
(2026-10-19).

Durée : 1246 s, à ne PAS comparer. Le doctor d'avant le run disait
« pression élevée », 3,5 Go récupérables ; les appels M ont tourné à
47–201 s pour 136–240 jetons (au lieu de 1–4 s), swap passé de 12,6 à
18,6 Go. Ollama est hors du venv : la lenteur est la machine, pas Python.
