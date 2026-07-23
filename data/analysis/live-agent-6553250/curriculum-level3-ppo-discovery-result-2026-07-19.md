# Curriculum Level 3 corrected PPO discovery result — 2026-07-19

## Verdict

Pass.  The corrected four-million-decision run clears the frozen prospective functional gate and
the separately frozen role-action audit.  It improves both closed-loop reliability and the clone's
weak farmer target precision.  This authorizes exactly one independently seeded confirmation; it
does not yet accept Level 3, change the resident, or authorize an Arena submission.

## Prospective functional result

The deterministic final actor was evaluated on exact seeds 2,011,000--2,012,999 (2,000 episodes,
240 referee turns), whose teacher and random controls were frozen before learned evaluation.

| Metric | Final PPO | Frozen gate | Margin |
|---|---:|---:|---:|
| Overall success | 1,986/2,000 (99.30%) | 90% | +9.30 pp |
| Nontrivial success | 1,384/1,395 (99.21%) | 85% | +14.21 pp |
| Worst height success | 99.00% | 80% | +19.00 pp |
| Tracked crop created | 99.35% | 92% | +7.35 pp |
| Renewable harvest | 99.40% | 90% | +9.40 pp |
| Advantage over random legal | +99.30 pp | +50 pp | +49.30 pp |
| Paired teacher median delay | 0 turns | <=30 | 30 turns |

The four height buckets score 99.00% (8), 99.40% (9), 99.40% (10), and 99.40% (11).  Median
training/completion turns are 18/45 and median post-training score gain is 15.  The deterministic
teacher completes at median turn 46 on the same bank, so PPO is one turn faster in the aggregate
while retaining every required renewable milestone.

Relative to the 600,000-decision clone, PPO raises overall success from 95.20% to 99.30%, crop
creation from 95.40% to 99.35%, and renewable harvest from 96.35% to 99.40%.

## Strict role-action audit

The audit uses the same exact bank but scores actions only at post-training productive teacher
opportunities, including exact spatial targets.  Waiting on the tracked unripe BANANA crop is the
sole exemption.

| Role/metric | Clone diagnostic | Final PPO | Frozen gate |
|---|---:|---:|---:|
| Chopper exact productive choice | 88.42% | 95.43% | >=60% |
| Farmer exact productive choice | 55.39% | 84.63% | >=60% |
| Chopper productive verb | 99.21% | 99.38% | diagnostic |
| Farmer productive verb | 91.25% | 92.45% | diagnostic |
| Combined unjustified current waits | 11,273 | 24 | <=20,000 |

The previously localized farmer spatial-target deficit improves by 29.24 percentage points and
now clears its threshold by 24.63 points.  There are 37,111 justified waits on the tracked unripe
crop; they are excluded exactly as precommitted.

## Training and amendment observations

Stage A passed at one million decisions with 98.45% overall success.  The unchanged run then
completed all 400 updates and improved to 99.30%.  Across four million auxiliary labels, 762
(0.01905%) were undefined because learner-diverged states made the deterministic teacher target
illegal.  The frozen amendment skipped only those rows; valid auxiliary labels, PPO data, rewards,
and masks were unchanged.  All losses remained finite.

Wall time was 4,026.54 seconds and process CPU time was 56,170.14 seconds, equal to 69.75% of the
20-logical-CPU host.  The final deterministic evaluation processed 192,500 actor decisions at
10,720 decisions/s.

## Reproducibility anchors

- final checkpoint:
  `e2e211882c679e682529ce069ee9b1f5c29e36a02f8de45d4b888b6c21645afd`;
- exact final evaluation:
  `5480d9acc13438e23c4463c76bfdfb159a5ade35a275e921c721309bf513d0dc`;
- full training summary:
  `25bc0b372c3a6f71af69e444ed215f8df554e7635dd2613b05c51a7da490e2a5`;
- strict action audit:
  `fbf3bfea00002406b526f14de34526cb2ae78b4257ccd12f6dc70e142ae379ed`;
- corrected trainer:
  `e55a8cf1f1ff3b9bc77b8f24769d35cb89b3098e630574cbb4ab47abb83b4351`;
- frozen base protocol:
  `b43a586e2e8593b5044a219271721ece9c9d273f7cbf4d2b63d7cd86e59f896d`.

## Next eligible experiment

Run the one authorized independent confirmation with model seed 79, new clone/PPO streams, and a
new exact 2,000-seed bank frozen before its controls or labels are generated.  The complete clone,
PPO, functional, and strict role-action sequence must reproduce without tuning.  Level 3 is
accepted only if that confirmation passes.
