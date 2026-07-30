# N6 — denial-distance weight sweep protocol

- Owner: `local_codex_1`
- Reviewer: `chatgpt_1`
- Frozen UTC: 2026-07-30T20:47:30Z
- Base commit: `bf224757ddffe867799bd138814fc2669eb62ab9`
- Scope: one nonzero scalar sweep on the exact resident, referee-mode local panels only

## 1. Why this narrow reopening is allowed

The 2026-07-16 record closes removing the global focus bonus (`weight=0`, arena 0–6 /
−150.7 margin) and restricting it to capable workers (local −1.21). Those results remain
binding: denial stays globally enabled, and N6 may not retry either edit.

N6 addresses a narrower unfinished reproduction obligation. The source design explicitly
registered G1—measure 2–3 nonzero proximity weights instead of guessing—and H13 later
found new same-architecture directional evidence: placebo-adjusted denial signal 1.24 for
the resident versus 1.64 for yamo. This permits exactly one preregistered scalar sweep
around the live 900, not iterative threshold tuning. After N6, the scalar line closes
regardless of verdict.

## 2. Exact change and arms

The exact control is
`rust/src/d171a_control_resident_snapshot.rs`, SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
It contains exactly one target line:

```text
score += 900.0 / (1 + opponent_distance) as f64;
```

A fail-closed materializer generates two runner-local sources by replacing only the
numeric literal on that exact line:

- `LOW`: `450.0 / (1 + opponent_distance)`;
- `CONTROL`: unchanged `900.0 / (1 + opponent_distance)`;
- `HIGH`: `1800.0 / (1 + opponent_distance)`.

The snapshot's exact leading crate-only attribute
`#![allow(dead_code, unused_imports)]` cannot occur inside `include!` modules. The
materializer therefore removes that one identical leading line from all three generated
modules, while the runner applies the equivalent outer allow attribute to each module.
The normalized CONTROL must otherwise be byte-exact to the snapshot, and LOW/HIGH may
differ from normalized CONTROL only at the scalar line. In particular, the
`opponent_trolls <= 2` gate,
`typeToCut`, tree throughput score, candidate grammar, pair selector, pathing, endgame,
and every execution repair remain exact.

This wrapper-only normalization was admitted at 2026-07-30T21:05:36Z after the first
compile attempt rejected the crate attribute inside a module and before any development
range execution.

## 3. Locked evaluation substrate

Use the A2-0b referee path, not the historical local referee approximation:

- `rust/src/game/a2_referee_parity.rs` SHA-256
  `518c222881ac23f8548cc13c858bacc93577ea920ecfbdbf0fd0e588cad1bf83`;
- `rust/src/game/a2_continued_mapgen.rs` SHA-256
  `8e841958c47db42920ca23150bd2afbdb88acaa06c1a13f97ee684fbfea2a84d`;
- the same eight `MacroOpponentMode` families and both seats as A2-0b;
- referee-legal parsing, continued SHA1PRNG movement ties, terminal turn/stall semantics,
  and reason-accounted noncritical errors.

Critical, unclassified, fallback, ownership, and unsupported-command errors are
zero-gated. Source-defined noncritical reasons are counted per arm and may not increase
by more than 10% in the selected confirmation arm.

The runner must be isolated: runner-local `include!` sources only, no `game/mod.rs`,
`Cargo.toml`, resident, A2-0b source, or module-registry edits. One-thread/multi-thread
rows must be byte-identical after deterministic sorting.

## 4. Development selection

Fresh maps **9,858,000–9,858,031** (32 maps) × both seats × all eight families =
**512 paired tasks** across all three arms. Pre-freeze search found no `9,858` occurrence
in live ledgers, constraints, state, or task records.

For each alternative, compare against CONTROL on the identical task. It is eligible for
selection only if:

1. at least 5% of tasks have a command divergence from control;
2. at least 60% of directionally comparable exact common-state first divergences change
   focus-tree intensity in the arm's intended direction: HIGH introduces a focus-tree
   target or moves it nearer the opponent shack; LOW removes a focus-tree target or moves
   it farther;
