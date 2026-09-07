# PLAN — frozen chopup: field activation + ONE broader 24-map/576-pair sample

Frozen 2026-09-07T01:52Z, before any field replay row or panel row existed.
Run artifacts only. No candidate/parent/canonical/neighbor source changes, no
parameter tuning, no platform calls, no commits, no agents.

## Frozen sources (verified by `sha256sum` at 01:48Z, unchanged)

- Candidate readable `claude_candidate_chopup_a.rs`
  `7a5722e48742d1e2712a5a37853f02e7edc860660a361bdaba9c34a219346a01`
- Candidate compact `claude_candidate_chopup_a.min.rs`
  `d40ed6449518d9eb00d60a95bd7c5d8c37eafa610c398e5a1d1a6a866eaef59d`
- Parent readable `claude_candidate_policy_flat.rs`
  `95ee691ee1b26e074ac90851575a6a56d5b0bec738ff3851cd141585d85c6d23`
- Panel modules: control `claude_candidate_chopup_control_module.rs`
  (parent verbatim), candidate `claude_candidate_chopup_a_module.rs`.

## Stage 1 — stored field activation (descriptive, not a strength test)

Replay the 12 archived official screen games in
`/data/separate_troll_farm-working/planning/2026-09-06/policy-flat-field/screen/`
through exact standalone binaries of the parent and the candidate, using the
existing `audit_candidate_command_streams` decoder/renderer helpers (read-only;
no framework change, no source edit). Compare command streams turn by turn and
record the first-hire TRAIN spec each arm emits. These are recorded field states
from games the candidate did not play: valid only up to the first divergence,
and never an adaptive counterfactual strength claim. 12 games cannot establish
that the rule is unreachable on all maps.

## Stage 2 — ONE broader comparison (prospective; NOT the old 192 gate)

- Seeds **426092000..426092023** (24 maps). Verified unconsumed at 01:49Z: a
  recursive grep for `426092` over the repository and over
  `/data/separate_troll_farm-working/` finds it only in prospective planning
  text (`WORKSTATE.md`, `tasks/frozen-chopup-generalization.md`, this run's
  `prompt.txt`/`input.md`) and as an incidental substring of one latency value
  in an unrelated TSV. No panel row, plan or manifest records any seed in the
  block. Excluded as spent: `426091000..023`, `9963000..023`, `9947500..007`.
- 24 maps x 2 seats x the same 12 adaptive opponents = **576 pairs**, both arms
  on identical initial state per pair, `ALLOW_ANY_MAP_SEED=1`, exact-source
  build snapshot, run-local `CARGO_TARGET_DIR`, Rust 1.90 toolchain.
- Maps are NOT curated on eligibility or on any measured outcome. One sample
  only: no repeat, no look-again, no extra variants, no threshold tuning.

## Decision rule (frozen before the panel was opened)

Positive **only if both**: (1) whole-panel candidate-minus-control `W + 0.5D`
is strictly positive, and (2) the candidate records **zero** issues over all
576 pairs. Anything else — including a failure-free tie or zero activation — is
**inconclusive/PARK**, not success. Every failed outcome stays in the
denominator. Report W/D/L, points, own/opponent score, margin, per-opponent
rows, shared-map correlation, and exact first-hire/spec-change counts.
Movement/carry/harvest spec changes must be 0. No rank or ladder claim.

## Certification

Full 160-game exact export/runtime/startup certification on the SHIPPED compact
only if Stage 2 is positive and clock remains; otherwise deferred to a next
batch. No latency measurement while any panel or compile is running.
