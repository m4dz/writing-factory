# pipeline

## ADDED Requirements

### Requirement: Sampling is configuration

The temperature of every writing call SHALL come from
`Settings.write_temperature`; `min_p`, `top_p` and `repeat_penalty` SHALL be
sent to the model only when set; all four SHALL be run overrides recorded in
the resolved configuration.

#### Scenario: Default request
- **WHEN** no sampling knob is set
- **THEN** the request options are temperature, `num_predict` and `num_ctx` only, byte-identical to the measured pipeline

### Requirement: The writer bench moves one variable

`factory bench` SHALL run the write node alone on an entry of a chapter whose
plan is imposed, for every model named, N draws each with consecutive seeds,
unloading the previous model before a swap and restoring the configured
model afterwards; it SHALL write one `kind: bench` directory under the runs
root with a manifest (models, seeds, commit, resolved configuration,
per-model aggregates), one file per draw, `prompts.md` and `report.md`
carrying the comparison table and an empty judge line per draw. The run
registry and the API SHALL ignore bench directories.

#### Scenario: Two models, two draws
- **WHEN** `factory bench --models a,b --draws 2 --seed 100` runs
- **THEN** four draw files exist with seeds 100 and 101 per model, the report tables name both models, and `factory runs` lists nothing new

#### Scenario: A chapter without imposed plan
- **WHEN** the bench is asked for chapter 2
- **THEN** it refuses before any model call and says the plan must be imposed by the brief
