# D11 resident-native tactical layer — development protocol (2026-07-20)

## Question

Can the accepted PPO actor add tactical value after the stable resident has completed its own
opening, without replacing the resident's funding engine, worker specification, or both workers'
continuation?

This is the first direct test of PPO as a specialist layer rather than a complete bot.

## Frozen adoption mechanism

The resident controls every command until it has trained its normal second worker.  The actor
runs in shadow on the exact referee state.  Once a second worker exists, V7 replaces the actor's
requested target channels with that worker's actual stats before inference.  This makes the
actor recognize the resident-created worker without changing the resident's opening.

- V7 research source:
  `curriculum-level5-seed-reacquisition-d11-live-v7-resident-worker-adoption-research.rs`,
  69,608 bytes, SHA-256
  `9beae086bd92b4d4be4f7a1e2c40042102ed15ff4bd427cf53ad7e249f859f5b`.
- V7 binary SHA-256:
  `30d584ee89c6f225039d8e9c3900622745e328760daed0cc597cedc41f0db9d5`.
- `--adopt-worker` is research-only.  With neither adoption nor fallback enabled, V7 matches V5
  on all 16 seed-0 resident smoke streams across every common non-timing field.

The seed-0 native-layer smoke test trained the resident worker in 8/8 games and confirmed that
all three post-training command compositions execute to terminal play.

## Policies

| Policy | Before resident train | Starter after train | Trained worker after train |
|---|---|---|---|
| `resident` | resident | resident | resident |
| `native_actor_all` | resident | PPO | PPO |
| `native_resident_starter_actor_second` | resident | resident | PPO |
| `native_actor_starter_resident_second` | resident | PPO | resident |

The decomposition identifies whether value belongs to whole-pair PPO control, the PPO crop-role
starter, or the PPO trained-worker role.  It also retains the exact resident as the paired
control in every cell.

## Development block

- Reused seeds: 0--7.
- Seats: both.
- Opponents: `resident`, `gold_adaptive`, `compact_gold`, `norx_native_three`,
  `legend_balanced`, and `mybot`.
- Games: 8 × 2 × 6 × 4 = 384.
- Parallelism: 20 independent exact-engine games.

Absolute local-opponent margins remain mechanism evidence.  The primary estimand is each layer's
paired margin delta from the resident on the identical seed/seat/opponent.

## Analysis

For each layer report:

- game-, map-, and opponent-balanced margin delta from resident;
- wood-edge delta and final worker-spec distribution;
- training and terminal completion;
- head-to-head delta in the `resident` opponent block;
- worst opponent mean, worst decile, and per-map deltas;
- action-mix shifts, especially whether assigning PPO to the starter preserves the resident
  chopper's production.

## Frozen gate and selection

A layer is eligible for a disjoint prospective protocol only if:

1. all 96 games retain the resident's successful worker count;
2. map-balanced mean margin delta is at least +5;
3. the normal-approximation 95% lower bound of the eight map deltas is nonnegative;
4. worst opponent mean delta is at least -5;
5. worst-decile cell delta is at least -20;
6. mean delta in direct games against the resident opponent is nonnegative.

Select the eligible layer with the largest map-balanced mean.  Among layers within one point,
prefer a one-worker PPO layer over whole-pair PPO.  If the two one-worker layers remain within
one point, prefer `native_actor_starter_resident_second`: it preserves the resident's established
wood-specialist control while assigning PPO the renewable-supply role closest to its curriculum.

No eligible layer means close direct command substitution and move to advisory/objective-level
PPO integration; do not relax the gates after results.

## Outputs

- rows: `d11-native-layer-development-seeds0-7.tsv`;
- analysis: `d11-native-layer-development-2026-07-20.json`;
- result: `d11-native-layer-development-result-2026-07-20.md`.

