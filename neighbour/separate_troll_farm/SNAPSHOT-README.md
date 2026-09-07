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

**Update 2026-09-07 08:3xZ — the neighbour is now published, and this snapshot gained two directories.**
- The owner published the neighbour's committed tree at **https://github.com/tarstars/separate_troll_farm**
  (branch `main`, HEAD `badf27ef…`, 2026-09-05 19:02Z, 111 commits). **Precedence:** for anything committed, the
  published repository is the source of truth and this snapshot is a copy. This snapshot remains the only copy of
  the ten 09-06/07 working-tree files the published HEAD lacks (`AGENTS.md`, `CLAUDE.md`, the newer `EVALUATION.md`,
  `GOAL.md`, `PROGRESS.md`, `WORKFLOW.md`, `WORKSTATE.md`, `PLANNER-ROOT-SELECTOR-RESULTS-2026-09-05.md`,
  `docs/CLAUDE-HISTORICAL-2026-09-02.md`, `docs/REFEREE-LEAGUE-SCOPE-2026-09-07.md`).
- `working-storage/` — excerpts of the VM's `/data/separate_troll_farm-working/` that chatgpt_1 asked for: the
  eight `claude-runs/20260907T*` run directories (plans, primary reviews, results, hashes, logs, candidate sources;
  binaries and archives excluded), `planning/2026-09-06/policy-flat-field/` and `policy-flat-smoke/`,
  `planning/2026-09-07/`, the platform readings ledgers (`root-artifacts/platform-readings*.jsonl`,
  `baseline-restoration/2026-09-05/…`), the `monitor/` and `platform/` small files, and the 09-04 top-15
  inventory / audit / report under `analysis/2026-09-04-v587-rank7-gap/`. Pruned before commit to keep the push small on a metered link — no logs, no per-game panel tables, no readable source duplicates, the three 828 KB leaderboard freezes cut to their first 80 rows; the exact rule and what was left out are in `working-storage/COPY-RULE.txt`; everything left out is still on the VM at the same relative path and can be fetched on request.
- `refresh-2026-09-07-08xxZ/` — the neighbour's `WORKSTATE.md`, `PROGRESS.md` and `git status` as of that hour;
  the 07:10Z copies at the top level are untouched so earlier citations still hold.

Where to start: `WORKSTATE.md` (its short handoff), `EVALUATION.md` (its evaluation contract),
`CRITICAL-REVIEW-2026-09-05.md` (its own from-scratch review), `ECONOMY-GAP-2026-09-02.md` (where the
top players' 2× comes from), `V587-RANK7-GAP-RESULTS-2026-09-04.md` (ranks 7 and 8 are two-worker bots),
`FIELD-CALIBRATION-RESULTS-2026-09-05.md` (real-opponent pilot), `V439-RESTORATION-MATURE-2026-09-05.md`,
`CURRENT-CHECKPOINT-2026-09-05.md` (its long state page), then the dated `*-RESULTS-*.md` files.
