# test-harness

## ADDED Requirements

### Requirement: Served prompts are frozen

The test suite SHALL record every prompt served to the model during a full
graph run on each reference scenario and SHALL compare it byte for byte to a
golden file under `tests/snapshots/<scenario>/prompts.md`, together with the
assembled chapter and the pipeline warnings.

#### Scenario: A refactor that does not change prompts

- **WHEN** the code is moved, renamed or reorganised without intent to change
  what the model sees
- **THEN** `pytest tests/snapshots` passes without regenerating any golden file

#### Scenario: A change that moves a prompt

- **WHEN** a change alters the wording, order or served sections of any prompt
- **THEN** the snapshot test fails, the change regenerates the golden files
  with `make snapshots`, and its openspec proposal names the prompt moved

### Requirement: The model and the vector store are faked

The suite SHALL run without Ollama, without Chroma and without macOS. The fake
model SHALL recognise the node from the prompt and answer with text that
conforms to the validators applied to that node's output; the fake store SHALL
be built from the indexer's chunker over `bible/` so that the firewall rules
apply to what the tests serve.

#### Scenario: Fixture conformance is itself tested

- **WHEN** a fixture stops passing the validator the pipeline applies to it
- **THEN** `tests/unit/test_fixtures.py` fails naming the fixture, before any
  snapshot run

#### Scenario: Failing twins trip their validator

- **WHEN** the failing variant of a fixture (out-of-role reply, resolving
  beat, English or short accumulation) is given to its validator
- **THEN** the validator rejects it

### Requirement: The deterministic lint is frozen on the calibration corpus

The lint report on every file of `journal-des-murs/` and `runs-ch7/` SHALL be
compared to a golden file, and the corpus SHALL be asserted non-empty.

#### Scenario: A detector changes behaviour

- **WHEN** a detector starts firing on a run it accepted, or stops firing on a
  run it flagged
- **THEN** the lint snapshot test fails on that file

### Requirement: Machine stages are tested against fakes

The preflight gate SHALL be tested with fabricated probe results such that
every blocking rule fires on its known case and stays silent on a healthy
machine. The render stage SHALL be tested with a fake synthesizer for
segmentation, WAV assembly, pause insertion, rate check and per-resource
fallback. The API SHALL be tested in-process with the pipeline replaced.

#### Scenario: Healthy machine

- **WHEN** all probes report a healthy machine
- **THEN** `preflight()` returns no warnings in both modes

#### Scenario: Known failure

- **WHEN** one probe reports a condition that has crashed or slowed the
  machine before (low disk, hot swap while timing, critical pressure, busy
  maintenance daemon, Ollama not generating, two hot LLMs)
- **THEN** `preflight()` raises `PreflightError` naming the condition

### Requirement: One command runs everything

`make check` SHALL run ruff and the full pytest suite and SHALL be the exit
criterion of every task of the revamp.

#### Scenario: A task is declared done

- **WHEN** a revamp task is marked complete
- **THEN** `make check` has run green on the working tree at that commit
