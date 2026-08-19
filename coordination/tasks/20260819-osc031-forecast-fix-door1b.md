# 20260819-osc031-forecast-fix-door1b — the evidence rule, scoped to preserve dormancy

- Status: OPEN — OWNER-CHARTERED 2026-08-19T18:39Z in session ("charter
  Door 1b") after the Door-1 candidate's honest Phase-2 rejection
  (predecessor: `coordination/tasks/20260818-osc031-forecast-defect-fix.md`,
  CLOSED). This is the newly chartered design the rejection verdict requires —
  not a threshold change.
- Record owner: local_claude_1 · Work owner: **claude_1** ·
  Reviewer: **codex_1** (gates) · Integrator: local_claude_1
- Base: cure-C resident `ad3bfefe…` (byte-sacred; candidate built by generator).
- Priority: the owner's focus lane — first card in claude_1's queue
  (sentinel build moves to second).
- Created UTC: 2026-08-19T18:39:26Z

## OWNER DESIGN RULING — TWO TRUTHS (2026-08-19, superseding the 1b scope
design SAME SESSION, before any build; the owner rejected the scope carve-out
as a patch: "our task is to simplify the program")

The one lie doing two jobs is replaced by two single-purpose truths:

1. **The forecast tells only the truth.** `predict_tree` predicts from
   observed evidence ONLY: an opponent actually on the tree counts
   (`ON_TREE`); absent evidence, nothing decays. **`DAMAGED_FLAT1` is DELETED
   OUTRIGHT — no scope, no carve-out, no regime split.** The provenance
   branching collapses to evidence-or-nothing.
2. **The orchard knowledge is said out loud, once.** A single explicit named
   rule at the candidate level: orchard-context trees are excluded from chop
   candidacy. Its predicate is THE canonical orchard-eligibility definition
   the P3 panel property uses — imported or generated from it, never a second
   implementation (one predicate systemwide).

**Simplification is itself a deliverable:** the candidate diff must be
net-simpler (the fiction fully gone — reviewer verifies no remnant of it
anywhere), and each surviving rule must state its meaning.

**Named risk, measured not hoped:** the explicit rule is BROADER than the
accident it replaces (the fiction silenced only DAMAGED orchard trees; the
rule silences healthy ones too). Panel divergences on healthy-orchard-chop
games are expected findings; they fail the gate only where games become
blocking (the gate keys harm, not difference).

## Design constraints (the day's lessons, made binding)

1. **One dormancy definition.** The scope test in the candidate must be THE
   SAME predicate the P3 property/panel uses for "orchard-eligible view" —
   imported or generated from it, never a reimplemented approximation
   (the wall-blind-Manhattan lesson; one counting path, one predicate).
2. **Builder guards as before:** generated from `ad3bfefe…`, refuses wrong
   subject digest, non-unique anchors, edits touching the on-tree evidence
   path, or any edit outside the declared hunk set.
3. **The five non-P3 de-novo games (m021s0, m040s0, m063s1, m078s1, m090s1)
   are DIAGNOSED, not hoped away:** per-game, on the existing decomposition
   artifacts + targeted replay, BEFORE the panel gate is attempted — are they
   second-order effects of the candidate's extra activity, and does the 1b
   scope change them? Measured attribution per game travels in the gate
   handoff; "the panel will tell us" is not a diagnosis.

## Gates (unchanged battery, fail-first)

1. Gate-1 rerun on the two-truths candidate with the ACCEPTED unified runner
   (attribution split reported; on the four P3 fixtures the dormancy rule
   observed excluding the previously-introduced chops).
2. 240-game panels, fresh provenance, vs the cure-C matched floor: **zero
   de-novo by (map_id, seat), both directions exercised** — the frozen gate,
   unchanged.
3. Latency p95 + full parity (shared timing path).
4. codex_1 unified review. END STATE: ready-with-gates.

## Boundaries

No Arena action (a submission night is the owner's separate decision). No
threshold changes. Resident and dev copy untouched. Registry discipline as
ever; all standing transport rules (cards, deferrals, evidence gate) apply.

- Authority: owner charter in session, 2026-08-19.
