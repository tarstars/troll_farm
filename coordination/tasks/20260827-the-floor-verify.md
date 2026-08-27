# Task — 0-6: independent re-run of the floor's build, bed and smoke

- Born 2026-08-27 18:2xZ by the coordinator (board row 0-6), as rows 0-4 and 0-5 were: the bot that goes on the ladder for the owner's experiment must be the bytes the diff says, and the coordinator built it alone.
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: the coordinator reads the verdict.
- Status line: **CHARTERED 18:2xZ.** The submission does not wait for this verdict (it waits for the ladder slot); a NOT REPRODUCED before the submission stops it.

## What to run (on a clean checkout of `main` at the charter's commit or later)

1. `python3 local_claude_1/the-floor/make_the_floor.py` — regenerates the arm from the champion's diagnostics arm (sha256 `32172393…`) and the readable champion (sha256 `4ce3d1e8…`) with five replacements applied identically to both; compiles, compacts, round-trips. Expected: arm sha256 `75afaf8bd1d380fc…` (sidecar `local_claude_1/the-floor/champion-the-floor-v6-instrument.rs.sha256`), submission sha256 `31cd23c021f184b0…` (sidecar next to the submission; 63,791 bytes), +17 / −23. It overwrites tracked files; `git status` must be clean afterwards.
2. `python3 local_claude_1/the-floor/fixtures_diff.py` — expected: plays 34/34, differs from the champion on 2/34 (OSC-010 first divergence turn 13, OSC-032 turn 49), deterministic 34/34, compacted == arm 34/34, telemetry errors 0, arm trained below the floor: none.
3. `python3 local_claude_1/the-floor/smoke.py --records local_claude_1/the-floor/smoke-maps-seed0.jsonl` — the 24 sampled real maps with their draws and opponent profiles (the slice replays the coordinator's corpus run identically). Expected: PASS 24/24 (the arm trains in every game, never below 2/2/0/2), the resident below the floor on 11/24, training turn median 30 vs 11, own-score sum arm − resident +149.
4. Read `readable/diffs/the-floor.diff` (+17 / −23) and say in one sentence whether anything in it can train a troll weaker than speed 2 / carry 2 / chop 2, or stop the bot from ever training — or "nothing".

## Done means

One verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the bed's counts, the smoke's numbers, and the one sentence.

## Dead means

A hash, a count or a number that differs: the first differing line, and stop. No edits to the generator.

## Budget

One run of each, one message, today. No Arena, no builds of your own.

## Log

- 18:2xZ chartered (handoff message to codex_1).
- 18:15Z codex_1 (`181522Z`): **NOT REPRODUCED at the first metadata field** — the candidate bytes reproduced (arm `75afaf8b…`, submission `31cd23c0…`, +17/−23, round trip exact), but `results/build.json` and the round-trip report carried `rustfmt_check: "NOT clean"` where the VM (no rustfmt) writes `"unavailable"`; per the dead condition it restored the two fields and stopped before the bed and the smoke.
- 19:4xZ coordinator: the field was environment-dependent in a tracked file — my mistake. Fixed in `make_the_floor.py` (the rustfmt line is printed, never written); regenerated: arm and submission bytes unchanged, the two reports no longer carry the field. Steps 2–4 re-issued to codex_1 (handoff pinned to the fix commit). The floor's ladder round is unaffected (the bytes are the bytes).
