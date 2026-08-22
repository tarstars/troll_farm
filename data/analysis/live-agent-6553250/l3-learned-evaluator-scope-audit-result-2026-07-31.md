# L3 learned evaluator scope audit

Date: 2026-07-31

Verdict: **`N4_DEPENDENCY_GATED`**

## Decision

L3 does not currently define an independent learned evaluator experiment. Regressing the
resident's hand-tuned numeric score or selected action can only reproduce its current
policy, with approximation error if imperfect. Fitting one-deviation terminal advantage
on exact resident alternatives is already closed by the D16-D19 resident-residual line.
A broad learned scorer over every live candidate would retain the grammar but could
change the compatible command pair on every ordinary turn, making it a whole-trajectory
controller rather than a local evaluator.

The only unconsumed exact-live continuation target is the value of alternative compatible
two-worker pairs. That is precisely N4's active, peer-owned surface. Do not create L3a,
instrument or export candidates, generate labels, or fit a scorer before accepted N4
Phase A and a separately authorized material Phase B.

## Exact live score flow

The executable constructs `SecureOrchardBot::new()` at
`rust/src/bin/yamo_orchard_live.rs:6008-6019`. The active inner constructor enables
idle/persistent regeneration, door unblocking, partial bank transit, and idle harvest
(1685-1695, 1723-1745, 3823-3832). It does not enable task-market, banana-factory,
opponent-crop scoring, or ScarceIntent; those accretions are excluded.

The score is one layer in a larger hard-coded pipeline:

1. Phase-specific generators first define feasible WAIT, bank, fruit, mine, chop,
   regeneration/conversion, idle-harvest, and MOVE candidates. Many branches return early
   and never offer the other actions (871-1327, 3084-3431).
2. Each candidate receives a hand-tuned score. The scale mixes categorical priority bands
   (`0`, `6,000`, `7,000`, `8,000`, `10,000`, `20,000`) with travel/wait, wood-per-turn,
   denial distance, conversion horizon, and bankable-fruit terms
   (780-813, 903-960, 1050-1117, 1223-1319, 3200-3425).
3. Live filters can remove protected-tree/PICK actions, add a forced egress, replace a
   unit's candidates for door clearing, or force an external unit to WAIT before ranking
   (3433-3628).
4. The selector takes a one-unit argmax or exhaustively maximizes the summed score of a
   compatible two-worker pair (1354-1413, 3629-3630).
5. Collision resolution may rewrite selected MOVEs (1425-1528, 3650-3673).
6. The secure-orchard wrapper can replace the starter command, protect the mother, and
   rerun conflict resolution independently of inner scores (5288-5428).

A learned score therefore cannot directly alter candidate legality, TRAIN specification,
the roster cap, protected-tree filtering, forced door clearing, collision rewrites, or
orchard invariant actions. But wherever alternatives exist it can change one or both
ordinary commands repeatedly. “Same action space” is not an authority budget and does not
prevent full trajectory replacement.

## Label and overlap matrix

| L3 interpretation | Label | What it would establish | Exact disposition |
|---|---|---|---|
| Regress live numeric scores | Deterministic source score | Fidelity only | **not improvement**; D41a shows an exact decoder is safer than approximate learned ordering |
| Imitate selected resident commands | Resident command/pair | Fidelity only | **not improvement**; D41a/L1 negative priors and closed-loop gating bind |
| Predict one candidate's terminal advantage | One deviation, then resident continuation | Sparse residual value | **closed** by D16-D19; D41d-D44 corroborate the sign/credit problem |
| Replace every candidate score with terminal value | Offline counterfactual or on-policy return | Repeated whole-trajectory control | **closed or programme expansion** under D36, D79-D84, D97-D158, D169-D172 |
| Evaluate exact compatible command pairs | Pair continuation value | Joint residual to immediate sum-score | **N4 dependency** |
| Add spatial planes to D172 options | Exact D172 macro-option labels | Budget-1 option selection | **separate H10a-r1 scope**, peer-gated |

The exact-resident evidence is already strong. D18 passed 0/40 compact spatial recipes;
the larger-capacity/oracle-identity D19 diagnostic also failed and closed single-state
terminal-advantage distillation. D36's four terminally selected resident-anchored joint
overlay epochs gained +10.633 margin, below the frozen +25 floor, and closed further
resident overlay work on that grammar.

Other schedulers supply consistent negative priors. D41a learned only
84.386-84.960% of an ordering that a deterministic decoder reproduced on
85,047/85,047 decisions. The strongest prospective D41 residual policy gained +4.116
against its +5 gate. D42-D44 could not learn a reliable contextual sign boundary or
reuse actor scores as values. D79's 32 random concrete-job scorers all changed 64/64 task
hashes, proving that a shared grammar can still produce global controller replacement.
D83 gained only +1.188 from a snapshot value model; D172 admitted 0/4 fits despite exact,
dense, zero-noise labels.

N6 is the direct live-score warning: changing only the denial-distance weight altered
commands in 53.32-73.83% of development tasks. LOW lost −0.754; HIGH gained only +0.559
with four of eight positive families. Even one scalar in the current score has broad,
heterogeneous trajectory authority.

## N4 gate and disposition

N4 Phase A owns the exact compatible-pair census on 2,048 already-consumed games: all
candidates, compatible pairs, live pair, score gaps, boundary semantics, reconstruction,
and latency. It has not yet produced the census. L3 cannot decide a label unit or
authority budget before N4 establishes that the pair surface is frequent, distinct,
exact, and cheap.

Mark L3 **dependency-gated on N4**:

- if N4 Phase A closes, L3 closes with it;
- if Phase A clears, make a separate Phase-B terminal-value decision;
- only if that Phase B establishes material value should the register replace L2 and L3
  with one bounded compatible-pair residual-evaluator item.

No source, instrumentation, candidate export, model, fit, game, map, candidate,
submission, or Arena action was created.
