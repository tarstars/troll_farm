# Prior art in this repository on the four top players, and on reconstructing top bots

Worker W2 of the reconstruction night (plan: `local_claude_1/reconstructions/PLAN.md`). Written
2026-08-28 ~03:30–04:15Z from the repository only — no Arena calls, no new measurements, no git.
Every number below has a file pointer; anything I could not verify from a file is marked
**(uncertain)**. Plain words, codes explained at first use.

Vocabulary used throughout. A **replay** is the referee's full record of one ladder game
(`data/raw/games/<id>.json`). **Teacher-forced** means a model is graded on the *real* bot's own
states from replays; **closed-loop** means the reconstruction plays the game itself and is graded
on the states *it* produces. **Held-game** accuracy means the games used for grading were not
used for fitting. A **spec** or **talent vector** is a trained troll's four numbers
speed/carry/harvest/chop (referee order). "**Phase n**" and "**Dnnn**" are the numbered
experiments of the July laboratory journal (`data/analysis/live-agent-6553250/
legend-top3-experiment-cycle-2026-07-18.md`, vol 2/3 beside it; reader's guide
`docs/LEDGER-MAP.md`; closed branches `docs/CONSTRAINTS.md`).

---

## 0. Who they are in our data

| player | agent id | ladder (PLAN, 08-27 19:50Z) | earlier ranks in our records | corpus coverage |
|---|---|---|---|---|
| delineate | `6479768` | #1, 30.89 | #1 throughout (31.00 on 07-29; stored score 30.99 in the L1 audit) | 223 games in the turn corpus (`local_claude_1/second-troll-census/train-census.json`); 199 games / 59,403 turns / 145,448 per-unit decision rows in the 07-31 L1 audit; 26 games in Phase 9 (07-18) |
| norxondor_gorgonax | `6480540` | #2, 29.66 | #4 on 07-16/07-18 ("rank-4 agent 6480540"), #2 by 07-27 (29.52) | 217 games in the turn corpus; 30 games / 8,738 decision rows / 62 TRAINs in Phase 10 |
| Bubaptik | many ids (a lineage that resubmits) | #3, 27.90 | #8 on 07-16 (agent `6542619`, 80 appearances); 7 of the newest 60 resident games on 07-30 (M4) | ~35 agent ids from `6529176` to `6568138`, 1–190 games each in the turn corpus; "3,917 corpus game lines by name" (PLAN.md, coordinator's count) |
| MSz | `6479460` | #4, 27.72 | #14 on 07-16 (26 appearances); #3 bar 28.22 on 07-27/29 | 215 games in the turn corpus; 24 games in the 07-19 per-opponent continuation panel |

Where the data lives: `/home/tarstars/prj/troll_farm/data/processed/games.jsonl` (23,613 games,
sha256 `150a5507…`), `turns.jsonl.gz` (13,313,072 seat-turn rows, sha256 `1e0ea236…`),
`maps.jsonl`, `trajectories/<id>.jsonl`, and the raw replays `data/raw/games/*.json`. The
worktree's `data/processed/` holds only manifests; the corpus is in the main checkout.
`local_claude_1/corpus-identity-2026-08-22.md`: **count corpus membership by parsing, never by
grep** (two greps gave 1,057 and 1,549 for a question whose parsed answer was 8,590).

The two-troll peer cohort of T-1 (`codex_1/top10/`, 25 identities from the N2 reconstruction)
contains **none** of the four — all four scale beyond two trolls. The second-troll census
(`local_claude_1/second-troll-census/`) covers every bot, including them.

Public write-ups (H5, 2026-07-29; journal vol 2 lines 415–470;
`chatgpt_1/2026-07-29-h5-h1-independent-review.md`): **delineate has a gist** (revision
`e8a005ddd7568d71bf1523a8c62202511e55bd86`, raw sha256 `18265467…`, hashed as an input of the L1
audit; before tonight the repo held only the L1 audit's summary of it — W1 archived the text
tonight at `local_claude_1/reconstructions/sources/delineate-gist.github.com-2026-05-25.md`);
**norxondor_gorgonax is a CodinGame auto-generated anonymous pseudonym, so no postmortem can
structurally exist**; **MSz published nothing**; Bubaptik was not searched for (H5's claim named
delineate, norxondor and MSz). The other write-ups found: Yann Moisan / yamo (#3), putibuzu (#2,
forum: two trolls, depth-12 rollouts, 3-ply beam), Astrobytes (README).

---

## 1. Per player

### 1.1 delineate (`6479768`)

**Measured.**

- Opening/workforce (`data/analysis/live-agent-6553250/top-player-macro-census-2026-07-16.json`,
  26 appearances): successful trains 1 in 14 games, 2 in 7, 3 in 5 (final roster 2/3/4);
  mean 1.65 trains; median first train turn 4; **92% of appearances use a "hybrid chopper"
  role** (harvest-capable and chop-capable); 28 distinct specs across 43 trains (most common
  `3/4/1/3` ×4, `2/2/2/2` ×4, `2/4/1/3` ×3, `1/2/2/2` ×3).
