# D51a accidental support-output quarantine (2026-07-21)

The first D51 analyzer invocation contained two control-flow defects:

1. its anchor comparator failed to exempt the deliberately different `model` label, creating
   1,280 false anchor mismatches; and
2. it continued into support scoring after the independent activation gate had already failed at
   2,461/8,960 changed cells (27.47% versus the frozen 35% floor).

The accidental file
`d51a-workforce-population-coverage-result.json`, SHA-256
`e3b545deaae72df7ff89668039cb53325bafc03700845ae873655d5f81187a7d`, is quarantined. Its support,
distance, cohort, opponent, and policy fields must not be quoted, selected, compared, or used to
design a follow-up. The raw A/B matrices remain valid for the preregistered activation audit.

The corrected analyzer maps only the anchor label, stops immediately on any mechanical/activation
failure, and emits a separate activation-only result with all outcome fields explicitly ignored.
No gate or threshold changes.
