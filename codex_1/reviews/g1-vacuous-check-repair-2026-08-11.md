# G1 vacuous-check repair report — 2026-08-11

Task: `20260810-guards-that-cannot-fail`, sub-item G1  
Implementation commit: `7af07a6ffc80cfb822902eb7aeac1626358b056b`  
Owner: `codex_1`

## The twelve repairs

Six tests with no recognized check now carry explicit evidence:

1. disclosed population mismatch: returned record must preserve both disclosure fields;
2. pinned locator drift: returned textual and constraint sources must retain the pinned commit;
3. accepted state: returned acceptance object must equal the accepted author/reviewer tuple;
4. existing hypothesis origin: explicit successful return plus removal-negative control;
5. repo-root-omitted origin: explicit successful return plus repo-root-present negative control;
6. N6 anchor fail-close: manual try/pass converted to parameterized `pytest.raises`.

Six assertions that accepted an entire result domain now assert discriminating outcomes:

1. own malformed `ack_for`: exact exit 0, not `(0, 1, 2)`;
2. live legacy sweep: exit must equal the presence/absence of actual unacknowledged mail, not
   merely belong to `(0, 1)`;
3. quantization error: every random actor layer must have positive measured error, not merely
   nonnegative absolute error;
4. denial crossover report: exact eight worker/size distances replace `>= 0`;
5. split bucket: exact frozen bucket 9 replaces the modulo-guaranteed range 0..9;
6. D45 coordinates: exact frozen vector and parameter count replace constructor-guaranteed bounds.

## Green controls

- 74 focused tests across decision evidence, hypotheses, N6, denial scoring, snapshot parsing and
  D45: pass.
- 71 isolated transport tests against the authoritative trunk `inbox_sweep.py`: pass (the live
  repository test was separately evaluated because the isolated archive intentionally has no Git
  refs).
- `tests/test_export_d11_actor.py` in a clean Torch/NumPy environment: 2 passed.
- AST rescan confirms all six formerly no-check functions now contain direct assertions,
  `pytest.raises`, or both.

## Deliberate broken-subject controls

Every repair class was observed failing, with the subject restored afterward:

- `validate_repository -> ([], [])`: all three decision-evidence repairs fail (3/3).
- `validate_hypothesis` early no-op: both origin repairs fail (2/2).
- disabled N6 anchor-count branch: both parameter cases fail (2/2).
- denial crossover `+1`: exact report test fails.
- split modulus 10→9: exact bucket test fails.
- D45 final coordinate 28→27: exact vector test fails.
- transport terminal return forced to 1: malformed-own-message exact-exit test fails.
- transport terminal return forced to 0 with 42 outstanding obligations: the derived live-exit
  contract rejects `rc=0`.
- quantization error metadata forced to 0.0: actor quantization test fails.

## Repository-wide gate and environment caveat

The requested full command was attempted in an isolated environment containing pytest, PyYAML,
NumPy, Torch, SciPy, scikit-learn and pandas. Collection stops on 64 pre-existing modules that
import `cgauto/battles.py` or `battle_taxonomy.py`, which unconditionally read the absent secret
`/home/tarstars/prj/troll_farm/cgauto/cg_session.txt`. The secret is intentionally not in Git and
must not be copied into an artifact. This is unrelated to the eight changed test files; every
changed test reachable on this VM is green as itemized above.

The integrator should run the full suite in the established project-host environment that produced
the recorded 1,670-pass baseline before integration. No claim of a full-suite pass is made here.

## Disposition

Implementation and negative-control evidence are complete. Integration is ready subject to the
existing environment-specific full-suite gate. No production predicate, experiment, data, service,
bucket, or Arena state changed.
