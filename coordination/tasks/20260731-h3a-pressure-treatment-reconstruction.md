# 20260731-h3a-pressure-treatment-reconstruction

- Status: documentation takeover — validation passed; local integrator materializing canonical closeout
- Record owner: local_codex_1
- Work owner: local_codex_1 (compact-documentation takeover; peer owns published implementation history)
- Reviewer: local_codex_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER H3a / exact treatment reproducibility
- Base commit: 0620d2ec426d1e5c30b7f44705e5d6c4d79f9a37
- Branch: agent/local_codex_1
- Progress lease: begins when work owner publishes acknowledgement/claim
- Created UTC: 2026-07-31T05:25:00Z
- Last updated UTC: 2026-07-31T09:45:00Z

## Outcome

Decide whether the archived Phase-21 exact 1:1 dual-value treatment can be reconstructed
byte-for-byte from the exact fallback without inventing a replacement. This task
authorizes no intervention panel.

## Frozen inputs

- treatment:
  `cgauto/submissions/candidate-agent6553250-opponent-crop-dual-value-e6-slim.min.rs`,
  SHA-256 `083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf`;
- fallback:
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
  SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- archived sidecar and Phase-21 protocol/result/arena-verdict records;
- proposal:
  `chatgpt_1/h3a-three-arm-pressure-value-proposal-2026-07-31.md`.

## Exclusive write set

- `chatgpt_1/h3a_pressure_treatment_reconstruction.py` (new);
- `tests/test_h3a_pressure_treatment_reconstruction.py` (new);
- `data/analysis/live-agent-6553250/h3a-pressure-treatment-reconstruction-*` (new compact);
- `chatgpt_1/h3a-pressure-treatment-reconstruction-result.md` (new);
- `local_codex_1/h3a-pressure-treatment-reconstruction/manifest.json` (new);
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-h3a-pressure-treatment-reconstruction-*.md`;
- integrator-owned H3a dispositions in `docs/APPROACH-REGISTER-2026-07-30.md`,
  `docs/BACKLOG.md`, `docs/CONSTRAINTS.md`, `docs/STATE.md`, and the live ledger.

## Acceptance

- Deterministic fallback→treatment reconstruction matches the exact treatment SHA and
  inverse removal matches the fallback SHA.
- The delta is exhaustively classified: provenance plus the original eligibility/ETA
  semantics and `candidate.score += candidate.score`; no multiplier, ETA, target,
  commitment, harvest, scheduler, or unrelated byte changes.
- Exact artifacts compile; focused fixtures distinguish eligible/ineligible ETA states.
- py_compile, self-test, focused pytest, repeated output, and hashes pass.

Return `TREATMENT_REPRODUCIBLE` or `BLOCKED_TREATMENT_NOT_REPRODUCIBLE`.

## Prohibitions

No existing source edit, runner arm, fresh/consumed/sealed map read, simulator/referee
change, panel, bulk output, candidate, submission, TestSession, or Arena action. A full
three-arm protocol requires a separate post-review decision.
