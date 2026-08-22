# Phase 3b pre-build design review — REVISION_REQUIRED

Task: `20260820-pair-selector-anti-benching`  
Reviewed artifact: `claude_1/picker3/phase3b-design-proposal-2026-08-22.md` at
`802e13883faabda1d241379703e93c7b41d2d4b2`  
Reviewer: `codex_1`  
Date: 2026-08-22

## Verdict

**REVISION_REQUIRED at G-f. Do not build.** The proposed EXTEND change matches the
coordinator's ruling, the reachable-content enumeration is supported by the function guards, and
the proposal correctly exposes duplicated bank candidates as Δ-B rather than silently changing the
ruled snippet. The operational gates are not yet satisfiable and unambiguous, however: G-c requires
identity on the first Δ-A tick even though a successful rescue must be able to change that tick's
command, and G-b does not define how its comparison remains state-aligned after an earlier Δ-A
divergence.

This review is design-only. I did not build a candidate, run a probe or panel, edit either candidate
source, or take Arena action.

## Blocking finding 1 — the first-rescue identity boundary is one tick too late

The proposal defines rescued-game inertness as byte identity "up to and including the first tick"
on which the fallback preserves a candidate that the old code discarded. But the intended success
case is that one of those preserved `PICK`s is selected on that same tick. The base cannot emit that
rescued `PICK`, because its generator discarded it. Therefore:

- if the new candidate selects the rescued `PICK`, the proposed G-c fails at the intended effect;
- if G-c passes through that tick, it proves only that the first rescued candidate was not selected
  then, not that the change is inert before its effect;
- this conflicts with §6 falsifier 1, which correctly treats formation without selection as a
  possible inert outcome.

Required repair: define a **state-entry boundary** and an **effect boundary** separately.

1. On the paired base state immediately before every tick, classify the new list as Δ-A, Δ-B, both,
   or neither (with the design's mutual-exclusion claim asserted).
2. Require command-stream identity strictly **before** the first tick on which a newly preserved
   Δ-A candidate is actually selected.
3. On that first effect tick, require the changed command to be one of the specifically preserved
   candidates and record its provenance; divergence is permitted there, not one tick later.
4. If Δ-A candidates are formed but never selected, the whole game remains in the no-effect class
   and must be byte-identical throughout.

This retains the ruling's inertness requirement while allowing the change to do the one thing it is
being built to test.

## Blocking finding 2 — Δ-B must be measured on aligned states

G-b says that every Δ-B tick must emit a byte-identical command stream. In an ordinary paired
closed-loop run, the states cease to be comparable after a prior selected Δ-A changes the trajectory.
A later candidate-side Δ-B tick then has no well-defined corresponding base tick with the same unit,
inventory, adjacency and candidate set. Comparing turn numbers would conflate the duplicate-list
question with downstream state divergence.

Required repair: test Δ-B command inertness by a **same-state fork**. Feed the identical pre-command
state and identical bot memory into the before/after generator+selector, and compare the selected
command while also asserting that the only candidate-list multiset delta is duplicate, element-identical
bank candidates. Run that fork on every naturally reached Δ-B state from both arms, including states
reached after a Δ-A effect. Whole-game byte parity remains appropriate only for games with no selected
Δ-A effect.

## Required clarification — make the partition exhaustive in observable terms

The current G-c labels games `no rescue` versus `rescued`, while G-a also calls Δ-B an extra-content
case and §2 uses “rescue” for the intended Δ-A only. Replace the overloaded word with explicit counts:

- `delta_a_formed_ticks`;
- `delta_a_selected_ticks`;
- `delta_b_duplicate_ticks`;
- `first_delta_a_selected_tick` or null;
- `whole_game_identical`.

Every game must have exactly one effect class: `first_delta_a_selected_tick = null` (whole-game
identity required) or non-null (identity strictly before it; named divergence from it onward). Δ-B is
an orthogonal per-state property, not a third game class.

## Findings accepted

- The ruled code edit is represented faithfully and preserves the single seeded `WAIT`.
- From the displayed guards, the only pre-fallback additions are the adjacent-shack bank candidates
  and the guarded replant `PICK`s; the two are mutually exclusive on `carried > 0` versus `== 0`.
- Δ-B is a real reachable source-level delta and belongs in the gate even if it is expected to be
  command-inert.
- Stateful `regeneration_commitments` means post-effect whole-game parity is not a valid acceptance
  requirement.
- The four named falsifiers are appropriate once the identity boundary is repaired. A fifth falsifier
  should be stated explicitly: **Δ-A is selected and makes local progress, but its commitment-induced
  continuation creates a new or worse P3/P4/r5-horizon event elsewhere**; G-d/G-e must stop on that
  outcome rather than letting an aggregate improvement hide it.

## Re-review bar

Return a revised design only. It must repair the first-effect boundary, specify the same-state Δ-B
fork (including bot-memory cloning), use non-overloaded counters/classes, and add the downstream
commitment falsifier. A build remains separately unauthorized by the coordinator's policy.

DEFERRED: `20260820-pair-selector-anti-benching` Phase 3b build. Postponed pending a revised G-f
design acceptance and a separate written build authorization. UNBLOCK-SIGNAL: both are published.

