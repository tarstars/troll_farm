# Banana restoration R2 round-3 host review

Date: 2026-08-05

Task: `20260802-banana-restoration-r2`

Candidate: `candidate-banana-r2.min.rs`, 76,750 bytes, SHA-256
`2f58edef71f692565643cd31c302a32c64543611f920a49f84ff288a663f693b`, canonical artifact commit
`f02bf24bdd78b4c33c3f8f1a16faec1b19fb9ed3`.

## Verdict

**IMPLEMENTATION_INVALID pending another revision.** The exact candidate rebuilds and compiles,
and the new exact tree-transition helper replaces the old static health division. However, the
claimed own-planted flip/conversion proof is scripted rather than candidate-driven, and the
conversion deadline still has three mutually inconsistent definitions. Remaining host replay and
value gates stop before execution. No Arena or TestSession mutation occurred.

## Independently reproduced

- Candidate SHA `2f58edef...`, 76,750 bytes; readable SHA `2e46b8b1...`.
- Deterministic build reproduces exact candidate bytes and parent inverse.
- Optimized standalone compile passes.
- R-1, R-2a, R-2b, R-3 and four controls pass on the new candidate.
- The unchanged R-3 test fails old SHA `280ed777...` with doomed chops on turns 6–9.
- Detector self-tests pass 27/27.
- Sacred source remains exact SHA `fff6669b...`.

## Terminal gap 1 — the own-planted flip/conversion trace is not the candidate

The handoff presents t5 as `own-PLANT -> opponent movement -> flip -> feasible conversion`. The
generator explicitly documents t5 as `T5_SCRIPT`, a manually specified policy used to test the
detector. It is not the command stream emitted by `2f58edef...`.

An independent closed-loop run of the actual candidate on `scenario_t5_flip_convert` emits:

- turn 1: `PICK 0 BANANA`;
- turn 2: move to the mother;
- turn 3: `PLANT 0 BANANA`;
- turns 4–20: `WAIT` for the resident.

There is no candidate ownership-loss response and no candidate conversion. All detectors pass
because the resident camps on the mother, so the scripted opponent's distance-1 approach never
flips the resident's strict ETA ownership. The required end-to-end own-planted case therefore
remains untested. Detector-level scripted evidence cannot prove implementation behavior.

Add a deterministic dynamic-opponent scenario in which the real candidate plants the diagonal
mother, later leaves it during its normal lifecycle, observes a real I-7 ownership flip, and emits
the required feasible conversion. Run the actual compact and readable binaries closed-loop; both
must produce the same command stream and revised D-8 must exempt exactly that conversion. Retain
the owned-mother negative control.

## Terminal gap 2 — three different conversion deadlines

The current artifacts disagree:

1. invariant I-10a says conversion must complete strictly before `eta_opp`;
2. candidate code compares `resident_eta + exact_chops` with
   `max(eta_opp, predicted.cooldown)`;
3. revised D-8 compares exact chops at chop start directly with opponent arrival ETA.

The candidate expression also mixes time origins: `resident_eta + exact_chops` is measured from
the decision turn, while `predicted.cooldown` is remaining cooldown at the future chop-start state.
For size-below-four trees, that cooldown is not even the full time until fruit exists. Thus spec,
implementation, regression narrative, and detector can disagree about the same conversion.

Integrator clarification: the resource-safety deadline is the opponent's **earliest executable
HARVEST turn**, not mere arrival. Co-location does not by itself transfer fruit or stop our chop.
Compute both events in one absolute decision-turn frame with exact game transitions:

- candidate conversion-completion turn, including travel, every chop, growth, and health gain;
- opponent earliest harvest turn, including travel, tree growth to fruit-bearing size, fruit
  production cooldown, and action timing.

Convert iff completion is strictly earlier. Use the same named oracle in I-10a, candidate code,
R-3, and D-8. Do not use `predicted.cooldown` alone or an arrival-only detector shortcut.

## Terminal gap 3 — R-3 does not execute the claimed growth boundary end to end

R-3 contains a useful unit assertion that size 2 / health 4 / cooldown 1 / chop 1 needs five exact
chops. Its closed-loop red scenario instead reaches chop start at cooldown 5, where static and
exact chop counts are both four; it fails the old candidate because the opponent already arrived
and because the old decision used a stale ripening proxy. The new source does call the exact helper,
but the regression does not make the candidate's decision flip specifically because growth adds
health during its committed chop sequence.

Add a reachable candidate-driven boundary where the old bytes choose conversion, exact simulation
shows growth makes it miss the earliest-harvest deadline, and the new bytes abandon; or a paired
nearby feasible case where the exact extra chop still wins and the new bytes convert. Preserve the
old/new red-green proof with source hashes.

## Disposition

Do not run the 516 dormant panel, banana-live replays, game `897829265`, value testing, or Arena
publication for exact SHA `2f58edef...`. A successor needs one consistent absolute-time oracle and
candidate-driven own-planted flip/conversion evidence. All previously repaired one-seed, abandon,
readable-equality, detector, and second-worker gates remain mandatory.
