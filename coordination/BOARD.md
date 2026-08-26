# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-26T14:45Z (coordinator); rows D-1/D-2 evidence refreshed 13:38Z/13:49Z and row D-3 delivered 15:05Z (claude_1). Trunk: see `git log -1 origin/main`.

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Verdict — CLOSING under the bound.** The one panel ran 13:20Z: the loop is cured (`xc=0` on all six loop games; blocking games 52→40; D-1 27→23) **but −65 own-score points / 240 games** (`m061` −47/−43) and a goal kept **171 turns** vs the 30-turn stop → the pre-committed §9.10 gate fires: *the absolute form is too strong*; no re-tuning (owner bound). | **the reproduction has LANDED** (codex_1 `132717Z`, acked by claude_1 `133400Z`): fresh archive of `d34429cc`, every panel JSON differs in one leaf only (`wall_time_seconds`) — totals confirmed, `GATE_UNREADY / DO NOT ADVANCE`. Left: coordinator's obituary in GRAVEYARD, owner reads the diff | — | reproduction SPENT; 1 owner read, then stop | 08-26 13:34Z (G-1 handoff `132000Z`; diff `readable/diffs/candidate-3-keep-your-goal.diff` +927/−9 and packet `claude_1/cure3/g1-packet-2026-08-26.md` now on `main`) |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviews) | **Re-review SPENT — ACCEPT (claude_1 `134853Z`).** The integration landed at `agent/codex_1@cafb0204`: `p4b_gate.evaluate_rows` keeps the row-taking API `fuzz_panel` calls and takes an explicit narrator; panel gains `--p4b-dialect v4|v5|v6|none` (v4 default, `none` → `NOT_APPLICABLE` and fails closed on NARRATE). | **Coordinator's to close**: append the P4b obituary footnote drafted in claude_1 `134853Z`, then D-2 is done. Landing both branches on `main` also clears finding (a). | — | re-review SPENT (0 left) | 08-26 13:48Z — claude_1 re-review `claude_1/cure3/p4b-rereview-2026-08-26.md` @`1a9df55f`: all six claims reproduced independently (10 + 11 tests; v6 archive 240 games `READY`, **0 decode errors**, 15 episodes on 15 units; v5 both arms match `c12-idle-with-work.json`; the **172,364 → 0** headline reproduces to the digit). Three non-inertness probes pass. Recorded, non-blocking: (a) `cafb0204` cannot run its own proofs — `narrate4|5|6` and `c12-idle-with-work.json` are only on `agent/claude_1`; (b) the v6 archive is **not** tripwire-clear — `m001` seat 1 unit 0, longest run **53** vs W=60, not a P4b failure. |
| D-3 | Why did a troll on `m061` keep one goal for 171 turns, and what did it cost? — read on the Candidate 3 archives (`coordination/tasks/20260826-m061-stale-goal-read.md`) | claude_1 (codex_1 reviews) | **Read — DELIVERED 15:05Z, all five deliverables.** The goal was never released because a `Tree` goal ends only on *carry full at the tree* (one fruit a visit against a carry of 3) and *unreachable on the STATIC map* (a teammate in a one-wide corridor is not an obstacle to it); the immortal goal pins the tree to one troll and hands the other the `WAIT` candidate, stranding it in the corridor. **The cost is not the wasted turns**: the stranded troll is no longer beside its shack, so the champion's turn-100 wood engine (`is_adjacent(unit.cell, shacks[0])`, `door1-champion.rs:1789`) never starts — **+44/+47 the champion earns and the candidate does not, i.e. the whole −43/−47.** | **codex_1: gate D3-G1, one round** (handoff `150500Z`). Then the coordinator accepts or kills; a fix is a NEW candidate (3b) with its own card. | — | 0 rounds used of 1; 0 builds, 0 panels, 0 ladder spent | 08-26 15:05Z — `claude_1/cure3/m061-stale-goal-read-2026-08-26.md` + the turn tables and probes in `claude_1/cure3/m061/`. Item 4's headline: a **turn cap** reaches into 4 games the cure WINS worth **+39** (the whole win outside `m061` is +25) and 54 of the 57 long goals are choppers felling a tree; the packet's own price tag **`xd` is 0 on all 200 turns of `m061:0`** and cannot see this defect at all; a **2-cell-dance-and-no-work** release fires at t72/t108 and touches **4** non-`m061` games, **none of them winning (+risk +0)**. Item 5: 57 of 240 games hold a goal >30 turns, the two `m061` seats the only ones >100. Panel release census reproduces the G-1 packet §2.4 to the digit. |

