# Read-only snapshot of the neighbouring project `separate_troll_farm` (taken 2026-09-07 ~07:10Z)

**What this is.** A copy of the documents and the main source files of the owner's *other* Troll Farm
project, which lives on the VM at `/home/tarstars/prj/separate_troll_farm` (working storage
`/data/separate_troll_farm-working/`, not copied). It was taken by the coordinator (`local_claude_1`) so
that agents who work through GitHub and cannot reach the VM — `chatgpt_1`, `chatgpt_2` — can read it.

**Provenance.** The neighbour's git HEAD was `badf27efee7eca794c149f0707c087f7ed1eb0ff` (committed
2026-09-05 19:02Z); its working tree also held uncommitted files written 2026-09-06 and 2026-09-07
(`WORKSTATE.md`, `PROGRESS.md`, `WORKFLOW.md`, `GOAL.md`, `EVALUATION.md` and others) — **this snapshot
copies the working tree, not HEAD**, so it is more recent than the neighbour's own last commit. The
neighbour's commit log and `git status` at copy time are in `GIT-LOG-AND-STATUS-2026-09-07.txt`.

**What is included.** Every `*.md` at the neighbour's top level and under `docs/` (115 files, about
1.2 MB, of which `README.md` is the 162 KB historical ledger of candidates V1 → V630);
`bot.rs` (the live bot, V439, 4,404 lines); `lookahead_search.rs`, `home_growth.rs`,
`serviced_source.rs` (its three experimental planner/kernel modules); `next_bot/*.rs` (its
experimental modular controller). **Excluded:** its ~1,000 archived candidate `.rs` files and
builders, all binaries, panels, replays and the working storage.

**Rules.**
- **Never edit anything here.** It is evidence, not our code. To refresh, re-run the copy from the VM and
  commit the result as a new snapshot with the new date in this file.
- The neighbour's own rules (its `CLAUDE.md`, `AGENTS.md`, `WORKFLOW.md`, `EVALUATION.md`) make *our*
  repository read-only for *it*; the same courtesy applies in reverse — nothing of ours writes there.
- Its vocabulary: "Astra" is its primary agent (the owner's other run); "Claude" there is an implementer
  driven through `claude-proxy`; "V439", "V468", "V543" … are its candidate numbers ("V468" is "V439
  without the denial bonus" and is what it calls our champion of record's design; its README records
  our submission `6699467` as "the original V468 resident").
- Its live bot **shares the CodinGame account with ours**: its V439 (submission `41245746`, agent
  `6704418`) has held the ladder since 2026-09-05 08:01Z at rank 28, rating 23.35–23.43. That is the
  reason for the owner's 2026-09-04 rule that nothing of ours goes on the platform.

Where to start: `WORKSTATE.md` (its short handoff), `EVALUATION.md` (its evaluation contract),
`CRITICAL-REVIEW-2026-09-05.md` (its own from-scratch review), `ECONOMY-GAP-2026-09-02.md` (where the
top players' 2× comes from), `V587-RANK7-GAP-RESULTS-2026-09-04.md` (ranks 7 and 8 are two-worker bots),
`FIELD-CALIBRATION-RESULTS-2026-09-05.md` (real-opponent pilot), `V439-RESTORATION-MATURE-2026-09-05.md`,
`CURRENT-CHECKPOINT-2026-09-05.md` (its long state page), then the dated `*-RESULTS-*.md` files.
