# 20260816-t1-transport-level: the trolls' transport coordination level (swap / yield / visibility)

- Status: stage 1 REOPENED 2026-08-16 for grader repair (codex_1 review: restored-rule relaxation + fidelity check too weak; no grading until repaired). Harness RED 34/34 baseline stands. Visibility-fix design ruled: option (B) separate occupancy check, idleness marker untouched, :1016/:1413 protected with regression checks — OWNER-DIRECTED 2026-08-16 ("I want implement this feature, re-run
  tests and dwell on cases where this fix wouldn't help")
- Programme: stage-3 fix path of `docs/PROGRAMME-banana-farm-2026-08-15.md`; grounded in
  rules-ledger **R-1** and adjudication `local_claude_1/adjudications/OSC-001-ruling-2026-08-16.md`
- Code owner: `claude_1` · Reviewer: `codex_1` · Integrator/record: `local_claude_1`
- Base: readable resident `98628e98…` (candidate build; the resident file itself stays
  byte-exact until an owner base-change ruling after measurement)

## What is built — three primitives, staged, each observed failing first

1. **Fixture harness first:** replay each of the 34 frozen situations under a candidate;
   FIXED = detector silent over the window AND progress restored (grading rule frozen in
   `local_claude_1/t1-prediction-registry-2026-08-16.md`). Harness must fail on the
   unmodified resident for all 34 before any fix lands.
2. **Target::None visibility** — the compatibility check stops waving through idle
   trolls (readable :643-646).
3. **Idle-yield** — a stationary troll with no task yields the square/path a tasked
   troll needs.
4. **Swap** — the resolver may emit the coordinated exchange (both step toward each
   other in one tick); LEGAL per `docs/mechanics.md:54-56` "circular swaps allowed".
   Covers working-blocker corridors where yield would interrupt work.

## Acceptance (pre-registered)

- The 25 PREDICTED-FIXED situations all resolve with progress; prediction misses in
  either direction are named individually (they are owner-session material, not
  failures to hide).
- **240-game panel re-run:** zero de-novo oscillation (D171a's failure mode), D-1 rate
  reported against the 8.50% baseline and the 2.88% D176a reference.
- Latency: warm p95 < 50 ms preserved. Thread parity as standard.
- **Value expectation written in advance: ≈ +0.045 ladder points, i.e. none.** The
  feature's value is control, tests, and a sane movement substrate for the banana farm
  (stages 4–6 build on it). Nobody argues score from this fix later.
- Every new check observed failing (guards standing rule).

## Sequencing for claude_1

Viewer blocker 1 (item-order mislabeling — it lies to the judge) is a minutes-scale fix:
do it first. Then T-1 stages 1→4. Remaining viewer blockers (entry frame, evidence
panels, target marker) after T-1 stage 1 or interleaved at your judgment. P-1 registry
completion continues as your background thread; it is NOT displaced (the residue
adjudications will need packets).

## Out of scope / boundaries

No resident mutation, no Arena action, no banana code. The owner hand-reviews the
residue (predicted: OSC-026..034) with the viewer once fixed. OSC-026's door-pricing
(level-3) fix is a separate future item, not smuggled into T-1.
