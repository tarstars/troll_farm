# 20260731-owner-far-denial-no-return-arena

- Status: claimed — owner-directed implementation and single Arena cycle
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: owner-directed; peer review may follow after submission
- Integrator: local_codex_1
- Arena controller: local_codex_1
- Area: initial resource denial / far post-chop wood return
- Base commit: 993d18a
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T12:15:00Z
- Last updated UTC: 2026-07-31T12:15:00Z

## Owner directive

> Set threshold in 3 cells of map distance. If the route longer than that, then in initial
> resource denial trolls shouldn't bring chopped wood back. Patch the bot and send to
> Arena.

## Frozen interpretation

- Distance is terrain BFS from the denied tree to the nearest own shack door.
- Threshold is inclusive: distance `<= 3` preserves the existing post-chop wood return;
  distance `> 3` suppresses only the return leg caused by that initial-denial assignment.
- Ordinary wood production, near-denial returns, unrelated carry banking, endgame logic,
  and all other behavior remain unchanged.
- Implement in a new candidate copy; sacred
  `rust/src/bin/yamo_orchard_live.rs` remains byte-exact.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-owner-far-denial-no-return-arena-*.md`;
- one new candidate and checksum under `cgauto/submissions/`;
- `cgauto/make_far_denial_no_return_candidate.py` and
  `tests/test_far_denial_no_return_candidate.py`;
- one compact result under `data/analysis/live-agent-6553250/`;
- one manifest under `local_codex_1/owner-far-denial-no-return-arena/`;
- integrator-owned live docs/ledger disposition;
- one controlled Codingame candidate submission plus required cycle reads/restoration.

## Acceptance

- Diff only the intended far initial-denial post-chop return behavior.
- Compile the exact submission artifact and run focused deterministic tests/smoke checks.
- Prove distance 3 keeps return and distance 4 suppresses it.
- Verify sacred source SHA before and after.
- Commit and push the exact submitted artifact before the platform write.
- Start at most one Arena candidate cycle and record agent/submission identifiers.

## Stop conditions

Stop before submission on compile/test/integrity failure, unresolved semantic ambiguity,
HTTP 422, concurrent Arena cycle, or sacred-source drift. Do not open sealed maps/ranges or
modify raw games/cron.
