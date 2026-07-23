# D163a resident-native resource-control component audit — result

Date: 2026-07-23  
Decision: **close the fixed shadow-reserve resource-control grammar**

## Integrity and execution

D163 evaluates exact resident plus the seven nonempty subsets of fruit
routing/banking, IRON routing/banking, and consumption protection at turns
72, 104, and 136. Every intervention lasts at most 32 turns and never creates
or suppresses TRAIN. The panel contains 128 already-consumed tasks on maps
`9,844,144--9,844,151`, disjoint from D162 and from reserved maps.

The one-worker and 20-worker runs each contain exactly 2,816 sorted rows and
are byte-identical at SHA-256
`05d6a2297e60d22415f9809b4bf70faed20480d82f94433ed593b05957f018b2`.
The serial run takes 230.534 seconds; the 20-worker run takes 24.852 seconds,
a 9.3x wall-time speedup while consuming 1,926% aggregate CPU.

Exact resident reproduces D161 on all 128 tasks with zero mismatch. All 21
arms reproduce the resident action/state prefix at activation, activate on at
least 90% of tasks, remain within their horizon, preserve exact workforce and
training counts, and have zero command, provenance, reward, lifecycle,
component-purity, or reserved-map failures. Treatment is real:

| Component | Exercised / enabled rows | Rate |
| --- | ---: | ---: |
| Fruit routing/banking | 1,358 / 1,536 | 88.41% |
| IRON routing/banking | 1,417 / 1,536 | 92.25% |
| Consumption protection | 84 / 1,536 | 5.47% |

Thus the negative result is not a disabled-controller artifact, and all value
comparisons are workforce-independent.

## Factorial causal result

Each component has 1,536 paired observations across the other flags, three
starts, both seats, eight maps, and eight opponent families.

| Component | Mean margin effect | Map-clustered normal 95% interval | Positive families | Own / opponent score effect | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Fruit | -1.982 | [-5.408, +1.444] | 1 / 8 | +0.774 / +2.757 | fail |
| IRON | -3.551 | [-5.691, -1.412] | 0 / 8 | -2.994 / +0.557 | fail |
| Protection | -0.029 | [-0.094, +0.035] | 1 / 8 | +0.024 / +0.053 | fail |

Fruit routing sometimes adds own score and reduces pooled negative-margin
mass from 4,170 to 3,972, but it adds still more opponent score, is negative
in both seats and all three starts, and is positive only against
`gold_adaptive`. Its worst family effect is -6.969 against
`legend_balanced`.

IRON routing is robustly harmful: its whole clustered interval is below zero,
all eight family means are negative, catastrophes rise from 12 to 16, and
negative-margin mass rises from 3,997 to 4,145. Its worst family effect is
-8.938 against `norx_native_three`.

Protection is an adequately exercised but essentially null treatment. Turn
72 is exactly inert; turns 104 and 136 remain near zero, with no stable seat,
start, or family support. Its negative-margin mass rises from 4,044 to 4,098.

## Interactions and fixed arms

Fruit x IRON has a positive difference-in-differences of +2.665, but its
clustered interval `[-1.405, +6.736]` crosses zero. This means their combined
harm is sometimes subadditive; it does not make the combination beneficial.
Fruit x protection (+0.027) and IRON x protection (+0.046) are null. The
three-way interaction is small and negative at -0.279 with interval
`[-0.518, -0.039]`.

No fixed arm passes. All 21 have nonpositive resident-relative mean margin.
The best is the inert `protection_t072_h032` at exactly zero on all 128 tasks.
The best action-changing arm is `protection_t136_h032` at -0.148
(`5` improvements, `116` ties, `7` regressions). The best routing arm is
`fruit_protection_t136_h032` at -2.211. Several combined or early IRON arms
are significantly negative.

## Interpretation and next move

D162's positive hindsight envelope does not decompose into a transport,
mining, or protection mechanism on a disjoint consumed panel. The stable fact
is opportunity cost: taking a worker away from exact resident work to fill a
fixed shadow reserve usually helps the opponent more than us, while passive
protection is too rare and too weak to matter.

Close this grammar. Do not tune the reserve vector, extend the horizon, choose
D162/D163 winners by task, build a state gate, or spend fresh maps on another
resource-control variant. This also removes the remaining justification for a
resident-native capital controller.

The next experiment should change abstraction rather than refine this branch:
refresh the public Arena replay/leaderboard corpus and audit current-resident
losses for recurring opponent actions and state transitions that are absent
from the local proxy panel. Any new intervention must be motivated by that
fresh distribution evidence, not by another shadow-bill schedule.

## Reproducibility

- protocol SHA-256:
  `b576344d73768e11d80bf4210a2f7192d3d96a4b3b0347a9e48fe9befbee0650`;
- lock SHA-256:
  `856f957b0e0a55fa96af767145d57783d32179b92f7362d2fa043a8c1955026a`;
- build script SHA-256:
  `e06e96bf7ba9f1b2a3eb99444a7cd380058e493f4377a0116f13d287921e5c6f`;
- runner SHA-256:
  `08c669d60f2bc6681760e963070ff67e3d0157914cdde00bfbef65e88f94e7fc`;
- analyzer SHA-256:
  `d10945abc3f768f2a30a0e82b823fee6c427fecd1d57ea58b8568e1e600d13ec`;
- machine-result SHA-256:
  `560e5651ae0f8079175db5d521cedf9021c807a4d69c2b8d2e6b2487fa69afe7`.
