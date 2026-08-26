# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-26T15:40Z (goal wake 1, cont.)

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Verdict — CLOSING under the bound.** The one panel ran 13:20Z: the loop is cured (`xc=0` on all six loop games; blocking games 52→40; D-1 27→23) **but −65 own-score points / 240 games** (`m061` −47/−43) and a goal kept **171 turns** vs the 30-turn stop → the pre-committed §9.10 gate fires: *the absolute form is too strong*; no re-tuning (owner bound). | codex_1: the one reproduction (last allowed act); coordinator: obituary in GRAVEYARD, owner reads the diff | — | 1 reproduction, 1 owner read, then stop | 08-26 13:20Z (G-1 handoff `132000Z`; diff `readable/diffs/candidate-3-keep-your-goal.diff` +927/−9 and packet `claude_1/cure3/g1-packet-2026-08-26.md` now on `main`) |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviewed) | **DONE 13:57Z** — integrated behind the panel API; claude_1 re-review ACCEPT (Candidate 3's v6 archive: 0 decode errors, 15 episodes; Candidate 2's v5 row reproduces) | record only: the two proof inputs live in `/tmp` on the VM (915 KB + 437 KB) — owner decision whether to keep them out-of-tree | — | spent | 08-26 13:57Z |
| D-3 | Why did a troll on `m061` keep one goal for 171 turns? (`coordination/tasks/20260826-m061-stale-goal-read.md`) | claude_1 (codex_1 reviewed) | **CLOSED — ACCEPTED 15:08Z** (codex_1's re-run of `idleprobe.py` byte-identical) | — | — | spent | 15:08Z |
| D-4 | **Candidate 3b** — Candidate 3 + the stuck-holder release (`coordination/tasks/20260826-candidate-3b-stuck-holder-release.md`) | claude_1 (codex_1 reproduces) | **Verdict — FAIL 15:27Z, CLOSING under the card's dead condition.** Built, panelled and read against the nine pre-commitments written into the card at 15:16Z before any source existed. Rule iii fires **twice in 240 games**, at `m061:0` t73 and `m061:1` t109 — exactly D-3's predicted t72/t108 — and cures the goal (`ka` 171/170 → **43/78**), but **recovers 0 of the 44/47 points**: `m061` scores 32/35, identical to Candidate 3, still −43/−47 vs the champion. **Gate 4 fails** (within 10 of champion) and **gate 6 fails** (`ka` max < 60, measured 88 on `m068:1`, a game the rule correctly does not touch — that pre-commitment was mis-specified). Seven gates pass, two of them stronger than Candidate 3's: containment **byte-identical on all 240 panel games at command level** + 34/34 fixtures, `xc=0` on all six loop games, +25 outside `m061` preserved, no Candidate 3 win lost, determinism 0/240, every changed game named. The rule is free — 238/240 games are byte-for-byte Candidate 3. Wire is v7 (`rs=`); `narrate6.py` byte-unchanged so 0-3a's ladder arm keeps its decoder. | codex_1: the one reproduction (last allowed act); then GRAVEYARD with `claude_1/cure3b/g1-packet-3b-2026-08-26.md` as the obituary | — | 1 reproduction left; build + panel + determinism re-run spent; **slot 2 released** | 08-26 15:27Z (handoff `152743Z`; packet, diff `readable/diffs/candidate-3b-stuck-holder-release.diff` +80/−3, `results/panel-read3b.json`) |

## Track T — Top-10 analytics (what the strong bots do that we don't)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| T-1 | Field comparison of the 25 strong two-troll Legend bots vs the champion (`coordination/tasks/20260826-track-t-top10-field-comparison.md`) | codex_1 (claude_1 reviews, one round) | **T-G1 ACCEPT-WITH-EDIT 15:33Z (claude_1) — the one review round is spent.** Every table cell reproduces from the pinned JSON (`ce6b58bb`); three labelling edits, no number and no conclusion changed: §1's *successful* plants and §3's *issued* PLANT commands share one header (and agree to 2 dp for all four heavy planters — a free cross-validation), the JSON's `corpus.rows` 4,476,062 is the measured seat-turns (33.6 % coverage), not the corpus, and §5's own table shows our last-30 `MOVE` at **7.96** against the leaders' 32–38, unread in its prose. Review `claude_1/reviews/track-t-field-comparison-review-2026-08-26.md`. **DELIVERED 15:15Z** — `codex_1/top10/field-comparison-2026-08-26.md`: **the top banana planters (yaichi, Stounate, skotz, goq) run a persistent wood farm** — 3.2–5.9 banana PLANTs/game in turns 1–50 (ours 0.05), 21–30 HARVESTs at own-planted cells (ours 2.85); our suppression is already stronger (8.7 CHOPs at opponent-planted cells vs 0.5–2.5). Boundary: commands issued, not referee-accepted. | claude_1: one review round | claude_1 | spent | 15:15Z |
| T-2 | Per-turn commands extracted from the 6.6 GB raw replays (`coordination/tasks/20260826-track-t-per-turn-extraction.md`) | local_claude_1 (subagent on the host); codex_1 consumes + reviews | **Running** (subagent started 15:00Z) | `scripts/extract_turns.py` → `data/processed/turns.jsonl.gz` + manifest; sanity vs `games.jsonl`; ship to the VM if it fits | — | ~1 h | 15:00Z |

## Track F — Banana farm (conditional, smallest form)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| F-1 | Who ate the b100 farm? (`coordination/tasks/20260826-track-f-b100-theft-split.md`) | codex_1 (claude_1 reviewed) | **STOPPED under its dead condition 14:22Z; F-G1 ACCEPT-WITH-EDIT, edits published 14:41Z** — the corpus holds only 4 of the b100's 98 ladder games (the first batch, score still 0.0) and no per-turn detail; from the permitted checkpoint file: 98 games, mean margin +4.6, 49 losses, worst −348 — wins narrowly, loses catastrophically. **The theft-vs-own-crop split cannot be measured from what we kept**; with T-2 it becomes measurable on the 4 games only. | closed; re-ask on fresh instrumented games (0-3a/0-3) | — | spent | 14:41Z |
| F-2 | CBF design + build (three states, two one-way edges, Spec B) | claude_1, after D-1 | queued | not before T-1 + F-1 answer "worth it" **and** the owner's go | T-1, F-1, owner go | ≤ 2 design rounds, 1 panel, 1 ladder slot | — |

## Track 0 — Instruments (a verdict that cannot be computed is a stall in disguise)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| 0-2 | Integrate the peer branches onto `main` (`coordination/tasks/20260826-integrate-peer-branches.md`) | local_claude_1 (codex_1 verifies) | **DONE 15:35Z** — `agent/claude_1` (304), `agent/codex_1` (282), `agent/chatgpt_1` (36) merged; `main` won on every shared path (one BOARD conflict, `docs/sentinel.md` change not taken — claude_1 may resubmit it as a diff); `claude_1/pipeline` = codex_1's accepted gate; champion readable `ad1ae4ef` 2,210 lines; quarantine + delivery errors 0; all three peers 0 ahead. Peers told to **rebase** (not merge). | codex_1: one verification (sweep clean on its side after rebase) | — | spent | 15:35Z |
| 0-1 | 34 frozen fixtures (`coordination/tasks/20260826-fixture-drift.md`) | — | **CLOSED 14:45Z — RETIRED as gates (owner)**; successor 0-3 | — | — | spent | 14:45Z |
| 0-3a | Champion + v6 telemetry arm (`coordination/tasks/20260826-champion-instrument-v6.md`) | claude_1 (codex_1 ACCEPT 15:06Z); coordinator submitted | **DONE — ON THE LADDER 15:10Z, submission `41198581`** (sha `72673124…`, 63,962 B; parity 240/240 command streams + 34/34 fixtures, 0 decode errors). Condition from codex_1: the 328-char payload exceeds anything collected so far (127) — **decode the first collected ladder game before treating telemetry as evidence** | first collected game (08-27 02:17Z snapshot) → decode check | — | spent | 15:10Z |
| 0-3 | Fixtures as a generated dataset from real instrumented games (`coordination/tasks/20260826-fresh-fixture-dataset.md`) | codex_1 (claude_1 reviews) | queued — after T-1's first tables and one day of instrument games | `cut_fixtures.py`: windows of interest by class, tagged with bot hash; first library from the instrument's first day | 0-3a on the ladder; T-1 first tables | 1–2 days | 14:45Z |

## Ladder queue (single file; one bot at a time)

| slot | bot | purpose | state |
|---|---|---|---|
| 1 | **champion + v6 instrument `72673124…` — submission `41198581` (08-26 15:10Z)**; replaces the bare champion `41197542` (11:38Z, never read) | the resident; identical in play to `547fa706`; its reads ARE the champion's baseline; its games carry telemetry | on the ladder; first read + first telemetry decode at the 08-27 02:17Z snapshot |
| 2 | Candidate 3b arm | 8-read block vs the resident's reads | booked **only if** D-4's panel passes its pre-commitments |
| 3 | CBF arm | same | not booked |

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

1. **T-1 is delivered** (`codex_1/top10/field-comparison-2026-08-26.md`, review pending): the top bots run a persistent **wood farm** on early-planted bananas. This is the farm question's answer in the wrong direction from Spec B — read it before any F-2 charter.
2. *(was 1)* **T-1's first table is in** (`codex_1/top10/field-comparison-first-table-2026-08-26.md`): the top three plant 27–36 bananas a game, we plant 6. Read it; the farm question sharpened.
2. (when it lands) Candidate 3b's panel verdict — pass = ladder slot 2.
2. (when it lands) T-1's first table — read it; it decides F-2.
3. **Candidate 3's diff is on `main` now** — `readable/diffs/candidate-3-keep-your-goal.diff` (+927/−9) with the packet `claude_1/cure3/g1-packet-2026-08-26.md`: the code read you asked for, and your verdict on it as code (the code-control goal), independent of its score.
