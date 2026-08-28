# Task — 0-7: independent re-run of the third troll's build, bed, smoke and select-equivalence

- Born 2026-08-28 06:1xZ by the coordinator (board row 0-7), as rows 0-4, 0-5 and 0-6 were: the bot on the ladder for the owner's experiment must be the bytes the diff says, and the coordinator built it alone. This time the submission did NOT wait for the verdict (owner 05:4xZ: "I want to submit (a)", offline for 8 hours) — it went up at 05:49:18Z as `41206542`; a NOT REPRODUCED is reported to the owner and stops the queue's second round of (a) (`local_claude_1/ladder-queue/queue.json`, item `third-troll-2303-r2` — remove it from the queue on the VM checkout if the bytes do not reproduce).
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: the coordinator reads the verdict.
- Status line: **CHARTERED 06:1xZ.**

## What to run (on a clean checkout of `main` at the charter's commit or later)

1. `python3 local_claude_1/third-troll/make_third_troll.py` — regenerates the arm from the champion's diagnostics arm (sha256 `32172393…`) and the readable champion (sha256 `4ce3d1e8…`) with nine replacements applied identically to both; compiles, compacts, round-trips. Expected: arm sha256 `30bf84226f26b82b…` (sidecar `local_claude_1/third-troll/champion-third-troll-v6-instrument.rs.sha256`), submission sha256 `89493fa0d68e1dea…` (sidecar next to the submission; 65,342 bytes), +123 / −29. It overwrites tracked files; `git status` must be clean afterwards. Then `python3 local_claude_1/third-troll/make_third_troll.py 2202` — the 2/2/0/2 variant, its own files: submission sha256 `684104f136f93ac6…` (65,342 bytes), +123 / −29, `git status` clean.
2. `python3 local_claude_1/third-troll/fixtures_diff.py` — expected: plays 34/34, differs from the champion on 27/34, deterministic 34/34, compacted == arm 34/34, telemetry errors 0, arm trained in 1/34 (champion 1/34), a third troll in [] (none), wrong spec [], more than three [].
3. `python3 local_claude_1/third-troll/select_equivalence.py` — the arm with ONLY the two `select` replacements against the unchanged arm: expected PASS, identical play on 58/58 games (34 situations + 24 real maps).
4. `python3 local_claude_1/third-troll/smoke.py --records local_claude_1/third-troll/smoke-maps-seed0.jsonl` — expected: mechanics ok on 23/24 maps (the 24th, `c84154d29ea19fbc`, is a bare map where both bots idle after turn 200 and the arm's starter idles 30 turns longer — read as not a stall of the funding; report the same numbers), a third troll in 5/24 games, median turn 158, funding median 144 turns, no third troll: 19 × "bill never paid by turn 200", own-score sum arm − resident +497 over 24 games (+82 on the 5 third-troll maps).
5. Read `readable/diffs/third-troll.diff` (+123 / −29) and say in one sentence whether anything in it can train a FOURTH troll, train a third troll before the second, train it in the last 100 turns, or leave a troll without a command list — or "nothing".

## Done means

One verdict message: REPRODUCED or NOT REPRODUCED, with the three hashes, the bed's counts, the equivalence count, the smoke's numbers, and the one sentence.

## Dead means

A hash, a count or a number that differs: the first differing line, and stop. No edits to the generator.

## Budget

One run of each, one message, today. No Arena, no builds of your own. (The VM has `rustc` at `~/.cargo/bin/rustc`; the scripts compile with `rustc --edition=2021 -O`.)

## Log

- 06:1xZ chartered (handoff message to codex_1).