- Opening archaeology (`data/analysis/live-agent-6553250/top-player-opening-analysis-2026-07-17.md`,
  n=26): mean plants 44.0, final wood 94.3, margin +163.6. Named family **"adaptive max-bank
  hybrid scale"**: buy a strong hybrid whose stats are derived from the starting bank
  stay compact on slow/remote openings, add later hybrids only after the first pair has
  actively replenished the missing resources. **The first-troll spec rule is written down**
  (that record, "Level 4", n=26): in 22/26 games the four stats are exactly the independently
  maximum affordable stats from the bank just before training,
  `stat(resource) = floor(sqrt(bank[resource] − current_worker_count))` (plums→speed,
  lemons→carry, apples→harvest, iron→chop); the four exceptions reserve one or two harvest
  levels and still maximize the other three. First train at median turn 4; 22/26 first
  workers are hybrid choppers. Expansion is conditional: 14 games stop after one train, 7 add
  a second (median turn 106, always unfunded at the window start), 5 add a third; during the
  second-train window the starter drops 14.5 LEMON and the first hybrid 7.5 IRON + 4.0 PLUM
  against a mean bill of 8.25 PLUM / 13.67 LEMON / 2.92 APPLE / 8.92 IRON. The first hybrid
  stays mixed (6.5 harvests, 4.5 plants, 28.7 effective chops per 100 active turns); the
  second and third trained workers deposit 65.3 and 83.6 wood. What predicts scaling: nearest
  tree at the door (distance 0.5 in multi-train games vs 1.5; a `distance ≤ 0.5` split has
  in-sample balanced accuracy 0.762); a fully affordable first bill continues to a second
  train in 64.3% of games vs 22.2% when two or more resources are short; mean first-train turn
  11.1 in games that later scale vs 39.9. Planting mix per game: 10.65 PLUM, 10.23 LEMON,
  2.08 APPLE, 21.08 BANANA — a mixed replenishment loop, not a banana-only farm.
- Scaler archaeology D95a (journal vol 1 lines 2200–2216, 10 games): scales in 6/10; all nine
  later TRAINs execute within one turn of first affordability; each uses material from at least
  two existing workers; every first trained worker works at least two material domains before
  worker three; later workers spend 93.87% of successful material actions on CHOP/DROP. Verdict:
  no universal hand-written pair grammar — deterministic scaler distillation closed.
- Messages: zero `MSG` commands in ten fixed games (journal vol 1 line 2758) and zero in all 199
  L1 games — **no task grammar is readable from its chat channel** (unlike yaichi, D88).
- Determinism: on a fixed TestSession map delineate replays **byte-exactly** (A/A 148-92 twice;
  `data/analysis/live-agent-6553250/legend-top5-common-seed-bank-aa-result-2026-07-19.md`).
- Second-troll census (08-27, 223 games): median first-train turn 6 (mean 19.9); 125/223 seats
  train a second time; top vectors `2/2/2/2` ×45, `2/2/1/2` ×23, `2/3/1/2` ×17, `1/2/2/2` ×11,
  `2/2/2/1` ×11 — harvest-capable in 222/223.
- Against us (07-16 loss trio, `data/analysis/live-agent-6553250/matchup-loss-analysis.json`):
  13 games, 4–9, mean margin −77.1; in losses −132 with opponent wood 81.3 vs ours 53.1. The
  trio's shared loss signature (28 losses vs delineate/wala/norxondor): we lead wood at turn 100
  and trail by 300 in 23/28; every loss opponent has ≥20 successful plants and ≥20 harvests;
  we land more chops (138.3 vs 117.1) but bank less wood (53.3 vs 81.2; 0.418 vs 0.773
  wood/chop).
- Field test of our Norxondor-shaped three-worker candidate against it (Stage 2A, 07-19):
  actual margin −245, far below any local model's prediction (bottom +57) —
  `data/analysis/live-agent-6553250/norxondor-field-map-model-gap-result-2026-07-19.md`.

**Fitted rules and how well they predicted.** Only one fit was ever made on delineate: Phase 9's
state-only 18-class objective lookup (`cgauto/top_policy_objective_study.py`, result
`top-policy-objective-study-2026-07-18.json`): **60.41% held-game accuracy / 0.329 macro F1 on
17,743 unit-turns (26 games)** — it failed the "coherent architecture" gate (needs ≥0.60 accuracy
*and* ≥0.35 macro F1 in every fold); only Escdemon passed cleanly. No chop-target, plant-cell,
training-trigger or endgame rule has ever been fitted for delineate.

**What its author says the bot is** (from the gist, as summarized in
`data/analysis/live-agent-6553250/l1-delineate-cloning-readiness-audit-result-2026-07-31.md`):
a trained neural network, no per-turn search, 2–3 ms of the 50 ms budget; observation
104×11×22; four-block ResNet; 13 spatial action types per cell; a shared 144-candidate
train-plan head; sequential inference for the plan and then each troll; a final joint-action
beam; trained by a five-level PPO curriculum (not behaviour cloning); ~101k parameters;
~98k-character submission. **Consequence for the owner's goal:** the "algorithm" is an
architecture plus a training recipe; the per-turn decision procedure is the network's output,
and replays expose only its final commands.

**What failed and why.** L1 (behaviour cloning from delineate) reached readiness only:
verdict `DISTINCT_PRIMITIVE_ONLY` (`docs/l1-delineate-cloning-readiness-protocol-2026-07-31.md`,
result above, manifest `local_codex_1/l1-delineate-cloning-readiness-audit/manifest.json`,
review accepted `coordination/messages/chatgpt_1/20260731T022500Z-…`). Label surface: 144,265
explicit primitive commands (MOVE 62,409; CHOP 34,806; DROP 19,097; HARVEST 15,511; PLANT 7,762;
PICK 3,045; MINE 1,582; WAIT 53) plus 378 TRAINs with exact specs, 53 distinct opponents, seats
98/101. Not recoverable from replays: the train-plan target, the previous internal target, the
3,290 logits, alternatives, beam probabilities, weights. The successor L1a (extractor parity
first, then a frozen closed-loop gate) was never started; the 2026-08-02 all-agent review
rejected "primitive-only delineate L1" as a ranked idea
(`local_codex_1/top-player-new-games-final-ranked-ideas-2026-08-02.md` line 164).

