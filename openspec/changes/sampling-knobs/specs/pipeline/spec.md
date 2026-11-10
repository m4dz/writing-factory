# pipeline

## ADDED Requirements

### Requirement: Sampling of the writing calls is configuration

The temperature of every writing call SHALL come from
`Settings.write_temperature`; `min_p`, `top_p` and `repeat_penalty` SHALL be
sent to the model only when set, and only on the writing calls; all four
SHALL be run overrides recorded in the resolved configuration.

#### Scenario: Default request
- **WHEN** no sampling knob is set
- **THEN** the request options are temperature, `num_predict` and `num_ctx` only, byte-identical to the measured pipeline

#### Scenario: A knob set for the writer
- **WHEN** `min_p` is set
- **THEN** the writing calls (continuations included) send it and `prompts.md` shows it, while plan, review, QA and gesture calls send the same options as without it
