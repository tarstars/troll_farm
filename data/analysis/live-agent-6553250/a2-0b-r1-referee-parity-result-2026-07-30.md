# A2-0b r1 referee/evaluation parity — QUALIFIED

The locked r1 confirmation passes every inherited v1 gate and replacement G3r. The
Architecture-2 programme may use only the locked referee-mode path for a separately
preregistered Phase 1 experiment. Reviewer acknowledgement remains pending, so this is a
scientific verdict rather than protocol closure.

## Protocol history

V1 stopped correctly before implementation lock: its zero-error G3 was invalid because
ordinary source-defined play emits noncritical failures. R1 froze a 24-reason supported
noncritical taxonomy, exact state-effect fixtures, complete own/opponent accounting, and
zero gates for critical or unclassified outcomes. Every other v1 gate remained unchanged.

The implementation was locked before confirmation at commit
`cd424a19a1f746d72afcfc8b7c824284cdda4012`; the machine lock is
`data/analysis/live-agent-6553250/a2-0b-r1-implementation-lock.json`.

## Confirmation integrity

- matrix: seeds 9,854,000–9,854,127 × two seats × eight families = 2,048 tasks
- terminal rows: 2,048/2,048 in both modes
- one-thread time: 461.205 seconds
- 20-thread trajectory run time: 55.033 seconds
- one-thread and 20-thread TSV SHA-256, byte-identical:
  `3f8071978cedf82c991562bb893bc1990bfc371077d3563f85fed4294b7bee2b`
- legacy trajectories: 2,048 records, SHA-256
  `0c2b81ee704832d2213cc26d119ecb9e793b1552e571dcd52070374f98c7e146`
- referee trajectories: 2,048 records, SHA-256
  `9b7281fb374d229524afc8341cf119ff30b073c73121f0fd4d87b8597c2af6f4`

The legacy arm reproduces the preregistered D173b control exactly: **49 catastrophes and
12,749 total negative-margin mass**.

## G3r legality accounting

| mode | all issues | own | opponent | critical | unclassified |
|---|---:|---:|---:|---:|---:|
| legacy state + shadow checker | 88,615 | 440 | 88,175 | 0 | 0 |
| referee path | 86,363 | 229 | 86,134 | 0 | 0 |

All 440 legacy-own and 229 referee-own issues are source-defined simultaneous
`opponent_plant_blocking`; both colliding commands are rejected exactly as tested. Every
other issue comes from the frozen opponent side. All row, ownership, reason, phase,
critical, and example invariants pass. The result JSON retains the full per-mode,
per-role, per-family, per-reason, and per-phase breakdown.

## Six-detector bridge

Every trajectory decoded without error, with exact task coverage and no duplicates.

| detector | legacy episodes / turns | referee episodes / turns |
|---|---:|---:|
| idle_with_work | 66,052 / 91,364 | 66,122 / 91,397 |
| unbanked_carry | 122 / 5,151 | 104 / 4,781 |
| harvest_slack | 22,059 / 168,786 | 22,098 / 169,703 |
| door_queue | 1,530 / 1,537 | 1,481 / 1,489 |
| late_train_window | 1 / 33 | 1 / 33 |
| repeated_failed_command | 0 / 0 | 0 / 0 |

These are descriptive calibration counts, not tuned gates.

## Semantics change

Continued movement RNG changes 1,781/2,048 terminal trajectories; the first divergence
ranges from turn 1 to 283 (mean 15.37). Legacy movement uses 416,521 bounded draws,
including 129,211 true ties; referee trajectories use 415,629 draws, including 128,261
true ties. Only 382 action hashes and 396 terminal state hashes remain equal across modes.

The referee calibration tail is 53 catastrophes and 13,646 negative-margin mass, versus
49 / 12,749 in legacy. Mean referee-minus-legacy margin is −1.888; own score is nearly
flat (+0.082) while opponent score rises +1.969. This difference does not fail A2-0b:
the protocol explicitly treats it as the cost of correcting semantics, not as an A2 value
estimate. It proves that legacy absolute outcomes are not a safe substrate for Phase 1.

## Verdict

**QUALIFIED.** G1–G2, G3r, and G4–G6 pass. Phase 1 must:

1. use the locked referee-mode generator/checker/runner substrate;
2. declare fresh, unconsumed selection and confirmation ranges;
3. preregister its own policy-owned command-quality gate; and
4. treat the legacy arm only as a historical reproduction control.

Canonical machine result:
`data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result.json`, SHA-256
`eacdb600e29e59966f45a78225b193594231bbd8f42d9429c77e551712fef8dc`.
Only four display paths were mechanically normalized from the isolated worktree prefix to
repo-relative `artifacts/...` after the locked analyzer wrote the file; all counts, gates,
hashes, and scientific fields are byte-unchanged.