3. paired mean terminal-margin delta is positive;
4. seat-0 and seat-1 deltas are both positive;
5. at least six of eight opponent-family deltas are positive;
6. zero critical/unclassified/unsupported issues and complete terminal coverage.

If neither alternative passes, return `CLOSED_AT_DEVELOPMENT`; do not consume confirmation
maps. If both pass, choose the larger paired mean; an exact tie chooses LOW as the smaller
absolute source perturbation. There is no second development grid.

## 5. Fresh confirmation

Only the selected alternative and CONTROL continue on fresh maps
**9,859,000–9,859,127** (128 maps) × both seats × eight families =
**2,048 paired tasks**. Pre-freeze search found no `9,859` occurrence in the same live
records.

Run once with one worker and once with 20 workers; TSVs must be byte-identical. Dump the
20-worker control and selected trajectories to the external-backed artifacts root after:

```text
python3 cgauto/check_external_storage.py --required-free-gib 1
```

The analyzer must execute the six standing waste detectors on both trajectory sets and
require no detector episode rate to worsen by more than 10%.

Inference uses deterministic seed `20260730` and 20,000 percentile bootstraps resampling
whole map seeds, retaining all 16 seat/family tasks within each sampled seed.

## 6. Confirmation gates

Integrity:

1. exact source/dependency/range/task hashes and 2,048/2,048 paired coverage;
2. one/20-worker byte identity;
3. zero critical, unclassified, fallback, ownership, or unsupported issues;
4. selected noncritical issue count ≤1.10× control;
5. first divergence is attributable to the weight-only source delta;
6. all six detector gates pass.

Mechanism:

7. at least 5% of confirmation tasks diverge from control;
8. at least 60% of directionally comparable common-state first divergences change
   focus-tree intensity in the selected direction under the same introduced/removed/
   nearer/farther ordering;
9. mean opponent terminal-score delta is ≤ **−1.0** point;
10. at least six of eight family opponent-score deltas are nonpositive.

Value and safety:

11. overall paired mean margin delta ≥ **+20.0**;
12. map-cluster bootstrap 95% lower bound > 0;
13. both seat deltas are positive;
14. worst family margin delta ≥ **−5.0**;
15. mean own-score delta ≥ **−5.0**;
16. candidate catastrophes ≤ control;
17. candidate negative-margin mass ≤1.05× control.

All gates pass: `QUALIFIED`. Integrity or mechanism failure:
`CLOSED_AT_MECHANISM`. Otherwise: `CLOSED_AT_VALUE`. A qualified result authorizes only
candidate packaging and peer promotion review; the integrator must notify the owner before
any Arena cycle and run the full promotion runbook. No retune or second confirmation.

## 7. Outputs and boundaries

Exclusive outputs:

- `cgauto/n6_denial_weight_sweep.py`;
- `rust/src/bin/n6_denial_weight_sweep.rs`;
- `tests/test_n6_denial_weight_sweep.py`;
- compact lock/result/report under
  `data/analysis/live-agent-6553250/n6-denial-weight-sweep-*`;
- local compact bundle under `local_codex_1/n6-denial-weight-sweep/`;
- bulk rows/trajectories under
  `artifacts/experiments/n6-denial-weight-sweep/`.

Forbidden: editing either resident source, historical focus artifacts, locked A2-0b
files/results, sealed or consumed ranges, raw games, cron, submission tooling,
TestSession, or Arena state; formatting `rust/src/bin/` or `cgauto/`.

Before either panel, remotely publish an implementation/source/dependency lock. Before
confirmation, remotely publish the selected development arm and exact confirmation
command. Compilation, focused tests, a one-map/16-task three-arm smoke, source-diff
identity, command-divergence attribution, and one/four-worker smoke identity must pass
before the implementation lock.

The direction ordering above was clarified at 2026-07-30T21:05:36Z after the one-map
instrumentation smoke showed that first divergences commonly introduce or remove focus
rather than select two different focus targets. Non-focus-to-non-focus divergences are
reported but are not directionally comparable. This was a pre-lock telemetry correction:
no development map beyond the one-map smoke had been executed, and no selection/value
threshold changed.
