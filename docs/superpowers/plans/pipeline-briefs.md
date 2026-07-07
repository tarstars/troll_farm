# Pipeline stage briefs (copy into Agent prompts; fill {PLACEHOLDERS})

## Common context (prepend to every brief)
Repo: /home/tarstars/prj/troll_farm (bot crate in rust/, tools in cgauto/, run python via
`uv run --no-sync python`). The bot: rust/src/botmain.rs + rust/src/botmain/{state,motion,
tactics,planner}.rs; submission = tools/bundle.py (module inliner) → tools/minify.py.
Champion/live reference: cgauto/submissions/v1.28.3-sticky6.min.rs (arena-live twin of v1.28.2; equality gates compare against THIS). Read
docs/ROADMAP.md §2 (iron rules) before acting. NEVER submit to the arena unless you are the
arena-runner. Record everything you conclude in your final report.

## builder brief
You implement ONE candidate: {CHANGE DESCRIPTION + exact code/diff}. Work in the current
tree (worktree if instructed). Steps: (1) apply the change; (2) `cd rust && cargo build
--release && cargo test --release` — all suites green; (3) self-determinism:
`./target/release/equality target/release/bot target/release/bot 8 300 target/release/bot`
must print EQUAL; (4) bundle+gates: `uv run --no-sync python tools/bundle.py`, copy
target/refactor/bundled.rs to a dot-free name, `rustc --edition 2021 -O` it (must compile),
`uv run --no-sync python tools/minify.py target/refactor/bundled.rs <out>` (<100000 bytes),
compile the minified copy too; (5) {EXTRA GATE, e.g. flag-off equality vs champion};
(6) freeze: cp bundled.rs and the minified file to cgauto/submissions/{VERSION}.rs/.min.rs
and to data/candidates/{VERSION}/; (7) write data/candidates/{VERSION}/report.md: what
changed, every gate command + its output line, size, anomalies. Commit with the trailer.

## gatekeeper brief
You gate candidate {VERSION} (files in data/candidates/{VERSION}/). Build the DEBUG probe:
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' on the candidate .rs →
minify → rustc-compile-check → keep the DEBUG .min.rs path. Play: `uv run --no-sync python
cgauto/collect_debug_games.py <dbg.min.rs> boss 8` then vs field agentIds {FIELD_IDS}
(2 games each; get IDs via `cgauto/field_targets.py 95 130`; include ≥1 denial-style
opponent: mikdiet 6480914 or plcc 6480966, and ≥1 ≥19.6 player). Read: `cgauto/ramp.py
--last 8` (wood ≥45, t300 delta vs −15.3 baseline), telemetry from the newest .raw files
(grep @TFFARM / @TFPHASE): {PHASE_INVARIANTS}. Append a verdict section (PASS/FAIL + all
numbers) to data/candidates/{VERSION}/report.md. FAIL on: wood <40, crater signature
(delta worse than −15), invariant violation, or any game crash.

## arena-runner brief
You own the ONE arena slot for candidate {VERSION} (already gated PASS). Procedure:
(1) bracket read: `uv run --no-sync python cgauto/cg_rank.py` — record the ARENA-ROOM line;
(2) submit: `uv run --no-sync python cgauto/api_submit.py cgauto/submissions/{VERSION}.min.rs`
(expect SUBMIT-OK); (3) wait ~20 min, read; wait ~15 min, read; wait ~15 min, read — converged
when two reads ≥15 min apart move <0.1; (4) verdict: keep if converged score ≥ bracket−0.2,
else `api_submit.py cgauto/submissions/v1.28.2-steady2.min.rs` (revert) and verify the
champion reconverges (~40 min, one read ≥18.7); (5) if KEPT and it beats the champion's band,
update the default path inside cgauto/api_submit.py to {VERSION}.min.rs; (6) append the
verdict (all reads with timestamps) to docs/silver-experiment-log.md and to
data/candidates/{VERSION}/report.md. Never leave the arena on a regressed bot.

## analyst brief
The arena verdict for {VERSION} is {VERDICT}. Run `uv run --no-sync python cgauto/battles.py
40`, summarize: win rate + margins by opponent band, new blowout patterns (fetch 1-2 loss
replays via gameResult/findByGameId — see cgauto/battles.py source for the call — and count
both players' command mixes per 75-turn phase). Compare against the 2026-07-07 00:55 census
(17/35, +4 avg, 100-150 band). Deliver: (a) 5-line summary, (b) a re-ranked hypothesis
queue (append to docs/silver-experiment-log.md), (c) whether the NEXT queued candidate is
still the best bet.
