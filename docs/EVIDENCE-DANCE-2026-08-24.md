# EVIDENCE — the troll dance, everything measured, 2026-07-10 → 2026-08-24

Compiled 2026-08-24 by `local_claude_1` at the owner's request ("write down all evidences we
collected"). Every number carries its source; nothing here is new measurement. Plain words, every
code explained where it first appears. Where the record later withdrew a claim, the withdrawal is
recorded beside it — this file is the evidence, not the verdicts.

## 0. Definitions used throughout

- **Dance / oscillation / D-1** — one of our trolls alternating between two cells (a, b, a, b, …)
  for at least 7 turns (`k ≥ 3`) with **zero progress events** for that troll inside the window:
  no change of what it carries, no inventory change on a turn it dropped or picked, no plant
  created or removed on its cell. Own units only. Detector:
  `claude_1/banana-restoration-r2/trace_detectors.py:555-621`.
- **Blocking / contention / D-3** — two of our own trolls wanting the same cell (two MOVEs to one
  destination on consecutive turns, or a landing on a stationary working teammate's cell).
- **P4 stall** — no progress for our side in a rolling 60-turn window (`claude_1/pipeline/fuzz_panel.py:33-44`);
  a different pathology from the dance, often co-occurring.
- **Terminal dance** — an episode of ≥ 62 turns; on fixtures these mostly never resolved.
- **Caveat on every replay-measured count:** the replay reader reconstructs plant clocks it cannot
  observe; the error direction *invents* dances. **D-1 off replays is an upper bound**, applied
  identically to every bot and cohort (`claude_1/adapter1/replay-to-trace-adapter-2026-08-23.md` §6).
- Bots named below: **very-old** `98628e98…` (readable, no orchard; the fixture library's subject);
  **cure C** `ad3bfefe…`; **door 1 / champion** `547fa706…` (cure C minus a "fictional decay" hunk —
  a pure deletion); **instrument** = door 1 + swap rule R-1 + per-turn `MSG` telemetry (v2
  `aaebc503…`, v3 `9a3e8758…`); **July pre-cure** `v1.2.2-farmcap` `1a55319e…` (agent 6536563).

## 1. First sighting and the Legend-era quantification (July)

1. Owner's own observation, 2026-07-10 (Silver era): both trolls flapping on a water-constrained
   ring, 17 and 21 cell-revisits within 3 turns. `docs/archive/bronze-to-gold/silver-experiment-log.md:2704-2725`.
2. A Gold-era lineage carried an anti-stall watchdog (per-troll position memory, sidestep after 2
   stuck turns) and camp-cell claiming; the current resident has neither. `rust/src/botmain/motion.rs:3,12-13,112`.
3. **H13 (Legend corpus):** we oscillate in **40 of 220 games (18.2 %), worst 133 turns**; yamo, the
   published bot our resident reproduces, in **4 of 140 (2.9 %), worst 6**. Our own engineered
   move-conflict tie-break (no cross-turn memory) made it worse. `docs/CONSTRAINTS.md:981-990`.
4. Root cause pinned: the memoryless detour tie-break in `resolve_move_conflicts_with_priority_and_forbidden`
   (`yamo_orchard_live.rs:1505-19`) plus a coverage gap in `force_unique_door_clear`. `docs/BACKLOG.md:753-755`.
5. **D171a** (hard-forbid breaker): long runs −45.7 % against an 80 % floor, **+117 % displacement into
   short runs**, de-novo oscillations in 72 clean tasks — the fix manufactured what it fought.
   `docs/CONSTRAINTS.md:459-466`.
6. **D176a** (bounded-arming preference breaker, 2026-07-29): ≥10-turn task rate **8.50 % → 2.88 %**,
   zero de-novo, all six value gates pass — worth **+0.045 margin, CI [−0.024, +0.114] ≈ 0.005
   rating** on a 2,048-task paired panel. Closed on value: "does not justify a promotion cycle".
   Two of its four mechanism gates were mis-specified. `docs/CONSTRAINTS.md:1003-1008,1054-1061`,
   `docs/evidence/records/D176a.md:14-45`. Reopened 08-09/08-15 on control/understanding grounds.

## 2. The fixture library (August, subject = very-old bot, synthetic stress maps)

7. **34 frozen situations / 46 episodes = 38 D-1 + 8 P4-only.** Mechanism labels (inferred from
   transcripts): **M1 corridor block 11, M2 idle occupier invisible to planning 14, M3 goal cycle
   1, unclassified 8.** Blocker state: IDLE 17 / WORKING 8 / NONE 9. D-1 length min 7 / median 74 /
   max 195; 20 episodes ≥ 62. Maps: `choke_corridor` 12, `orchard_eligible` 6, `single_door_tent`
   4, … — harvested from the fuzz-panel floor, **not ladder games**.
   `claude_1/banana-restoration-r2/oscillation-library-98628e98/README.md:7-15`;
   `…/oscillation-library-subject-correction-2026-08-11.md:180-205,388-400`.
8. **Every terminal (≥ 62-turn) episode has an IDLE blocker** (20 of 20); with a working blocker or
   no blocker, none reaches 62 turns. Wait fractions 0.98–1.00. `…subject-correction-2026-08-11.md:270-300`.
9. M2's mechanism as read from the code: a standing troll's `WAIT` carries `Target::None`, which the
   pair-compatibility check treats as compatible with anything, so the standing troll is a physical
   obstacle planning cannot see. `build_oscillation_library.py:241-282`.
10. **−13.6 below par:** terminal-oscillation games mean margin +1.58 (n=19) vs +16.74 (n=208), map-class
    controlled gap −13.6 (choke_corridor −24.7 … open_field −0.2). `docs/PROGRAMME-banana-farm-2026-08-15.md:82-84`.

## 3. Owner adjudications and the named mechanisms (08-16 → 08-21)

11. **OSC-001** (195 turns pacing (6,2)↔(5,2), peer idle at (4,2), wait fraction 1.00): owner ruled
    the fault at the **transport level** — "the two-troll movement coordinator is broken"; ideal
    resolution a coordinated swap. → **Rule R-1**: the transport must detect and execute swaps; the
    referee allows own-unit circular swaps (`docs/mechanics.md:54-56`), our bot never generates them.
    `local_claude_1/adjudications/OSC-001-ruling-2026-08-16.md`; `docs/RULES-LEDGER.md:7-18`.
12. **4a sitting (08-20):** in 24 of 34 cases the team picker benched a troll with real work
    (GOAL_SPLIT). Owner ruled BUG on 194-, 187-, 94- and 12-turn cases → **Rule R-2**: a troll with
    available work must be employed, no materiality boundary. `local_claude_1/session-inputs/4a-sitting-package-2026-08-19.md`; `docs/RULES-LEDGER.md:20-39`.
13. **4b buckets (08-21):** OSC-005/027 — pass blocked by a *working* teammate in a one-wide corridor
    (swap shape); OSC-010 — open-map pass blocked, a zero-cost detour ignored; OSC-030 — same tree
    wanted while the teammate works it, a free tree two cells away; OSC-026 — a lone troll flips
    between two near-tied jobs 9 turns; OSC-012 — a troll with **no chop or harvest power** parked on
    the only tree **193 turns** while the able troll dances in front of it. All BUG, none fixed on
    the champion, no cure chartered. Coordinator's own "harmless" stamps withdrawn: they had judged
    the blocker, not the dancer. `local_claude_1/adjudications/4b-bucket-B-ruling-2026-08-21.md`, `4b-buckets-D-E-ruling-2026-08-21.md`.
14. **Rule fact supplied by the owner:** enemy trolls never block ours; two of our own units cannot
    share a cell but may swap in one turn. Every recorded jam is two of our own trolls. `4b-bucket-B-ruling:26-28`.
15. **OSC-031:** 315 of 315 chop-planner tree evaluations over 167 turns rejected every tree via a
    "fictional decay" inference (`DAMAGED_FLAT1`, past damage read as ongoing chopping). Owner:
    defect. Cured by deleting the inference = **door 1 = the champion**. The benching in that case
    still fires. `local_claude_1/adjudications/OSC-031-ruling-2026-08-18.md`.
16. **OSC-032/033:** map bare from turn 82/13; our own troll felled the last fruiting tree with seeds
    in the shack; the lone troll barred from replanting by the bot's `own units ≥ 2` rule; second
    troll unaffordable from turn 1 (map lacked a fruit kind — owner's "denial" refuted, "absent"
    confirmed). Ruled UNPLAYABLE, then **narrowed**: those numbers are the champion's replay; the
    recorded stalls were real on the very-old bot. `local_claude_1/adjudications/OSC-032-033-ruling-2026-08-21.md`.
17. **Final tally of the 34:** 8 "FIXED on the champion" · 18 BUG benching class (cure on the shelf)
    · 6 BUG ruled at 4b · 2 unplayable/not reproducible. **Zero harmless.** Then the identity gate:
    the champion's replay reproduces only **11 of 34** recorded episodes and **all 8 "FIXED" are among
    the 23 it does not reproduce** — those verdicts are unproven. `coordination/tasks/20260821-episode-identity-regrade.md`.
18. **"Two correct doors make a wall":** resident `:1189` (empty chop list → endgame generator) +
    `:1418` (harvest only behind true endgame) ⇒ **325 proven parked turns beside ripe fruit** (032
    110, 033 143, 028 51, 008 7); a second gate (`OPPONENT_SITTING_ON_PLANT`) declined 28 harvests.
    `docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`; `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md`.

## 4. The parked troll and the margin (08-16/17)

19. Reframe (owner-approved 08-16): the dance is the symptom, the **parked troll** is the disease
    (150+ idle turns = half the workforce on fixtures). The proposed cause "stuck regeneration
    commitment" was **refuted** (`commitMid = 0` everywhere); the first audit's numbers were measured
    in a world where plants never grew (missing `referee.grow()`) and were withdrawn.
    `coordination/tasks/20260816-h-starve-1-standing-troll-audit.md:81-113`.
20. **Cause table, final (pool #3, 34 situations, non-exclusive):** `GOAL_SPLIT_WRONG` 24 ·
    `NO_GOAL_ASSIGNED` 8 · `CANNOT_USE_WORK` 2 · `WORLD_INTERACTION` 0; status PARKED 29 /
    NOT_STARVED 4; idle turns 2,240 / 521 / 349 / 0. `coordination/messages/claude_1/20260817T175500Z-…-pool3-incidence-revision-handoff.md`.
21. **Margin decomposition (pool #4, 240-game panel, par 17.40):** clean +2.50 (n=197) · dance-only
    −9.58 (16) · stall-only −5.02 (8) · dance+stall −15.71 (19). Map-blocked exact sign test: **stall
    vs no-stall −24.29 per pair, p = 1.5e-5 (n=17 pairs) — survives**; **dance-only vs clean −7.07,
    p = 0.134 (n=14) — not established.** "Dance is a marker" withdrawn to hypothesis. If all 27
    stall games scored at par the corpus mean would rise ≈ 1.41 — a scenario with two unresolved
    IFs (causal direction, fixability). `local_claude_1/pool4/margin-decomposition-2026-08-17.md`.

## 5. Cures and what the ladder said (08-17 → 08-23)

22. **Cure C** (a chopless mid-game troll gets an explicit harvest → bank → WAIT chain instead of the
    endgame generator): 325 of 521 fixture idle turns cured; panel blocking 119 → 58; on the
    all-34 grader 3 FIXED. Arena night 08-18: 5 of 5 pairs, mean **+1.02** → owner KEEP 08-19.
    Re-paired the other way: +0.43; drift-cancelled **+0.72, below the 1.0 floor** that carried the
    KEEP. `coordination/tasks/20260817-cure-c-implementation.md`; `local_claude_1/cure-c-night-2026-08-18.md`; `docs/DISCUSSION-architecture-over-score-2026-08-22.md:114-129`.
23. **Door 1** (delete the fictional decay): panel blocking 53 → 47, 15 healed vs 9 de-novo; 8/34
    FIXED (see 17). Arena session 2: pairs [1.9, −0.6, 0.4, 1.1, −1.7], mean **+0.220, IMMATERIAL**;
    owner KEEP 08-21 — at equal score the smaller program wins. **Champion.** `local_claude_1/door1-night-2026-08-20.md`.
24. **Swap R-1 (α):** rev 1 **manufactured dances** — 27 fires, 98 re-swaps in one game, the displaced
    troll resumed in 25–29 ticks not 2; rev 2 (fire only when the partner WAITs): panel dances 27 →
    9, re-swaps 111 → 13, blocked at G-1 on the residual 13; the narrowing dropped the chop/harvest
    displacement path (half of R-1). Never graded on the ladder as a candidate. **Retired 08-23**:
    its target (blocking) is 0 in 469 real games. `coordination/tasks/20260821-swap-r1-cure.md`; `docs/DISCUSSION-…:44-100`.
25. **Anti-benching P1+P2** (refuse self-impossible pairs; break ties toward fewer WAITs): benched
    turns → 0 on every fixture, but FIXED moved only 3 → 4 (cure-C base) and 8 → 8 (door 1): the
    detector went quiet **without progress**. Plus an orchard-inertness regression. `BLOCKED AS
    QUALIFIED CURES`; owner: revise. **r2:** blocking games **35 → 115**, 80 de-novo, 0 healed, 5 new
    P3, 73 new P4 → rejected; `chatgpt_1`: result valid, causal claim unproven (the P4 labels use
    later trajectory information). `coordination/tasks/20260820-pair-selector-anti-benching.md`; `…20260823-anti-benching-result-strategy-rereview.md`.
26. **Two generations vs the very-old bot, ten pairs (08-22):** block 1 +0.54, block 2 −0.20,
    pooled **+0.17, re-paired −0.16, drift-cancelled +0.00**, against a composed estimate of +1.24.
    "We have been measuring cures by the alarm going quiet." `local_claude_1/door1-vs-old-pooled-verdict-2026-08-22.md`.
27. **PEEK** (let a troll see the standing teammate's target): fires **0 times in 34 fixtures** — of 989
    partner encounters, 960 declined because a waiting troll carries `Target::None`, 29 because the
    working troll's target is its own cell. Intention measurement over **2,605 benched turns: 2,245
    had a real want** (score preference 1,435; tie order 810; no work offered 360) — **2,010 wanted to
    stay and work in place, 235 the partner's square (withdrawn as contention evidence: no wrong-
    pairing control), 0 a different square.** Displacement would refuse, not fire wisely.
    `coordination/tasks/20260822-peek-planner-target-map.md:99-138`; `docs/STATE.md`.
28. Root named by the 08-22 discussion: our two trolls are planned independently and every
    collision is repaired afterwards by a layer that cannot see what the other troll intends; an
    acceptance rule counting episodes without a progress term can be satisfied by silencing
    detectors. `docs/DISCUSSION-architecture-over-score-2026-08-22.md:160-205`.

## 6. Real games I — NARRATE, 469 ladder games (08-23)

29. Bot rebuilt to print each troll's intention every turn (`MSG`, v2 chosen target; v3 also the
    best candidate the picker discarded). 149 + 160 + 160 games, three agent ids, no overlap.
30. **Blocking (D-3): 0 % of our games** — opponents in the same games **23 %**, our pre-cure lineage
    **43 %** at two trolls; the detector fires 206 times on 240 in-repo pairs (control).
    `coordination/messages/local_claude_1/20260823T105300Z-…-handoff.md`; swap chain retired `…20260823T131600Z…`.
31. **Dancing: 22 episodes in 17 of 149 games (11.4 %)**, replicated on batch 2 (24 in 18 of 160).
32. **Idleness (v3, 160 games): a troll given nothing while its own best candidate was real work on
    615 of 84,928 troll-turns (0.72 %)**, present in 96 of 160 games, absent in 64, worst game 51,
    median 1, wanted a tree 505 / bank 108 / cell 2. v2 join: 109 of 76,305 rows (0.14 %) wanted
    and silent; 54 of 54 adjudicable intention/command divergences were post-selection rewrites (45
    rewritten to WAIT, 9 manufactured by the swap). `local_claude_1/narrate/v3-discarded-want-2026-08-23.json`; `coordination/messages/claude_1/20260823T112215Z-…-idleness-handoff.md`.

## 7. Real games II — the lineage (08-24, `local_claude_1/dance-lineage/`)

33. Same detector, unmodified, over 11,342 (game, seat) traces / 3.07 M turns from the corpus on
    `project_host`; 46 agent ids pinned to a source hash by written record; four controls PASS
    (identity 22/17/0/0 exact; detector-alive 580 pairs → D-1 77 / D-2 90 / D-3 1,565 — the
    08-23 "240 pairs" figure was the first 240 rows of this sweep; 15 refusals of 11,357 listed;
    byte-identical across worker counts).

| bot, two trolls | games | dance games | rate | D-3 |
|---|---:|---:|---:|---:|
| July pre-cure | 51 | 0 | **0.0 %** | 43 % of games |
| very-old | 1,808 | 314 | 17.4 % | 0 |
| cure C | 1,098 | 185 | 16.9 % | 0 |
| **champion** | 1,821 | 306 | **16.8 %** | 0 |
| instrument | 446 | 65 | 14.6 % | 0 |
| opponents, same games | — | — | 9.9–12.9 % | 14–15 % |

34. Same-ladder alternating slots: cure C vs very-old −0.5 pts (p 0.81); door 1 vs cure C +0.9
    (p 0.71); **door 1 vs very-old +0.00 over 2,268 games**. Every recent bot vs July: p ≈ 0.001–0.004.
    The dance appears at no step of the recent lineage; it was present three generations back. The
    swap rule is not its origin.

## 8. Real games III — what the dancing troll was doing (08-24, `claude_1/dance1/`)

35. Definitions fixed before counting (three revisions, accepted by `codex_1`); execution reproduced
    byte-identically from a fresh archive; controls K0–K5 fired. 469 instrument games → **80
    episodes** (batches 22 / 24 / 34; 11.4 / 11.3 / 18.8 % of games); 306 champion games → **382**.

| what was beside the dance | instrument (80) | champion (382) |
|---|---:|---:|
| a teammate on one cell, orthogonally adjacent, **working** (wait fraction ≤ 5 %, exactly 0 in 29 of 34) | 34 (42.5 %) | 146 (38.2 %) |
| a teammate on one cell, adjacent, **idle** (the library's M2/M1-idle shape) | **0** | 16 (4.2 %) |
| a teammate alive, none qualifying as a blocker | 46 (57.5 %) | 214 (56.0 %) |
| no teammate alive | 0 | 6 (1.6 %) |

36. Of the 34 working blockers: 24 stand on a live plant at entry; **10 never leave that cell for the
    rest of the game**; at the minimum window (k = 3) every blocker later moves freely (7–40 cells),
    at k > 3 10 of 23 never move again. 34 of 80 and 159 of 382 episodes are the minimum 7-turn window.
37. The 46 no-blocker instrument episodes: **22 `FIXED_TARGET`** (one stated target all window, still
    bouncing), **21 `UNCLASSIFIED`** = target CHANGING (36 `MIXED` windows overall; 31 name ≥ 2 distinct
    real targets, 30 contain no `NONE` turn; the tidy period-2..4 `GOAL_FLIP` occurs **0** times),
    **3 `POSITIONAL_EXCHANGE`** (the two trolls traded cells). **`NO_TARGET` = 0 of 80.** On v3, the
    picker overruled a real want on exactly 2 window turns across 34 episodes.
38. How dances end — instrument: dancer makes progress 52, the parked teammate moves 16, game ends 9,
    a cell-swap 3; champion: 218 / 75 / 79 / 10. Late-appearing peers: 0. Blocker died mid-window: 0.
39. **Swap-tick control:** positive 9 of 9; negative side **fired 3,256 times in 132 of 141 pre-cure
    game × seat pairs** (49 % with both units commanding a MOVE into each other) — so the class is
    named descriptively and the ledger's "the resident never generates swaps" is unverified for the
    July lineage. 11 of 80 and 23 of 382 episodes contain a dancer swap tick.
40. Cross-corpus agreement on the mechanism layer (no telemetry on either side): working blocker
    42.5 % vs 38.2 %; no blocker 57.5 % vs 56.0 %; idle blocker 0 % vs 4.2 %.

## 9. Withdrawn or refuted along the way (do not re-derive)

- "An aggressive opponent dissolves the parked-peer precondition" — mooted (blocking 0/469).
- "A waiting troll has nothing to do, so displace it" — refuted (2,010 of 2,245 wanted to stay and work).
- H-starve-1's stuck-commitment cause; the first audit's numbers (frozen world); the plurality-vote
  cause table; "dance is a marker" (p = 0.134); the four "harmless" stamps (wrong unit judged);
  "none of the recorded idle turns exist" (crossed two games); the 8 "FIXED on the champion" (not
  reproduced); the "235 wanted the partner's square" contention reading (no control); the 08-23
  "240 pairs" control scope; **"the surviving dance is swap-induced" (this session: champion has no
  swap rule, same rate); "the real-game blocker is idle" (0 of 80)**.

## 10. Open questions the evidence leaves

1. Is a teammate working the plant it stands on, indefinitely, beside the dance, acceptable play or
   a defect? (four episodes in ten)
2. Why does a troll bounce with **no teammate in the way** — 22 with a fixed target, 21 with a
   changing one? Nothing is measured about the resolver's per-turn choice in those windows.
3. Are the 7-turn windows the same object as the long ones? (the blocker's later mobility differs)
4. Which of the swap-tick readings is right — predicate too broad, or the July bot swapped?
5. Why do we dance more than our opponents (≈17 % vs ≈10–13 %) while blocking less (0 % vs 14–23 %)?
   The July bot had the opposite profile (0 % dance, 43 % blocking) — did the contention fix create
   the dance? (confounded)
6. The dance-only cost (p = 0.134) and the causal direction of the stall association remain open.

## 11. Sources (all pinned on `origin/main` unless noted)

`docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, `docs/evidence/records/D176a.md`, `docs/RULES-LEDGER.md`,
`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md`,
`docs/DISCUSSION-architecture-over-score-2026-08-22.md`, `docs/PROGRAMME-banana-farm-2026-08-15.md`;
`local_claude_1/adjudications/*.md`, `local_claude_1/pool4/`, `local_claude_1/session-inputs/4a-*`,
`local_claude_1/narrate/`, `local_claude_1/dance-lineage/` (`@6595935e`, package `@4b9bd563`),
`local_claude_1/dance-attribution-owner-brief-2026-08-24.md`; `claude_1/banana-restoration-r2/`
(detectors, library builder, frozen library `oscillation-library-98628e98/`), `claude_1/hstarve1/`,
`claude_1/adapter1/`, `claude_1/narrate1..3/` (on `agent/claude_1`), `claude_1/dance1/`
(`agent/claude_1@4c92432f`: definitions r3, execution report, fact tables, brief);
`codex_1/reviews/real-game-dance-attribution-*.md`; task records under `coordination/tasks/`
(`20260815-oscillation-deep-dive`, `20260816-h-starve-1-standing-troll-audit`,
`20260820-pair-selector-anti-benching`, `20260821-swap-r1-cure`, `20260822-peek-planner-target-map`,
`20260823-narrate-real-game-telemetry`, `20260824-real-game-dance-attribution`).