**Open gaps.** Everything below the workforce layer: chop-target choice, plant cell/type choice,
harvest choice, endgame; the train-plan rule ("max-bank hybrid") as a formula; the 04:00Z
corpus is 223 games and no decision-rule fit exists on it.

### 1.2 norxondor_gorgonax (`6480540`) — the most-studied of the four

**Reconstructed (Phase 10, 2026-07-18;
`data/analysis/live-agent-6553250/norxondor-controller-iteration-2026-07-18.md`; 30 games,
8,738 decision rows, 62 TRAINs).** Its workforce ladder is an online rule: at roster size n,
wait until the stage's **floor** spec is affordable, then buy the componentwise-maximum
affordable spec clamped by the stage's **cap** (specs as speed/carry/harvest/chop):

| current trolls | floor | cap |
|---:|---|---|
| 1 | `2/2/1/1` | `3/3/2/2` |
| 2 | `2/3/1/2` | `4/5/2/2` |
| 3 | `2/3/0/3` | `3/3/1/3` |
| 4 | `2/4/0/3` | `3/4/1/3` |

This rule **reproduces all 8,738 trigger decisions and all 62 specs in-sample** (no false or
missed TRAIN); held-game: trigger timing exact, **57/62 specs (91.94%)**, worst fivefold fold
7/9. Final roster: 1 in 2 games, 2 in 7, 3 in 11, 4 in 7, 5 in 3. All 62 trained workers
eventually bank value; ordinal productivity 98.25–100%. Code: `cgauto/norxondor_workforce_ladder_study.py`
(fits floors/caps by cross-validation), result `norxondor-workforce-ladder-study-2026-07-18.json`.

Movement decomposition (same record; `cgauto/norxondor_navigation_intent_study.py`,
`norxondor_intent_state_machine_study.py`, `norxondor_goal_selector_study.py`): 10,391/10,406
MOVE targets (99.856%) equal the end-of-turn cell, i.e. it commands the next step, not the
destination; 9,068/9,707 episode endpoints (93.417%) lie on a shortest route to the next
non-MOVE action — so the structure is **intent → goal → shortest route**. Intent (which verb the
walk ends in) predicted once per movement episode: **74.11% held-game accuracy**, macro F1
0.525, worst fold 71.81% (4,427 episodes). Goals: DROP 1,469 endpoints all legal, 95.17% in
the nearest-path tie set; PICK 74 all legal; MINE 126 all legal, 84.13% nearest; **CHOP target
ranker 41.83% held exact vs 23.27% for "minimum cycle time"** (676/722 goals covered);
**HARVEST ranker 37.10% vs 4.85% baseline** (1,423 goals); PLANT: all 561 cells lie in the
static bank-door footprint, 88.24% currently free, 82.17% adjacent to an existing tree.

Phase 14 (`…/norxondor-offline-distillation-and-native-controller-2026-07-18.md`): the
compact pieces — a 107-node intent tree (**76.937% held-game accuracy**, 0.530 macro F1,
75.456% worst fold, ~1,923 bytes), a CHOP selector with 128 weights, a HARVEST selector with
32 weights — were joined with the ladder, persistent goals, equivalent endpoints and
deterministic planting into a native research controller
(`rust/src/strategies/norxondor_native.rs`, 1,203 lines). Closed-loop it **lost −172.663
paired margin / −97.263 score** vs our resident and produced ~38 CHOP / 68 PICK per game
against the replay target's ~159 / 17: autoregressive covariate shift — accurate on the
teacher's states, but small goal errors change inventory and geometry and the visited states
drift away.

**Other measurements.**
- Funding mechanism (Phase 10 rollouts on generated maps, eight local opponents): transplanting
  the ladder alone fails (with the CompactGold continuation −164.59 score / −170.19 margin;
  with Silver, mean roster 1.47); one explicit funder +33.70/+76.65 vs Silver; **a temporary
  two-worker funding coalition +68.56 score / +105.68 margin, mean 3.82 workers (replicated
  +65.59/+100.89)**; "stop at exactly three workers" +24.94/+8.18 vs resident, 6/8 opponents
  positive but −66.35 vs adaptive Gold. Lesson: the purchase rule is worthless without the
  mechanism that funds it.
- Opponent-label portfolio (resident vs three-worker chosen by opponent identity): **+6.213
  margin on untouched seeds 210–239** — an information ceiling only, identity is invisible in
  the arena. Observable-signature switch (first opponent TRAIN stats + turn band; offline
  +7.546): the real resident-prefix implementation **lost −6.169 margin on seeds 270–299**
  (roster 3 in only 46/480 cells) — signatures measured on a three-worker trajectory are not
  policy-invariant. Closed (`docs/CONSTRAINTS.md` (f) "Signature-only late switching").
- Phase 11 shared-state Monte Carlo: the turn-three terminal teacher +26.081 margin / +15.194
  score, all eight opponents positive; but 209.487 ms median / 279.460 ms p95 vs 50 ms, 0/80
  decisions fit; 240-turn proxy keeps 89.19% of the gain at 88.33% precision (<90%).
- Phase 12/13/15: trajectory-feature value models reach 91.43% blocked-seed precision at turn
  10 but 73.08% leave-one-opponent-family-out; 0/26 post-funding role policies and 0/20
  funding profiles robust (best +48.213 but −44.300 vs adaptive Gold; worker three median
  turn 92 vs replay median ~101); map-only selection: 65 positive groups of 600, oracle
  +4.591, precision 89.615% < 90%, all ten forests fail (best 47.059%, −0.277).
