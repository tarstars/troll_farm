# D110a robust one-use q6 linear population — frozen protocol

Date: 2026-07-22  
Status: frozen before any D110 outcome exists

## Hypothesis and causal change

D109a closes duration-only recurrent PPO. Four times the transition budget still yields `-0.150`
versus D40, 90.039% held activation, five positive families, and a `-7.875` family floor. The
policy reduces both own and opponent scores almost equally. Across independent D108/D109 panels,
family means are uncorrelated (`-0.014`) and rotate by 4.631 points on average.

The q6 representation itself remains strong: D107a's one-use population oracle retains `+31.469`
of the four-use oracle's `+35.227`, while the additional three interventions add only `+3.758`.
On the consumed diagnostic panel, an unselectable random one-use linear policy reaches `+2.648`
with a `-3.625` worst family. These facts support a new abstraction: select a sparse actual policy
by complete-game outcomes, avoiding PPO credit assignment and repeated-intervention interference.

D110a changes the controller and optimizer together. It is a bounded preflight, not evidence that
the D107 controller or any D110 discovery winner is deployable.

## Immutable inputs

- D107 result: `8ab7ca603686cf4bf26e6026429f7df57fc395242bdb4d8606a10c1b28c989c2`;
- D109 result: `22ebe0a9bf3f992e0ed88d92cbbbf1e4b7a8fb1ed635e8d8737a804eeb469e1f`;
- q6 expert bank: `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- population generator: `13cbe478d2d725a25608d1a2e5dd6089a89ca0d1dc9ed4927857228af62d41f5`;
- generated population: `d68eb48e5c091c02472b33c2b6d251dd3bc37dce34a1e06f41908c3e45f6aabb`;
- previously byte-exact D107 runner source:
  `2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514`; and
- release executable: `96030ca2ab75e7b98b74942863b9b4c53124790bf62bf7c6946ab546e3a78547`.

The population is generated from PCG64 seed `11001`: 32 independent 379-weight Gaussian
directions at standard deviation `0.25`, their exact antithetic negatives outside feature zero,
and the same 16-level negative control-threshold ladder (`-0.15` through `-2.40`) on both halves.
Each of the 64 vectors has matched one-use and four-use rows. The generator is outcome-blind.

## Discovery

Run exact complete games on untouched seeds `9,838,000--9,838,015`, both seats and all eight
opponents: 256 tasks. Execute the complete 129-row compatibility grid once with 20 workers. Analyze
only the 64 one-use policies; four-use terminal outcomes are execution by-products and remain
sealed from selection and diagnosis.

Require exact population reconstruction, a complete grid, exact zero-controller reproduction of
D40, finite returns, paired reward error below `1e-4`, zero direct-command/provenance/deposit
failures, and exact controller accounting.

For each one-use policy compute whole-panel metrics and two interleaved map folds. Admit it only if:

- mean margin gain is at least `+1.5` and strict improvement at least 30%;
- both fold means are nonnegative;
- every family is at least `-5` and at least five families are positive;
- own score is nonnegative or opponent score is nonpositive;
- intervention is between 10% and 85%; and
- crop creation is 100% and worker-three reach is within five percentage points of D40.

If none qualify, stop without opening the held rows. Otherwise select exactly one admitted policy
lexicographically by: highest minimum fold mean, highest worst-family mean, highest overall mean,
highest strict rate, then smallest source index. Reorder its unchanged weights into `one_00` in a
new D107-compatible population. No refit, mutation, threshold change, combination, or alternate
selection rule is allowed.

## Repeated held qualification

Only after discovery admission, run controller limit two (exact zero plus selected `one_00`) on
untouched seeds `9,839,000--9,839,031`, both seats and all eight opponents: 512 tasks. Repeat the
entire run from a new process and require byte-identical 1,024-row policy matrices and 512-row
baseline matrices.

Require all mechanics gates again. Fixed-policy value requires mean gain at least `+2`, strict
improvement at least 40%, every family at least `-3`, at least six positive families, nonnegative
own score or nonpositive opponent score, 10%--85% intervention, 100% crop creation, and
worker-three reach within five percentage points of D40.

## Decision

- **Discovery mechanics failure:** repair only; do not interpret value.
- **No discovery admission:** close random one-use linear selection without held evaluation.
- **Held failure:** close random one-use linear selection; do not inspect another random member,
  mutate the selected vector, weaken authority/value gates, or reuse discovery/held maps.
- **Full held pass:** open deployable q6-plus-379-weight reconstruction and an entirely new final
  confirmation panel. D110a is not itself an automatic submission.

No branch authorizes TestSession, Arena, submission, or resident change.
