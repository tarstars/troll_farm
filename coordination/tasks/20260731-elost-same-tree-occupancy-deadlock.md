# 20260731-elost-same-tree-occupancy-deadlock

- Status: exact inherited mechanism reproduced; narrow on-site ownership candidate next
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 after materialization
- Integrator: local_codex_1
- Area: live incident / own-unit same-tree occupancy contention
- Base commit: d1d3436
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete remote evidence
- Created UTC: 2026-07-31T16:20:00Z
- Last updated UTC: 2026-07-31T16:25:00Z

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

## Exact reproducible result

- The owner-observed interval is in latest game `897556967`; tass is correctly resolved
  as seat 1. A discarded intermediate scan of seat-0 commands in older game `897556692`
  belonged to Elost and is not evidence about our bot.
- Exact game result: valid 132–160 loss, 300 turns, zero unknown official updates.
- Both workers are full with one wood. Unit 1 (stats 1/1/1/1) occupies LEMON `(19,6)`,
  CHOPs on turns 55–57, then emits ten WAITs on turns 58–67.
- Unit 2 (stats 2/1/0/2) receives the same tree before collision resolution on all ten
  turns: exact pair `WAIT` + `MOVE 2 19 6`.
- Unit 2 alternates between `(18,5)` and `(18,6)` across eight decision states,
  turns 61–68. Unit 1 resumes CHOP on turn 68.
- Current sticky-bank, tent-proximity parent, and far-denial parent each reproduce
  300/300 recorded commands with zero stderr. The incident is inherited, not introduced
  by B3.14.
- Raw SHA-256:
  `7d2531710ecf7a3d6e71de923476e717272c6e65582cbb454d9c11d0d29f1b31`.
- Trajectory SHA-256:
  `2a809f316e03471cc9f8e54fdd1ae9410bde3abe9f3819b82677973d78ea7ec6`.
- Analyzer:
  `cgauto/analyze_elost_same_tree_deadlock.py`, SHA-256
  `4b5979f28270606ed784abdf21a3dfe3ebb839346f162b3e2c8321cb26694695`.
- Compact result JSON/MD SHA-256:
  `ac5263ba96087ee397cbacaf0515e9048c8293c5373c7d771a698ad6def03b1c` /
  `20fa1fbcf3f4314e3d96746acefb2802a1fa8bba00731826a5588b524bf53982`.

## Narrow correction

If a capable own worker already occupies a live tree, suppress that tree's chop candidate
for every other worker for the current decision. This keeps the on-site CHOP candidate
instead of selecting `WAIT + off-tree MOVE`; it does not globally retie scores, reorder
different trees, or add cross-turn memory.