- **The one field test.** A standalone candidate ported from the research ladder
  (`cgauto/submissions/candidate-agent6553250-norxondor-three-worker-silver.min.rs`, sha256
  `69237902…`; builder `cgauto/make_norxondor_three_worker_candidate.py`; parity
  `rust/src/bin/norxondor_three_worker_parity.rs`) played five TestSession games vs the then top
  five (delineate, wala, norxondor, escdemon, laconic;
  `data/analysis/live-agent-6553250/norxondor-three-worker-stage2a-result-2026-07-19.json`):
  candidate mean score 150.0 vs baseline 245.4, margin −127.2 vs −97.0, wins 0 vs 1; reached
  worker three in 3/5 (turns 77, 98, 84; stopped at two vs Escdemon and laconic). Model-gap
  diagnosis (`…norxondor-field-map-model-gap-result-2026-07-19.md`): on those exact five maps the
  three-worker policy funds worker three in 39/40 local cells yet loses −28.975 margin to the
  resident locally; actual margins vs delineate/wala −245/−265 lie far outside every local
  model's range — the eight-model generated-map zoo was retired as a transfer gate. It was
  **never submitted to the Arena**: the name does not occur in
  `data/analysis/arena-submission-history.json`, and the Phase 10/14 records say "no
  submission follows".
- Determinism: on a fixed map norxondor **diverges from turn 22** (272/300 turns differ,
  excluding MSG), changing our resident's game from turn 50 and the score by 83 points; it
  **prints runtime telemetry as `MSG` every turn** (timing strings) — A/A result 07-19. My
  inference, not a measurement: a bot that prints timings and is non-deterministic on a fixed
  map is probably time-budgeted and randomized (search or rollouts) **(uncertain)**.
