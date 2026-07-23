# D24 phase-boundary complete-policy handoff — frozen protocol (2026-07-20)

## Question and hypothesis

Can the exact resident preserve its strong opening and early opponent suppression, then hand the
whole side to a coherent production controller before the observed turn-150--200 reversal?

The central hypothesis is complementarity, not a generic claim that a farm or an extra worker is
better.  The resident used from turn one suppresses opponent reproduction but remains a fixed
two-worker, roughly eleven-plant economy.  The private-farm family used from turn one creates much
more own production but loses badly to self-compounding opponents.  A common-state handoff may
retain the resident-induced early state while replacing the late production regime.

This is the policy-level phase-boundary experiment recommended by D19 and selected by D23.  It is
not a low-level action residual, an opening selector, an isolated `TRAIN` wrapper, or online Monte
Carlo.

## Frozen control, options, and state semantics

Every scenario begins with the exact promoted resident `SecureOrchardBot` and one deterministic
opponent.  At the selected boundary, clone the exact engine state.  The control continues the
fully warmed resident.  Each alternative is newly initialized at that state and controls **all**
own workers through terminal play:

1. `private2`: the explicit two-worker `GoldElite` private-farm configuration used under the
   ownership-aware study;
2. `ownership2`: the same complete private farm with future opponent-crop provenance and
   race-conditioned denial;
3. `hybrid3`: the fixed three-worker Gold hybrid architecture;
4. `accumulate4`: an environment-independent four-worker, two-chopper, one-planter farm; and
5. `norx3`: the recovered exact-three-worker Norxondor/Silver macro continuation.

Cold initialization is intentional and part of the gate: a deployable phase option must interpret
the visible current state without counterfactual hidden history.  The opponent is warmed by
replaying every actual prefix state, so the control and all alternatives face the same continued
opponent process.

Decision turns are exactly **75, 100, 125, and 150**.  No state-dependent selector is fitted in
D24.

## Frozen data

- Development smoke may use already-consumed seeds 0--4 only for compilation, schema,
  determinism, and activation checks.  Its outcomes cannot select an option or turn.
- Discovery: previously undesignated generated seeds **50,000--50,059**, both seats, all eight
  fixed structural opponents.
- Confirmation: seeds **50,060--50,119** remain sealed until one discovery option/turn passes.
- Opponents: `compact_gold`, `gold_adaptive`, `gold_elite`, `mybot`, `printer_bot`, `sched_bot`,
  `script_boss`, and `silver_boss`.
- The independent statistical unit is the map seed.  Both seats and all opponent cells are
  averaged within seed before confidence calculations.

The official-map holdout, field replays, current resident, candidate source, submit helper, and
Arena are outside D24.

## Readiness and integrity gates

Before discovery:

1. the Rust runner compiles with warnings denied;
2. a five-seed smoke produces the complete option/turn/opponent/seat grid;
3. every control branch from the same root is deterministic on an exact repeat;
4. the exact resident prefix and warmed control terminate cleanly in every cell;
5. each option emits only legal engine-resolved play and differs from control in at least 20% of
   smoke scenario/cut cells; and
6. no source constructor may read environment-tunable policy parameters.

Failure closes or repairs infrastructure before fresh discovery; smoke outcome values may not
alter the option library, cut grid, or gates.

## Discovery estimands and gates

For every option/decision-turn combination report:

- seed-clustered final margin, own-score, opponent-score, and wood deltas versus the common-state
  resident continuation;
- 5%-trimmed mean and normal seed-clustered 95% interval;
- positive/tied/negative seed counts;
- all eight opponent-family means and the worst opponent;
- final/max workers and first third-worker turn;
- control-tail effect for roots whose resident continuation ends at margin at most -100; and
- candidate catastrophic frequency and negative-margin mass versus control.

An option/turn is discovery-eligible only if all conditions hold:

1. mean margin delta at least **+5**;
2. 5%-trimmed margin delta at least **+2**;
3. mean own-score delta at least **+5**;
4. at least **6/8** opponent-family margin means are nonnegative;
5. worst opponent-family mean at least **-5**;
6. mean delta on control-catastrophic cells is positive;
7. candidate catastrophic frequency and negative-margin mass do not exceed control; and
8. the seed-clustered 95% interval lower bound is greater than **-2**.

If multiple combinations pass, freeze exactly one by this lexicographic order: highest worst-
opponent mean, then lowest catastrophic frequency, then highest seed-clustered mean, then later
decision turn, then option name.  This order is fixed before discovery.

If none pass, do not inspect confirmation and close unconditional complete-policy handoffs for
this option library.

## Confirmation and disposition

Run the one frozen option/turn once on seeds 50,060--50,119, with only the resident control and
selected option.  Confirmation requires all discovery gates plus a seed-clustered 95% margin-
delta lower bound above zero.  No thresholds may be relaxed and no second option may inherit the
same block after failure.

A confirmation pass authorizes only deployment-feasibility work: standalone source integration,
exact prefix/control parity, latency, source-size, and an independent local regression block.  It
does not authorize submission or Arena activity.  A failure closes the family without tuning on
confirmation outcomes.

## Outputs

- runner: `rust/src/bin/d24_phase_handoff.rs`;
- analyzer: `cgauto/d24_phase_handoff_analysis.py`;
- smoke/discovery/optional confirmation TSV and JSON files with `d24-phase-handoff` prefixes;
- final result: `d24-phase-boundary-complete-policy-handoff-result-2026-07-20.md`.
