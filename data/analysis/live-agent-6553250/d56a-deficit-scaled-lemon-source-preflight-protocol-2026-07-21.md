# D56a deficit-scaled LEMON source preflight — frozen protocol (2026-07-21)

## Question

D55 selects source acquisition and finds LEMON deposited shortage in 73.77% of blocked
target-three cells; 55.74% remain LEMON-short even after all carry and ripe LEMON. Does one
coefficient-free LEMON source-building role broaden the otherwise transaction-correct V5 workforce
ladder?

## Frozen V6 treatment

Create `LegendFieldProxyV6` with the same eight configs and all V5 behavior. Only while a worker
three or four bill is pending (current workers at least two and TRAIN not currently affordable):

1. set the own-side radius-six LEMON source floor to
   `ceil(next_cost[LEMON] / MAX_FRUITS)`; with `MAX_FRUITS=3`, this is four sources for the hybrid
   worker bill;
2. if current own-side standing LEMON is below that floor, designate the highest-ranked existing
   producer as the sole source builder;
3. after the unchanged endgame-bank check, the source builder plants carried LEMON using the
   unchanged V2 farm cap/radius and target reservation;
4. if empty, it PICKs deposited LEMON when adjacent to the shack, otherwise harvests or moves to
   the nearest ripe LEMON; and
5. if no source-building command is legal, fall back to the unchanged V5 producer/chopper logic.

The source role is disabled whenever TRAIN is already affordable, so it cannot spend an executable
bill. Every accepted PICK still decrements V5's shared planning inventory. Do not alter worker
specs, caps, producer quotas, unit/role order, other deficit preferences, fallbacks, farm caps,
ordinary planting, banking, transaction rules, or shack behavior.

Cross hp2/balanced first spec, cap three/four, and one/two retained producers for exactly eight V6
configs. No parameter may change after execution.

## Execution and gates

Run exact `b100_e6` as player 0 against all eight V6 configs on the same 160 consumed maps, twice
with 20 threads. Retain every D54 transaction gate and original D52 workforce/crop/activation gate.
Additionally require:

- worker-two reach is exactly unchanged from D54 for every corresponding config (130/160 hp2 and
  134/160 balanced), since treatment cannot activate before worker two;
- among the 732 exact D55 target-three-blocked cells, at least 183 (25%) create more successful
  LEMON plants than their V5 counterpart; and
- mean successful LEMON plants across those 732 cells increases by at least one.

Compare species telemetry to D55 by exact `(game_id, corresponding config)`. Record all current
fields, but ignore score direction, support, distance, cohorts, opponent identity, policy value,
and platform outcomes.

Frozen evidence includes D55 result SHA-256
`eca4391b6f39400ad4683972268971ccfd2b00227a6c7f15255b5fec4782067c`, D55 matrix SHA-256
`59240f763c285c5961be0eea417b5a66ad5e049ccb076f7835caeb67fdb766fa`, the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`, and V2 parent SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

## Decision rule

- **Full pass:** freeze V6 and specify a separate consumed-map support audit.
- **LEMON mechanism pass but workforce fail:** close one-resource source building and advance to a
  separately frozen exact deficit-vector source allocator using the D55 secondary shortages.
- **LEMON mechanism fail:** diagnose whether seed access or farm-cap saturation prevents the role
  from activating; do not tune the floor on these maps.
- **Transaction fail:** reject before any workforce interpretation.

No fresh map, candidate generation, TestSession game, submission, Arena action, or resident change
is authorized.
