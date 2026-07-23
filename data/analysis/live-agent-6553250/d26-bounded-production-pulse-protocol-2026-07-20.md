# D26 bounded production pulse — frozen protocol (2026-07-20)

## Question and mechanism

Can a fixed early production interval capture the replicated turn-75 farm gain while restoring the
resident before the private-farm policy releases too much opponent compounding?

Every branch shares the exact resident prefix through turn 74.  At turn 75, `ownership2` takes
complete control of all own workers.  At one fixed exit turn, discard the farm controller and
initialize a fresh `SecureOrchardBot` from visible current state for the rest of the game.  A cold
restart is intentional: it cannot carry phantom resident commands or misinterpret unexecuted
shadow commitments.  Existing plants become its visible initial state; it tracks later changes
normally.

The frozen pulse exits are turn **100, 125, and 150**, corresponding to 25, 50, and 75 scheduled
farm turns.  Control is the fully warmed resident continuation from the same turn-75 root.  D26
fits no selector and changes no unit-specific command.

## Why this is distinct

- D24 tested a permanent farm handoff; D26 returns to a complete resident policy.
- D25 tried to predict option value; D26 constrains downside structurally and has no learner.
- The earlier resident-chopper hybrid mixed commands from incompatible controllers every turn;
  D26 gives one coherent controller full authority in each phase.
- The lineage-liquidation experiment switched the resident to destructive liquidation after an
  opponent stock condition; D26 switches temporarily to productive farming at a fixed early
  phase boundary.

## Frozen data and integrity

- Outcome-blind compile/schema/determinism smoke: already-consumed seeds 0--4, both seats, all
  eight structural opponents.
- Duration discovery: already-consumed D24/D25 maps 50,000--50,119.  These outcomes may choose one
  fixed pulse but are development evidence only.
- Prospective confirmation, if discovery passes: previously undesignated seeds
  **51,000--51,059**, both seats and all eight opponents.
- Independent statistical unit: map seed; average seats/opponents before confidence estimates.

Readiness requires a complete control/three-pulse grid, byte-identical repeat, common root fields,
legal clean terminal play, exact control determinism, and command-stream divergence in at least
20% of reached-cut cells for every pulse.

## Discovery gates

For every exit report seed-clustered margin/score/wood deltas, 5%-trimmed mean and 95% interval,
all eight opponent means, catastrophe frequency, negative-margin mass, control-catastrophe value,
and phase action/workforce telemetry.

A pulse passes only if:

1. mean margin delta >= **+5**;
2. 5%-trimmed mean >= **+3** and 95% lower bound > **0**;
3. own-score delta >= **+5**;
4. at least **6/8** opponent means are nonnegative and worst mean >= **-5**;
5. control-catastrophic-cell mean delta is positive;
6. catastrophic frequency and negative-margin mass do not exceed resident; and
7. at least 95% of reached branches execute both the farm phase and resident restart.

If multiple durations pass, freeze one by highest worst-opponent mean, then lowest negative-mass
ratio, then highest mean margin, then shortest pulse.  No state feature or outcome-dependent exit
may be fitted.

## Prospective disposition

If none passes, close fixed production pulses and open no new seed.  If one passes, record its
exact source/result hashes and execute only that duration once on seeds 51,000--51,059.
Confirmation repeats every gate and also requires the seed-clustered 95% lower bound above zero.
Failure closes the family without trying another duration on the same block.

A pass authorizes standalone integration, current-resident prefix parity, source-size, latency,
and an independent local regression block only.  It does not authorize submission or Arena.

## Outputs

- runner: `rust/src/bin/d26_policy_pulse.rs`;
- analyzer: `cgauto/d26_policy_pulse_analysis.py`;
- smoke, discovery, optional confirmation TSV/JSON;
- result: `d26-bounded-production-pulse-result-2026-07-20.md`.
