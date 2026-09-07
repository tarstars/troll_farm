# Task 20260907-two-project-analysis-and-plan — one analysis of BOTH Troll Farm projects, and the plan for what to build next

- **Born:** 2026-09-07 07:2xZ, on the owner's word to the coordinator: *"give a task for chatgpt_1 to perform the
  similar analysis of troll_farm and separate_troll_farm and give a detailed plan for the further project development."*
  The "similar analysis" is the one the coordinator did this morning (its conclusions are in §2 below, so they can be
  checked and disagreed with, not inherited).
- **Work owner:** **chatgpt_1** (interactive; the owner activates it). **Verifier:** the coordinator, by execution —
  every number in the deliverable that can be recomputed from a file in the repository will be recomputed.
  **chatgpt_2** may be asked for a cross-review afterwards, on the owner's word; it does not own this card.
- **Kind:** **a read and a plan. No bot, no build, no panel, no ladder, no platform, no cluster.**
- **Budget:** **two days, to 2026-09-09 08:00Z**; one review round after delivery; the coordinator sends a daily
  ack-required heartbeat (`WORKING-RULES.md` §8) and chatgpt_1 sends a progress message each working session.

---

## 1. The situation, which the owner has not yet seen on one page

There are **two projects and one CodinGame account.**

**Ours** (`tarstars/troll_farm`, this repository): coordinator `local_claude_1`; agents `claude_1`, `codex_1`,
`chatgpt_1`, `chatgpt_2`; the board `coordination/BOARD.md`; the flush entry
`coordination/HANDOVER-2026-09-07-port-reopened.md`. Champion of record: the simplified bot (the old champion minus
its four-line plum/lemon denial bonus), sha `0e92f8fa…`, `readable/denial-off-champion.rs`. Its identical file read
**18.19 / 17.04 / 18.14 / 18.72 / 19.23** (mean 18.26, sd 0.82) between 08-28 and 09-04. Since 08-27: twelve ladder
readings, **every candidate at or below the champion, fifteen lines in `coordination/GRAVEYARD.md`**. Nothing of ours
may go on the platform (owner, 09-04).

**The neighbour** (`separate_troll_farm`, the owner's other line, on the VM; **read-only snapshot in
`neighbour/separate_troll_farm/`**, start with its `SNAPSHOT-README.md`): primary agent "Astra", Claude as its
implementer; goal **rank ≤ 7**; **publication authorized**. Its lineage V54…V630 read **mean 23.1, spread 1.1, range
21.06–25.21** on the ladder (V370 25.21 / rank 17). Its live bot **V439** (submission `41245746`, agent `6704418`)
has held the account since **2026-09-05 08:01Z at rank 28 / 23.43** (mature, 95 wins / 0 draws / 65 losses;
23.35 / rank 28 of 178 on 09-07). **It replaced our champion (`6699467`).** Its "V468" is "V439 without the denial
bonus" — our champion of record's design. Its four-worker adaptive economy V543 read **13.92 / rank 155** despite
+96 points of local margin. Its own from-scratch review of 09-05 (`CRITICAL-REVIEW-2026-09-05.md`) found that its
selection rule (own score at turns 100/200/300, +40 final) did not express the objective and that its eight-map
panel is not a ladder instrument — the same two findings as our instrument audit of 09-04.

**So the family's strongest bot is the neighbour's, four rating points and thirty ranks above ours, and both
projects are stuck below the top ten for what look like the same reasons.**

## 2. What the coordinator's own reading found — to be checked, not inherited

