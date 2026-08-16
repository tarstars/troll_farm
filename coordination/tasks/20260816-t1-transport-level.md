# 20260816-t1-transport-level: the trolls' transport coordination level (swap / yield / visibility)

- Status: **stage 2 DELIVERED + ACCEPTED (partial); stages 3–4 next.** History:
  - Stage-1 grader holds CLOSED 2026-08-16: repair `7b843635` (claude_1) fixes both
    false-positive defects; codex_1 independent re-review (`codex_1/reviews/
    t1-transport-level-stage1c-grader-repair-review-2026-08-16.md` @ `25bcd39b`)
    reproduces 13/13 controls, resident 0/34; codex_1 explicitly WITHDREW its OSC-006
    positive-control sentence (the control passed via progress, not the relaxation).
  - **GRADING DISPOSITION RULED 2026-08-16 (local_claude_1, integrator ruling):
    progress-only grading is FROZEN, conservative, with disclosure.** The frozen rule's
    "target reached" arm needs candidate-intent capture = P-1 rollout step 2; it arrives
    with P-1, not as a second weaker intent instrument inside this harness.
    **Disclosure: a candidate that truly reaches its target but emits no progress event
    grades NOT_FIXED (false negative — understates the fix).** Safe direction given the
    pre-registered ≈+0.045 expectation. Any prediction miss at final grading must cite
    this disclosure in the owner-session material. Ruling message:
    `coordination/messages/local_claude_1/20260816T153513Z-20260816-t1-grader-closure-stage2-integration-ack.md`.
  - Stage 2 (visibility, option B) delivered `9d99d62a` and **ACCEPTED AS PARTIAL** by
    codex_1 (`…stage2-occupancy-review-2026-08-16.md` @ `ef87f462`, independent
    execution): **0 FIXED / 34 — expected for a partial feature, NOT a prediction miss**
    (the registry's 25 are predicted for visibility+yield+swap together). OSC-008 and
    OSC-012 flipped to quiet-but-stalled (detector silent, no progress) — counted
    NOT_FIXED by the frozen rule, deliberately. Both protected branches (:1016/:1413)
    verified reachable under (B) and broken under the committed naive control
    (`candidate-t1-naive-BROKEN.rs`); source-level invariant, not a runtime proof.
  - **Stage 3 (idle-yield, destination-based) delivered `853dc8b2` 2026-08-16:
    0 FIXED / 34 and ZERO rows changed vs stage 2** (same two detector-silent rows
    OSC-008/012; integrator re-parsed the committed JSON). Root cause named by the
    author: **design fault, not tuning** — the `wanted` set is built from MOVE targets
    (GOAL cells) while the library's dominant mechanism M1 is blocker-on-ROUTE, so the
    contested test never fires for its target population (the viewer-V1 error class,
    "a command target is not the next cell", self-identified).
  - **Harness soundness vs the frozen-world bug class VERIFIED, not asserted**
    (`c673dd37`, `claude_1/t1/verify_world_evolves.py`): the harness uses the shared
    `regression_tests` runner (apply + grow) AND world evolution was MEASURED on
    OSC-006 (fruit ripens t18–23, impossible frozen). T-1 numbers are uncontaminated
    by the H-starve-1 runner defect; integrator confirmed both the import and the
    check.
  - **RULING 2026-08-16 (integrator, sequencing): NO `next_cell` path mirror now —
    proceed directly to stage 4 (swap).** The charter's yield wording covers "the
    square/path"; the delivered yield covers the square only — **that shortfall is
    RECORDED, not erased**, and goes to the post-grading owner session with the
    residue. If corridor cases remain unfixed after full-set grading, chartering a
    path-aware yield (with the mirror's divergence risk priced) is an OWNER decision
    then. Grounds: the mirror-drift class was paid for twice TODAY alone (viewer V1,
    H-starve-1 grow()); pre-registered value ≈ +0.045 does not buy the riskiest
    construct available; the frozen registry's own reasoning assigns working-blocker
    corridors to swap — stage 4 MEASURES that assumption instead of building on it.
    The destination-yield stays in the candidate stack (inert on fixtures, possibly
    live off-fixture; the 240-game panel guards de-novo effects). Two consecutive
    zeros (stages 2+3) stated plainly per the author — still not a prediction miss;
    the registry's 25 are graded only against the full set after stage 4.
  - Earlier: stage 1 REOPENED 2026-08-16 for grader repair (codex_1: restored-rule
    relaxation + fidelity check too weak). Harness RED 34/34 baseline stands.
    Visibility-fix design ruled option (B) separate occupancy check, idleness marker
    untouched, :1016/:1413 protected with regression checks — OWNER-DIRECTED 2026-08-16
    ("I want implement this feature, re-run tests and dwell on cases where this fix
    wouldn't help")
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
