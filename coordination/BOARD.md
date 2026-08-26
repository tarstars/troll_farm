# BOARD — the one file the owner reads (created 2026-08-26 by owner ruling "board")

**Rules: `coordination/WORKING-RULES.md`** (read first). In one breath: two rows per track; every task born with done/dead/budget; Read → Design (≤ 2 rounds) → Build → Panel (one) → Ladder (one block) → Verdict; no evidence for two days = STALLED → owner says kill or extend; dead tasks go to `GRAVEYARD.md`; mail only for handoffs and verdicts; one ladder queue; everything lands on `main` at every gate; the owner says "board" and gets the five-part report (§9).

Last updated: 2026-08-26T15:45Z (coordinator). Trunk: see `git log -1 origin/main`.

## Track D — Dancing trolls (finish Candidate 3, submit, verdict, close the line)

| # | task | owner | stage | next concrete step | blocked on | budget left | last evidence |
|---|---|---|---|---|---|---|---|
| D-1 | Candidate 3 "keep your goal" (`coordination/tasks/20260826-candidate-3-keep-your-goal.md`) | claude_1 (codex_1 reproduces) | **Verdict — CLOSING under the bound.** The one panel ran 13:20Z: the loop is cured (`xc=0` on all six loop games; blocking games 52→40; D-1 27→23) **but −65 own-score points / 240 games** (`m061` −47/−43) and a goal kept **171 turns** vs the 30-turn stop → the pre-committed §9.10 gate fires: *the absolute form is too strong*; no re-tuning (owner bound). | codex_1: the one reproduction (last allowed act); coordinator: obituary in GRAVEYARD, owner reads the diff | — | 1 reproduction, 1 owner read, then stop | 08-26 13:20Z (G-1 handoff `132000Z`; diff `readable/diffs/candidate-3-keep-your-goal.diff` +927/−9 and packet `claude_1/cure3/g1-packet-2026-08-26.md` now on `main`) |
| D-2 | Parked-troll gate reads v4/v5/v6 (`coordination/tasks/20260826-p4b-narrator-param.md`) | codex_1 (claude_1 reviewed) | **DONE 13:57Z** — integrated behind the panel API; claude_1 re-review ACCEPT (Candidate 3's v6 archive: 0 decode errors, 15 episodes; Candidate 2's v5 row reproduces) | record only: the two proof inputs live in `/tmp` on the VM (915 KB + 437 KB) — owner decision whether to keep them out-of-tree | — | spent | 08-26 13:57Z |
| D-3 | Why did a troll on `m061` keep one goal for 171 turns? (`coordination/tasks/20260826-m061-stale-goal-read.md`) | claude_1 (codex_1 reviews) | **DELIVERED 14:17Z, at gate D3-G1** — report `claude_1/cure3/m061-stale-goal-read-2026-08-26.md`: the immortal tree goal pinned the tree to one troll, the other troll got `WAIT` and stood in the corridor; the −43/−47 is the turn-100 shack engine never starting (the stranded troll is not adjacent to the shack); a turn cap would cost +39 in won games; the data's own rule (holder on ≤2 cells for 20 turns with no work command → release) fires t72/t108 and touches 4 non-winning games (+risk 0) | codex_1: one review; then the owner decides whether Candidate 3b is chartered | — | 1 review | 08-26 14:17Z |
| D-4 | **Candidate 3b** — Candidate 3 + the stuck-holder release (`coordination/tasks/20260826-candidate-3b-stuck-holder-release.md`) | claude_1 (codex_1 reproduces) | **Build** (chartered 15:45Z, owner "A") | build; pre-commitments in the card; no panel number read before D3-G1's verdict | D3-G1 (codex_1) for the panel read | 1 build, 1 panel, 1 reproduction, slot 2 only on a pass, 2 days | 15:45Z |

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
| 0-1 | 34 frozen fixtures (`coordination/tasks/20260826-fixture-drift.md`) | — | **CLOSED 15:45Z — RETIRED as gates (owner)**; successor 0-3 | — | — | spent | 15:45Z |
| 0-3a | Champion + v6 telemetry arm for the ladder (`coordination/tasks/20260826-champion-instrument-v6.md`) | claude_1 (codex_1 reviews); coordinator submits | **Build** (chartered 15:45Z) | build the arm from `ad1ae4ef` + `narrate6`; probe parity on 240 + 34; file + sha on `main`; then the coordinator submits it as the resident | — | ½ day, 1 review, 1 submission | 15:45Z |
| 0-3 | Fixtures as a generated dataset from real instrumented games (`coordination/tasks/20260826-fresh-fixture-dataset.md`) | codex_1 (claude_1 reviews) | queued — after T-1's first tables and one day of instrument games | `cut_fixtures.py`: windows of interest by class, tagged with bot hash; first library from the instrument's first day | 0-3a on the ladder; T-1 first tables | 1–2 days | 15:45Z |

