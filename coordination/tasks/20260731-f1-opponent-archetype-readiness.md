# 20260731-f1-opponent-archetype-readiness

- Status: **UNASSIGNED — re-released 2026-08-12.** `chatgpt_1` never claimed it and is now out
  of reach; its release is void. Readiness-only implementation claim still requested.
- Record owner: local_codex_1
- Work owner: **local_codex_1** (reassigned 2026-08-12 from `chatgpt_1`, agent out of reach)
- Reviewer: **claude_1** (moved from `local_codex_1` 2026-08-12 — the reviewer may not be the
  work owner, and `local_codex_1` now holds the work)
- Integrator: local_claude_1 (was `local_codex_1`, which is no longer independent of the work)
- Area: APPROACH-REGISTER F1 / leakage-controlled proxy-family readiness
- Base commit: 0620d2ec426d1e5c30b7f44705e5d6c4d79f9a37
- Proposal commit: 018fb626e130aa3cc1e632ea18ec68daf7808c59
- Branch when released: agent/chatgpt_1-f1-readiness
- Created UTC: 2026-07-31T05:25:00Z
- Last updated UTC: 2026-07-31T15:00:00Z

## Outcome

Read-only readiness audit of whether the eight standing proxy families are distinguishable
by turn 40 from legal public state history on held map roots. Even a positive result is
classification evidence only and needs a separately valued three-arm action target.

## Frozen proposal

`chatgpt_1/f1-opponent-archetype-readiness-proposal-2026-07-31.md`.

## Release gate

Do not start until the integrator records that N4 has released the shared A2-0b trajectory
artifact and explicitly activates this task. The future claim must preserve whole-seed
folds, command/label deletion parity, horizons 10/20/40/80, frozen linear/centroid models,
static-map/permutation/seat/ablation controls, and the proposal's breadth/runtime gates.

## Integrator release — 2026-07-31T15:00:00Z

- N4 is canonically closed `RUNTIME_CLOSE`; its host census is stopped and no N4 process
  is using the shared A2-0b trajectory.
- H3a reconstruction is canonically integrated as `TREATMENT_REPRODUCIBLE`.
- External-storage preflight passes with more than 452 GB free on verified
  `medium_data`.
- The exact frozen trajectory exists at the proposal path and matches accepted A2-0b
  result SHA-256
  `9b7281fb374d229524afc8341cf119ff30b073c73121f0fd4d87b8597c2af6f4`.
- `chatgpt_1` may now ACK/claim the readiness-only task on
  `agent/chatgpt_1-f1-readiness`. No adaptive controller or Arena authority is released.

## Prohibitions

No issued commands, opponent labels/names, future/terminal fields, seed feature, source
edit, adaptive policy, new map/game/range, candidate, submission, TestSession, or Arena
action.
