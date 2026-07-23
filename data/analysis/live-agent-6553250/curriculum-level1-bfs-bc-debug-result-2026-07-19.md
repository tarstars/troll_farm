# Curriculum Level 1 BFS + BC debug result — 2026-07-19

## Verdict

**Part D passes all frozen gates.**  A 34,926-parameter spatial policy behavior-cloned from 100,000
teacher states solves 834/1,000 unseen debug maps.  It clears the functional, nontrivial, height,
completion-time, HARVEST, and DROP thresholds.  This authorizes a fresh clone on the official
training stream followed by PPO; it does not authorize held-out evaluation, deployment, or Arena
writes by itself.

## Result

Training used model seed 41 and teacher trajectories beginning at seed 0.  Labels were 82,003 MOVE,
9,019 HARVEST, and 8,978 DROP.  Two online cross-entropy passes per 1,000-state chunk took 49.06
seconds, peaked below 0.9 GiB RSS, and used 66.1% aggregate host CPU.  Final chunk accuracy was
83.3%; teacher generation solved 2,160/2,162 completed episodes.

Prospective debug evaluation on seeds 5,000--5,999:

| Gate | Frozen boundary | Observed | Verdict |
|---|---:|---:|---|
| overall success | >=80% | 83.4% | pass |
| nonzero-deficit success | >=75% | 80.94% (705/871) | pass |
| height-bucket floor | >=65% | 79.92% | pass |
| paired median teacher delay | <=15 turns | 0 turns | pass |
| legal HARVEST selection | >=80% | 83.75% (3,975/4,746) | pass |
| legal DROP selection | >=80% | 100% (3,615/3,615) | pass |

Median successful completion is turn 36 versus teacher turn 35 on the full bank, while the paired
median difference on jointly solved maps is zero.  Success by initial LEMON deficit remains broad:
92.17%, 86.21%, 81.51%, 76.80%, 79.09%, 77.11%, 85.15%, and 67.65% for deficits 1 through 8.

## Causal interpretation

The predecessor with implicit path geometry solved 3/876 nontrivial maps after 250k PPO steps.
Adding explicit BFS fields plus teacher initialization solves 705/871 after 100k labels.  Because
both modifications were bundled, this experiment does not separately estimate their effects, but
it establishes the combined successor's capability and validates the diagnosis: the main failure
was destination/phase representation and initialization, not simulator throughput or inability of
the compact spatial head to express direct actions.

Residual errors concentrate at the hardest deficit-8 maps and at 771 legal HARVEST opportunities
where the policy moves instead.  They are appropriate PPO targets; no further debug tuning is
authorized before the official Stage A result.

## Checksums

- training summary: `3327b870392650c0f54663e81e9aadbda9213b14ccfdcccd48f65b05cd965c7d`
- functional evaluation: `96e8a830c54f4255e9049c3bb05a2b9cb1d2e9df16dcf8ea0f8a14e06a53b29d`
- action audit: `dbc5a71670faa959af1c975c48cdc8f413580b90abf697dd03ad0fd74749f7b6`
- checkpoint: `90ea38c50bfc0fa52df09b64e1d1b193f73bf313c3427fd864e1c330e63bfe0d`

