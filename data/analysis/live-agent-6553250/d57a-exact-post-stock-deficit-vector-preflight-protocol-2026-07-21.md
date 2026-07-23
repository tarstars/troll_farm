# D57a exact post-stock deficit-vector preflight — frozen protocol (2026-07-21)

## Question

D56 creates substantially more LEMON but reduces worker-three/four reach because the sole source
role displaces PLUM, IRON, and the rest of the renewable economy. Can a coefficient-free allocator
that assigns labor from the whole exact uncovered bill vector complete the workforce ladder while
preserving V5's repaired transaction?

## Frozen V7 treatment

Create `LegendFieldProxyV7` with the same eight configs and all V5 transaction, opening, workforce,
ranking, quota, fallback, and ordinary production behavior. Do not retain V6's fixed LEMON role.
Only while a worker-three or worker-four bill is pending (at least two current workers and TRAIN is
not affordable), compute for each payable PLUM, LEMON, APPLE, and IRON coordinate:

`uncovered[r] = max(next_cost[r] - deposited[r] - all_own_carry[r] - ripe[r], 0)`.

Ripe stock is all current fruit on matching plants; IRON has no ripe stock and is ignored on maps
without IRON terrain. Sort positive coordinates by descending uncovered units, then stable resource
index. Assign at most one coordinate to each highest-ranked existing producer, without cycling: one
producer per coordinate and any unassigned producer retains exact V5 behavior.

For an assigned fruit coordinate, set its own-side radius-six source requirement to
`ceil(uncovered[r] / MAX_FRUITS)`. After the unchanged endgame-bank check:

1. if current matching sources are below that requirement and the producer carries the matching
   fruit, plant it using the unchanged V2 farm cap, radius, and reservation;
2. if the matching source requirement is unmet, the producer is empty, adjacent to the shack, and
   matching deposited fruit exists, PICK exactly that fruit;
3. otherwise, bank useful carried bill currency or harvest/move to the nearest ripe assigned fruit;
4. for assigned IRON, bank useful carried currency or mine/move to the nearest IRON source; and
5. if no exact-coordinate command is legal, fall back to unchanged V5 producer/chopper logic.

When no post-stock coordinate is uncovered, use V5 unchanged so carried/ripe bill currency can be
materialized. Disable the vector whenever TRAIN is affordable. Every accepted PICK must still
decrement V5's shared planning inventory. Do not alter specs, caps, producer quotas, unit or role
order, ordinary deposited-deficit preferences, bank timing, farm caps, shack behavior, or any
other parameter. No value/score term is permitted.

Cross hp2/balanced first spec, cap three/four, and one/two retained producers for exactly eight V7
configs. No definition or threshold may change after execution.

## Verification before execution

Unit tests must prove all of the following on constructed pending-bill states:

- a PLUM-only uncovered vector makes V7 PICK/PLANT PLUM while V5 does not;
- an IRON-only uncovered vector makes V7 issue the exact IRON funding command;
- two uncovered resources assign distinct coordinates to the two ranked producers; and
- an affordable bill disables the vector and retains the V5 TRAIN/PICK transaction behavior.

The runner must expose exactly eight unique V7 configs and retain all D55 stock/species and D54
TRAIN telemetry.

## Execution and gates

Run exact `b100_e6` as player 0 against all eight V7 configs on the same 160 consumed maps, twice
with 20 threads. Retain every D54 transaction gate and every original D52 workforce, crop,
activation, opening, cap, completeness, and repeat gate. Additionally require worker-two reach to
match D54 exactly in every corresponding config: 130/160 for hp2 and 134/160 for balanced.

Compare workforce counts to V5/D56 descriptively, but use the original absolute conjunction; do
not lower a threshold or select configs. Record species telemetry and exact transition counts, but
ignore score direction, support, distance, cohorts, opponent identity, policy value, and platform
outcomes.

Frozen evidence includes D56 result SHA-256
`2ad610b248ae0af6933465079c0de510ee6bfd3b9fa08cea8f588c08060b7d50`, D56 matrix SHA-256
`90ac87e0f5140192bafb346d161a116d84821fa317f3b6d30880acc9b443a912`, D55 result SHA-256
`eca4391b6f39400ad4683972268971ccfd2b00227a6c7f15255b5fec4782067c`, the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`, and V2 parent SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

## Decision rule

- **Full pass:** freeze V7 and specify a separate consumed-map support audit.
- **Transaction or worker-two invariance fail:** reject before workforce interpretation and trace
  the regression; do not tune allocation.
- **Vector active but workforce fail:** close this exact allocator and diagnose allocation time
  spent versus bill-coordinate progress before choosing another controller representation.
- **Vector inactive:** trace exact seed/source access and command fallbacks; do not add weights or
  thresholds on these maps.

No fresh map, candidate generation, TestSession game, submission, Arena action, or resident change
is authorized.
