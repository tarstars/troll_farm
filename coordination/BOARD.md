# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-26T13:40Z (coordinator). Trunk: see `git log -1 origin/main`.

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" — build + panel + diff on `main` (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Build** (G-0 r6 ACCEPT-WITH-EDIT 12:20Z) | apply the one-line edit (five v5 fields into the distribution list); refresh `readable/door1-champion.rs` to `main` (2,210 lines); build the three arms; run the one panel | G-1 *verdict* waits on D-2 (the parked-troll gate) | 1 panel, 1 reproduction, 1 owner read, ladder slot 2 — **then stop** (owner bound 08-26) | 08-26 12:26Z |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviews) | Build (G-1 BLOCK 11:36Z: unpack outside `try`) | index instead of destructure in `evaluate()`; test through `evaluate()`; fix the empty-`all()` exit 0; one re-review | — | 1 re-review | 08-26 12:23Z |

## Track T — Top-10 analytics (what the strong bots do that we don't)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| T-1 | Field comparison of the 25 Legend agents ranked 7–54 on our exact two-worker roster vs the champion (`coordination/tasks/20260826-track-t-top10-field-comparison.md`) | codex_1 | **Read** (chartered 08-26) | identify the 25 agents' games; **state which corpus** (STATE says 21,496 games; the collector on the host is at 23,613 as of 08-26 02:32Z — use the newest and say so); first table = score composition + planting counts by type and time | — | 2 days, 0 ladder | chartered 12:40Z |

## Track F — Banana farm (conditional, smallest form)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| F-1 | Who ate the b100 farm? theft vs own-crop split on the Aug-2 arena games (`coordination/tasks/20260826-track-f-b100-theft-split.md`) | codex_1 (after T-1's first table) | **Read** (chartered 08-26) | list the b100 games (agent `6590083`) in the corpus; per game, opponent's banked bananas from our trees vs their own | T-1's game-identification step (shared code) | 1 day, 0 ladder | chartered 12:40Z |
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
| 2 | Candidate 3 arm | 8-read self-replacement block vs slot 1's reads | booked **only if** D-1's panel passes its pre-commitments |
| 3 | CBF arm | same | not booked |

## Decisions (dated)

- 2026-08-26: Candidate 3 bounded (one packet, one review, one panel, one reproduction, one owner read; Candidate 2 re-run only on an own-score gain). Ladder measures again (champion restored). Goals: ≥ 25.40 **and** control over the code / cleanliness. Next item after the code clean-up: the banana farm. Board organisation adopted. — owner
- 2026-08-26: `/home/tarstars/prj/troll_farm` (the checkout new agents start in, host of the 05:17 collector cron) switched from `session-2026-07-01` to `main` — owner ("b"); cron paths verified. `coordination/WORKING-RULES.md` written and linked from every entry file. — owner
- 2026-08-26: branches cleaned (owner "1. 2. do it"): dead branches deleted, archive kept as a tag, integration of peer branches chartered as 0-2 after D-1's build. — owner
- 2026-08-26: Track T goes first and fast; F starts as reads; F-2 needs T-1 + F-1 + owner go. — coordinator, under the owner's "board"

## Owner's queue (≤ 3)

1. Track 0-1: who owns the fixture drift, and does it go before F-2?
2. (when it lands) T-1's first table — read it; it decides F-2.
3. (when it lands) D-1's diff `readable/diffs/candidate-3-keep-your-goal.diff` — the read you asked for.