1. **Three independent reads name the same missing architecture.** Ours: `codex_1/top10/field-comparison-2026-08-26.md`
   (the strong two-troll bots plant 4.5–5.9 bananas in turns 1–50 against our 0.05, harvest their own trees 21–30
   times a game against our 2.85, and fell them 26–54 turns after planting against our 4.6) and
   `chatgpt_2/port-postmortem/RESULTS.md` (the #2 bot banks 334 wood points off 32 plants; our port 100 off 13; the
   orchard turnover is the engine). Theirs: `ECONOMY-GAP-2026-09-02.md` (same number of chops, half the wood — 0.28
   wood per chop against the #1's 0.58; 60 % of our chops at chop power 1; own trees felled at size 1 five turns
   after planting, 1,702 of 1,931; wood income flat 15/15/15 per hundred turns against 8/32/59) and
   `V587-RANK7-GAP-RESULTS-2026-09-04.md` (ranks 7 and 8 finish 114 of 116 and 121 of 122 games with **two**
   workers; the #1's two-worker games average 34.7 plants and 47.5 wood from its own crops; recommendation: a
   scratch two-worker allocator owning a multi-cell crop pipeline). **The renewable own-crop lifecycle near the
   shack — plant, grow to size 4, harvest the fruit as seeds and points, fell with the stronger axe (banana first),
   bank, replant the same kind — run continuously by two workers.**
2. **Every graft of that lifecycle onto the yamo job planner failed, in both projects.** Ours: the b100 ring, the
   banana R2 rounds, orchards 1–8, the champion-prefix orchard macros (rows 3-8/3-9, zero on two instruments).
   Theirs: V441–V454 (putibuzu's door factory), V455–V586 (protected saplings made the assigned worker wait),
   V557–V559 and V569–V571 (banana reserves), V588–V618 (parallel orchards, owned lifecycles, seed transactions),
   the home-growth kernel (an exact tie), grow-before-fell. **Nobody has built the lifecycle as its own controller.**
   chatgpt_2's "native orchard-turnover controller" (row P-2) and the neighbour's V587 prescription are the same
   proposal with different rosters.
3. **The roster is closed on both sides.** Ours four ways (`HANDOVER-2026-09-04-orchard-turn.md`); theirs by census —
   zero of 41,879 two-worker states afford any specialist third troll (`SURPLUS-HIRE-FEASIBILITY-2026-09-05.md`).
4. **The instruments differ, and theirs has the one thing ours lacks:** paired unranked games against the *real*
   ranked agents (putibuzu, tonigineer, viewlagoon, delineate …; `FIELD-CALIBRATION-RESULTS-2026-09-05.md`,
   `SERVICED-SOURCE-RESULTS-2026-09-05.md`). Ours has the referee-exact engine, the replay corpus, the exact
   reconstructions, the sealed holdout (row 0-8) and the two-agent reproduction discipline. Our four-opponent field
   panel mis-ranks (orchard 6 read "dead" and was ladder-neutral: `coordination/tasks/20260904-instrument-audit.md`).
5. **Open disagreements between the two records:** the second troll's talents (our census T-4 says the strong
   two-troll bots buy 2/2/0/2 and never harvest power; their V587 says putibuzu's commonest second worker is 2/2/2/2,
   49 of 116); the denial bonus (their V439 and V468 both 1 of 6 on fresh real-agent maps; our July bench predicted
   a collapse without it; our 08-27 ablation read 21.2 against 21.8–22.1); selection by own score (theirs, retired)
   versus paired margin with an interval (ours) versus match points (theirs now).
6. **Organisation:** one account, two contradictory standing rules (ours frozen, theirs publishing), our board
   saying our champion held the ladder when it did not, and neither project reading the other's record until today.

## 3. The questions — answer each with numbers and the file they come from

1. **One scoreboard.** A single table of every mature ladder reading of both lineages since 2026-08-20: date,
   which project, which file (sha or V-number), what it changed, rank, score, the top-ten boundary that day. Ours:
   `local_claude_1/ladder-queue/readings.jsonl` and the board's ladder queue; theirs: the README ledger,
   `ECONOMY-GAP-2026-09-02.md` §1, `V543-MATURE-PLATFORM-RESULTS-2026-09-04.md`, `V439-RESTORATION-MATURE-2026-09-05.md`,
   `WORKSTATE.md`. Say what the noise of one reading is on each side's own evidence (ours: sd 0.82 over five identical
   readings; theirs: spread 1.1 over 23, and V368's identical file at 25.21 then 21.06).
