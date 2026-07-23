# D21 competitive closed-loop preflight — result (2026-07-20)

## Decision

**PASS.**  All 11 frozen preflight gates passed.  This opens only the preregistered local
1,000,000-transition PPO pilot.  It does not create a submission candidate or authorize Arena.

The machine-readable decision is
`d21-competitive-preflight-gate-2026-07-20.json`.

## Results

| Policy | Mean margin | Win rate | Training | Crop | Renewable harvest | Illegal actions |
|---|---:|---:|---:|---:|---:|---:|
| Random legal, seed 2101 | -129.942 | 0.21% | 40.83% | 9.58% | 0.83% | 0 |
| Scripted teacher | +22.021 | 60.83% | 100.00% | 93.54% | 94.79% | 0 |
| Accepted D11 actor | **+23.833** | 60.21% | **100.00%** | **98.33%** | **98.96%** | 0 |

The teacher and actor beat random by +151.963 and +153.775 mean margin respectively.  Every
episode ended at turn 300.  The largest return-versus-final-margin error was
`1.1444091796875e-05` margin points, below the frozen `1e-4` ceiling.  The actor's least populated
opponent and recipe buckets contained 73 and 56 episodes, above the required 40.

Actor mean margin by opponent:

| Opponent | Mean margin |
|---|---:|
| Complete baseline | -60.828 |
| Renewable planter | +84.077 |
| One-shot reaper | +109.740 |
| Funded pair | -9.187 |
| Sustained funded trio | +39.766 |
| Crop-first repeated pressure + reacquisition | -2.333 |

This is a useful, unsaturated objective: the actor has both wins and losses, and all six opponent
means are distinct.  It also identifies where optimization has leverage: complete baseline is the
largest weakness, followed by funded pair and repeated-pressure reacquisition.

## Readiness defect found and fixed before acceptance

The first full-length pass failed the legality gate with five teacher actions, all on seed
8,000,107.  The complete-baseline opponent occupied the teacher's fixed crop cell; later it also
invalidated a tracked crop, while the competitive wrapper did not activate the existing dynamic
crop replanning path.  The pre-fix outputs are preserved with the
`pre-replanning-fix` filename marker.

The fix is narrow: competitive episodes now clear stale crop tracking and replan when the planned
cell is occupied.  An exact 300-turn regression for seed 8,000,107 was added.  The optimized Rust
library was rebuilt, and all four controls were rerun from scratch.  Both teacher runs then had
zero illegal actions and byte-identical aggregate plus episode rows.

## Gate audit

All frozen conjunctions passed:

- exact 1,440 primary-control episodes at turn 300;
- zero illegal selected actions, including the repeat teacher;
- opponent and recipe coverage floors;
- exact telescoping reward identity;
- deterministic teacher repetition;
- teacher and actor margin advantages over random;
- actor mechanics retention; and
- non-saturated outcomes and opponent response.

## Next authorized action

Run the frozen local pilot from the exact accepted D11 checkpoint, model seed 2107, training stream
starting at 8,200,000, and then evaluate only the final learned checkpoint against the unchanged
D11 actor on reserved seeds `[8,100,000, 8,100,960)`.  The promotion conjunction remains the one
in the frozen protocol: at least +5 mean margin, improvements on at least four of six opponent
means, no opponent regression below -15, at least 90% training, at least 70% crop creation, and
finite/legal execution.
