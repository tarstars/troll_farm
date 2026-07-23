# Curriculum Level 5 D11 sole four-million-transition PPO result — 2026-07-20

## Frozen run

The backend benchmark selected local CPU because YT failed the preregistered recipe-floor parity
limit, despite a large time advantage.  This is therefore the sole run authorized by the D11
learning protocol:

- initialization NPZ SHA-256
  `182a7fd6e738070a38c8f31d617824be851f099d9bc7071d6720dbedaa34cd99`;
- model seed 139 and environment stream beginning at 7,400,000;
- 100 environments x 100 decisions per update;
- Stage A at 1,000,000 and final at 4,000,000 transitions;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` decaying linearly to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value coefficient 0.5,
  reward scale 0.01, gradient norm 0.5, target KL 0.03; and
- constant legal-teacher auxiliary coefficient 0.10 with 14 CPU threads.

## Stage A — pass

At exactly 1,000,000 transitions, the deterministic actor was evaluated once on the complete
development interval `[6500, 7000)`:

| Gate metric | Result | L5A floor | Verdict |
|---|---:|---:|---|
| Overall success | 95.40% | 85% | pass |
| Nontrivial success | 93.92% | 82% | pass |
| Worst recipe | 88.33% | 75% | pass |
| Worst height | 90.40% | 78% | pass |
| Terminal crop | 96.40% | 80% | pass |
| Renewable harvest | 96.40% | 90% | pass |
| Paired teacher median delay | 0 turns | <=35 | pass |
| Original D11 opponent-mechanism gate | pass | pass | pass |

The opponent retained at most three workers and three destructions; at least three destructions
occurred in 94.20% of episodes.  The Stage-A checkpoint SHA-256 is
`1addcb82d38e16b60e0cff908b815c5a78439cc02511825597102f9590c23698`; its evaluation SHA-256 is
`52535989067ef7ef2d17d494aba39fe4939455db2155d9e32e0c3b3cba2ae514`.

**Decision:** Stage A passes, so the same uninterrupted run continues through the remaining three
million transitions.  Stage A is not a selectable candidate and no prospective seed has been
opened.

## Final

The same uninterrupted run reached exactly 4,000,000 transitions and was evaluated once on the
complete development interval `[6500, 7000)`:

| Gate metric | Result | Final floor | Verdict |
|---|---:|---:|---|
| Overall success | 97.40% | 90% | pass |
| Nontrivial success | 96.28% | 88% | pass |
| Worst recipe | 90.16% | 82% | pass |
| Worst height | 96.06% | 85% | pass |
| Terminal crop | 97.80% | 90% | pass |
| Renewable harvest | 97.40% | 95% | pass |
| Paired teacher median delay | 0 turns | <=30 | pass |
| Original D11 opponent-mechanism gate | pass | pass | pass |

Every final mechanism floor passed.  The opponent retained at most three workers and three
destructions; at least three destructions occurred in 96.00% of episodes.

The one permitted strict development action audit also passed:

| Action metric | Result | Final gate | Verdict |
|---|---:|---:|---|
| Farmer exact productive command | 92.03% | >=55% | pass |
| Chopper exact productive command | 97.05% | >=90% | pass |
| Empty-seed recovery MOVE verb | 99.93% | >=99% | pass |
| Empty-seed recovery exact source | 45.42% | >=30% | pass |
| Worst nonempty-recipe recovery exact source | 15.81% | >=10% | pass |
| Unjustified current-cell waits | 84 | <=3,000 | pass |

The final checkpoint SHA-256 is
`44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`; the functional
evaluation is `a028ddd1717954130e1674f90cad257d1c50f7ded05b46839218b80fdd211d98`, and the strict
action audit is `e967d83884b42737ebcce9c7690b3bf8f74c2704e0cd8d289d556d2ce3ee5a6c`.

The trainer completed all 400 updates in 4,343.21 seconds of inner wall time
(920.98 transitions/s; 69.61% aggregate host CPU).  Only 27 of 4,000,000 online auxiliary
teacher labels were undefined and skipped under the frozen policy, for 99.999325% legal labels.
The training-summary SHA-256 is
`32b0166580899ef8ceafc0636300304581f3912ab4d7882b561f9c2bb76d3bb2`; outer timing is
`f3a84a25dcdeb3e1a5465f66d4b17cbebe26a7445b4fb02b3f51cbebd3c889a2`.

**Decision:** the sole PPO run passes complete development acceptance and opens exactly one
preregistered prospective confirmation.  It does not authorize checkpoint substitution,
deployment, resident replacement, or Arena submission.
