# chapter-spec

## ADDED Requirements

### Requirement: A run may use a variant spec

`factory generate --spec-file PATH` SHALL load the chapter from a variant spec
outside `chapters/`, with the same loader assertions as a canonical spec. The
run directory SHALL hold a copy of the variant and the manifest SHALL record
its source and its diff against the canonical spec of the same chapter. The
canonical files under `chapters/` SHALL NOT be modified.

#### Scenario: Entry 2 written in one call

- **WHEN** a variant spec sets entry 2 of chapter 7 to `strategy: single`
- **THEN** the run makes one write call for entry 2 and the manifest records `strategy: beats → single` in the spec diff

### Requirement: Run options from the command line

`factory generate --option KEY=VALUE` SHALL pass `rag`, `micro_nodes` and
`segments` to `spec.state()` as keyword overrides, record them under
`options:` in the manifest, and refuse any other key.

#### Scenario: Unknown option

- **WHEN** `--option strategy=single` is given
- **THEN** the command exits with an error naming the allowed keys and no run is created