2. **The two graveyards side by side.** Cluster every dead line of both projects by mechanism (third troll / roster;
   orchard and banana grafts; denial; opening order and the second troll's timing; lookahead planners and
   distillation; the neural network; instruments). For each cluster: what the union of the evidence establishes,
   what it does **not** establish (name the untested thing), and which project's evidence is the stronger and why.
   Sources: our `coordination/GRAVEYARD.md` and `docs/CONSTRAINTS.md`; their `README.md` ledger,
   `CURRENT-CHECKPOINT-2026-09-05.md`, `RESEARCH-QUEUE.md` (closed list) and the dated `*-RESULTS-*.md` files.
3. **The gap, in one statement.** Reconcile the three gap reads of §2.1 into one mechanism separating a 23-point bot
   from a 27-point one, with the numbers beside it (chops, wood per chop, plants, own-crop wood, harvests, wood by
   hundred-turn window, waits), and settle or name as unsettled the second-troll question of §2.5. Say plainly
   whether the gap is one mechanism or several, and how much of it the two-worker leaders close without a third troll.
4. **The instruments.** Which selectors on either side have ever been calibrated against the ladder, with what
   result (our instrument audit findings 1–7; their field pilot, their dev-panel-versus-rollout history — V543's +96
   local margin and rank 155). Propose **the one evaluation pipeline** for the family — screening, selection,
   confirmation, and what a ladder slot may be spent on — using the best of both sides (their real-agent paired
   games, our sealed holdout and reproduction rule), with the resolution each stage buys and its cost in games.
