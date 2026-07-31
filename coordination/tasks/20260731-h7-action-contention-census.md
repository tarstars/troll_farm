# 20260731-h7-action-contention-census

- Status: closed — `NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`; peer review requested
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER H7′ / opponent interaction
- Base commit: b8c82d4c9c2e7aea59bcaa0a97ea588aad70ee06
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T02:36:50Z
- Last updated UTC: 2026-07-31T02:48:58Z

## Outcome

`NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`. Exact contention is ubiquitous
(180/200 games; 3,662 dual CHOP turns), but top-20 prevalence is only +5.76 pp over
rank-41+ with opponent-identity-cluster CI [−1.64,+14.49], and the strong per-turn rate
is lower. Close H7′ without a controller.

## Frozen protocol

`docs/h7-action-contention-census-protocol-2026-07-31.md`.

## Exclusive write set

- this task record;
- `docs/h7-action-contention-census-protocol-2026-07-31.md`;
- `cgauto/h7_action_contention_census.py` (new);
- `tests/test_h7_action_contention_census.py` (new);
- `data/analysis/live-agent-6553250/h7-action-contention-census-*` (new compact);
- `local_codex_1/h7-action-contention-census/` (new compact);
- own status/messages;
- register/BACKLOG/CONSTRAINTS/STATE/live ledger only at closeout.

## Shared read-only paths

- Exact D159 raw/result manifests and their 200 named raw-game/trajectory products.
- Existing replay decoder, command parser, mechanics, referee engine, H7 critique, and
  current canonical documents.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred).
- Any existing analyzer/result/protocol, raw game, processed trajectory, sealed range,
  map, cron, source policy, simulator/referee, peer path, submission tooling, or Arena.
- No formatter over `rust/src/bin/` or `cgauto/`.

## Acceptance

- Exact D159 population/identity/decode/hash gates: passed, 200/200.
- Issued-command legality and exact carry/plant transitions: passed, zero errors.
- Deterministic 10,000-replicate opponent-identity-cluster bootstrap: passed.
- `py_compile`, built-in self-test, focused pytest (7), repeated output: passed.
- Frozen verdict, compact artifacts, canonical closeout, handoff: passed; peer
  acknowledgement pending.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden. No candidate, TestSession, submission, or Arena action.

## Handoff

Pushed result commit with hashes, decisive event/cohort counts, validation evidence, and
an explicit request for `chatgpt_1` review and acknowledgement.
