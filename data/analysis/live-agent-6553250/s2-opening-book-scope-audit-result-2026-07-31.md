# S2 opening-book per map class — scope audit

Date: 2026-07-31

Verdict: **`DEPENDENCY_GATED_REPRESENTATION_BLOCKED`**

## Question

Can the project now precompute strong first-K-turn sequences by map class and look them up
at runtime, or are the book's action library and map selector still missing?

## Required chain

An opening book is not just a fast lookup. It requires, in order:

1. a non-closed bounded sequence library;
2. terminal continuation value for every sequence;
3. pre-action map features that transfer prospectively;
4. a class→sequence policy with abstention and held-map/held-opponent support;
5. only then, a runtime lookup.

The last step is cheap. The first four are the current evidence bottleneck.

## Action-library evidence

E1 already reconstructs the historical coverage. The project tested CONTROL plus dynamic
max-affordable and all 27 harvest-0 worker specs; complete farm-first/max-bank/later-funding
macros; a terminal-valued turn-one rollout; fixed one-source prefixes; an eight-action
recurrent portfolio; and all four one-batch and 16 two-batch sequences.

Those are not available book entries:

- first-worker choices have no opponent-robust activation;
- farm-first loses 97.57 score and later funding loses 56.78;
- the turn-one rollout was +2.717 locally, then decayed to 21.7 in Arena versus 24.1
  control;
- fixed source prefixes reach only 45–60% first-generation receipt;
- the recurrent opening policy loses 1.758;
- one-batch breadth is 38.54%, while all two-batch means span only 3.455.

Canonical synthesis:
`data/analysis/live-agent-6553250/e1-opening-micro-optimality-scope-audit-2026-07-30.md`;
closures in `docs/CONSTRAINTS.md` §(a) and §(f).

E1 leaves exactly one action/value object: a bounded multi-turn prefix over the resident's
own candidate pairs, evaluated to terminal. It is not yet enumerable. It depends on
accepted N4 Phase A instrumentation and then a separately frozen E1 oracle. S2 cannot
construct a downstream book before that library exists and demonstrates material,
opponent-broad value.

## Map-representation evidence

The independent representation blocker is equally strong:

- D63 static opening/map features fall from discovery AUC 0.830 to validation 0.479
  (balanced accuracy 0.503).
- D91's large development selector (+31.012 overall, +158.780 selected) occupies only
  5/16 maps; its map-cluster interval crosses widely [−1.738,+63.761], so prospective maps
  remain unopened.
- Phase 15 expands to 600 seed-seat groups. Oracle precision is 89.615%, below its frozen
  90% gate; the best fixed map-only forest reaches 47.059% precision and −0.277 margin.
- D153 map-fold value is about +14 to +17 in training but only +1.820 held, with 44.44%
  harmful selections and a −0.992 worst fold. Confidence does not rescue it.
- Generated maps cannot supply field selection evidence: constant six-water layouts put all
  80 official roots outside support, with a −78.05 domain shift (−72.12 from scalars).

Sources: the D63, D91, and D153 entries in
`data/analysis/live-agent-6553250/legend-top3-experiment-cycle-2026-07-18.md`;
Phase 15 in `docs/archive/legend/session-handoff-2026-07-16.md`; canonical closures in
`docs/CONSTRAINTS.md` §(a)–(c).

These failures target different actions, so they do not prove every possible opening
representation impossible. They do prove that no currently accepted pre-action map
representation can supply S2. Opponent families are not map classes, and consumed panels
are not available validation blocks.

## Decision

S2 is not ready for an implementation protocol. It is:

- **dependency-gated** on accepted N4 instrumentation, a separately frozen E1 terminal
  prefix oracle, and a material sequence library; and
- **representation-blocked** until a genuinely new pre-action map representation transfers
  on disjoint official maps and held opponents.

Keep S2 on the register as `DEPENDENCY_GATED_REPRESENTATION_BLOCKED`. Do not enumerate
sequences, fit map classes, reuse consumed labels, open a panel, build a book, modify source,
construct a candidate, or run Arena. H11 remains the general map-conditioned-configuration
question; N4 and E1 retain their own scopes.

Machine matrix:
`data/analysis/live-agent-6553250/s2-opening-book-scope-audit-result-2026-07-31.json`.
