# Full review replication — new games from the current best bot

Agent: `claude_1` · Task: `20260802-top-player-full-review-replication` · 2026-08-02
Current bot: agent/submission `6589709`/`41079653`, source SHA-256 `6f992a5a…`
Frozen package commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`

## Disclosure — I am not a blind replication

I read and formally reviewed `local_codex_1`'s integrated final report before this task was
assigned. I know its three ranked ideas. **Agreement between my ranking and its ranking is
not independent confirmation.** Every idea below is labelled `NOT INDEPENDENT` where the
local report reached it first. `chatgpt_1`'s report is the genuinely blind one and should
outweigh mine wherever we differ. What is mine alone is the phase decomposition in §3 and the
ranking consequences I draw from it — the local report does not contain that analysis, and it
leads me to a **different order** from the one it published.

Everything here is recomputed from the committed package. Nothing is inherited.

---

## 1. Package and cohort verification

All six artifacts hash-exact against the task record. Independently recomputed:

| quantity | value | status |
|---|---|---|
| side rows / current-new games / top20-source / union | 5,672 / 153 / 2,684 / 2,836 | matches manifest |
| our identity in every current row | `6589709` only | verified |
| both sides present | 153/153 | verified |
| outcomes / seats | 95W-2T-56L / 68 seat-0, 85 seat-1 | matches manifest |
| durations | 96 full-300, 57 short | verified |
| rank bands | 1 / 73 / 52 / 27 | matches the frozen split exactly |

| opponent band | n | W-T-L | mean margin | win rate |
|---|---:|---|---:|---:|
| 1–20 | 1 | 0-0-1 | −70.00 | 0.0% |
| 21–50 | 73 | 42-1-30 | +13.55 | 57.5% |
| 51–100 | 52 | 33-1-18 | +34.21 | 63.5% |
| 101+ | 27 | 20-0-7 | +34.74 | 74.1% |

**Package defect worth recording:** `planted_ok_*` is not a subset of `plant_cmd_*` —
aggregated over top-20 sides it *exceeds* commands issued (86,023 vs 81,280 = 105.8%; our
opponents 107.1%). Any plant-success rate derived from these two columns is unsound. I
publish none and would reject one in cross-review without a stated column definition.

## 2. Behaviour versus the top-20 benchmark

Per 100 turns, per side:

| action | ours | top20 | our opponents |
|---|---:|---:|---:|
| chop | **65.28** | 50.85 | 34.17 |
| harvest | **3.18** | 19.55 | 14.48 |
| plant | 4.74 | 10.19 | 9.10 |
| mine | 0.25 | 2.10 | 1.19 |
| wait | 8.42 | 2.31 | 11.45 |
| move | 94.54 | 126.08 | 117.00 |

Our final roster is **exactly 2.00 in all 153 games** — one TRAIN, median t10, every game —
against top-20's mean 2.83 and our opponents' 2.33.

This is observational benchmark context, not treatment evidence. Two of the three largest
gaps are **closed ground and I do not propose them**: mining at workforce ≥2 is closed as
harmful (`docs/CONSTRAINTS.md:344`, D174a −10.76) and the resident deliberately stops mining
at worker two (`:348`); worker-three scaling is closed by A2-1's K1 failure (`:133`) and is
permitted only opportunistically, never as a funding detour (`:355`).

## 3. Where the games are actually lost — my principal independent result

Points scored per 50-turn window, both sides, 96 full games, split by the opponent's final
roster.

**Against ≤2-worker opponents (n=60) — they never accelerate:**

| window | ours | theirs | net |
|---|---:|---:|---:|
| t50→t100 | 33.30 | 21.47 | +11.83 |
| t100→t150 | 30.82 | 24.77 | +6.05 |
| t150→t200 | 29.37 | 22.82 | +6.55 |
| t200→t250 | 30.87 | 21.17 | +9.70 |
| t250→t300 | 36.02 | 25.60 | +10.42 |

Terminal +59.07, 41/60 wins. Net positive in **every** window.

**Against ≥3-worker opponents (n=36) — they multiply by 12×:**

| window | ours | theirs | net |
|---|---:|---:|---:|
| t50→t100 | 36.92 | 8.64 | +28.28 |
| t100→t150 | 37.64 | 16.47 | +21.17 |
| t150→t200 | 39.75 | 46.06 | **−6.31** |
| t200→t250 | 40.83 | 79.81 | −38.97 |
| t250→t300 | 42.56 | 102.19 | −59.64 |

Terminal −38.19, 11/36 wins.

**Our production never declines. It is higher in the games we lose.** Per-window scoring is
36.92 → 42.56 against scaling opponents versus 33.30 → 36.02 against non-scaling ones, and
our mean final score is **234.28** in games lost to scaled opponents against **198.58** in
games won. We are not playing worse when we lose; we are playing better and losing anyway.

Opponent final score by their roster, full games:

| opp roster | n | their final | our final | margin |
|---:|---:|---:|---:|---:|
| 1 | 8 | 29.25 | 170.88 | +141.62 |
| 2 | 52 | 156.48 | 202.85 | +46.37 |
| 3 | 22 | 232.95 | 226.09 | **−6.86** |
| 4 | 14 | 334.57 | 247.14 | −87.43 |

Each opponent worker is worth roughly **+100 points to them and ~+22 to us**. Break-even is
their third worker. The net flips negative in **t150→t200**, one window after the cohort's
worker-three appearances, so an activation window exists before the damage compounds.

Within the 36 scaled-opponent games: our chops landed correlate **+0.354** with margin, their
chops landed **−0.379**, their roster **−0.337**, our WAIT commands **−0.046**. The chop
correlations are not separable from roster in this package and I do not claim they are causal.

### What this rules out — the most useful thing in my report

**Any candidate that improves our own economy, harvest, banking or conversion is attacking
the wrong variable.** It cannot close a gap that opens entirely on the other side of the
board, in games where our own output is already higher. This is a 96-game statement, not an
inference from the single direct game, and it disposes of more candidate families than any
positive finding here. It is also why my ranking differs from the local report's.

## 4. Direct-game postmortem — `897780884` (rank-13 Astrobytes, we lost 333–403)

From the committed replay and trajectory only.

| | us | Astrobytes |
|---|---:|---:|
| TRAIN turns | t11 | **t1, t56, t105** |
| final roster | 2 | 4 |
| chops landed | 187 | 125 |
| wood collected | 83 | 97 |
| fruit harvested | **2** | **121** |

Margin by checkpoint: **+29, +93, +112, +77, −1, −70**. Our own scoring per window is 53,
72, 56, 56, 55, 41; theirs is 24, 8, 37, 91, 133, 110. The game is a scale model of §3 — we
never collapse, they accelerate after their third and fourth workers land.

Action mix by phase confirms two different games being played: t1–100 we issue MOVE 90 /
CHOP 78 / HARVEST 2, they issue HARVEST 44 / PLANT 10 / MINE 10 / TRAIN 2. We issue our first
PLANT only after t200.

**`UNAVAILABLE_FROM_PACKAGE`:** which specific tree each opponent CHOP felled, who received
the wood, and the 79-initial/42-own decomposition of their 121 harvested fruit. These need
frame/view state. The 121 total *is* verifiable from the CSV; the split is not. I did not
infer any of it from the local report.

## 5. Ranked improvements

### Rank 1 — H3a: activate the exact frozen opponent-crop scoring only after visible opponent worker three · `NOT INDEPENDENT`

- **Mechanism / IDs.** Opponents reaching ≥3 workers: **46/153**, 31 identities, both seats.
  That group 16W/30L at mean margin −28.91; the other 107 79W/2T/26L at +46.41; difference
  **−75.32**, game-bootstrap 95% CI [−109.57,−41.87] (20k resamples, my own). Full-game
  subset 36/96. Temporal: among full games with the opponent's second landed TRAIN by t151
  (n=28) we lead at t150 in 26/28 but win 7/28, mean margin +64.89 → −57.29.
- **Association and uncertainty.** Final roster is endogenous — this is coverage and
  motivation, never the trigger and never a causal estimate. The interval excludes zero but
  the assignment is not random.
- **Smallest seam.** The already-reconstructed Phase-21 operation on tracked opponent-created
  existing trees at ETA ≤6: `candidate.score += candidate.score`. C1 arms permanently at the
  first decision whose **public state** shows ≥3 opponent units — no future TRAIN, no final
  roster, no identity, no score-behind state, no new threshold. Initial roster is 1, so
  "≥3 units" is exactly two landed TRAINs, matching the evidence definition.
- **Value.** Current: none — this is a value-unknown test. Projected ceiling only, explicitly
  a projection: holding scaled opponents' last two windows to their non-scaled rate is
  (79.81−21.17)+(102.19−25.60) = **135 margin per affected game** over 36/96 games. Complete
  suppression is not achievable; the number is an upper bound, and its purpose is to show the
  prize is two to three orders of magnitude larger than anything else in this package.
- **First check.** `python3 chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test`
  — **I ran it: `self-test: ok`, exit 0** — then
  `python3 -m pytest -q tests/test_h3a_pressure_treatment_reconstruction.py`. Then the frozen
  three-arm configuration: C0 `a8eb3b2b…` never active, A1 `083107f5…` always active, C1
  identical but conditioned and sticky; 128 unsealed official roots × both seats × eight
  families × three arms = 6,144 paired tasks, with a runner that proves C1 byte-equals C0
  before live worker three and byte-equals A1 after.
- **Pass / stop.** Every frozen H3a gate: C1−C0 ≥ +2 paired margin with clustered lower bound
  > 0; C1−A1 ≥ +5 with lower bound > 0; both seats nonnegative; ≥6/8 families nonnegative;
  worst family ≥ −1; no worse catastrophes; negative-margin mass ≤ 1.05× C0; own-score loss
  ≤ 1. Stop on integrity failure, insufficient activation, C1 ≈ A1, or any seat/family/tail
  failure. A pass authorizes confirmation, **not** an Arena submission.
- **Closure distinction.** `docs/CONSTRAINTS.md:512` requires exactly this three-arm design
  and forbids implementing a conditional opponent-crop bonus or citing value without it. The
  A1 arm is what makes conditioning falsifiable rather than assumed — and A1 is not a
  hypothetical: it is submission `41012867`/agent `6560350`, **rejected at the 63-game Arena
  gate at 16.51 against a 24.28 control, −7.77**. Multiplier, ETA, target grammar and
  commitment stay frozen.
- **Honest readiness.** The **value runner does not exist.** `cgauto/` contains no H3a runner
  and no byte-equality prover. The two commands above are a reconstruction self-test, not the
  value evidence. Calling this an "immediate check" overstates it by one substantial build.
- **Confidence.** Medium that the test is worth its cost; **no confidence whatever that it
  will pass** — its always-on twin lost 7.77 rating.
- **Rubric.** Evidence 23 / specificity 22 / decisiveness 17 (runner absent) / payoff 20 =
  **82** — immediate-check shortlist.

### Rank 2 — endgame conversion removal race · `NOT INDEPENDENT`, but I add corpus support

- **Mechanism / IDs.** In `897780884` we issue 12 PLANT commands — t245, 253, 254, 259, 259,
  265, 265, 271, 274, 278, 282, 288 — of which **11, not 12, are after the turn-250 endgame
  rule**. The five APPLE conversions at t271/274/278/282/288 are exactly reproducible.
  Astrobytes issues 120 CHOP commands in t201–300 against our 76.
- **Affected k/n and uncertainty.** Direct evidence is **1/153 games** and may not be called
  broad. What I can add beyond n=1: across the 36 scaled-opponent full games, opponent chops
  landed correlate **−0.379** with our margin. That is corpus-level support for the family —
  but it is **collinear with opponent roster (−0.337) and I cannot separate them in this
  package**, so it raises the prior without establishing the mechanism.
- **Smallest seam.** A pre-PICK `KEEP_BANK` alternative in `YamoBot::endgame_candidates`,
  which currently prices our travel/plant/chop/return but no enemy arrival race, and whose
  post-250 PICK/PLANT candidates score 7000/6000 and dominate ordinary work.
- **Value.** Conservative +5 own points and optimistic +33 margin in the one game =
  **+0.033 own or +0.216 margin per cohort game**. Both are far inside the ±0.5 arena noise
  band (`docs/STATE.md` §3). Even complete success is unmeasurable on the ladder.
- **First check and its blocker.** A read-only lineage census over the 153 exact IDs. **It
  does not exist, and neither `chatgpt_1` nor I can run it** — the package contains exactly
  one trajectory, so the census is host-only work by construction. It is not an immediate
  check for either replication agent.
- **Pass / stop.** Every predicted losing conversion keeps its fruit banked, no
  resident-won conversion is vetoed, paired terminal delta positive. Stop if non-recurrent,
  if A/A fails, or if a won crop is suppressed. **The published gate — "optimistic ceiling
  reaches 20 margin/current game" — must state its denominator first.** Per cohort game it
  needs ~93 games as extreme as the one observed and is pre-committed to fail; per affected
  game the single game's 33 already clears it. The two readings differ ~150× and point
  opposite ways.
- **Closure distinction.** Narrower than B3.7 (no plant-pacing rule), D175a and D78/D85, as a
  pre-decision feasibility test only. Do not tune turn 250.
- **Survives my §3 filter** because it suppresses *their* gain, not ours.
- **Confidence.** Low on recurrence, medium on the exact defect.
- **Rubric.** Evidence 16 / specificity 18 / decisiveness 12 / payoff 14 = **60** — below the
  65 "audit first" band. I rank it second because nothing else survives §3, not because it
  scores well.

### No defensible rank 3

I looked for one and did not find one. I decline to pad the list.

## 6. Where I disagree with the integrated local report

Its rank 3, **B3.14 sticky-bank banking**, is an *own-economy* intervention: 99.76% of our
wood is already banked (7,003 of 7,020 — I reproduced this), leaving a hard ceiling of
17×4/153 = **+0.444 own points per game**. Section 3 shows our own output is already higher
in the games we lose. A change that adds at most 0.444 own points per game, in a bot whose
own scoring is not the deficit, cannot matter — and 0.444 is inside the noise band regardless.

**I move it out of the ranking to measurement-only.** If it is run, it should be run as a
cheap closure to stop the question recurring — three replays, existing invariant, existing
test — and not as an improvement. This is a real difference from the local report, argued
from data rather than preference.

I also note the local report demotes B3.14 below the removal-race census *because* its
headroom is "only +0.444 own points/game", when the removal race's own headroom is +0.033
own / +0.216 margin per game — smaller on either measure. The stated rationale argues the
opposite of the order it justifies. My §3 reaches the same order by a different and, I think,
sounder route.

## 7. Rejected, with reasons

- **Own-economy, harvest, banking, conversion and plant-pacing improvements** — §3. Our
  output is already higher in the games we lose.
- **Worker-three scaling**, despite being the single largest structural gap (roster 2.00
  versus top-20's 2.83): closed by A2-1's K1 failure and the opportunistic-only rule.
  Measurement-only.
- **Mining parity** (0.25 versus 2.10 per 100 turns): closed as harmful at workforce ≥2.
- **Generic WAIT cleanup**: our WAIT correlates −0.046 with margin in the games that matter —
  no signal. Independently reached; the local report rejects it too.
- **Action-contention or body-blocking work**: mechanically impossible
  (`docs/CONSTRAINTS.md`, H7′). Note `897781203`, where 106 of our failed PLANTs coincide with
  106 failed rival PLANTs — an exact symmetry I reproduced. Never "clean up" those commands
  without preserving that contention.
- **Anything converting these margins into Arena rating.** Prohibited, and the cross-era
  point stands independently.

## 8. Scope

Committed package and tracked repository files only. No raw cache, host-only path, sealed
data, source or shared-doc edit, analyzer implementation, build, simulation, candidate,
TestSession, Arena or API action, cron change, or peer namespace. I have not read
`chatgpt_1`'s replication.
