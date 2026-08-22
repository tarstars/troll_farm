# Banana R2 stable gate v1

This gate implements the owner's ruling that oscillation is a defect even when it is inherited
from the stable parent.

## Immutable panel

- source commit: `b16f44d62caa9802253adaf255eb07b98273421b`
- 120 generated maps, both seats, 200 turns: 240 candidate games
- seeds: `982451653`, `15485863`, `32452843`, `49979687`, `67867967`, `86028121`
- the effective config and every executable input are SHA-256-bound in the result JSON

## Hard acceptance

1. Candidate build is fail-closed, reconstructs the frozen parent after removing insertions,
   compiles, stays below 100,000 bytes, and passes empty-input smoke.
2. Candidate-founded banana lifecycle tests pass.
3. Raw candidate detector counts satisfy `D-1 == 0` and `D-4 == 0` over all 240 games.
4. No inherited-parent, byte-identical-command, aligned-prefix, or score attribution may demote a
   D-1 or D-4 episode. Attribution remains in the report for diagnosis only.
5. The existing Banana safety gates remain active for bounded planting, opponent fruit capture,
   cargo disposition, mother protection, and funding displacement.
6. `claude_1` independently reruns the exact candidate and gate bundle; `local_claude_1` accepts
   the hashes and result before any host or Arena action.

## Result requirements

The JSON must contain:

- raw per-game detector counts and episodes;
- the hard stability verdict and blocking game manifest;
- full hashes for candidate, parent, gate contract, panel, effective config, detector, oracle, and
  gate runner;
- Python, Rust, and platform versions.

A run is `CLEAR` only when the candidate has zero blocking games and zero raw D-1/D-4 episodes.
The gate contract is machine-readable in `gate-contract-v1.json`.
