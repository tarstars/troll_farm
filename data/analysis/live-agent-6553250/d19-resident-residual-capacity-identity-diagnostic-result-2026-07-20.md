# D19 residual capacity/identity diagnostic — development result (2026-07-20)

## Decision

**Close single-state terminal-advantage distillation.  Neither research capacity nor oracle
opponent identity passes its frozen diagnostic.**

Do not train a larger teacher, add opponent-history features for this target, reopen D17/D18
thresholds, generate a locked block, or build a policy from D19.  The exact Monte Carlo tooling
remains useful for bounded causal analysis, but this label/policy formulation is exhausted.

## Capacity result

The research models were 4--7 times larger than the D18 students:

| Model | Parameters |
|---|---:|
| Large geometry | 33,153 |
| Large geometry + oracle identity | 33,921 |
| Large spatial | 22,301 |
| Large spatial + oracle identity | 22,685 |

No non-oracle model passed at any useful activation rate.  The best precision among rates of at
least 2% was 44.59% (`geometry_large_s1901`, 4%), but its conditional advantage was -1.65, its
map CI crossed zero, and it introduced a catastrophe.  At 2%, the best large geometry seed reached
41.38% precision and -3.08 mean; large spatial models were no better and produced more
catastrophes.

This is worse than the compact D17/D18 tails.  Extra capacity fits training-specific terminal
discontinuities rather than discovering a transferable boundary.  The capacity diagnostic has
zero passing recipes.

## Oracle-identity result

Oracle development-opponent identity also fails.  Its largest matched precision gain was +9.48
percentage points for the large spatial model at 2%, below the frozen +10-point gate.  More
importantly, that oracle slice still had only 43.97% precision, -4.51 conditional mean, a map CI
of [-0.232,+0.040], and one new catastrophe.  Other identity gains were smaller or reduced mean
value.  Zero comparisons pass.

Opponent policy contributes some variance, but it is not the missing key: even giving the exact
development identity cannot make the terminal label safe or positive.

## Final abstraction-level conclusion

- **Density:** positive interventions are real and common; D16--D18 repeatedly establish this.
- **Predictability:** terminal effects are not a stable function of one visible decision state at
  the precision required for a conservative residual policy.
- **Learning:** PPO collapses to `KEEP`; compact supervised students admit harmful lookalikes;
  larger students overfit; oracle opponent identity does not rescue them.
- **Monte Carlo:** exact continuation is best retained as an experiment microscope, not distilled
  into this per-decision controller and not placed in the runtime agent.
- **Project:** the stable resident and candidate status remain unchanged.  D15--D19 produced
  infrastructure and a decisive branch closure, not a submission improvement.

## Next move

Return to policy-level interventions whose effect is repeated and structurally constrained, so
the hypothesis itself controls downside.  The best next family is a small portfolio of resident
macro modes selected at the opening or at one explicit phase boundary, evaluated by complete
paired games on new maps.  This uses Monte Carlo/statistics at the policy-selection level rather
than attempting to predict chaotic single-action terminal effects.

## Evidence

- diagnostic analysis SHA-256:
  `c2e697de985dbd69fd7e1941c4d2a9727626c5ddedf4b791f48d3fd5556d11a1`;
- diagnostic program SHA-256:
  `44a9e6caaf71c4854ef6ee1c990e17c71a49573737229cf4b03b75a8a2a7c8d6`;
- data and observation hashes are inherited unchanged from the D18 result.
