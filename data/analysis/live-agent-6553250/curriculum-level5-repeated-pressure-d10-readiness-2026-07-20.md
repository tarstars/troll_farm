# Curriculum Level 5 bounded repeated-pressure D10 readiness — 2026-07-20

## Verdict

**Ready for the single frozen fresh control execution on seeds 5,000--5,499.**  The distinct D10
mode is implemented and its recurrent path is active.  The consumed teacher result is below
several future acceptance floors, so a fresh rejection is more likely than a pass; this warning
does not authorize changing the frozen cap or gates.

## Implementation evidence

- D10 is a separate turn-180 mode with an exact confirmed-destruction limit of three.
- D9 and every earlier funded mode retain their limit of one; their focused invariant tests pass.
- The new chopper reuses the D9 scheduler and roles.  Only the comparison against the destruction
  limit differs.
- Confirmed destruction still requires an opponent `CHOP` at the tracked banana crop followed by
  exact-referee absence of that crop.
- The deterministic Rust test observes actual two-to-three-worker transitions and asserts that a
  rival crop was created before each transition, two fresh funding events were recorded, the
  worker cap is three, and the destruction cap is three.
- Twelve focused Rust Level-5 tests pass.  Thirty Python PPO/Level-5 tests pass, including FFI
  determinism, recurrent activation, and the hard cap.
- Release compilation and Python byte-compilation pass.  The only Rust build messages are four
  pre-existing warnings outside `rl_level3.rs`.

## Consumed smoke bank

Teacher and random legal were run on consumed seeds 0--499 only, with 100 environments, timeout
240, and random seed 107.

| Measure | Teacher | Random |
|---|---:|---:|
| Success | **433/500 = 86.60%** | **0/500** |
| Nontrivial success | **87.12%** | 0% |
| Worst recipe / height | **78.57% / 82.11%** | 0% / 0% |
| Terminal player crop / renewable harvest | **86.60% / 87.20%** | 0.80% / 0.40% |
| At least one / two / three destructions | **100% / 98.40% / 89.40%** | 16.80% / 2.20% / 0.20% |
| Maximum destructions / workers | **3 / 3** | **3 / 3** |
| First / third-worker training | **100% / 98.20%** | 100% / 99.00% |
| Fresh first / second funding receipt | **100% / 100%** | 100% / 100% |
| Chopper / feeder productivity | **100% / 94.00%** | 100% / 96.60% |
| Rival crop / own renewable harvest | **100% / 91.00%** | 100% / 94.40% |
| Illegal selected actions | **0** | **0** |

The recurrence mechanism is therefore neither dormant nor unbounded.  Random remains fully
discriminative.  Teacher loss is concentrated in terminal crop recovery: success, terminal crop,
and renewable-harvest rates cluster at 86.6--87.2%, while opponent funding and productive-role
activation remain strong.  This is exactly what the fresh control must distinguish from sampling
variation.

## Frozen execution rule

Run teacher and random exactly once on `[5000, 5500)`.  Evaluate every gate from the frozen
protocol before opening the fixed actor.  A single control failure closes D10; it does not permit a
threshold change, actor replay, PPO, YT write, prospective access, deployment, or Arena action.

## Reproducibility anchors

- protocol: `c52483727f2eee6988ba083a83a50bb8254bbdcab32af8513fa17b4bef4349a4`;
- consumed teacher: `348a3c9f90568fd91176f9114a95a11d43be4a9de4aff3a7f13965d5804f766f`;
- consumed random: `b04cd44196b1a7a1224b88417ea32bef9a9d4ed4996c4da0a191bbefb55462ab`;
- Rust source: `e0914fe1fbbe555b103730134e43e6a01901bb93c51aef76125a5ee0e5634696`;
- Level-5 environment: `353491ee78d59f3403c678f93062c6390aa07218ddefb6925ec11c9a478b6050`;
- PPO/evaluation selector: `711aefa2adb20719af4df9eeb5265224b32fc48b3e11041ca3a2cf3d7ef9f66c`;
- evaluator: `20a82651f318934001f994639e1944deac611d6240a814fb47174bf8b3640ec3`;
- focused tests: `ccf0b4355b179cf86ea66c0563b680be866c3b8995cf16adb3edcc07d983ba79`;
- release library: `afd1f4fbb405a66f2a260d25181f0025ecd22a584bcb2b648198e0f290c22f21`;
  and
- fresh interval: `[5000, 5500)`, unopened at readiness freeze.