5. **The design decision.** Rank the candidate directions with expected size, cost, dead condition and what would
   make each one wrong: (a) a from-scratch two-worker crop-lifecycle controller (V587's prescription); (b) chatgpt_2's
   native orchard-turnover controller with the #2's roster (row P-2, gates = the real bot's own trajectory
   checkpoints); (c) continuing the neighbour's late-game lookahead planner line (ties locally, three platform
   compile timeouts); (d) the network line (Track N, best artefact 37 of 144 against the champion's file, the
   self-play road closed); (e) small one-variable rules on the champion (e.g. E-2's late PICK/PLANT suppression);
   (f) stop and hold V439. **Do not pick by preference; pick by the record**, and say which evidence would move you.
6. **The plan.** Phases with *done means / dead means / budget* for each; the evaluation pipeline of §3.4 built in;
   the division of labour between the two projects and their agents (who owns the account and the queue; what each
   side's tooling is for; whether to merge the repositories or keep two with a protocol); a calendar; the decisions
   that are the owner's, each answerable in one word; the risks and the traps already recorded (a multi-day card needs
   a heartbeat; push first, pin second; never model the opponent as idle; a control arm must pass mechanics; a
   duel with our own clear-cutter is not a ladder proxy; nothing below 2.2 on the ladder is evidence from one reading).

## 4. Done means

Under `chatgpt_1/two-project-plan/`:

1. `ANALYSIS-<date>.md` — the answers to §3.1–3.5 with their tables, every number citing the file it came from.
2. `PLAN-<date>.md` — §3.6, the detailed plan.
3. `OWNER-PAGE.md` — **one page in plain words for the owner**: the situation, the one mechanism, the recommendation,
   the decisions to make (≤ 3), what it costs and how long. Every code or abbreviation explained at first use.
4. Any script used to compute a number, with its command line.
5. A handoff message pinning the commit; the board row A-1 updated in the same commit is the coordinator's job on
   integration.

The coordinator then reproduces every recomputable number by execution and records the verification on this card.

## 5. Dead means

- If the snapshot lacks a document or number needed for a question, **say exactly which, in a progress message, and
  go on with the rest** — the coordinator fetches it from the VM. That is not a death.
- If two load-bearing facts in the two records contradict each other and cannot be settled from the files, **say so
  and propose the single cheapest measurement that settles it**; do not pick a side.
- The card dies only if chatgpt_1 has not been activated by 2026-09-09 08:00Z; then the coordinator writes the plan
  itself and says so on the board.

## 6. What this card must NOT do

- No bot, no build, no panel, no ladder, no platform, no cluster; no edits to `neighbour/` (evidence, not code) or to
  any file outside `chatgpt_1/`.
- No number without its source file; no rating claim from a single ladder reading; no margin-to-rating slope; no
  judging a bot by per-decision agreement with a stronger bot (our record: 77 % agreement, −173 points closed-loop).
- Distinguish what a document *claims* from what it *verified* — on both sides. Our own coordinator's diagnosis of
  the port was wrong and its repair could not have worked (`HANDOVER-2026-09-07-port-reopened.md` §2); the
  neighbour's own review found its selector did not express its goal. Treat every conclusion in both records, and in
  §2 above, as a claim to check.
- Plain words for the owner; the board shorthand (row ids, track letters, V-numbers) explained wherever it appears.

## 7. Inputs — where to read, on each side

**Ours:** `coordination/WORKING-RULES.md`, `coordination/BOARD.md`, `coordination/HANDOVER-2026-09-07-port-reopened.md`
and the handovers of 09-04 and 09-03 it points to, `coordination/GRAVEYARD.md`, `docs/CONSTRAINTS.md` (the older
closures), `coordination/tasks/20260904-instrument-audit.md`, `coordination/tasks/20260904-sealed-holdout.md`,
`chatgpt_2/port-postmortem/RESULTS.md`, `chatgpt_2/late-bankable-wood/`, `codex_1/top10/field-comparison-2026-08-26.md`,
`local_claude_1/second-troll-census/README.md`, `local_claude_1/reconstructions/README.md` and the four
`ALGORITHM.md`, `local_claude_1/nn-bot/ANALYSIS-2026-08-29.md` and the `GATE-*-VERDICT-*.md` files,
`claude_1/endgame-gap/READ-2026-09-02.md`, `local_claude_1/ladder-queue/readings.jsonl`, `docs/mechanics.md`.

**Theirs (the snapshot):** `SNAPSHOT-README.md` first, then `WORKSTATE.md`, `EVALUATION.md`, `WORKFLOW.md`, `GOAL.md`,
`CRITICAL-REVIEW-2026-09-05.md`, `ECONOMY-GAP-2026-09-02.md`, `V587-RANK7-GAP-RESULTS-2026-09-04.md`,
`FIELD-CALIBRATION-RESULTS-2026-09-05.md`, `NEXT-BOT-RESULTS-2026-09-05.md`, `DENIAL-CONFIRMATION-RESULTS-2026-09-05.md`,
`V439-RESTORATION-MATURE-2026-09-05.md`, `V543-MATURE-PLATFORM-RESULTS-2026-09-04.md`,
`CURRENT-CHECKPOINT-2026-09-05.md`, `RESEARCH-QUEUE.md`, `PUBLIC-STRATEGY-REVIEW-2026-09-05.md`,
`SURPLUS-HIRE-FEASIBILITY-2026-09-05.md`, `LOOKAHEAD-*.md`, `HOME-GROWTH-RESULTS-2026-09-05.md`,
`SERVICED-SOURCE-RESULTS-2026-09-05.md`, `PLANNER-*.md`, the `V5xx`/`V6xx` results files, and `README.md` (the
162 KB ledger; read it by section, not whole). The live bot's source is `bot.rs`; its experimental modules
`next_bot/`, `lookahead_search.rs`, `home_growth.rs`, `serviced_source.rs`.

## Amendment 2026-09-07 08:3xZ — check again against the published repository, and extend

**Owner:** *"I published separate_troll_farm. Give chatgpt_1 task to check again and extend the analysis."*

**What changed since the charter.**

- **The first packet is delivered and verified.** chatgpt_1 delivered at 08:13Z (handoff
  `coordination/messages/chatgpt_1/20260907T081307Z-20260907-two-project-analysis-and-plan-handoff.md`, pin `1141f74e…`),
  integrated by merge at `eda83df6` (merge, not cherry-pick — our git rule). The coordinator's verification by
  execution: `audit.py --self-test` 6/6 PASS; the default run reproduces (mean 18.264, sample SD 0.8155, range 2.19,
  half-widths 0.923 / 0.493 at 6 / 21 per arm); `--source-root` against the integrated checkout **PASS** (readings
  blob `2909dab7…`, 16 final records, the 162-game row flagged). **Its six corrections are accepted** and carried to
  the board: standalone controllers *have* been built (our A2-1 in July; the neighbour's V543, `next_bot`, and the
  09-07 dispatch line); the second-worker "harvest zero" statement over-generalised one cohort (our own census records
  putibuzu's second worker harvesting in 100 % of its sample, most often 2/2/2/2); the policy-flat planner is
  deployed under Rust 1.90 and its fresh real-agent screen is 2W/4L for both arms; fruit-first was not the port's
  error; the 23-reading summary is V54–V440 and mixes policies; the sealed bank's two-arm cost is 1,024 games.
- **The neighbour is now public:** https://github.com/tarstars/separate_troll_farm — branch `main`, HEAD
  `badf27efee7eca794c149f0707c087f7ed1eb0ff` (2026-09-05 19:02Z), 111 commits since its 09-02 baseline snapshot;
  the whole committed tree (the ~1,000 candidate sources and builders, the tests, the tooling, the README ledger).
  **Precedence:** for anything committed, the published repository is the source of truth and the snapshot here is a
  copy; the snapshot is the *only* copy of the ten working-tree files of 09-06/07 that the published HEAD lacks
  (`AGENTS.md`, `CLAUDE.md`, the newer `EVALUATION.md`, `GOAL.md`, `PROGRESS.md`, `WORKFLOW.md`, `WORKSTATE.md`,
  `PLANNER-ROOT-SELECTOR-RESULTS-2026-09-05.md`, `docs/CLAUDE-HISTORICAL-2026-09-02.md`,
  `docs/REFEREE-LEAGUE-SCOPE-2026-09-07.md`).
- **The evidence asked for in the ack, the progress note and the handoff is in the snapshot now**, under
  `neighbour/separate_troll_farm/working-storage/` (copied from the VM's `/data/separate_troll_farm-working/`,
  secret-scanned): the eight 09-07 `claude-runs/20260907T*` directories' `PLAN`, `PRIMARY-REVIEW`, `RESULT`, hashes,
  logs and candidate sources — including the **complete-funding run `20260907T065010Z-749733-1`** and the dispatch
  ledger / forestry / fruit / timed runs; `planning/2026-09-06/policy-flat-field/SCREEN-RESULT.md` with its plan and
  manifest, the policy-flat smoke, and `planning/2026-09-07/`; the platform readings ledgers
  (`root-artifacts/platform-readings*.jsonl`, the V439 restoration's readings under `baseline-restoration/`); the
  `monitor/` and `platform/` directories' small files; the 09-04 top-15 inventory, audit and report JSON under
  `analysis/2026-09-04-v587-rank7-gap/`. `neighbour/separate_troll_farm/refresh-2026-09-07-08xxZ/` holds the
  neighbour's `WORKSTATE.md`, `PROGRESS.md` and `git status` as of that hour. The 07:10Z snapshot files are untouched.

**The extension — same directory, new files, append-only (do not rewrite the 08:13Z packet), same deadline
2026-09-09 08:00Z:**

- **E1 Re-check** (`RECHECK-<date>.md`): every statement in the first packet that changes when read against the
  published repository and the new evidence, as a numbered corrections list; confirm the snapshot's committed
  documents match the published ones (by hash or by diff of the files you relied on); name what you could not check.
- **E2 Phase 0, done now** (`PHASE0-AUDIT-<date>.md`): the comparison matrix of PLAN §5 — every existing controller
  (theirs: `next_bot`, the 09-07 dispatch variants, the complete-funding run, V543/V564, the home-growth kernel;
  ours: A2-1, the port v2/v3.1 in `codex_1/norxondor-port/`, the b100 / banana R2 line, the orchard macros of rows
  3-8/3-9) against the nine lifecycle properties (a)–(i), IMPLEMENTED / ABSENT / UNKNOWN with the code path and a
  trace where one exists. **Read the complete-funding run's primary review first** and say whether it implements
  the lifecycle and what it measured; then say whether TURNOVER survives as a non-duplicate hypothesis, or is
  DUPLICATE_HYPOTHESIS, and what follows.
- **E3 The lineage diff** (`LINEAGE-DIFF-<date>.md`): what V439 (`bot.rs` in the published repository) contains that
  our champion of record (`readable/denial-off-champion.rs`) and the old champion with the denial bonus do not; which
  of those additions carry measured evidence in the neighbour's ledger and which do not; and whether the same-day
  readings show the neighbour's lineage above ours for reasons in the code rather than in the field (08-28: the
  neighbour's V2 23.03 / rank 32 against our champion 18.19 / 85 and orchard 6 18.84 / 70 the same day; 09-04/05:
  19.23 / 60 against 23.43 / 28). End with what, if anything, is worth carrying from V439 into a unified champion,
  with its evidence, and what it would cost to test.
- **E4 The scoreboard, second edition** (`SCOREBOARD-v2.md`): the neighbour rows' mature dates from the readings
  ledgers; top-ten boundaries where the inventories give them; the same-day pairs; NA where the record is silent.
- **E5 The tooling inventory as code** (`TOOLING-<date>.md`), from the published repository and ours: the unranked
  real-agent collector (its twelve-game limit, manifests, identity checks), the rank monitor, the replay/command
  audit, the panel runner and legacy gate; ours: the sealed-holdout runner (`codex_1/sealed-holdout/`), the field
  panel (`claude_1/h2h-panel/`), `cgauto/field_panel.py`. For each: what it does, what it needs, whether it can
  serve PLAN Phases 3–5 as written, and the exact gap (the chunked, resumable execution path).
- **E6 The candidate census** (`CANDIDATE-CENSUS-<date>.md`): every V-candidate V1–V630 from the README ledger, the
  results files and the published builders and sources, clustered by mechanism family with counts and the best
  mature or paired outcome per family — so the owner sees what was tried, how many times, and with what best result.
- **E7 Revise** (`PLAN-<date>-v2.md`, `OWNER-PAGE-v2.md`): fold E1–E6 in; keep the three one-word decisions or
  replace them with better ones; if E2 finds the mechanism already implemented and lost, say so and name the next
  hypothesis.

Rules of §6 unchanged; the heartbeat both ways unchanged; a handoff pinning the commit when done, progress messages
per working session.

## Log

- 2026-09-07 07:2xZ born on the owner's word; the neighbour's documents snapshotted into `neighbour/separate_troll_farm/`
  (it has no git remote and lives on the VM, which chatgpt_1 cannot reach); charter sent to chatgpt_1, ack-required;
  the owner asked to activate it. — coordinator
- 2026-09-07 07:25:58Z chatgpt_1 acked (the owner activated it); 07:45Z progress with five corrections; **08:13:07Z
  the first packet delivered** (`chatgpt_1/two-project-plan/`: ANALYSIS, PLAN, OWNER-PAGE, SCOREBOARD,
  DECISION-MATRIX, VERIFICATION, `audit.py`). Its recommendation: UNIFY the account queue and coordination; HOLD
  V439; TURNOVER only as a bounded offline audit / design / prototype conditional on the mechanism being genuinely
  missing from the neighbour's completed attempts; a conditional budget of 1,092 unranked games and a separately
  approved 1,280-game ladder block; zero games run. — chatgpt_1
- 2026-09-07 08:3xZ the coordinator's verification by execution (above) PASS; the packet merged at `eda83df6`; the
  owner published the neighbour and asked for a re-check and an extension; the requested evidence copied from the
  VM; the amendment above sent as the extended charter, ack-required. — coordinator
