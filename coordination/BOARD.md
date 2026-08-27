# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-27T03:25Z (cron wake 8)

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Verdict — CLOSING under the bound.** The one panel ran 13:20Z: the loop is cured (`xc=0` on all six loop games; blocking games 52→40; D-1 27→23) **but −65 own-score points / 240 games** (`m061` −47/−43) and a goal kept **171 turns** vs the 30-turn stop → the pre-committed §9.10 gate fires: *the absolute form is too strong*; no re-tuning (owner bound). | codex_1: the one reproduction (last allowed act); coordinator: obituary in GRAVEYARD, owner reads the diff | — | 1 reproduction, 1 owner read, then stop | 08-26 13:20Z (G-1 handoff `132000Z`; diff `readable/diffs/candidate-3-keep-your-goal.diff` +927/−9 and packet `claude_1/cure3/g1-packet-2026-08-26.md` now on `main`) |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviewed) | **DONE 13:57Z** — integrated behind the panel API; claude_1 re-review ACCEPT (Candidate 3's v6 archive: 0 decode errors, 15 episodes; Candidate 2's v5 row reproduces) | record only: the two proof inputs live in `/tmp` on the VM (915 KB + 437 KB) — owner decision whether to keep them out-of-tree | — | spent | 08-26 13:57Z |
| D-3 | Why did a troll on `m061` keep one goal for 171 turns? (`coordination/tasks/20260826-m061-stale-goal-read.md`) | claude_1 (codex_1 reviewed) | **CLOSED — ACCEPTED 15:08Z** (codex_1's re-run of `idleprobe.py` byte-identical) | — | — | spent | 15:08Z |
| D-4 | **Candidate 3b** (`coordination/tasks/20260826-candidate-3b-stuck-holder-release.md`) | claude_1 (codex_1 reproduced) | **CLOSED — DEAD 15:27Z, REPRODUCED FAIL 15:49Z.** The release fires exactly where D-3 predicted (`m061` t73/t109), cures the kept-goal age (171/170 → 43/78), and recovers **0 of 44/47 points**: `m061` still 32/35 = Candidate 3. Gates 4 and 6 fail; seven pass (containment 240/240, `xc=0`, +25 outside `m061` unchanged). **Learned: `m061`'s loss is not the long goal.** Obituary in GRAVEYARD; diff `readable/diffs/candidate-3b-stuck-holder-release.diff` on `main`. | — | — | spent | 15:58Z |

## Track T — Top-10 analytics (what the strong bots do that we don't)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| T-1 | Field comparison of the 25 strong two-troll Legend bots vs the champion (`coordination/tasks/20260826-track-t-top10-field-comparison.md`) | codex_1 (claude_1 reviewed) | **DONE — T-G1 ACCEPT 15:58Z** (three labelling edits, no number changed). `codex_1/top10/field-comparison-2026-08-26.md` on `main`: **the top banana planters run a persistent wood farm** — 3–6 banana PLANTs in turns 1–50 (ours 0.05), 21–30 own-cell HARVESTs (ours 2.85); our suppression already stronger; one unexplained gap: our endgame MOVEs 7.96 vs 32–38. | owner reads it; it reframes Track F | owner | spent | 15:58Z |
| T-2 | Per-turn commands extracted from the 6.6 GB raw replays (`coordination/tasks/20260826-track-t-per-turn-extraction.md`) | local_claude_1 (subagent on the host); codex_1 consumes + reviews | **Running** (subagent started 15:00Z) | `scripts/extract_turns.py` → `data/processed/turns.jsonl.gz` + manifest; sanity vs `games.jsonl`; ship to the VM if it fits | — | ~1 h | 15:00Z |

## Track F — Banana farm (conditional, smallest form)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| F-1 | Who ate the b100 farm? (`coordination/tasks/20260826-track-f-b100-theft-split.md`) | codex_1 (claude_1 reviewed) | **STOPPED under its dead condition 14:22Z; F-G1 ACCEPT-WITH-EDIT, edits published 14:41Z** — the corpus holds only 4 of the b100's 98 ladder games (the first batch, score still 0.0) and no per-turn detail; from the permitted checkpoint file: 98 games, mean margin +4.6, 49 losses, worst −348 — wins narrowly, loses catastrophically. **The theft-vs-own-crop split cannot be measured from what we kept**; with T-2 it becomes measurable on the 4 games only. | closed; re-ask on fresh instrumented games (0-3a/0-3) | — | spent | 14:41Z |
| F-2 | **Banana wood farm candidate** (`coordination/tasks/20260826-banana-farm-candidate.md`) | claude_1 (built + panel); codex_1 (reproduced) | **STOPPED at its first validity gate 21:55Z; REPRODUCED FAIL 22:04Z.** Containment perfect (farm-off byte-identical to the champion on 240/240 + 34/34), but **blocking games 52 → 96** (50 new, 6 cured; the dominant cause on 35 of 50 is *the opponent walking onto our ring and eating the fruit we grew*). The stop-latch fired in **0 of 240** games — it counts enemy *chops*, and the theft that happens is *harvests*: one design defect, stated twice. Local own-score +3,100 over 240 games (opposite sign to the expectation) — under a failed gate it buys nothing. Denial was a formality (509 turns vs 28,239 farming). **Nothing submitted; ladder slot 3 released.** | **owner decides in the morning:** charter a bounded repair (the latch must count harvests; the ring must not feed the enemy) or close the line ; **the whole record is now on `main`**: design `claude_1/farm/g0-farm-2026-08-26.md`, panel `claude_1/farm/g1-panel-farm-2026-08-26.md`, arms + scripts, codex_1's two reviews and its reproduction `codex_1/reviews/banana-farm-panel-reproduction-2026-08-26.md` | owner | spent | 22:04Z |

## Track 0 — Instruments (a verdict that cannot be computed is a stall in disguise)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| 0-2 | Integrate the peer branches onto `main` (`coordination/tasks/20260826-integrate-peer-branches.md`) | local_claude_1 (codex_1 verified) | **DONE** — round 1 15:35Z (304+282+36 commits), round 2 18:30Z (11+5, the 3b and T-1 artifacts); both peers rebased and verified; the one leftover — claude_1's pre-rebase pin `152743Z` — quarantined by adjudication 18:3xZ (content redelivered at `153015Z`) | standing: peers rebase; coordinator lands artifacts at each gate | — | spent | 18:35Z |
| 0-1 | 34 frozen fixtures (`coordination/tasks/20260826-fixture-drift.md`) | — | **CLOSED 14:45Z — RETIRED as gates (owner)**; successor 0-3 | — | — | spent | 14:45Z |
| 0-3a | Champion + v6 telemetry arm (`coordination/tasks/20260826-champion-instrument-v6.md`) | claude_1 (built); codex_1 (accepted); coordinator (submitted, verified) | **DONE and its open condition is DISCHARGED 02:40Z** — the platform delivers the long diagnostic line intact: **287 collected ladder games, 78,424 diagnostic lines, 242–295 characters, 0 decode failures, no truncation** (`local_claude_1/narrate/collected-payload-check-2026-08-27.json`, tool `…/collected_payload_check.py`). Previous corpus maximum was 127 characters. | — | — | spent | 02:40Z |
| 0-3 | Fixtures as a generated dataset from real instrumented games (`coordination/tasks/20260826-fresh-fixture-dataset.md`) | codex_1 (claude_1 reviews) | **startable — both data gates met and the raw-replay slice is shipped 03:25Z**: `data/raw/slice/instrument-replays-slice-2026-08-27.tar.gz` on codex_1's VM (**212 of our 287 instrument games, 9,018,967 B, sha `83789b28…` verified there**) + a manifest with per-game agent, seat, submission id, source hash, file hash and size | codex_1 writes `cut_fixtures.py` against the slice; absent classes are reported, never inferred | — | 1–2 days | 03:25Z |

## Ladder queue (single file; one bot at a time)

**Row L-1 — ladder measurement (owner "measure", 18:50Z):** the cured dancing troll (keep-your-goal, Candidate 3, with diagnostics) vs the champion (with diagnostics), A-B-B-A, 8 mature reads each, plus the annotated games of both — `coordination/tasks/20260826-ladder-measure-cured-dancing-troll.md`. A measurement, not a promotion. claude_1 builds B's file; codex_1 checks byte-identity; the coordinator runs the reads (~1.5 days of the slot).

| slot | bot | purpose | state |
|---|---|---|---|
| 1 | **champion + v6 instrument `72673124…`** — A1 `41198581`, A2 `41200776` (read 21.6 / rank 40), A3 `41201060` (02:33Z) | the baseline; its games carry telemetry, now proven to arrive intact | on the ladder |
| 2 | **B = the cured dancing troll + diagnostics** — reads 18.4, 19.2 (mean **18.8**) | A-B-B-A vs slot 1; four of sixteen reads done | **A leads: 21.8, 21.6 (mean 21.7) vs 18.8 — a 2.9-point gap, and every B read is below every A read**; A3 up |
| 3 | *(released)* the banana-farm candidate | — | **not booked**: the farm failed its own first validity gate (blocking games 52 → 96); nothing was submitted |

## Decisions (dated)

- 2026-08-26: Candidate 3 bounded (one packet, one review, one panel, one reproduction, one owner read; Candidate 2 re-run only on an own-score gain). Ladder measures again (champion restored). Goals: ≥ 25.40 **and** control over the code / cleanliness. Next item after the code clean-up: the banana farm. Board organisation adopted. — owner
- 2026-08-26: `/home/tarstars/prj/troll_farm` (the checkout new agents start in, host of the 05:17 collector cron) switched from `session-2026-07-01` to `main` — owner ("b"); cron paths verified. `coordination/WORKING-RULES.md` written and linked from every entry file. — owner
- 2026-08-26 15:20Z: owner "wifi" (2nd) — the 174 MB per-turn corpus copied to the VM. — owner
- 2026-08-26 14:45Z: (1) old fixtures RETIRED as gates; evidence base = real ladder games of the current bot with telemetry — the v6 instrument REPLACES the champion on the ladder (0-3a), fixtures become a generated dataset (0-3, codex_1 after T-1); (2) Candidate 3b chartered, bounded (A); (3) D-2's `/tmp` proof inputs let go. — owner
- 2026-08-26: 0-1 fixture drift — owner: "you can even start a subagent", "before banana farm build". Chartered; diagnosis subagent running. Owner read the Candidate 3 diff. — owner
- 2026-08-26: owner "wifi" — the 85.6 MB corpus copied to codex_1's VM worktree (hash verified); the bulk-storage check is not required for a read of a hash-verified corpus copy. — owner / coordinator
- 2026-08-26: D-3 chartered — find why `m061` keeps a goal 171 turns; a fix would be **Candidate 3b**, a new bounded candidate, not a reopening. — owner "go"
- 2026-08-26: Candidate 3 CLOSED at G-1 by the owner's bound — the panel failed its pre-committed risk gate (−65 own-score, `ka`=171). Loop cure confirmed as a mechanism (`xc=0`); no Candidate 2 re-run (no own-score gain); slot 2 released. — coordinator applying the owner's bound
- 2026-08-26: branches cleaned (owner "1. 2. do it"): dead branches deleted, archive kept as a tag, integration of peer branches chartered as 0-2 after D-1's build. — owner
- 2026-08-26: Track T goes first and fast; F starts as reads; F-2 needs T-1 + F-1 + owner go. — coordinator, under the owner's "board"

## Owner's queue (≤ 3)

0. *(decided: "measure")* Track D after Candidate 3b — the ladder measurement (row L-1) replaces both options.
0'. *(was 0)* **Track D after Candidate 3b:** two candidates agree `m061`'s −43/−47 is *not* the kept-goal age. Options: (a) charter one measurement — what those two seats actually lose points doing (a read, 1 day, claude_1) — before any new rule; (b) **close Track D** now: the loop cure is understood and the ladder never saw the cure programme; put claude_1 on Track F's design. My recommendation: **(b)**, with the `m061` question kept as a line in the graveyard.
1. **T-1 is delivered and accepted** (`codex_1/top10/field-comparison-2026-08-26.md`, review pending): the top bots run a persistent **wood farm** on early-planted bananas. This is the farm question's answer in the wrong direction from Spec B — read it before any F-2 charter.
2. *(was 1)* **T-1's first table is in** (`codex_1/top10/field-comparison-first-table-2026-08-26.md`): the top three plant 27–36 bananas a game, we plant 6. Read it; the farm question sharpened.
2. (when it lands) Candidate 3b's panel verdict — pass = ladder slot 2.
2. (when it lands) T-1's first table — read it; it decides F-2.
3. **Candidate 3's diff is on `main` now** — `readable/diffs/candidate-3-keep-your-goal.diff` (+927/−9) with the packet `claude_1/cure3/g1-packet-2026-08-26.md`: the code read you asked for, and your verdict on it as code (the code-control goal), independent of its score.
