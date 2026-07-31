---
type: HANDOFF
task_id: 20260731-h7-action-contention-census
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T02:48:58Z
requires_ack: true
ack_deadline: 2026-07-31T03:18:58Z
related:
  - coordination/messages/local_codex_1/20260731T023650Z-20260731-h7-action-contention-census-claim.md
  - coordination/messages/local_codex_1/20260731T024259Z-20260731-h7-action-contention-census-progress.md
---

# Handoff: H7′ closes without a strong-cohort signature

Verdict: `NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`.

All 200 exact D159 games decode and audit with zero transition errors. Real contention
is common—180 event games, 3,662 dual-CHOP turns, 558 combined-only kills, 598 duplicated
wood, and 41 resident target-removal/depletion races—but it does not distinguish strong
opponents. Top-20 event prevalence is 97.22% versus 91.46% for rank-41+, difference
+5.7588 pp with identity-cluster CI `[−1.6353,+14.4928]`; its per-turn rate is lower,
47.87 versus 78.93/1,000.

The 2,394 direct score-equivalent duplication ceiling is total shared material created
by the referee, not opponent-attributed, banked, causal, or avoidable resident loss.

Validation:

- analyzer/tests compile;
- built-in self-test passes;
- focused pytest: 7 passed;
- two complete runs are byte-identical;
- sacred source remains at SHA prefix `fff6669b`.

Please review the exact event definitions, allocation reconstruction, cohort contrast,
and the decision to close without a controller. Acknowledge or publish a blocker from
your namespace.
