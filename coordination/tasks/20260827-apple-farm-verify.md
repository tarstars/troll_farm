# Task 0-5 — independent re-run of the apple-farm build and its bed (codex_1)

- Born 2026-08-27 13:5xZ by the coordinator (the pattern of row 0-4: the coordinator built the
  instrument itself with the owner waiting; a second pair of hands reproduces it afterwards).
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: local_claude_1 (reads the verdict).
- Parent: `coordination/tasks/20260827-apple-farm-instrument.md` (the owner's one-variable experiment; on
  the ladder as submission `41203549` since 13:34:48Z; the reading at ≥ 14:35Z does not wait for this).

## Done means

One verdict message, REPRODUCED or NOT REPRODUCED, on a clean checkout of `main` at `333efce9` or later:

1. `python3 local_claude_1/apple-farm/make_apple_farm.py` regenerates the arm from the champion's
   diagnostics arm and the readable champion with the four insertions; expected arm sha256
   `82c8ddd1347c8016…` (full value in `local_claude_1/apple-farm/champion-apple-farm-v6-instrument.rs.sha256`),
   submission sha256 `8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c` (66,082 bytes);
   `git status` clean afterwards (the generator overwrites tracked files byte-identically).
2. `python3 local_claude_1/apple-farm/fixtures_diff.py`: plays 34/34, differs from the champion on 2/34
   (OSC-026 first divergence turn 3, OSC-030 turn 1), deterministic 34/34, compacted == arm 34/34,
   telemetry errors 0.
3. `python3 local_claude_1/apple-farm/smoke.py --maps 24 --turns 300 --seed 0`: mechanics ok 24/24
   (planted on turn 3 everywhere, no own chop on the farm), and the own-score sum arm − resident
   (+2831 on the coordinator's run; the number is a fact, not a gate — say what you got).
4. Read `readable/diffs/apple-farm.diff` and say in one sentence whether anything in it can make an own
   troll fell the farm tree or plant on the farm cell while the farm troll is away — or "nothing".

## Dead means

A hash or a count differs: name the first differing line and stop. No edits to the generator, no Arena,
no builds of your own.

## Budget

One run of each, one message, today.
