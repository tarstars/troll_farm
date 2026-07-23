# D35b.1 root-support integrity amendment (2026-07-20)

## Why this amendment exists

The byte-repeat integrity run on development seed 9,200,000 completed all 16
seed/seat/opponent scenarios and 32 frozen roots.  Before computing or inspecting
any oracle choice or aggregate terminal outcome, I inspected only row identity,
enumeration size, role exposure, executor status, and worker-count fields.

The original integrity gate incorrectly conflated grammar coverage with the
availability of a job at a fixed game state.  On the exact frozen roots:

- 9/32 roots exposed `RENEW`;
- 17/32 exposed `FELL_BANK`;
- 17/32 exposed `MINE_BANK`; and
- all 32 exposed a syntactic train goal, but none of the seed's evaluated goals
  became affordable before its original jobs ended.

The pattern is structural: at several roots there is no ripe tree, no tree, no
iron access, or no qualified worker with free capacity.  The frozen grammar says
those jobs must not be invented.  Requiring 95% of *all* roots to expose both
`RENEW` and `FELL_BANK` therefore contradicts the grammar and would reward an
invalid enumerator.

No terminal score delta, winning option, role value, or opponent outcome was
examined before writing this amendment.

## Corrected integrity support gate

The first five D35b integrity requirements are unchanged.  Requirement six is
replaced by both of the following:

1. opportunity fidelity: every emitted job must satisfy the frozen capability,
   target-state, reachability, capacity, collision, and remaining-time rules;
   direct executor commands must have zero pre-turn legality failures; and
2. development support: among the expected 320 fixed roots, at least 40 roots
   must expose `RENEW`, at least 80 must expose `FELL_BANK`, and at least 120 must
   expose `MINE_BANK` or contain at least one successfully completed train goal.

These are substrate-support checks, not policy-value thresholds.  Root turns,
opponents, seeds, job grammar, enumeration limits, oracle tie-breaking, and every
representation upper-bound gate remain frozen.  Confirmation remains sealed.

## Runner clarifications made at the same integrity boundary

- Jobs whose predicted completion exceeds turn 300 are excluded, as the frozen
  grammar already required.
- The 96-bundle truncation order is exactly reward rate, ETA, then role/target
  key; total reward is recorded but is no longer an extra tie-break.
- A global train goal terminates as soon as an original job invalidates.
- The output records pre-turn invalid direct-command count and maximum own worker
  count explicitly.

These changes enforce the written protocol and do not alter outcome selection or
qualification thresholds.
