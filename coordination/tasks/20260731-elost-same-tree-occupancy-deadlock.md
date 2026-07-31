# 20260731-elost-same-tree-occupancy-deadlock

- Status: active — exact replay reconstruction
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 after materialization
- Integrator: local_codex_1
- Area: live incident / own-unit same-tree occupancy contention
- Base commit: d1d3436
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete remote evidence
- Created UTC: 2026-07-31T16:20:00Z
- Last updated UTC: 2026-07-31T16:20:00Z

## Owner observation

> I checked game agains Elost. One troll is on tree, the other tries to go its place,
> both stuck

## Exact identity preflight

- Latest matching completed game: `897556967`.
- Resident agent/submission `6585765`/`41071067`, seat 1.
- Elost agent/submission `6579290`/`40706516`, seat 0.
- Both exact agents are valid; the game has 601 frames.
- Two earlier exact pairings also exist (`897556692`, `897556421`) and remain out of
  scope unless the latest game does not contain the reported interval.

## Question

Find the exact interval where one resident worker occupies a tree and the other repeatedly
selects/moves toward that cell. Determine:

1. both unit states, cargo, commands, intended targets, candidate scores, selected pair,
   and post-collision outcome;
2. whether the tree occupant has a sticky-bank commitment, whether the mover does, and
   whether B3.14 introduced or merely inherited the loop;
3. the earliest state transition that makes the intent inconsistent;
4. the narrowest persistent-intent or compatibility correction that prevents the loop
   without changing unrelated pair ranking or reopening generic oscillation/tree-order
   work.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-elost-same-tree-occupancy-deadlock-*.md`;
- one compact exact-game analyzer and focused tests under `cgauto/` and `tests/`;
- exact raw/trajectory cache only under
  `data/external/elost-same-tree-occupancy-deadlock/` after storage preflight;
- one fail-closed successor generator, immutable candidate/checksum, compact report, and
  manifest only if the exact mechanism supports a distinct correction;
- integrator-owned live disposition after validation.

## Shared read-only paths

- exact Codingame game `897556967`;
- current sticky-bank artifact, its parent, replay decoder, simulator, and unsealed smoke
  tooling.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred);
- existing immutable candidates, frozen protocols/locks, peer namespaces, sealed maps,
  `data/raw/games/`, and the 05:17 cron;
- Arena/TestSession. Current `6585765`/`41071067` remains live and is monitored read-only.

## Acceptance

- Cache and hash the exact latest game only after external-storage preflight.
- Reconstruct every turn with zero unknown official updates.
- Publish the exact repeated interval and causal state transition, not only the visual
  symptom.
- Compare current sticky artifact with its parent on the exact recorded state stream.
- If a distinct correction exists, generate fail-closed, add focused compiled boundaries,
  reproduce the intended divergence, and run bounded unsealed both-seat smokes.
- Preserve sacred SHA and make no Arena mutation.
