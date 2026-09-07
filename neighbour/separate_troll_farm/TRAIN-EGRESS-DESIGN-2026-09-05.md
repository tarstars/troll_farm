# Correct same-turn training after resolved movement

The reproduced referee ordering in TRAIN-EGRESS-FINDING-2026-09-05.md permits MOVE followed by
TRAIN. Implement that correction in the experimental controller, separately from all frozen
denial/production-baseline comparisons. No worker talent, ceiling, denial value or production
scoring change. No publication follows from this correctness fix alone.

Plan an affordable train if the shack is already clear or its occupant can leave, unless an
enemy currently occupies the shack. Reserve the bill in the shared PICK ledger. Give the chosen
egress move priority in movement resolution. After resolution, predict the endpoints of our
explicit reachable MOVE commands and emit TRAIN only if the shack will be clear. A withheld
purchase does not change stored inventory or pretend a worker exists; the next observed state
is authoritative. Existing stock reservation can conservatively withhold a PICK in that case.

Fixtures: initial legal egress plus TRAIN; occupied/blocked egress does not train; enemy shack
occupancy blocks training; another move into a previously empty shack suppresses TRAIN; a PICK
cannot consume the reserved bill. Check commands against the existing referee on real initial
maps as well as state fixtures, and run the full suite. Same-turn opponent arrivals remain
unobservable and can still block a train at application, as in the real rules.
