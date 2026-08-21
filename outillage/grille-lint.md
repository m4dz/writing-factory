# Grille de lint — test de style

Scorage binaire : ✗ = défaut présent, ✓ = tenu. Pas de nuance — un défaut
est bloquant ou n'existe pas. Lecture à voix haute obligatoire avant de
remplir (c'est le format de la section 7 du talk).

**Règle de décision :** un défaut présent sur les 3 runs → c'est la fiche
(ajuster le chunk fautif, incrémenter `version`, réindexer, régénérer).
Un défaut sur 1 run → c'est le tirage (ignorer). Sur 2 runs → zone grise,
relancer un run avant de toucher la fiche.

## Interdits (défauts bloquants — chunk *interdits* de la fiche)

| Défaut | Run 1 | Run 2 | Run 3 | Contrôle |
|---|---|---|---|---|
| Pastiche gothique (lexique d'époque, « ténèbres », « effroi ») | | | | |
| Tics IA (« un mélange de X et de Y », parallélismes mécaniques) | | | | |
| Adverbes en rafale | | | | |
| Météo dramatique | | | | |
| Glissement omniscient (sortie du strict point de vue narrateur) | | | | |
| Résolution de l'ambiguïté (l'anomalie expliquée ou surnaturalisée) | | | | |

## Régimes (la scène doit traverser les quatre)

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle |
|---|---|---|---|---|
| Beat 1 : anomalie à plat (phrases courtes, ton neutre) | | | | |
| Beat accumulation : une vraie phrase longue, puis couperet | | | | |
| Dialogue décalé (si présent dans la scène) | | | | |
| Clôture obsessionnelle (rationalisation finale) | | | | |
| Bascules aux bons beats (pas de fondu homogène) | | | | |

## Mécanique de la voix

| Contrôle attendu | Run 1 | Run 2 | Run 3 | Contrôle |
|---|---|---|---|---|
| Fantastique par le détail concret (objets, heures, gestes) | | | | |
| Première personne tenue, narrateur qui rationalise | | | | |
| 400–550 mots (rempli automatiquement par run_scene.py) | | | | |
| Lisible à voix haute (attaques nettes, pas de gigognes) | | | | |
| On *entend* un style en 90 secondes | | | | |

## Lecture du run de contrôle

Le contrôle (brief sans lignes régime) ne se score pas comme les autres :

- **Bascules tenues sans les lignes régime** → le style ET la dramaturgie
  vivent dans la fiche. Meilleur cas.
- **Voix tenue mais registre monotone** → la fiche porte la voix, le plan
  de scènes devra porter la dramaturgie. Acceptable en production —
  l'orchestrateur fournira toujours les directives de régime — mais à
  savoir avant la keynote : c'est ce qui casse si le plan généré est pauvre.
- **Voix perdue** → la fiche ne tient pas sans béquille. Retravailler les
  chunks voix/interdits avant toute chose.

## Verdict

- [ ] Fiche validée en l'état
- [ ] Chunks à ajuster : ______________________
- [ ] Température à revoir : trop sage (monter vers 0.9–1.0) /
      pastiche dès le run 1 (renforcer *interdits* avant de toucher la temp.)

Notes :