- Census 07-16 (30 appearances): trains 0:2, 1:7, 2:11, 3:7, 4:3; median first train turn 6;
  specs `2/3/1/2` ×12, `2/2/2/2` ×8, `2/2/2/1` ×8, `2/2/1/2` ×5, `2/3/1/3` ×5; first troll
  `2/2/2/2` ×8 / `2/2/2/1` ×8 / `2/2/1/2` ×5, second troll `2/3/1/2` ×12 / `3/3/1/2` ×4; roles:
  hybrid chopper in 90% of appearances, harvest specialist 30%, wood specialist 17%. Opening
  analysis (n=30): mean plants 35.0, final wood 63.5, margin +64.4; family "hybrid adaptive".
  D95a: renews (harvest→plant) in 8/10 scaler foundations while capitalizing in 10/10.
  Counter-intuitive and unexplained in that record: norxondor scales *more* often on maps with
  lower initial iron and fruit ("policy response, replenishment, opponent pressure, or
  sampling — not a reason to prefer poor starts").
- Phase 9 objective lookup (same study as delineate's; 22,177 unit-turns, 30 games):
  **66.70% held-game accuracy / 0.360 macro F1, worst fold 64.99%** — it passed the
  coherent-architecture gate "at a lower level" than Escdemon, which is why it became the
  Phase 10 target.
- Census 08-27 (217 games): median first-train turn 10 (mean 23.6); 186/217 seats train twice or
  more; top vectors `2/2/2/2` ×84, `2/2/1/2` ×40, `2/2/2/1` ×33, `2/2/1/1` ×19, `3/2/2/2` ×11.
- Against us (07-16): 13 games 4–9, margin −77.3 (losses −126.1, opponent wood 75.8).
- Successor returns (D167, `…/d167a-successor-acquisition-path-result-2026-07-27.md`): norxondor
  is among the 4/5 top-five agents whose production returns acquire the seed from the bank
  (BANK_SEED), both seats.

**Open gaps.** Target choice is the weak layer (CHOP 41.8%, HARVEST 37.1% exact); the plant
rule is only "somewhere in the bank-door footprint, usually next to a tree"; no endgame rule;
what the per-turn telemetry says (never decoded); the ladder table is from 30 games of 07-18
and has n=3 at the fifth-troll stage — it should be re-fitted on the 217-game corpus; whether
the agent id is still the same code (same id `6480540` since 07-16 — the platform keeps one id
per submission, so yes **(uncertain: verified for delineate in the L1 audit, assumed here)**).

### 1.3 Bubaptik (many ids)

Never reconstructed; measured only in censuses.

- 07-16 census (agent `6542619`, rank 8, 80 appearances): trains 0:9, 1:17, 2:24, 3:25, 4:5
  (final roster up to five); mean 2.00 trains; median first train turn 12; hybrid chopper in
  82.5% of appearances, wood specialist 27.5%, harvest specialist 18.75%; 40 distinct specs
  (most common `2/3/1/3` ×16, `2/2/2/2` ×12, `4/3/1/3` ×11, `3/3/1/3` ×11, `2/2/1/2` ×9) —
  the widest spec spread of the four, including speed-4 and chop-3 trolls. Opening analysis
  (n=80): mean plants 26.7, final wood 58.8, **margin −63.7** (a losing average at the time);
  family "hybrid adaptive" with delineate, norxondor, Astrobytes, putibuzu, DoubtinGiyov.
- 08-27 second-troll census shows the lineage **changed strategy over time**: older ids
  (`6542200`–`6557104`) train the second troll at median turn 4–28 with big vectors
  (`2/3/2/2`, `2/3/1/2`, `3/3/1/3`); the newer ids (`6563190` onward, e.g. `6568138` with 190
  games) train at **median turn 2** (mean 5–14) with cheap harvest-capable vectors (`2/2/2/2`,
  `2/2/2/1`, `2/2/1/2`, `1/2/2/2`), and 154/190 seats train again later. Which id is today's #3
  is not recorded in the repo (uncertain).
- Matchmaking (M4, `data/analysis/live-agent-6553250/m4-matchmaking-composition-result-2026-07-30.md`,
  `local_codex_1/m4-matchmaking-composition/opponents.csv`): 7 of the resident's newest 60 games
  were Bubaptik, across many version ids; rule: "use exact IDs for version-specific claims and
  pseudonyms for longitudinal composition". M2 (`local_codex_1/m2-opponent-specific-losses/`):
  no Bubaptik id clears the actionability gates.
- Not in the top five during Phases 9–10, so no imitation, no A/A block, no loss-trio decode.

**Open gaps.** Everything decision-level; even the current agent id.

### 1.4 MSz (`6479460`)

Never reconstructed; measured in censuses and one continuation panel.

- 07-16 census (rank 14, 26 appearances): trains 1:13, 2:8, 3:5; mean 1.69; **median first
  train turn 1**; roles generalist 54%, harvest specialist 46%, hybrid chopper 50%, wood
  specialist 19%. The ladder by ordinal: **first troll cheap and harvest-capable** (`2/2/2/1`
  ×8, `1/1/1/1` ×7, `1/2/2/1` ×4, `2/1/1/1` ×4, `2/2/1/1` ×2); **second troll big-carry hybrid**
  (`2/4/1/2` ×7, `2/4/1/3` ×4, `2/4/1/4`, `3/4/1/2`); **third troll big-carry wood specialist**
  (`2/4/0/3` ×3, `3/4/0/3`, `2/4/0/2`). Recorded training sequences include `1/1/1/1 → 2/4/1/…`.
- Opening analysis (n=26): mean plants 28.3, final wood 51.7, margin +31.4; family
  **"farm-first staged scale"** with wala, viewlagoon, uta_ccc, gaha, xSkyline — buy a
  harvest/planting worker on turn 1, build a training-resource orchard with two farming hands,
  add choppers later (that reconstruction is spelled out for wala: turn-1 spec
  `movement=min(2,floor(sqrt(PLUM−1)))`, `carry=min(3,floor(sqrt(LEMON−1)))`,
  `harvest=min(2,floor(sqrt(APPLE−1)))`, `chop=1`, matching 29/29 — **not fitted for MSz**).
- 08-27 census (215 games): median first-train turn 1, **mean 1.56** — it trains on turn 1
  almost always; 180/215 seats train twice or more; vectors `2/2/2/1` ×66, `1/2/2/1` ×37,
  `2/2/1/1` ×37, `2/1/1/1` ×30, `1/1/1/1` ×27, `1/2/1/1` ×17 — i.e. "buy whatever the starting
  bank affords on turn 1, harvest power ≥1".
- D167 (07-27): the only top-five agent whose production return acquires the seed from a
  field fruit rather than the bank (FIELD_FRUIT, one cycle).
- Per-opponent continuation panel (07-19, `…/per-opponent-continuation-result-2026-07-19.md`;
  `cgauto/per_opponent_continuation_dataset.py`, agents Bondo416, MSz, Meruem, celeria, gaha,
  viewlagoon; 24 games each): identity-conditioned history retrieval improved MSz's
  continuation error by only +0.2% over population state — closed as a proxy.
- Ladder: the #3 bar 28.22 on 07-27/29 (`docs/BACKLOG.md` line 661, `docs/PROMOTION-RUNBOOK.md`).

**Open gaps.** Everything decision-level; the turn-1 spec rule (probably bank-derived like
wala's — a guess).

---

## 2. What reconstruction attempts taught us (the closures)

Each item: lesson — decisive number — pointer.

1. **Imitating "the top five" as one policy fails.** State-only objective lookup: 59.886%
   held-game, **39.132% worst held-agent** — they are different architectures, not one
   average. `top-policy-objective-study-2026-07-18.md/json`; CONSTRAINTS (a) "Pooled top-5".
2. **Teacher-forced accuracy is not value.** Escdemon: tree ranker 56.08% held → 52.12% MOVE
   accuracy once integrated autoregressively (gate 55%); Norxondor: 76.937% intent → **−172.663
   paired margin** closed-loop. Any clone must pass a separate closed-loop gate on official
   maps. `escdemon-complete-policy-gate-2026-07-18.md`; Phase 14 record; CONSTRAINTS (b)
   "Native imitation … −172.663".
3. **Component gates and complete gates must be separate** — a component can pass and the
   assembled policy fail (Escdemon). Same record.
4. **Small samples cannot select an opening spec out of sample**: Escdemon's eventual spec
   8/26 under nested leave-one-game-out vs 14/26 for our existing planner; 2,750 policies
   collapse to 334 signatures. Do not tune opening formulas on ~26 games.
5. **A purchase rule without its funding mechanism is inert**: Norxondor's ladder + a
   chop-first continuation −170 margin; the ladder works only with a temporary two-worker
   funding coalition (+105.68). Phase 10 §3.
6. **Late switching on an observable signature is path-dependent**: +7.546 offline → −6.169
   prospectively; signals measured on one policy's trajectory are not invariant under another.
   CONSTRAINTS (f).
7. **Opponent identity is not an input the arena gives you**: label-aware portfolios (+6.213)
   are ceilings, not bots. Phase 10 §4.
8. **Online rollout teachers can be excellent and undeployable**: +26.081 margin at 209 ms vs
   the 50 ms budget. Phase 11; CONSTRAINTS (f).
9. **Fitted value models do not transfer across opponent families or map folds**: 91.43% →
   73.08% (Phase 12); +14–17 train → +1.82 held (D153); confidence anti-correlates with realized
   value. CONSTRAINTS (b).
10. **Map-only / opening-only selectors fail** (Phase 15 89.615% < 90%; D63 AUC 0.830 → 0.479;
    D91 5/16 maps). CONSTRAINTS (a)/(c).
11. **Replaying or retrieving another bot's command stream is not a model of it**: recorded
    commands as continuations match only 86.85% (D31); identity-conditioned retrieval beats an
    identity mean by 11.94% but loses to population state (per-opponent continuation, 07-19).
    "No reconstructed proxy may serve as a candidate acceptance judge." CONSTRAINTS (b).
12. **Transplanting a strong bot's three-worker policy loses as a complete policy** (−28.3
    trimmed vs six opponents; Stage 2A −30.2 margin unpaired vs the top five). CONSTRAINTS (a)
    first bullet; Stage 2A result.
13. **Generated maps are not real maps; the local opponent zoo is not the field**: D30 (six
    water cells vs 12–104), field-map gap (calibration 2/5 and 1/5). Evaluate on
    `generate_official` maps (D33) or real `maps.jsonl` maps.
14. **When the teacher is a rule system, fit a rule system**: an MLP reached 85% on D40's
    decisions, a parameter-free decoder 85,047/85,047 (D41a). Lexicographic filters and integer
    comparisons are not learnable by small nets. CONSTRAINTS (b).
15. **Only execution-class changes have ever transferred to the arena**; every wrapper,
    transplant, imitation, offline-value selector and economy re-architecture failed held-out
    gates or the arena. CONSTRAINTS (h); `docs/LEDGER-MAP.md` §16.
16. **The one reconstruction that worked came from a postmortem, not from replays**: Yann
    Moisan's #3 write-up (`docs/reference/yann-moisan-postmortem-2026-05-26.txt`) → a design
    spec listing five explicit gaps to resolve by measurement, G1–G5
    (`docs/reference/2026-07-11-yannbot-design.md`) → `MoisanBot`/`YamoOpeningPolicy` → the
    live resident. Verified correspondences: `1000·wood/turns` chop scoring, first-turn
    `typeToCut` by cluster-nearest-shack, denial gate `opponent_trolls <= 2`, endgame
    plant-for-points (H5; CONSTRAINTS (h) "IDENTITY"). Its cost: H13 attributes at most ~1
    point of our 2.94-point gap to yamo to code; our own movement "fix" made oscillation 6.4×
    worse than his (18.2% vs 2.9% of games). That is the template for W1/W3/W4's output:
    the write-up's rules, the gaps named, each gap measured.
17. **Check the chat channel before building a grammar decoder**: yaichi's MSG task grammar was
    decodable (D88, 10/10), delineate's is empty, norxondor's is timing telemetry.
18. **Determinism differs per bot**: delineate/Escdemon/laconic replay exactly on a fixed map;
    wala nearly; norxondor not at all — controlled A/B against norxondor needs replicated
    map-blocked samples. A/A result 07-19.
19. **Premises rot**: the register's "delineate was never imitated" was false (Phase 9 did);
    H8's tempo figure came from a stale census; four of six 07-29 hypotheses had false premises.
    Re-verify the premise before measuring. CONSTRAINTS (h) "Measure before you build".
20. **The 2026-08-02 all-agent top-player review** (`docs/reports/2026-08-02-top-player-all-agent-analysis.tex`,
    153 games, one direct game vs rank-13 Astrobytes) found no idea about the top players'
    algorithms — only that our catastrophes (10/153, −167 each) are late crossovers under
    opponent scaling (every catastrophic opponent finished with 3–4 workers) and that scoring
    diverges after turn 150.
21. **Field facts about the whole top cohort** worth carrying into any reconstruction: top-5
    reap 24.16% of the crops they create (resident 0.94%), self-crop reap in 93.3% of games,
    78% of their suppression chops happen at roster ≥3 (D101, `docs/evidence/records/D101.md`);
    top-5 reach worker 3 in 75.6% of games (median turn 106) and worker 4 in 41.6% (median
    137); self-planted crops fund 37.2% of the third worker and 49.7% of the fourth; mined iron
    5.99 → 16.05 from worker 3 to 4; renewable base R≈0.75, labour-limited (A2 Phase 0a,
    CONSTRAINTS (h)); undocumented starting bank ~24 fruit / ~6 iron (four 2..10 fruit draws +
    2..10 iron, symmetric); the field is split on lookahead (delineate none, putibuzu depth-12
    + 3-ply beam) and on roster (yamo/putibuzu two trolls; the four here scale).

---

## 3. Tools that exist

"Ours only" = works on our instrumented bots' telemetry, not on other players' replays.
Arena/API tools are listed for completeness and **must not be run** under this task's rules.

### 3.1 Corpus builders and replay decoders (work on any player)

| tool | takes | gives | run |
|---|---|---|---|
| `data/scripts/parse.py` | `data/raw/games/*.json` | `processed/games.jsonl` (per game: scores, command counts, successful plants, training turns, six 50-turn score snapshots, final inventories), `maps.jsonl` (deduped maps with initial trees), `trajectories/<id>.jsonl` (per turn: `inv0`, `inv1`, `commands0`, `commands1`), `stats.json` | **do not run casually** — output paths are hardcoded and overwrite tracked manifests (`corpus-identity-2026-08-22.md`) |
| `scripts/extract_turns.py` | raw replays | `turns.jsonl.gz`, one row per (game, turn, seat) with the issued commands, agent id and name (13.3 M rows); `turns.manifest.json` | `python3 scripts/extract_turns.py` (reads raw only) |
| `cgauto/replay_state.py` (`DiffDecoder`) + `cgauto/recent_resident_field_census.py::decoded_states(game, trajectory)` | one raw replay + its trajectory | exact per-turn official states (units with id/x/y/player/speed/carry/hp/chop/cargo, plants with kind/cell/size/health/fruits/cooldown, inventories) — validated 361,755 transitions, zero material mismatches; also `successful_events(frames)`, `crop_provenance(...)`, `corpus_parser()` | import from Python; used by every D-series replay audit |
| `cgauto/top_player_opening_analysis.py` | processed corpus + raw replays | per-occurrence opening archaeology: turn-one geometry, every TRAIN's turn/spec/cost/deficit trajectory/funding window, per-worker actions and payback, per-agent summaries → `top-player-opening-analysis-*.json/.md` | `python3 cgauto/top_player_opening_analysis.py` (check `--help`) |
| `cgauto/top_player_macro_census.py` | replays of the top 20 | per-agent TRAIN count/spec/role census (`top-player-macro-census-*.json`) | as above |
| `cgauto/top_policy_objective_study.py` | replays of chosen agents | 18-class per-unit objective labels (CHOP, MOVE_TREE_RIPE, PLANT_BANANA …) and held-game/held-agent lookup accuracies | as above |
| `cgauto/make_agent_trajectory_dataset.py`, `cgauto/make_agent_initial_dataset.py` | one agent id | complete replay decision states / turn-one protocol records for that agent | as above |
| `cgauto/agent_trajectory_command_audit.py` | a local policy + one agent's replays | teacher-forced command agreement (objective / unit command / MOVE target) | as above |
| `cgauto/agent_opening_plan_audit.py` | a local opening planner + one agent | exact-spec agreement of trained workers | as above |
| `cgauto/norxondor_*.py` (17 scripts: workforce ladder, navigation intent, intent state machine, goal selector, compact intent, opening signature, shared-state distillation/selector/forest, value model, research rollout, partial rollout, parallel latency, portfolio upper bound, resident role, robust geometry, field map dataset) and `cgauto/escdemon_*.py` (4) | Norxondor/Escdemon replays or the research-rollout TSVs | the fits described in §1.2 | headers documented in each file |
| `rust/src/strategies/norxondor_native.rs`, `norxondor_research.rs`, `rust/src/norxondor_three_worker_live_bot.rs`, bins `norxondor_research_time.rs`, `norxondor_shared_state_time.rs`, `norxondor_three_worker_live.rs`, `norxondor_three_worker_parity.rs`, `norxondor_field_map_gap.rs`; `rust/tests/norxondor_research.rs` | — | the Norxondor reconstructions as runnable Rust strategies (research only) | `cargo` in `rust/` |
| `cgauto/crop_fate_census.py` (B3.7), `cgauto/analyze_d101a_production_suppression.py` (`reconstruct_generation_actions`), `cgauto/analyze_d95a_rank_one_scaler.py`, `cgauto/live_loss_analysis.py` | replays | crop lineage/fate per player; production vs suppression roles; scaler archaeology; per-opponent loss signatures | each documented in its header |
| `codex_1/top10/field_comparison.py`, `per_turn_field_comparison.py` | `games.jsonl` / `turns.jsonl.gz` | per-agent score composition, training turns, successful plants; per-turn PLANT buckets, HARVEST/CHOP at own-planted coordinates, last-30-turn verb mix | `python3 codex_1/top10/field_comparison.py --output …`; cohort is a hardcoded id list — edit `COHORT` to the four |
| `local_claude_1/second-troll-census/extract.py` | `turns.jsonl.gz` | first TRAIN per game-seat → `train-census.json` (713 bot ids) | `python3 local_claude_1/second-troll-census/extract.py` (10 s) |
| `claude_1/adapter1/replay_to_trace.py` (+ `run_adapter_panel.py`, report `replay-to-trace-adapter-2026-08-23.md`) | one raw replay + our agent id | transcript text + commands text for `trace_detectors.build_trace` → a `Trace` (per turn: inventories, plants, 14-int unit lines, own commands); replay layout measured over 290 games (`frames = 2T+1`, T is 300 in 266 of 290) | import; seat resolved only by agent id |
| `local_claude_1/apple-farm/ladder_read.py` | a collected package of sanitised replays (`.jsonl.gz`) + agent id | per game: map facts (`parse_map` from `view.global.inputmodule`), whether a rule ran, inventories, scores; split by map class | `python3 local_claude_1/apple-farm/ladder_read.py <package.jsonl.gz> <agent id> [label]` |
| `cgauto/export_agent_replays.py` | one agent/submission's replay queue | sanitised deterministic corpus (strips handles/user ids; keeps `gameId, refereeInput, scores, ranks, tooltips, frames`) | header |
| `claude_1/viewer/build_viewer.py` | the frozen situation library (ours) | one self-contained HTML page per situation, keyboard step-through; draws orders vs inferred landings honestly | `python3 claude_1/viewer/build_viewer.py --out …`; adaptable to replays **(uncertain)** |

### 3.2 Referee mirrors and local play

| tool | what it is | caveats |
|---|---|---|
| `sim/engine.py` (+ `sim/state.py`, `sim/mapgen.py`, `sim/runner.py`, `sim/boss.py`) | Python mirror of the referee: growth cooldowns and water boost (PLUM/LEMON 5, APPLE 7, BANANA 2), tree health `base + slope·size` (PLUM/LEMON 4+2s, APPLE 8+3s, BANANA 2+s), `WOOD_POINTS=4`, `apply_chop`, `step` (MOVE resolved before TRAIN) | movement tie-break is deterministic (smallest x,y) where the referee is random; strict command validation not reproduced (X1, `docs/reviews/2026-07-30-local_codex_1-x1-mechanics-rederivation.md`); `sim/runner.py` boss is weak — **not** a value gate |
| `sim/validate_replay.py` | replays a real game through the sim and compares per-turn inventories and positions to the referee | Gold-era; expects `@TF` debug lines from our own bot |
| Rust exact engine (`rust/` — `engine.rs::next_cell`, `generate_official` = SHA1PRNG map-generator port, 120/120 exact, D33; the A2-0b referee-parity implementation locked at `a2-0b-r1-implementation-lock.json`) | the substrate all D-series panels ran on; official-map geometry, undocumented starting bank implemented | continued referee RNG changes 1,781/2,048 trajectories — use the locked A2-0b path for anything called "referee-exact" |
| `local_claude_1/apple-farm/smoke.py` (and `the-floor/smoke.py`) | plays full local games of an arm on **real ladder maps from `maps.jsonl`** vs the pipeline referee's scripted `harvester` / `chopper_aggressor` opponents, same 2..10 draw both sides | mechanics check, not value |
| `local_claude_1/apple-farm/fixtures_diff.py`, `claude_1/t1/fixture_harness.py`, `scripts/cut_fixtures.py` | the 34 frozen situations (re-run harness) and the cutter of telemetry windows from our instrumented replays (classes: dance, parked_troll, blocked_troll, stall, …) | ours only |
| `local_claude_1/apple-farm/make_apple_farm.py`, `claude_1/cure3/build_arms3.py` etc. | builders of our own one-rule instruments through the generator-and-compactor chain | ours only |
| `claude_1/narrate1/narrate_decode.py` … `narrate8/` | decoders of our NARRATE v2–v8 `MSG` telemetry joined to the Trace | ours only |
| `docs/reference/2026-07-11-yannbot-design.md` | the template of a reconstruction from a write-up: faithful core, explicit gaps G1–G5 to measure, validation ladder V1–V5 | — |

### 3.3 Arena/API tools — listed only, not to be run here

`cgauto/field_panel.py` (TestSession/play vs fixed Legend agents; `TOP_FIVE` ids incl.
delineate `6479768`, norxondor `6480540`), `data/scripts/collect_snapshot.py` /
`collect_wide.py` / `parse_snapshot.py` (the immutable D61p replay collector; read-only GETs,
each run individually authorized), `local_claude_1/narrate/collect_submission_games.py`
(collect a submission's games before the ~160-battle window evicts them),
`scripts/top15_public_battle_audit.py`, `cgauto/battles.py`, `cgauto/field_targets.py`,
`cgauto/cg_rank.py`, `cgauto/api_*.py`.

### 3.4 Referee facts a rule-fitter needs (pointers)

Training cost with n trolls: plums `n+speed²`, lemons `n+carry²`, apples `n+harvest²`, iron
`n+chop²` (`docs/mechanics.md`; `local_claude_1/second-troll-census/README.md`). Chop takes chop
power off health; at death the wood (= size, ≤4) is dealt one per round to every chopper on the
cell with free carry (`sim/engine.py:apply_chop`). Starting bank ~24 fruit / ~6 iron, symmetric
(CONSTRAINTS (h)). Enemy units may share a cell; no body-blocking exists (`docs/mechanics.md:42-45`).
Shack occupancy must be checked after MOVE (H8).

---

## 4. Where the four stand against the closures — what W3/W4 can and cannot claim

- A rule table like Norxondor's ladder (floors/caps by roster size) is the proven **format** for
  a workforce layer: it reproduced 100% of triggers and 92% of held specs. The same fit should be
  attempted for delineate, MSz and the current Bubaptik id: `cgauto/norxondor_workforce_ladder_study.py`
  is generic — `--analysis <opening-analysis json> --agent-id <id> --output <json>` (it reads the
  per-occurrence rows of `top_player_opening_analysis.py`, so that analysis must be rebuilt on
  the current corpus first).
- For target choice, the record's best held exactness is ~42% (Norxondor CHOP) and 56% (Escdemon
  tree ranker); any W4 fit should quote its accuracy against the "nearest tree" (42.18%) and
  "minimum cycle" (45.97%) baselines from `escdemon-complete-policy-gate-2026-07-18.md`.
- A fitted description is a *description*; the record forbids calling it an algorithm until it
  regenerates the bot's own state distribution (Phase 14) — the ALGORITHM.md documents should
  say "matches X% of decisions, teacher-forced" and nothing stronger.
- For delineate the honest answer to "algorithm sufficient to write a program" is the
  architecture + training recipe in its gist; replays can only bound what the network does.

## 5. Sibling outputs of the same night (not prior art — listed so the integrator can join them)

Present under `local_claude_1/reconstructions/` at 03:25Z: `sources/` (W1: 27 files —
delineate's gist and forum post, eulerscheZahl's all-Legend-player stats for delineate /
norxondor_gorgonax / MSz, `Bubaptik-NOTHING-FOUND.md`, MSz's earlier 2024 postmortems on GitHub,
the contest feedback thread, putibuzu/wala/Escdemon/laconic_pixel/Konstant/xSkyline/Ztrk/
FinkPloyd/aangairbender/Astrobytes posts, the referee statement; `SUMMARY.md`), `profiles/`
(W3: `profile_bot.py` and `<player>.md/.json` for the four plus `tass` and `yamo`, with
`COMPARISON.md`), `fits/` (W4: `reconstruct.py`, `fit_rules.py`, `decision_tables.py`,
`delineate_fit_results.json`, `norxondor_fit_results.json`, `tables/`). I have not read them;
their claims are theirs.
