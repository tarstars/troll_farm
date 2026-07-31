# 20260731-h7-action-contention-census

- Status: claimed
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER H7′ / opponent interaction
- Base commit: b8c82d4c9c2e7aea59bcaa0a97ea588aad70ee06
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T02:36:50Z
- Last updated UTC: 2026-07-31T02:36:50Z

## Outcome

An exact read-only census decides whether the 200-game D159 resident panel contains a
material strong-opponent signature in mechanically real cross-player action contention:
simultaneous legal HARVEST/CHOP, duplication/combined kills, and exact target-removal
races. It explicitly excludes body-blocking and all policy work.

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

## Deliverables

- Frozen H7′ protocol, analyzer, synthetic tests, compact JSON/report/manifest.
- One frozen verdict, canonical closeout, and handoff to `chatgpt_1`.

## Acceptance checks

- Exact D159 population/identity/decode/hash gates and zero out-of-panel reads.
- Every event reconstructed from issued commands plus exact pre/post state; illegal or
  ambiguous actions excluded from causal families.
- Deterministic opponent-identity-cluster bootstrap for top-20 versus rank-41+ games.
- `py_compile`, built-in self-test, focused pytest, repeated output byte identity.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden. No candidate, TestSession, submission, or Arena action.

## Handoff

Pushed result commit with hashes, decisive event/cohort counts, validation evidence, and
an explicit request for `chatgpt_1` review and acknowledgement.
