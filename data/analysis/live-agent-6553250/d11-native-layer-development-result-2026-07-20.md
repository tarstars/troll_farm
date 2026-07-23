# D11 resident-native tactical layer — development result (2026-07-20)

## Decision

**Reject direct PPO command substitution at every tested role boundary.  Do not open a
prospective block.  Retain resident control and test only conservative, resident-gated local
PPO proposals.**

No resident, candidate, holdout, submission, or Arena state changes.

## Complete execution

All 384 planned exact-engine games completed on reused seeds 0--7, both seats, six opponents,
and four paired policies.  V7 successfully adopted all seven resident worker specs observed in
the block, and every layer retained the resident worker count in 96/96 games.  The failure is
therefore control quality, not integration or training.

| Post-training control | Mean margin | Delta vs resident | 95% map CI | Worst opponent | Wood-edge delta |
|---|---:|---:|---:|---:|---:|
| resident / resident | +71.15 | 0.00 | `[0, 0]` | 0.00 | 0.00 |
| resident starter / PPO second | +32.85 | **-38.29** | `[-57.96, -18.63]` | -82.88 | -10.90 |
| PPO starter / resident second | -3.29 | **-74.44** | `[-104.46, -44.41]` | -142.75 | -22.21 |
| PPO / PPO | -26.05 | **-97.20** | `[-137.84, -56.56]` | -161.56 | -35.41 |

Every non-control layer lost on all eight map means.  Their cell worst-decile deltas were -174,
-241, and -281.7 respectively.  None approaches any frozen promotion gate.

## Mechanism

The actor does not share the resident's task reservations, target ownership, or multi-worker
schedule.  Replacing the starter with PPO removes an average 82.58 chop commands, adds 71.90
moves and 23.28 harvests, and increases planting; that converts the resident's wood trajectory
into the narrow renewable-crop curriculum.

Replacing only the trained worker is less destructive to the aggregate action mix—4.18 fewer
chops and 45.06 more moves—but still loses 38.29 margin.  The worker wanders toward actor-local
objectives while the resident starter continues to plan as if its partner still owned the
resident assignment.  Actual worker-stat adoption solves observation identity but not joint
intent.

The seed-0 smoke's small positive actor-starter result was a single-map illusion.  The full block
reverses it on every map, showing why role decomposition needed paired breadth before any source
integration.

## Next interface

Do not let the actor own a route or role.  Keep each resident command unless the actor proposes
an immediately executable local action while the resident would wait or transit.  Test nested
conservative policies:

1. second-worker actor action only over resident `WAIT`;
2. second-worker local crop action (`PLANT`, `HARVEST`, `CHOP`) over resident `MOVE/WAIT`;
3. second-worker any local productive action over resident `MOVE/WAIT`;
4. the crop-only rule for the starter;
5. local productive opportunities for both workers.

Instrument exact and verb agreement, opportunity counts, and actual overrides.  If these rules
are inert or harmful, close inference-time use of D11 and move to new training on resident state
and intent distributions.

## Evidence

- protocol: `d11-native-layer-development-protocol-2026-07-20.md`;
- rows: `d11-native-layer-development-seeds0-7.tsv`, SHA-256
  `51aebfb569dd77ededb337ff6be2df82efedd27e7d25810ecb7d8efc04c1e188`;
- analysis: `d11-native-layer-development-2026-07-20.json`, SHA-256
  `655df300cf9f5f708fe4dc64244ca31daa0b7d26cda7a04724575658a2da6820`.

