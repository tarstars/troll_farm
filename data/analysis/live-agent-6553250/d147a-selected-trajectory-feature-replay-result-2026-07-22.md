# D147a selected-trajectory feature replay — result

Date: 2026-07-22  
Decision: **open D148 new-map 64-priority joint two-stage corpus**

Both deterministic replays are byte-identical. Each produces 2,726 complete legal-candidate rows
(SHA-256 `1e7487ba...`) and 57 selected terminal rows (SHA-256 `b8aafdd1...`). All 153 expected
decision groups have exactly one legal chosen action: 57 first actions, 57 second actions, 12
wait-before-first controls, and 27 wait-between-action controls.

The feature matrix has the locked 64 state plus 379 action columns. All 443 features are finite,
state and schedule metadata are invariant within each candidate group, control action features are
exactly zero, and every selected noncontrol action has nonzero action evidence. All 57 terminal
rows exactly reproduce D144, with zero invalid-command, provenance, or deposit-prediction failures.
The 137 `invalidated_jobs` events are environmental job rescheduling and exactly match the frozen
D144 trajectories; they are not integrity failures.

The first two file-path invocations stopped before import or simulation and wrote no output. The
unchanged locked collector was then invoked as a module for both complete repeats.

Result JSON SHA-256: `722ebf71975c7ad956b9af70cd9db9c232061181c694f8ad4bccb55b01e77410`.

Next collect a fresh-map teacher at D146's outcome-blind 64-schedule priority under
`//home/delivery_ml/research/tarstars/troll_farm`, preserving a separate untouched validation
panel. This result validates the training-data interface; it does not qualify a policy or candidate.