## Track T — Top-10 analytics (what the strong bots do that we don't)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| T-1 | Field comparison of the 25 Legend agents ranked 7–54 on our exact two-worker roster vs the champion (`coordination/tasks/20260826-track-t-top10-field-comparison.md`) | codex_1 | **Read — UNBLOCKED 14:45Z** (corpus copied to the VM, sha `150a5507…`, 23,613 games; storage check waived for a hash-verified copy) | identify the 25 agents' games; **state which corpus** (STATE says 21,496 games; the collector on the host is at 23,613 as of 08-26 02:32Z — use the newest and say so); first table = score composition + planting counts by type and time | — | 2 days, 0 ladder | chartered 12:40Z |

## Track F — Banana farm (conditional, smallest form)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| F-1 | Who ate the b100 farm? theft vs own-crop split on the Aug-2 arena games (`coordination/tasks/20260826-track-f-b100-theft-split.md`) | codex_1 (after T-1's first table) | **Read** (chartered 08-26) | list the b100 games (agent `6590083`) in the corpus; per game, opponent's banked bananas from our trees vs their own | T-1's game-identification step (shared code) | 1 day, 0 ladder | corpus on the VM 14:45Z |
| F-2 | CBF design + build (three states, two one-way edges, Spec B) | claude_1, after D-1 | queued | not before T-1 + F-1 answer "worth it" **and** the owner's go | T-1, F-1, owner go | ≤ 2 design rounds, 1 panel, 1 ladder slot | — |

## Track 0 — Instruments (a verdict that cannot be computed is a stall in disguise)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| 0-2 | Integrate the peer branches onto `main` — `main` wins on shared files, quarantine re-verified, peers rebase (`coordination/tasks/20260826-integrate-peer-branches.md`) | local_claude_1 (codex_1 verifies) | queued | after D-1 reaches Panel: merge `agent/claude_1` (287 ahead) and `agent/codex_1` (262 ahead) per the card's method | D-1 at Panel | one session, one review | chartered 13:40Z; branch hygiene done (3 dead branches deleted, archive → tag, stale worktree removed, local_codex_1's transfer messages merged) |
| 0-1 | 23 of 34 frozen fixtures `NOT_REPRODUCIBLE_ON_BASE` on every arm | **unassigned — owner decision: who, and before or after F-2?** | not started | charter: re-freeze the fixtures against the current referee build or retire them with a note | owner decision | — | surfaced 08-26 |

## Ladder queue (single file; one bot at a time)

| slot | bot | purpose | state |
|---|---|---|---|
| 1 | champion `547fa706…` — submission `41197542` (08-26 11:38Z) | baseline reads for every later comparison | **on the ladder**, agent id + first read pending |
| 2 | *(released)* Candidate 3 arm | — | **not booked**: the panel failed its own pre-commitment (§9.10) |
| 3 | CBF arm | same | not booked |

## Decisions (dated)

- 2026-08-26: Candidate 3 bounded (one packet, one review, one panel, one reproduction, one owner read; Candidate 2 re-run only on an own-score gain). Ladder measures again (champion restored). Goals: ≥ 25.40 **and** control over the code / cleanliness. Next item after the code clean-up: the banana farm. Board organisation adopted. — owner
- 2026-08-26: `/home/tarstars/prj/troll_farm` (the checkout new agents start in, host of the 05:17 collector cron) switched from `session-2026-07-01` to `main` — owner ("b"); cron paths verified. `coordination/WORKING-RULES.md` written and linked from every entry file. — owner
- 2026-08-26: owner "wifi" — the 85.6 MB corpus copied to codex_1's VM worktree (hash verified); the bulk-storage check is not required for a read of a hash-verified corpus copy. — owner / coordinator
- 2026-08-26: D-3 chartered — find why `m061` keeps a goal 171 turns; a fix would be **Candidate 3b**, a new bounded candidate, not a reopening. — owner "go"
- 2026-08-26: Candidate 3 CLOSED at G-1 by the owner's bound — the panel failed its pre-committed risk gate (−65 own-score, `ka`=171). Loop cure confirmed as a mechanism (`xc=0`); no Candidate 2 re-run (no own-score gain); slot 2 released. — coordinator applying the owner's bound
- 2026-08-26: branches cleaned (owner "1. 2. do it"): dead branches deleted, archive kept as a tag, integration of peer branches chartered as 0-2 after D-1's build. — owner
- 2026-08-26: Track T goes first and fast; F starts as reads; F-2 needs T-1 + F-1 + owner go. — coordinator, under the owner's "board"

## Owner's queue (≤ 3)

1. Track 0-1: who owns the fixture drift, and does it go before F-2?
2. (when it lands) T-1's first table — read it; it decides F-2.
3. **Candidate 3's diff is on `main` now** — `readable/diffs/candidate-3-keep-your-goal.diff` (+927/−9) with the packet `claude_1/cure3/g1-packet-2026-08-26.md`: the code read you asked for, and your verdict on it as code (the code-control goal), independent of its score.
