# Independent full review replication — current best bot versus recent/top-player games

- Task: `20260802-top-player-full-review-replication`
- Author: `chatgpt_1`
- Date: 2026-08-02 UTC
- Branch: `agent/chatgpt_1-top-player-full-review`
- Frozen package commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`
- Current agent/submission: `6589709` / `41079653`
- Current source SHA-256 prefix: `6f992a5a…`
- Independence: the integrated local report, Claude's narrower review, and Claude's replication were not read before this report was published.
- Platform mutation: none.

## Executive verdict

The strongest current-cohort signal is **not an opening failure and not evidence that the
resident should simply train another worker**. It is a recurrent **late crossover under
opponent scaling**:

- 10/153 open current games have final margin at most `-100` (6.54%; Wilson 95% interval
  3.59%–11.61%);
- all 10 catastrophic opponents finish with roster 3–4, while the resident remains at roster
  2;
- the resident is ahead at turn 150 in 9/10 of those games, but ahead at turn 250 in only
  1/10 and at the end in 0/10;
- those ten games contribute `-1674` total margin, or `-167.4` per catastrophic game.

That association is useful but non-causal. Generic TRAIN timing, worker-3 funding ladders,
and isolated scale grafts are already closed in `docs/CONSTRAINTS.md`; the current cohort
also has no resident-side workforce variation from which to identify a training treatment.
The highest-value permitted discriminator is therefore the existing **H3a mandatory
three-arm experiment**: unchanged control versus the exact opponent-crop treatment always
on versus the same treatment conditioned on the frozen workforce-pressure predicate.

Before spending a panel, run a read-only trigger-readiness audit on the ten exact late
crossovers and matched wins. If the predicate does not activate early enough and selectively
enough, stop H3a rather than retune it.

## 1. Evidence boundary and integrity

Only the task-authorized committed evidence was used:

- `top-player-new-games-shared-2026-08-02.manifest.json`;
- `top-player-new-games-shared-2026-08-02.sides.csv`;
- `top-player-new-games-shared-2026-08-02.direct-game.json`;
- `top-player-new-games-shared-2026-08-02.direct-trajectory.json`;
- the ranking rubric at the same package commit;
- `docs/CONSTRAINTS.md`, `docs/STATE.md`, and `docs/BACKLOG.md`.

Manifest identity and accounting:

| Item | Frozen value |
| --- | ---: |
| Current agent | `6589709` (`tass`) |
| Current submission | `41079653` |
| Current-new open games | 153 |
| Outcomes | 95 wins / 2 ties / 56 losses |
| Seats | 68 seat 0 / 85 seat 1 |
| Splits | 93 calibration / 56 discovery / 4 validation |
| Excluded sealed-tagged games | 7 |
| Direct current-vs-top20 games | 1 (`897780884`) |
| Top20-source open games | 2,684 |
| Top20-vs-top20 open games | 169 |
| Top20 side rows | 2,853 |
| Shared side rows | 5,672 |

Frozen file hashes from the manifest:

| File | Bytes | Physical lines | SHA-256 |
| --- | ---: | ---: | --- |
| `sides.csv` | 1,885,870 | 5,673 | `e4e4923446b6449dca35999fc83e6883cdc78b24fa4f2d17b957e394c1068883` |
| `direct-game.json` | 374,173 | 4,542 | `e1a94b84653493765ca224f80a83fad5563b4ae0efd09fa1793630e77e0e3ba5` |
| `direct-trajectory.json` | 79,504 | 6,302 | `c9d77aedc73e1e1537b17dc08d0948946023795d90aa67fea8e4dca63a228c27` |

The task text refers to an earlier pinned rubric SHA that is not independently resolvable as
a commit. The rubric path itself does resolve at the frozen package commit and has Git blob
SHA `c33f0ad3156ade905dcb106c4d8941ffa74d0973`; that package-commit version is the rubric used
here. This is a provenance defect to correct in the task record, not a reason to substitute a
peer report.

No sealed row, raw cache, host-only path, analyzer, source tree, build, simulation, candidate,
TestSession, Arena endpoint, or submission was touched.

## 2. Cohort accounting and recurrent loss mode

I define a **catastrophe** before inspecting mechanisms as final resident margin `<= -100`.
The ten qualifying current games are:

| Game | Opponent rank | Final margin | Opponent extra TRAINs / final roster |
| ---: | ---: | ---: | ---: |
| `897780891` | 104 | -166 | 2 / 3 |
| `897781216` | 90 | -126 | 2 / 3 |
| `897781413` | 50 | -219 | 3 / 4 |
| `897781719` | 48 | -416 | 3 / 4 |
| `897781840` | 50 | -141 | 3 / 4 |
| `897781987` | 33 | -100 | 3 / 4 |
| `897782076` | 34 | -115 | 3 / 4 |
| `897782213` | 42 | -113 | 2 / 3 |
| `897782302` | 44 | -169 | 2 / 3 |
| `897782366` | 33 | -109 | 3 / 4 |

The current side records one TRAIN and final roster 2 in 153/153 current rows. Thus the
catastrophe association cannot estimate the value of a resident training intervention: the
resident treatment has zero variation, and opponent scaling is entangled with every other
opponent-policy difference.

### Temporal order

Number of the ten catastrophic games in which the resident is still ahead:

| Checkpoint | Ahead k/10 |
| --- | ---: |
| Turn 50 | 9/10 |
| Turn 100 | 10/10 |
| Turn 150 | 9/10 |
| Turn 200 | 6/10 |
| Turn 250 | 1/10 |
| Final | 0/10 |

This is the decisive recurrent pattern: the resident usually establishes a lead, retains it
through the first half, then loses it during the late scaling/production phase. It is not a
recurrent opening-score collapse.

### Rank-band comparison

| Opponent band | Catastrophes | Rate | Wilson 95% interval |
| --- | ---: | ---: | ---: |
| Rank 13 direct | 0/1 | 0.00% | 0.00%–79.35% |
| Rank 21–50 | 8/73 | 10.96% | 5.66%–20.16% |
| Rank 51–100 | 1/52 | 1.92% | 0.34%–10.12% |
| Rank 101+ | 1/27 | 3.70% | 0.66%–18.28% |
| All current | 10/153 | 6.54% | 3.59%–11.61% |

Eight of the ten catastrophes occur in rank 21–50, but the intervals are broad and opponent
selection is not randomized. This supports prioritizing a discriminator against strong
scaling opponents; it does not establish a rank-conditional production policy.

### Matched-opponent checks

The association is not merely a single opponent identity:

- Against rank-48 `Wld`, game `897781719` loses `-416` when the opponent reaches four
  workers. Games `897782128`, `897782246`, and `897781650` beat the same opponent by `+158`,
  `+157`, and `+194` when that opponent does not scale. However, `897781674` is a clear
  counterexample: the opponent scales and the resident still wins `+91`.
- Against rank-42 `_H3R0_`, `897782213` loses `-113` when the opponent reaches three workers,
  while `897782201` and `897782068` win `+147` and `+119` under less opponent scaling.

These pairs strengthen the late-scale association but also prove that opponent workforce is
not sufficient as a causal rule. A treatment must target what scaling changes in competitive
resource control, not blindly mirror the TRAIN count.

## 3. Current versus top-player benchmark

The benchmark is 2,684 open top20-source games, including 169 top20-vs-top20 games and 2,853
top20 side rows. It is observational context, not treatment evidence. The one exact direct
comparison is game `897780884` against rank-13 Astrobytes; it receives its own postmortem
below.

The reproducible current-side contrast is stark: 153/153 current rows finish at roster 2,
whereas all ten catastrophic opponents finish at roster 3–4. Existing project evidence in
`docs/CONSTRAINTS.md` already explains why this cannot be turned into “train worker 3”:
worker-3 value belongs to a coupled renewable economy and role policy; isolated funding,
retiming, and transplant branches have failed.

I do not report a new top20-wide causal action-rate delta. The full benchmark contains
cross-agent, cross-opponent, cross-seat observational rows; no allowed intervention varies a
single mechanism. Detailed top20-wide turn-level action/resource aggregation was not
independently rerun in this no-analyzer execution. Any unsupported benchmark turn-level
claim is therefore **UNAVAILABLE_FROM_PACKAGE in this replication**, rather than inferred
from another report.

## 4. Direct game `897780884`: exact postmortem

### Identity and outcome

- Opponent: rank-13 `Astrobytes`, agent `6482167`, seat 0.
- Current: `tass`, agent `6589709`, seat 1.
- Final in-game score: Astrobytes 403, current 333; current margin `-70`.
- This is the sole direct current-vs-top20 game. It is one exact example, not broad field
  evidence.

Checkpoint score, written current–Astrobytes:

| Turn | Score |
| ---: | ---: |
| 50 | 53–24 |
| 100 | 125–32 |
| 150 | 181–69 |
| 200 | 237–160 |
| 250 | 292–293 |
| 300/final | 333–403 |

The current bot leads through turn 200 and crosses behind around turn 250. This matches the
cohort's late-crossover pattern even though the final margin is not catastrophic.

### Workforce trajectory

- Astrobytes TRAINs at turns 1, 56, and 105 and finishes with roster 4.
- Current TRAINs at turn 11 and finishes with roster 2.

Again, this is an architectural contrast, not an isolated TRAIN-treatment estimate.

### First 40 rounds

The exact early command sequence exposes a large strategic asymmetry:

- Astrobytes: TRAIN at turn 1; PLANT plum at 3, apple at 5, banana at 7, lemon at 31, plum at
  34; MINE at 10, 11, and 24; interleaved HARVEST/PICK/DROP cycles.
- Current: HARVEST at 2 and DROP at 3; five consecutive WAIT commands at turns 4–8;
  HARVEST at 9, DROP at 10, TRAIN at 11; 24 CHOP commands during turns 14–29; no PLANT or
  MINE through turn 40; then movement/harvest/drop activity.

The current side nevertheless leads strongly at turns 50–200. Therefore the five WAITs or
opening CHOP concentration cannot be promoted as the cause of the final loss from this game
alone. Whether a productive legal action existed on each WAIT turn—after movement,
occupancy, capacity, transaction, and target legality—is **UNAVAILABLE_FROM_PACKAGE** without
a dedicated exact-replay legality audit.

### Highest-leverage correction inferred from the direct game

The correction is not “copy Astrobytes' opening” and not “TRAIN at turn 1.” The direct game
shows that the resident's opening creates a large midgame lead, but that lead is not defended
against the opponent's later workforce and renewable production. The narrow current
question is whether workforce pressure should activate a stronger priority on existing
opponent crops while preserving the resident's known-good opening and scheduler.

## 5. Ranked immediately checkable improvements

### Rank 1 — H3a exact three-arm workforce-pressure-conditioned opponent-crop priority

**Rubric score: 84/100 — immediate-check shortlist. Confidence: medium (0.75).**

- Evidence: 21/25. Exact 10/153 recurrent catastrophes, exact IDs, temporal order and direct
  game; association remains non-causal.
- Specificity: 24/25. One existing pressure predicate and one seven-site target-score
  treatment; no TRAIN or scheduler edits.
- Immediate decisiveness: 23/25. Mandatory three-arm, same-map, both-seat paired design with
  integrity and stop gates.
- Payoff/safety: 16/25. Tail mass is material, but treatment displacement and opponent
  benefit remain unknown.

**Mechanism.** Under the already frozen H3a workforce-pressure predicate, increase priority
for tracked existing opponent trees within the exact ETA boundary. Compare this conditioned
arm against both the identical treatment always on and an unchanged resident. The
conditioned-versus-always-on contrast tests the proposed pressure mechanism; conditioned
versus control tests value.

**Affected evidence.** Primary observational target: the 10/153 catastrophic late
crossovers listed above. Supporting direct example: `897780884`, where the current lead
persists to turn 200 and disappears near turn 250. This does not imply all 11 games would be
changed by H3a; trigger coverage is the first audit.

**Association and uncertainty.** All ten catastrophic opponents scale, but scaling is a
bundle of opponent competence and economy. The experiment must not alter resident workforce.
The 6.54% catastrophe rate has Wilson 95% interval 3.59%–11.61%.

**Smallest source seam.** Only the already reconstructed seven opponent-tree candidate-score
sites in `rust/src/bin/yamo_orchard_live.rs`: the exact existing treatment doubles the
candidate score for a tracked existing opponent tree within ETA `<= 6`. The conditioned arm
wraps those same seven expressions in the frozen H3a pressure predicate. No other action,
threshold, crop catalog, TRAIN, funding, routing, or scheduler code changes.

**Current versus projected value.** The ten catastrophes contain `1674` points of negative
margin headroom. This is an upper bound, not expected value. A deliberately conservative
20% recovery projection is `334.8` total margin, or `+2.19` mean margin across all 153 games.
It is not an Arena-rating estimate.

**Exact first check: trigger-readiness audit before building a panel.** On the ten catastrophe
IDs and the matched wins named above, evaluate the frozen H3a predicate and exact ETA-6 tree
eligibility from committed trajectories/replays. Do not tune the predicate.

Preflight pass:

1. predicate becomes true by turn 150 in at least 8/10 catastrophe games;
2. its first true turn precedes the resident's observed lead-collapse interval in at least
   8/10;
3. false-positive activation by turn 150 is at most 20% on the named matched winning controls;
4. at least one exact eligible opponent-tree scoring decision exists after activation in at
   least 6/10 catastrophes.

Preflight stop: any gate above fails, state reconstruction is ambiguous, or an exact eligible
score site cannot be tied to the frozen treatment. Do not retune thresholds after failure.

**Exact three-arm config after preflight:**

```text
CONTROL       = byte-identical resident
ALWAYS_ON     = exact seven-site opponent-tree score treatment, ETA <= 6
CONDITIONED   = identical seven-site treatment only while frozen H3a pressure predicate true
PANEL         = same unsealed official maps/seeds, both seats, paired referee/resident semantics
PRIMARY       = CONDITIONED - ALWAYS_ON
SECONDARY     = CONDITIONED - CONTROL
```

Panel pass:

- primary paired mean margin `> 0` with 95% CI lower bound `>= 0`;
- secondary paired mean margin `>= +5.0`;
- secondary mean positive in both seats and at least 4/6 opponent families;
- catastrophe count does not increase versus control;
- opponent score does not increase versus control;
- all source/binary/referee/map/range hashes and the exact seven-edit diff pass.

Panel stop: primary `<= 0`, secondary `< +5`, either seat negative, breadth gate fails,
catastrophes or opponent score increase, or any identity/hash/scope mismatch. No Arena action
follows qualification automatically.

**Closure distinction.** This is not generic TRAIN retiming, a worker-3 graft, a fixed
opening, an always-on crop bonus, or an isolated crop-removal policy. The required
conditioned-versus-always-on arm is what distinguishes H3a from the closed opponent-crop
bonus/focus grids.

### Rank 2 — Read-only late-crossover/pressure discriminator for H3a

**Rubric score: 74/100 — audit first. Confidence: medium-high as a diagnostic (0.80), low as
field value.**

**Mechanism.** Turn the exact catastrophe slice into a deterministic preflight that asks
whether the frozen pressure predicate and an eligible existing opponent-tree decision occur
before the lead crossover. This is a protocol improvement: it prevents spending an official
panel on a trigger that does not cover the observed failure mode.

**Affected evidence.** 10/153 catastrophe games; matched controls:
`897782128`, `897782246`, `897781650`, `897781674`, `897782379`, `897782201`, and
`897782068`. The direct game `897780884` is a separate supporting trace.

**Association and uncertainty.** The late crossover is recurrent, but the exact pressure
predicate's coverage is not yet measured in this package review. The audit can falsify
relevance, not prove value.

**Smallest seam.** No resident-policy edit. Read the existing frozen H3a predicate and the
existing seven score-site eligibility state in exact replay. If later promoted, the only
resident seam remains Rank 1's seven sites.

**Current versus projected value.** Current value is zero policy change and avoided experiment
cost. Projected value is the same `+2.19` whole-cohort mean-margin scenario only if Rank 1
later passes; this audit itself claims no margin.

**First check, pass, and stop.** Use exactly Rank 1's four preflight gates. Pass releases the
three-arm panel; failure closes this current-cohort justification for H3a without threshold
retuning.

**Closure distinction.** This is read-only recurrence/coverage measurement, not a new
workforce policy, identity selector, maturity conditional, or outcome-triggered policy.

### Rank 3 — Direct-game WAIT legality and precedence audit

**Rubric score: 58/100 — do not build before the audit. Confidence: low (0.40).**

**Mechanism.** Determine whether the five WAITs at turns 4–8 in `897780884` are genuine
execution defects—productive legal action existed and was lost to precedence—or legal
consequences of occupancy, capacity, transaction, or target constraints.

**Affected evidence.** 1/153 games, specifically one five-turn sequence in `897780884`.
No recurrence claim is supported.

**Association and uncertainty.** The game is a late loss despite a large midgame lead, so
removing early WAITs may have no terminal value. Exact action legality is currently
`UNAVAILABLE_FROM_PACKAGE`.

**Smallest source seam.** Only the final action-selection branch that emits WAIT after all
legality checks; no fixed opening script and no target-score bundle.

**Current versus projected value.** Current measured headroom is unknown. Projected value is
zero until a legal productive alternative is proved on at least three of the five turns and
a one-line precedence change reproduces that alternative under exact resident semantics.

**Exact first check.** Replay turns 4–8 with post-move shack occupancy, inventory capacity,
transaction ordering, target ownership/reachability, and all candidate actions logged.

Audit pass: at least 3/5 WAIT turns have an unambiguously legal productive action that the
current selector generated and then discarded solely through one identified precedence
condition. Audit stop: fewer than 3/5, no generated legal candidate, multiple interacting
causes, or any need for a fixed turn/map prefix. A passed audit permits only a narrow
one-condition replay patch followed by same-map/both-seat testing; otherwise close.

**Closure distinction.** This is not a fixed opening harvest/drop script or generic idle-work
wrapper. It survives only if exact replay proves one current-source execution invariant.

## 6. Candidates rejected or retained as measurement-only

### “Train another worker” — rejected

The 10/10 association is visually strong but confounded, while the resident has no workforce
variation in 153/153 games. More importantly, generic TRAIN retiming, isolated worker-3
funding, direct policy transplantation, fixed funding ladders, and late bridges are already
closed. Reopening would require a materially different whole-economy representation, not an
immediate edit.

### B3.14 bank commitment — recurrence not established

The package does not provide a reproduced current-source bank-commitment failure trace with
legal-action proof. Existing constraints cap its current contribution and retain it as
read-only/audit-only. Do not promote.

### B3.15 on-tree-owner invariant — recurrence not established

No current recurrence is established from the authorized fields. Do not backport or build.

### B3.11 relative species-control feasibility — precheck only

The package aggregates fruit/resource behavior but does not establish the required relative
species-control provenance and feasibility predicate. Exact control/provenance claims are
`UNAVAILABLE_FROM_PACKAGE`; only a future read-only precheck is permitted.

## 7. Final ordering and requested next action

1. **Run the read-only H3a trigger-readiness audit on the exact ten catastrophes plus named
   matched wins.**
2. **Only if it passes, freeze and run the exact H3a three-arm panel.** Do not substitute a
   two-arm control/treatment panel; conditioned-versus-always-on is the mechanism test.
3. Keep the direct-game WAIT sequence as a low-priority legality audit. Do not implement an
   opening patch from one replay.
4. Do not retime TRAIN, add a worker command, or infer Arena rating from margins.

The highest-leverage correction is therefore **pressure-conditioned defense of existing
opponent crops while preserving the resident opening and scheduler**, tested through the
mandatory H3a three-arm design. The evidence motivates this discriminator; it does not yet
establish field value.
