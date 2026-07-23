# D31 replay-conditioned official-root option labeler — result (2026-07-20)

## Verdict

**Reject recorded-command continuation as a counterfactual label source.**  The complete frozen
80-game execution reproduces the exact turn-75 resident action in every game and keeps median
control fidelity for all 50 turns, but it fails seven conjunctive gates.  Recorded actions become
invalid after endogenous state divergence often enough that neither the control trajectory nor the
fixed-opponent option branch is trustworthy as an official-root value label.

No checkpoint suffix was inspected, no candidate was constructed, no Arena submission occurred,
and D29b remains closed.

## Fidelity result

| Measure | Observed | Frozen gate | Result |
|---|---:|---:|:---:|
| Complete identity-clean roots | 80/80 | 80/80 | pass |
| Exact warmed-resident root command | 80/80 | 80/80 | pass |
| Exact control command turns | 3,474/4,000 = 86.85% | >=95% | **fail** |
| Games exact for all 50 turns | 57/80 | >=60 | **fail** |
| Material-exact turn-125 states | 54/80 | >=72 | **fail** |
| Position-exact turn-125 states | 56/80 | >=64 | **fail** |
| Fully exact turn-125 states | 52/80 | >=60 | **fail** |
| Own/opponent/margin MAE | 0.213 / 1.488 / 1.500 | <=2 / <=2 / <=3 | pass |
| Opponent-action applicability, control | 97.789% | >=99% | **fail** |
| Opponent-action applicability, option | 94.809% | >=95% | **fail** |

The exact-prefix median is 50 turns and its mean is 41.925, but the lower tail is material: the
minimum is one turn, p05 is 6.95, and p25 is 41.  Small aggregate score errors therefore conceal
state and action divergence in a meaningful minority of games.  Full state identity holds in only
52/80 controls even though 62/80 terminal scores are exact.

## Interpretation at different abstractions

1. **Engine and root reconstruction:** sound.  All roots complete, all turn-75 resident commands
   match, and the three score-error gates pass.
2. **Trajectory fidelity:** insufficient.  A deterministic control can reconverge in terminal
   score while differing in commands, positions, plants, or inventory; terminal-score proximity is
   not evidence that the branch visited the official trajectory.
3. **Opponent validity:** branch-dependent recorded commands are not an adaptive opponent.  Their
   mechanical applicability is already below both frozen floors, with the option branch worse than
   control as expected after state divergence.
4. **Policy-value inference:** invalid.  The descriptive option deltas cannot estimate the value of
   switching against an opponent that observes and responds to the switch.
5. **Project methodology:** official replays are reliable for state-distribution diagnosis and
   exact-prefix audits, but not for long counterfactual labels unless the opponent is run live.

## Descriptive branch output — quarantined

The fixed-action option branch has mean margin delta `-1.988` over all 80 roots.  The seven D29b
switches have descriptive mean `+2.714` with four positives, while the 73 stays average `-2.438`;
prediction/delta Pearson correlation is `0.445`.  These numbers are explicitly **not labels** and
must not be used to train, calibrate, shorten the horizon, tune a threshold, or select a favorable
subset because the fidelity conjunction failed.

## Next eligible experiment

Use actual closed-loop opponents on common official maps.  D32 is frozen to the three opponent/seed
blocks whose exact A/A determinism was established before D29.  It compares the unchanged resident
with a fixed turn-75 permanent farm intervention through `TestSession/play`; a value pass can only
authorize a field-map-native selector and still requires a fresh confirmation bank.

## Reproducibility

- protocol SHA-256:
  `82a4974c22ba258e2911a8879d597b4044b23912d396a47c6a2c1f327d3e19ab`;
- machine result SHA-256:
  `901567a6eae8ee8e0a431bbe069e1f936372017e92c647b309036a97718a93d3`;
- Python analysis source SHA-256:
  `a95f4938c3911b20e7cbc609b353b56bd2486062f33f9fb08e9fc2398907f5c0`;
- Rust continuation source SHA-256:
  `f422b78782afdf7f7b65f251bc320db8968bcdd1ea1379182d7e1e21830c2b40`; and
- release diagnostic binary SHA-256:
  `242b990840d6ae7bc3bdb5b2803ad12d82ffb5fba0230de25b0d31b858bc1498`.
