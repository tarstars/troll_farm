# D62a no-crop tail audit — result (2026-07-21)

## Verdict

The two D62 zero-crop episodes are a genuine, symmetric establishment failure on one official map,
not unavoidable terrain and not PPO action noise. Retain the 100% crop gate for a controller that
claims establishment safety. Future reports should still distinguish unconditional crop rate from
feasibility-conditioned invariants, but these two rows receive no exemption.

This classification cannot rescue D62: its independent deterministic movement result remains
0/512 semantic decisions.

## Frozen evidence

- protocol SHA-256: `b422953ca835a639409182f8e2dc66e3bf44895104c051550c41f72744aa6ab3`
- audit runner SHA-256: `a61bf115c8280b1d71c9d4649834c543763a74265b02b5b2a971fae7d553af21`
- 2,048-row result SHA-256: `4678d09d6317f5da1fe5ea03a556e3d9be055daa0f6e524d14d88dcb383a65e5`

The audit covers task indices 0--2,047: 128 maps from seed 9,802,000, both seats, and all eight
frozen opponents under deterministic filtered-balanced semantics. This contains the early D62
training task stream; a zero-crop episode never unlocks a learned semantic action, so its trajectory
is exactly reproducible without the PPO checkpoint.

## Findings

- 2,040/2,048 tasks reach the turn limit.
- 8/2,048 terminate early under the exact no-plant stall rule.
- Exactly 2/2,048 create no own crop; they are task indices 352 and 360.
- Both are seed `9802022` versus `resident`, one for each seat.
- They terminate at turns 143 and 147 with scores 14–64 and 18–64.
- Each begins with ten natural plants and inventory `[10,2,2,5,4,0]`, including positive stock of
  all four seed species.
- The opponent creates six crops in each trajectory.
- The D40 side selects two renewal jobs in each trajectory but creates zero crops.
- All plants are gone at termination; direct, provenance, and deposit-prediction failures are zero.

The opponent's six successful crops on the same symmetric map are direct feasibility evidence.
The paired seats show a geometry/controller interaction rather than an isolated stochastic miss.
Early termination is downstream of failed materialization: it does not make establishment
unavoidable.

## Threshold interpretation

`99.88%` would be excellent as an ordinary average-rate estimate. It is insufficient for this
specific gate because the gate asserts a qualitative precondition—renewable supply is established
before option control—not merely a high expected frequency. One recurring map family can generate
repeated catastrophic Arena losses, and rank-three work cannot average that tail away without
measuring its value explicitly.

For future protocols:

1. keep a 100% feasibility-conditioned establishment invariant when claiming crop safety;
2. separately report unconditional crop rate and referee end reasons;
3. exempt only predeclared, mechanically proven infeasible cases; and
4. evaluate any intentionally crop-optional strategy under a different tail/value protocol instead
   of calling it renewable-safe.

No new checkpoint, candidate, or platform action follows.
