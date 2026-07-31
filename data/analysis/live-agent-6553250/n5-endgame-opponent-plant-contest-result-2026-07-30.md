# N5 — endgame opponent-plant contest result

**Verdict: `NO_MATERIAL_CONTEST_OPPORTUNITY`.**

The missing design instruction describes a real and common situation, but even a
deliberately generous replay-conditioned valuation stays below the frozen 20-margin
threshold across the resident's full game population. No policy experiment, resident
change, submission, TestSession, or Arena action follows.

## Exact population and integrity

The audit decoded all **382/382 cohort occurrences**: 242 resident occurrences and 140
yamo occurrences, representing 381 unique games because game `896350293` contains both.
The original frozen index selection was reused through its exact previously validated
input manifest after the live collector advanced from 9,082 to 9,372 rows. The manifest,
cohort-list, dependency, resident, raw-game, and trajectory hashes match. There are zero
decode, turn-count, target-origin, unique-PLANT, or cross-orientation lineage failures.

The exact generation reconstruction reproduces H13:

- resident: **388** opponent generations in **78/170 = 45.88%** of games reaching past
  turn 250, **2.2824** events per reaching game;
- yamo: **205** generations in **37/103 = 35.92%**, **1.9903** per reaching game.

Each event is an opponent-created generation born after turn 250 while the subject's
pre-turn bank-score margin is positive.

## What the resident leaves available

The geometry supports the design intuition. **287/388 = 73.97%** of target generations
are within Manhattan distance two of the opponent shack. Yet the resident has a unit at
ETA ≤1 for only **24/388 = 6.19%**, and subsequently contacts only
**51/388 = 13.14%**. Static-board reach within the observed remaining turns is much
broader, **366/388 = 94.33%**; this is optimistic access, not evidence that diverting a
unit is free. ETA now uses the literal post-birth lineage state; zero resident targets
have ETA 0, while 24 have ETA ≤1.

Opponents extract 1,487 carried score-equivalent units from the resident target
generations, while the resident extracts 241. These are `fruit + 4×wood` cargo gains.
They are not banked score: carried fruit or wood scores zero until dropped.

The frozen generous quantity credits both denial of every observed opponent unit and
capture/banking of the same value by the resident. It is therefore
`2 × opponent extracted score-equivalent` for generations optimistically reachable in
the remaining turns:

- conditional on the 78 resident target games: **37.2051**;
- across all 242 resident games, including zeros: **11.9917**, whole-game bootstrap
  95% CI **[8.7273, 15.7603]**;
- stricter never-contacted version across all resident games: **10.3140**;
- identical descriptive yamo quantity: **8.4714**, CI **[5.2571, 12.1004]**.

The target-game conditional number is not the decision unit: a policy's population
effect includes every game in which its trigger has no realized opponent yield. The
all-game upper confidence limit remains 4.24 points below the frozen 20-margin gate.

## Interpretation and boundary

There is no contradiction between early orchard reproduction and late conversion of
fruit into wood. N5 addresses the opponent's late generations only. It also does not
reopen H7: enemy units can share cells, so parking cannot body-block a plant. The only
plausible mechanism is positioning for a later HARVEST or CHOP.

This audit is observational. A changed route would alter later actions and crop growth,
so the factor-two result is a replay-conditioned ceiling on observed yield, not a
theoretical or causal policy-value bound. The result closes N5 as a current experiment
lead under its frozen gate; it does not claim the mechanic has literally zero value.

## Reproduction

```text
python3 -m py_compile cgauto/endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py --self-test
python3 -m pytest -q tests/test_endgame_opponent_plant_contest.py
python3 cgauto/endgame_opponent_plant_contest.py \
  --corpus-root ../troll_farm \
  --frozen-input-manifest \
    ../troll_farm/local_codex_1/n5-endgame-opponent-plant-contest/input-manifest.json \
  --output-dir local_codex_1/n5-endgame-opponent-plant-contest \
  --jobs 4
```

Compile and self-test pass; twelve tests pass. A second four-process full run reproduces
all four output hashes byte-for-byte. Canonical compact result:
`data/analysis/live-agent-6553250/n5-endgame-opponent-plant-contest-result.json`.
Machine bundle: `local_codex_1/n5-endgame-opponent-plant-contest/`.

## Review correction

The independent review found two protocol blockers. Both are corrected:

- `subject_eta_at_birth` now reads `states[birth_turn]`, the state containing the new
  generation, rather than the pre-PLANT state;
- focused tests now cover successful exact-generation cargo accounting, death/feller
  classification, BFS plus movement-speed ceiling division, strict turn/origin/pre-margin
  target filtering, unique successful PLANT, and cross-orientation lineage agreement.

The literal indexing change moves resident ETA-0 count 5→0 and reachable-within-remaining
count 368→366; the two removed reachable targets have zero opponent yield. Therefore the
primary mean, interval, and verdict remain exactly 11.9917, [8.7273,15.7603], and
`NO_MATERIAL_CONTEST_OPPORTUNITY`. Canonical closure awaits narrow corrected re-review.
