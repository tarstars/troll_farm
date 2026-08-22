---
type: HANDOFF
task_id: 20260731-b3-10-near-camp-harvest-scope
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T08:10:00Z
requires_ack: true
---

# B3.10 scope audit closes the near-camp harvest item

Verdict: **`CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`**.

B3.8's 496 optimistic captures are individual one-point fruit units across 205 games.
Full own credit is 2.4195 score/game; a deliberately generous factor-two
deny-plus-capture bound is 4.8390 margin/game. The underlying ≤2-turn “detour” explicitly
omits HARVEST, DROP, and scheduling displacement.

D173a/b supply the missing causal cost: compact_gold −2.0625/−1.3906, catastrophes
+5/+3, negative-margin mass 1.0959/1.0812, and all mechanism gates fail. Being outside
D173b's chop-shadow does not create action value, and D174a prevents reuse of the
synthetic-bill scaling story.

Validation:

- compact JSON valid; hashes in
  `local_codex_1/b3-10-near-camp-harvest-scope-audit/manifest.json`;
- semantic evidence checker: 11 records, 6 closures excluding void, 1 void premise;
- evidence tests: 25 passed;
- generated evidence views deterministic;
- STATE 150 lines; ledger 55,634 bytes; `git diff --check` passes;
- sacred resident SHA remains `fff6669b...`.

Please review the individual-fruit-unit semantics, the factor-two bound, D173 gate
arithmetic, and closure wording. No analyzer, replay/map/range, source, panel, candidate,
platform, or Arena action occurred.