## Ladder queue (single file; one bot at a time)

| slot | bot | purpose | state |
|---|---|---|---|
| 1 | champion `547fa706…` — submission `41197542` (08-26 11:38Z); **to be replaced by the champion + v6 instrument (0-3a) when its parity gate passes** | baseline reads; from the instrument on: real games with telemetry | on the ladder |
| 2 | Candidate 3b arm | 8-read block vs the resident's reads | booked **only if** D-4's panel passes its pre-commitments |
| 3 | CBF arm | same | not booked |

## Decisions (dated)

- 2026-08-26: Candidate 3 bounded (one packet, one review, one panel, one reproduction, one owner read; Candidate 2 re-run only on an own-score gain). Ladder measures again (champion restored). Goals: ≥ 25.40 **and** control over the code / cleanliness. Next item after the code clean-up: the banana farm. Board organisation adopted. — owner
- 2026-08-26: `/home/tarstars/prj/troll_farm` (the checkout new agents start in, host of the 05:17 collector cron) switched from `session-2026-07-01` to `main` — owner ("b"); cron paths verified. `coordination/WORKING-RULES.md` written and linked from every entry file. — owner
- 2026-08-26 15:45Z: (1) old fixtures RETIRED as gates; evidence base = real ladder games of the current bot with telemetry — the v6 instrument REPLACES the champion on the ladder (0-3a), fixtures become a generated dataset (0-3, codex_1 after T-1); (2) Candidate 3b chartered, bounded (A); (3) D-2's `/tmp` proof inputs let go. — owner
- 2026-08-26: 0-1 fixture drift — owner: "you can even start a subagent", "before banana farm build". Chartered; diagnosis subagent running. Owner read the Candidate 3 diff. — owner
- 2026-08-26: owner "wifi" — the 85.6 MB corpus copied to codex_1's VM worktree (hash verified); the bulk-storage check is not required for a read of a hash-verified corpus copy. — owner / coordinator
- 2026-08-26: D-3 chartered — find why `m061` keeps a goal 171 turns; a fix would be **Candidate 3b**, a new bounded candidate, not a reopening. — owner "go"
- 2026-08-26: Candidate 3 CLOSED at G-1 by the owner's bound — the panel failed its pre-committed risk gate (−65 own-score, `ka`=171). Loop cure confirmed as a mechanism (`xc=0`); no Candidate 2 re-run (no own-score gain); slot 2 released. — coordinator applying the owner's bound
- 2026-08-26: branches cleaned (owner "1. 2. do it"): dead branches deleted, archive kept as a tag, integration of peer branches chartered as 0-2 after D-1's build. — owner
- 2026-08-26: Track T goes first and fast; F starts as reads; F-2 needs T-1 + F-1 + owner go. — coordinator, under the owner's "board"

## Owner's queue (≤ 3)

1. (when it lands) T-1's first two tables.
2. (when it lands) Candidate 3b's panel verdict — pass = ladder slot 2.
2. (when it lands) T-1's first table — read it; it decides F-2.
3. **Candidate 3's diff is on `main` now** — `readable/diffs/candidate-3-keep-your-goal.diff` (+927/−9) with the packet `claude_1/cure3/g1-packet-2026-08-26.md`: the code read you asked for, and your verdict on it as code (the code-control goal), independent of its score.
