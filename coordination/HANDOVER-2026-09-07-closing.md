# Handover — 2026-09-07 11:xxZ — the contest is closed; the project is finalised

**The owner, 2026-09-07 ~10:5xZ:** *"it seems that the contest is closed on the platform. Our current task is to
finalize our participation, clean up data, commit and push code."*

**Read this page, then `coordination/BOARD.md`.** It is the last flush entry. It continues
`HANDOVER-2026-09-07-port-reopened.md` (the morning's state) and the two-project analysis
`chatgpt_1/two-project-plan/OWNER-PAGE-v2.md`; everything before those is history.

---

## 1. The last observed state of the platform (read-only reads; nothing of ours was submitted)

| when (UTC) | what the room said | whose bot |
|---|---|---|
| 09-04 08:27 | our champion of record `0e92f8fa…`: **19.23 / rank 60 of 177** (agent `6699467`) | ours — the last reading of our line |
| 09-05 08:50 | the neighbour's V439: **23.43 / rank 28** (agent `6704418`), mature, 95 wins / 0 draws / 65 losses | the neighbour project |
| 09-07 11:04 | **24.9 / rank 18 of 179 Legend, agent `6713059`**, `promotable=False` | **not in our record** — a submission after 08:33Z by the neighbour project or by the owner directly |

The 11:04Z listing (top 100) is saved at `local_claude_1/closing/leaderboard-top100-2026-09-07.txt`. The closure
itself is the owner's observation; the room still answered read-only calls at 11:04Z, and that is all this record
verified.

**Our own line's numbers, for the record.** Best reading ever: **22.6 / rank 36** (2026-08-23, the old champion
"door 1", `547fa706…`, `readable/door1-champion.rs`). Champion of record since 08-27: the same bot minus its four-line
plum/lemon denial bonus (`0e92f8fa…`, `readable/denial-off-champion.rs`, `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`);
five identical-file readings 18.19 / 17.04 / 18.14 / 18.72 / 19.23 (mean 18.26, sd 0.82). The family's best: the
neighbour's V370 **25.21 / rank 17** (09-01) and today's 24.9 / rank 18.

## 2. Where everything is

- **This repository** — `github.com/tarstars/troll_farm` (public). At the closing commit `main` equals
  `agent/local_claude_1`; **every agent branch is merged** (chatgpt_1's two packets at `8bcf5e08`, local_codex_1's
  leftover at `f74c5cfc`); the ref `rescue/chatgpt1-three-troll-optimized-start-2026-09-03` is kept as is. The closing
  commit is tagged `contest-closed-2026-09-07`.
- **The organisation:** `coordination/WORKING-RULES.md`, `coordination/BOARD.md`, `coordination/GRAVEYARD.md`, the cards
  under `coordination/tasks/`, the handovers `coordination/HANDOVER-*.md` (2026-08-27 → 09-07), `docs/STATE.md`,
  `docs/CONSTRAINTS.md` (the older closures), `docs/mechanics.md` (the referee facts).
- **The bots of record:** `cgauto/submissions/` (hash-locked, immutable), `readable/*.rs` and `readable/diffs/*.diff`
  (every experiment as a readable diff on the champion).
- **The science, by line:** the four top-player reconstructions `local_claude_1/reconstructions/` and the PDF
  `docs/reports/2026-08-28-top-four-algorithms.pdf`; the port of the #2 player and its post-mortem
  `codex_1/norxondor-port/`, `chatgpt_2/port-postmortem/`; the network programme `local_claude_1/nn-bot/`
  (`ANALYSIS-2026-08-29.md`, the `GATE-*-VERDICT-*.md` files, the pre-registrations); the opening solver
  `claude_1/opening-solver/`, `chatgpt_1/opening-dp-oracle/`; the clean-room package `cleanroom/package/`; the
  instrument audit `coordination/tasks/20260904-instrument-audit.md` and the sealed holdout `codex_1/sealed-holdout/`
  (never opened); the field comparison `codex_1/top10/`; the ladder ledger `local_claude_1/ladder-queue/readings.jsonl`
  with the seventeen collected 160-game packages `games-*/`.
- **The two-project analysis:** `chatgpt_1/two-project-plan/` — start at `OWNER-PAGE-v2.md`, then
  `SOURCE-CORRECTIONS-2026-09-07.md`, `PHASE0-AUDIT-2026-09-07.md`, `LINEAGE-DIFF-2026-09-07.md`, `PLAN-2026-09-07-v2.md`.
  Its recommendation at closing: **UNIFY / TRACE / HOLD** — one account operator and queue; trace the neighbour's
  concrete funding failure before any repair; keep V439. Its census of candidates is explicitly partial (189
  unresolved labels) and its re-check covered selected identities, not all 115 documents.
- **The neighbour project:** `github.com/tarstars/separate_troll_farm` (its committed tree of 09-05 19:02Z) and our
  read-only snapshot `neighbour/separate_troll_farm/` (the 09-06/07 working-tree documents that HEAD lacks, plus the
  working-storage excerpts and `COPY-RULE.txt`). Its working tree on the VM held 200 uncommitted entries at 11:0xZ.
- **Data:**

