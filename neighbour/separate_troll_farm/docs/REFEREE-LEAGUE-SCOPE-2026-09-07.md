# Referee scope: league is not terrain presence

Primary inspected the locally available official Java source at
`/data/strong-bot-sources/eulerscheZahl-Troll-Farm/src/main/java/engine/`.
`Unit.getTrainingCosts` charges IRON iff league>=3. `TrainTask` calls the same
affordability rule both at parse time and execution, and lower leagues restrict
positive chopping skill. Empty iron terrain is not the league flag.

The current Rust planning model has inconsistent synthetic empty-iron behavior:
`parity::parse_player` checks full cost including IRON; `engine::apply_train`
omits its charge when `game.iron` is empty. A fixture with chop1, zeroiron and no
iron terrain cannot assume this means free highest-league recruitment. Several
orchard tasks made that incorrect assumption. Failed no-iron hiring assertions
therefore do not alone establish a controller bug; observed economic and command
ownership failures are separate evidence.

For the highest-division goal, use full highest-league costs and reachable map
states. Label artificial fixtures with their actual rule domain. Do not silently
change frozen comparison models or claim lower-league support without a coherent
league parameter, aligned parse/apply rules, and conformance checks. This note
does not certify the rest of the simulator or any candidate.

Official `Board.getNextCell` resolves a distant MOVE to a reachable landing cell
(random ties), then `MoveTask.apply` handles same-player endpoint conflicts and
circular swaps. Local `parity::step_direct` intentionally accepts pre-resolved
endpoints. Direct endpoint emission avoids randomness; it is not an official
rule against distant goals. Pathing through and landing on occupied cells differ.
