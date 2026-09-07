# Historical charter — archived September 6; not current instructions

> Historical charter, superseded for current work on 2026-09-05. The owner requested a
> from-scratch rethink and has authorized publication. Read `EVALUATION.md` and
> `CRITICAL-REVIEW-2026-09-05.md` first: the target is rank <=7, the score-curve gate is
> retained only as a historical diagnostic, and the old queue is paused. The text below
> records the previous process; it must not silently reinstate that process.

This file is loaded into every Claude Code session here. It is the contract between the owner
and the agent. Read `RESEARCH-QUEUE.md` next, then the tail of `README.md` (the ledger).

## Scope and identity

- You work in this directory and in `/data/separate_troll_farm-working/` only. Large or temporary
  output goes under `/data/separate_troll_farm-working/` (see `AGENTS.md`); use
  `TMPDIR=/data/separate_troll_farm-working/tmp`.
- `/home/tarstars/prj/troll_farm*` are the team repository's checkouts. Import their tooling
  read-only. Never commit, push, create branches, worktrees, identities or messages there, and
  never follow their `GOAL.md`: its neural-network target is not this project's goal.
- This project is a git repository (`main`). Commit after every completed step with a message
  that states the measured result. Never leave generated candidates or results uncommitted.

## Goal and bar

A hand-written Rust bot for the Troll Farm platform ladder, one file under 100,000 UTF-16
characters, reaching a platform score of at least 25.40 and a rank inside the top ten. The
lineage's 23 mature readings have mean 23.1 and spread 1.1 with no trend, so this needs a step
change in the bot's economy, not one-game repairs. `ECONOMY-GAP-2026-09-02.md` is the evidence:
the top players bank about twice the wood per chop by growing many trees at once and chopping
them at size 4 with power-2 or power-3 trolls; V440 fells its own saplings at size 1 and chops
mostly with the power-1 starter.

## The gate (what "better" means)

1. Build the candidate as a module from the development base, `candidate_v468_no_denial_bonus_module.rs`
   (V439 without the denial bonus; owner-approved as base and baseline on 2026-09-02 at 11:25 after
   `CHOP-TARGET-RESULTS-2026-09-02.md`), with a `build_v<N>_<label>.py` script that
   applies marker substitutions and writes module, readable and compact files (see
   `build_v455_grow_before_fell.py`). The compact file must stay under 100,000 UTF-16 units.
2. Development panel: `candidate_compare_panel` with the V468 baseline bridge, maps 9941000 to
   9941007, both seats, 12 opponent families, 192 paired games, about two minutes:
   ```sh
   export TMPDIR=/data/separate_troll_farm-working/tmp
   B=$PWD/candidate_v468_full_baseline_bridge_module.rs
   E7A_HALF_BASELINE_MODULE=$B E7A_HALF_CANDIDATE_MODULE=$PWD/candidate_v<N>_<label>_module.rs \
     cargo build --release --bin candidate_compare_panel
   cp /data/separate_troll_farm-working/tmp/cargo-target-workspace/release/candidate_compare_panel \
     /data/separate_troll_farm-working/panels/<date>/runner-v<N>-vs-v468
   ALLOW_ANY_MAP_SEED=1 /data/separate_troll_farm-working/panels/<date>/runner-v<N>-vs-v468 \
     9941000 8 /data/separate_troll_farm-working/panels/<date>/v<N>-dev8.tsv 4
   /home/tarstars/venvs/nn-bot/bin/python panel_gate.py /data/separate_troll_farm-working/panels/<date>/v<N>-dev8.tsv
   ```
   The gate passes when mean own score is at or above the baseline at turns 100, 200 and 300 and
   at least +40 at the end. Read the mechanism from the TSV columns (wood, ring plants, harvests,
   chops, waits, train turn) and the command streams before deciding anything.
3. Only a candidate that passes the development panel goes on to the 16 fresh maps
   (`9941100 16`), then the 400-game duel legs against the champion of record and orchard 6
   (`duel.py` on `panel-400-seed2026.jsonl` under `/data/separate_troll_farm-working/nn/bench/`),
   then the readable-versus-compact command-stream audit (`audit_candidate_command_streams.py`).
4. The old 960-game no-regression count over archived platform games is a safety check for jams
   and protocol errors, never the selector.

## Platform rule

**Never submit to the platform without the owner's explicit approval in the conversation.** When a
candidate passes every step of the gate, stop, write the report, and wait. Do not run any
`platform_run*.py` or the one-use guard on your own. Earlier standing authorizations do not apply.

## One iteration per wake

1. Read `RESEARCH-QUEUE.md`; take the first open item. Do not reopen anything in its closed list
   or in `GROW-BEFORE-FELL-RESULTS-2026-09-02.md` without a new reason written down first.
2. Write the design in five to ten lines at the top of the item (mechanism, files, expected
   effect on the gate) before touching code. Python tooling gets pytest tests first.
3. Build, panel, gate, diagnose. If the panel fails, find the mechanism from the columns and
   streams and record it; a failure with a mechanism is a result, a failure without one is not.
4. Record: a dated results file for the candidate family, one paragraph appended to the end of
   `README.md` in its plain past-tense style, and the queue updated (item closed or split).
   Commit. Update the auto-memory only with facts a future session could not read from the repo.
5. Stop. An iteration ends within about 60 minutes of compute; if a panel is still running, wait
   for it rather than starting a second experiment. Never run two panels at once (4 cores).

## Stop rules

- Stop the programme and report when ten consecutive candidates fail the gate without a new
  mechanism being identified, or on 2026-10-17, whichever comes first.
- Stop and ask before changing the gate, the opponent pool, the panel maps or the baseline
  (V468 since 2026-09-02, replacing V439):
  those define what "better" means and are the owner's decisions.
- Stop and ask when an experiment needs more than the local machine (a cluster, the platform,
  another repository) or would touch the team repository.

## Build notes

- Tests: `/home/tarstars/venvs/nn-bot/bin/python -m pytest -q -p no:cacheprovider <file>` (system
  `python3` has no pytest; the scripts need only the standard library).
- A bare `cargo build` fails by design: the panel runners need the two `E7A_HALF_*_MODULE` env
  vars above. Compile a standalone program with `rustc --edition=2021 -O --crate-name <name> <file>.rs`.
- Everything that reads `troll_farm` sources points at the plain checkout `/home/tarstars/prj/troll_farm`
  at commit `c13f5635`; do not pull it forward.
- The referee's real constants (tree cooldowns, health, wood per size, training costs) are in
  `ECONOMY-GAP-2026-09-02.md` section 2 and in the Java source under
  `/data/strong-bot-sources/eulerscheZahl-Troll-Farm/src/main/java/engine/`.

## How the owner runs the loop

This session lives in tmux on the VM. The owner starts the self-paced loop with:

```
/loop Read CLAUDE.md and RESEARCH-QUEUE.md, then run exactly one research iteration as the charter describes: take the first open queue item, write its design, build, panel, gate, diagnose, record in a results file and the README, commit, update the queue, and stop. Never submit to the platform. Schedule the next wake no sooner than 30 minutes after finishing.
```

Pause it with `/loop` stop (or Ctrl+C in the session); every iteration leaves the repository
committed, so a stopped loop can be resumed from `RESEARCH-QUEUE.md` at any time.
