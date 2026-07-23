# D94c worker-three TRAIN transaction repair — amendment

Date: 2026-07-21  
Status: frozen after D94b mechanical readout and before repair execution

D94b's repeated rows are deterministic but fail the mandatory transaction gate: 189 affordable
TRAIN commands produce only 147 workers. The pre-command check sees an empty shack, then MOVE
resolution can place an existing worker onto the shack before the referee processes TRAIN. This is
the same execution-order mechanism established independently in D38--D39.

The D94b rows are quarantined for verdict purposes. Their outcome values have been observed and
must not influence the repair. D94c changes exactly one mechanical rule: on a turn where the
already-frozen D94b condition will issue TRAIN, add our shack cell to the move resolver's forbidden
set. All fruit/IRON priorities, worker spec, bootstrap condition, horizon, target order, role
commands, telemetry, maps, opponents, and gates remain unchanged.

Rerun the consumed panel once with one and 20 threads. D94c must have byte-identical repeats and
TRAIN attempts equal successes. Any remaining transaction failure rejects immediately. If clean,
apply the original D94b mechanism and value gates without amendment. No further repair, tuning, or
fresh-map run is allowed for this bridge.

