# PLAN — one authoritative dispatch controller

## Controller
`DispatchBot` replaces `SearchBot` as `candidate::bot::moisan::SecureOrchardBot`
from turn 1 to 300. It never constructs or calls the parent policy
(`policy::bot::moisan::SecureOrchardBot`). It reuses only leaf infrastructure:
`game::types`, `game::rules`, `game::nav` (BFS/next_cell), `game::protocol`
(stdin/stdout), and `simulation::parity` for fixtures only.

## Mechanism (falsifiable)
Each turn the controller enumerates *complete finite jobs* (Chop, Harvest, Mine,
Bank, Plant) for every own worker, prices each by actually bankable reward minus
travel/action turns under that worker's capability (carry cap truncates wood;
hp truncates fruit), then assigns at most one job per worker with exclusive
target claims and a single shared bank budget. Recruitment is one job with a
priced bill; deficit items carry the hire's marginal value so mining/foraging is
funded by the same ledger. Emission is joint: one action per worker, <=1 TRAIN,
bill reserved against same-turn PICK, own-unit move-destination de-confliction,
endgame forced banking.

## Comparison (frozen before any measurement)
Baseline `claude_candidate_policy_flat.rs`
sha256 95ee691ee1b26e074ac90851575a6a56d5b0bec738ff3851cd141585d85c6d23.
Panel: development pairs 9947500..9947507, 12 adaptive opponents, both seats =
192 games. Decision: positive whole-panel W+0.5D AND zero candidate issues =>
further evaluation; otherwise park or propose ONE repair with a reproducer.
No sweep, no map selection, no post-panel tuning.

## Gate before the panel
Focused executed fixtures must run first: realistic opening, acquisition of two
missing fruit kinds plus zero-initial iron via mining+bank+paid spawn, no-iron
map affordability, shared-stock conflict, friendly blocked bank, real capacity
wood yield, endgame banking.