| where | what | size | at closing |
|---|---|---|---|
| laptop `~/prj/troll_farm/data/raw` | the raw replay corpus (the collector's output) | 21 GB | **DELETED 11:3xZ on the owner's word** (`git clean -fdX` on `games/` and `snapshots/`: 32,589 ignored files; every one of the 325 tracked files under `data/raw` — the battles index, the 08-06 leaderboard, the logs, 290 sample game records — is still there; 91 MB remain). The cold archive up to 08-11 is in the Yandex bucket (memory `yandex-cloud-setup`); the games collected after 08-11 are gone. |
| laptop `~/prj/troll_farm/data/processed` | `games.jsonl`, `turns.jsonl.gz` (174 MB), `stats.json` (32,878 games, the last run, committed) | 1.7 GB | kept — the corpus of record |
| laptop `~/nn-data` | the network arms' checkpoints (r22, s22, s22L, hs22…), the host map corpus, bench replays | 1.2 GB | **DELETED 11:3xZ on the owner's word** (the battery-guard loop that lived there stopped first). The one-file exported network bot and every gate verdict stay in the repository under `local_claude_1/nn-bot/`. |
| VM `/data/archive` | the archive | 2.2 GB | keep |
| VM `/data/scratch` | verification scratch (3t / wg / sgo / 2a / audit-orchard6 / claude_1's runs / the corpus copy), plus neighbour-named panel files | 5.5 GB | **DELETED 11:3xZ on the owner's word, down to 297 MB.** The filter spared the neighbour's dash-named entries (`candidate-v3xx-*` panels, `v4xx-*` field records — the 297 MB that remain) but not its underscore-named ones (`candidate_v3xx_*panel_runner` build products, `candidate_v379_bridge`) or three `candidate-failure-summary-v38x/v392` JSONs, which went with ours. The exact deleted and kept lists: `local_claude_1/closing/vm-scratch-cleanup-2026-09-07.txt`. |
| VM `/data/separate_troll_farm-working` | the neighbour's working storage | 16 GB | not ours; untouched |
| cloud | the Yandex Object Storage cold archive; the YT cluster pool | — | bucket kept; no operation of ours running or pending at 11:0xZ |

## 3. What was switched off today, and how to switch it back on

| thing | state now | to reverse |
|---|---|---|
| laptop cron `17 5 * * *` wide replay collector | **disabled** 11:03Z, prefix `#DISABLED-2026-09-07-contest-closed` (backup `local_claude_1/closing/crontab-laptop-backup-20260907T1103Z.txt`) | remove the prefix with `crontab -e` |
| VM ladder-queue cron | disabled since 09-04 (`#DISABLED-2026-09-04-owner-no-platform`) | remove the prefix — only on the owner's word |
| VM coordinator-watchdog cron | disabled since 09-03 | remove the prefix |
| VM `agent-launcher.service` (the wake-on-mail doorbell) | **disabled** at closing | `sudo systemctl enable --now agent-launcher.service` on `troll-vm` |
| VM `night-runner.service` | down since August | leave down |
| build outputs `rust/target` (two checkouts) and `chatgpt_1/opening-dp-oracle/rust-anytime/target` | **deleted** (5.2 GB, regenerable) | `cargo build --release` |

The standing rule of 09-04 — nothing goes on the platform until the owner says so — stays in force at closing.

**The owner's cleanup rulings, 11:2xZ:** *"remove Raw replays, network checkpoints, VM verification scratch; keep VM;
keep neighbour's worktree."* All three removals are done (table above). The VM stays up; the neighbour's worktree
(200 uncommitted entries at 11:0xZ) is untouched. Disk after cleanup: the laptop 450 GB used of 899 (from 476 at the
start of the day); the VM `/data` 5.8 GB used of 98.

## 4. The honest scoreboard at closing

- **Our line:** best 22.6 / rank 36 on 08-23; the champion of record 18.3 ± 0.8 in September; twelve ladder readings
  since 08-27, none above the champion; the graveyard holds every closed line with what killed it; the network
  programme's best artefact won 37 of 144 against the champion's file.
- **The neighbour's line:** readings 21–25 across its lineage, best 25.21 / rank 17; V439 23.43 / rank 28 on 09-05.
- **What the two projects established together** (three independent reads and one joint analysis): the strong
  bots' extra points come from a renewable own-crop economy next to the shack — wood per chop 0.58 against our 0.28,
  income that compounds instead of staying flat — and every graft of it onto the yamo job planner failed on both
  sides; standalone controllers were built on both sides and lost too; the roster is closed on both sides; a single
  ladder reading resolves nothing below about 2.2 points, and the ladder was the wrong instrument for most of what
  was tried. The one thing never built and never disproved: the coupled native turnover of the #2 player (tree
  replacement and thinning with harvesting kept on in wood mode, with its own targeting) — chatgpt_1's Phase-0 audit
  calls the generic form a duplicate hypothesis and the native semantics unknown.
- **What worked as process, and is worth keeping:** verification by execution before anything reaches the owner;
  two independent implementations of one measurement; pre-registered dead conditions; the board with done / dead /
  budget on every card; readable diffs for every experiment; plain words for the owner.

## 5. How to resume, if the game is ever reopened

Start here → `coordination/BOARD.md` → `chatgpt_1/two-project-plan/OWNER-PAGE-v2.md` → its `PLAN-2026-09-07-v2.md`.
Re-enable the crons and the launcher as in §3; the platform rule needs the owner's word; the traps of
`HANDOVER-2026-09-07-port-reopened.md` §6 still apply (a mail-woken agent needs a heartbeat; push first, pin second;
never model the opponent as idle; a control arm must pass mechanics; a duel with our own clear-cutter is not a ladder
proxy; stamps from `date -u`).
