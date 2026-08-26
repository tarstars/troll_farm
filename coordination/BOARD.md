# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-26T15:25Z (coordinator). Trunk: see `git log -1 origin/main`.

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Verdict — CLOSING under the bound.** The one panel ran 13:20Z: the loop is cured (`xc=0` on all six loop games; blocking games 52→40; D-1 27→23) **but −65 own-score points / 240 games** (`m061` −47/−43) and a goal kept **171 turns** vs the 30-turn stop → the pre-committed §9.10 gate fires: *the absolute form is too strong*; no re-tuning (owner bound). | codex_1: the one reproduction (last allowed act); coordinator: obituary in GRAVEYARD, owner reads the diff | — | 1 reproduction, 1 owner read, then stop | 08-26 13:20Z (G-1 handoff `132000Z`; diff `readable/diffs/candidate-3-keep-your-goal.diff` +927/−9 and packet `claude_1/cure3/g1-packet-2026-08-26.md` now on `main`) |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviewed) | **DONE 13:57Z** — integrated behind the panel API; claude_1 re-review ACCEPT (Candidate 3's v6 archive: 0 decode errors, 15 episodes; Candidate 2's v5 row reproduces) | record only: the two proof inputs live in `/tmp` on the VM (915 KB + 437 KB) — owner decision whether to keep them out-of-tree | — | spent | 08-26 13:57Z |
| D-3 | Why did a troll on `m061` keep one goal for 171 turns? (`coordination/tasks/20260826-m061-stale-goal-read.md`) | claude_1 (codex_1 reviews) | **DELIVERED 14:17Z, at gate D3-G1** — report `claude_1/cure3/m061-stale-goal-read-2026-08-26.md`: the immortal tree goal pinned the tree to one troll, the other troll got `WAIT` and stood in the corridor; the −43/−47 is the turn-100 shack engine never starting (the stranded troll is not adjacent to the shack); a turn cap would cost +39 in won games; the data's own rule (holder on ≤2 cells for 20 turns with no work command → release) fires t72/t108 and touches 4 non-winning games (+risk 0) | codex_1: one review; then the owner decides whether Candidate 3b is chartered | — | 1 review | 08-26 14:17Z |

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
| 0-1 | 23 of 34 frozen fixtures `NOT_REPRODUCIBLE_ON_BASE` (`coordination/tasks/20260826-fixture-drift.md`) | local_claude_1 (subagent diagnosed); execution codex_1; codex_1 reviews | **Diagnosis DONE 15:15Z** — nothing rotted: the 34 were recorded from the very-old bot `98628e98`, and "reproducible" means the champion replays that bot's exact episode; 23 fail because the champion is a different bot (first divergence before the window's end). The 34/34 *containment* checks really do cover 34; only FIXED/NOT-FIXED grading is 11. Skips are printed, not hidden. | owner decision: retire 19 (Group A; coverage = the 21 champion-lineage fixtures) + re-freeze 4 (011/025/031/034, ~2 h); then codex_1 executes | owner | execution ≤ 1 day, before F-2's panel | 08-26 15:15Z |

## Ladder queue (single file; one bot at a time)

| slot | bot | purpose | state |
|---|---|---|---|
| 1 | champion `547fa706…` — submission `41197542` (08-26 11:38Z) | baseline reads for every later comparison | **on the ladder**, agent id + first read pending |
| 2 | *(released)* Candidate 3 arm | — | **not booked**: the panel failed its own pre-commitment (§9.10) |
| 3 | CBF arm | same | not booked |

## Decisions (dated)

- 2026-08-26: Candidate 3 bounded (one packet, one review, one panel, one reproduction, one owner read; Candidate 2 re-run only on an own-score gain). Ladder measures again (champion restored). Goals: ≥ 25.40 **and** control over the code / cleanliness. Next item after the code clean-up: the banana farm. Board organisation adopted. — owner
- 2026-08-26: `/home/tarstars/prj/troll_farm` (the checkout new agents start in, host of the 05:17 collector cron) switched from `session-2026-07-01` to `main` — owner ("b"); cron paths verified. `coordination/WORKING-RULES.md` written and linked from every entry file. — owner
- 2026-08-26: 0-1 fixture drift — owner: "you can even start a subagent", "before banana farm build". Chartered; diagnosis subagent running. Owner read the Candidate 3 diff. — owner
- 2026-08-26: owner "wifi" — the 85.6 MB corpus copied to codex_1's VM worktree (hash verified); the bulk-storage check is not required for a read of a hash-verified corpus copy. — owner / coordinator
- 2026-08-26: D-3 chartered — find why `m061` keeps a goal 171 turns; a fix would be **Candidate 3b**, a new bounded candidate, not a reopening. — owner "go"
- 2026-08-26: Candidate 3 CLOSED at G-1 by the owner's bound — the panel failed its pre-committed risk gate (−65 own-score, `ka`=171). Loop cure confirmed as a mechanism (`xc=0`); no Candidate 2 re-run (no own-score gain); slot 2 released. — coordinator applying the owner's bound
- 2026-08-26: branches cleaned (owner "1. 2. do it"): dead branches deleted, archive kept as a tag, integration of peer branches chartered as 0-2 after D-1's build. — owner
- 2026-08-26: Track T goes first and fast; F starts as reads; F-2 needs T-1 + F-1 + owner go. — coordinator, under the owner's "board"

## Owner's queue (≤ 3)

1. 0-1: retire 19 + re-freeze 4 (recommended), or re-freeze all 34 on the champion (~4–6 h)?
2. D-3: charter **Candidate 3b** (Candidate 3 + the "stuck holder" release, one bounded build) — after codex_1's review, yes/no?
3. D-2's proof inputs (1.3 MB in `/tmp` on the VM): keep out-of-tree, or let them go?
2. (when it lands) T-1's first table — read it; it decides F-2.
3. **Candidate 3's diff is on `main` now** — `readable/diffs/candidate-3-keep-your-goal.diff` (+927/−9) with the packet `claude_1/cure3/g1-packet-2026-08-26.md`: the code read you asked for, and your verdict on it as code (the code-control goal), independent of its score.
