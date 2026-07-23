# D14 resident residual environment — smoke result (2026-07-20)

## Decision

**The exact resident residual environment passes every frozen gate and is qualified for a short
PPO learning-signal run.**

This is infrastructure qualification only.  No candidate, stable resident, prospective,
submission, or Arena state changes.

## Exact KEEP parity

Scenario IDs 0--239 cover maps 0--19, both seats, and all six frozen opponents.  Deterministic
`KEEP` matched the independent D11/D12 resident rows in all five terminal fields for 240/240
scenarios:

- margin;
- wood edge;
- terminal turn;
- own worker count;
- opponent worker count.

There were zero overrides, zero rejected actions, no missing `KEEP` mask entries, and no return
errors.  Undiscounted environment return equals terminal margin / 100 in every scenario.  This
proves that sequential policy decisions, command reconstruction, seat normalization, resident
state, opponent mixture, early termination, and auto-reset preserve the exact resident when the
policy declines to intervene.

## Causal random control

| Policy | Map-balanced margin | Wood edge | Changed outcomes | Override episodes | Throughput |
|---|---:|---:|---:|---:|---:|
| all `KEEP` | **+47.75** | +17.49 | — | 0% | 2,812 decisions/s |
| uniform legal random | -138.35 | -26.55 | **240 / 240** | **100%** | 2,918 decisions/s |

Random local residuals lose -186.10 map-balanced margin versus `KEEP`; the 95% normal interval
over 20 map deltas is `[-216.60, -155.60]`, and random loses on all 20 maps.  The environment
therefore exposes real full-game causal choices rather than a no-op action interface.  It also
shows that an unbiased random policy is unusably destructive, so PPO must begin close to `KEEP`.

## Action-mask correction

The first infrastructure preflight found that random interventions can enter off-resident states
with seven executable local alternatives, yielding eight actions once `KEEP` is counted.  The
frozen protocol caps the mask at seven.  The environment now keeps at most six local alternatives
in fixed plane order; this does not change `KEEP` behavior or resident-state coverage.  The final
frozen rerun observed masks from one through seven actions and rejected zero selections.

This was an interface-boundary correction before training, not policy tuning.  Both correctness
policies were rerun from scratch after the correction, and only those final outputs are retained.

## Qualified training posture

The short signal run should use:

- the same 137-channel observation and 13-plane spatial head;
- a compact width-8, two-residual-block network;
- strong plane-0 (`KEEP`) initialization so early exploration remains near the resident;
- full-game score-margin-change reward;
- several independent training seeds on a disjoint development map stream;
- paired deterministic evaluation against all-`KEEP`, with override rate and worst-opponent
  deltas reported.

The signal run succeeds only if at least one learned policy makes nonzero deterministic
interventions without losing paired mean margin or materially damaging any opponent slice.  It
cannot create a candidate; a larger replication and source-size qualification would still be
required.

## Evidence

- protocol: `d14-resident-residual-environment-smoke-protocol-2026-07-20.md`;
- keep output SHA-256:
  `2d7daf01f3bfaa3300caa86403c1ac22ca9e0dd1035d7d3acf8dea9be72ecb10`;
- random output SHA-256:
  `10a563f87e665605e3c4db6a90f8fad9c6dc93d4a5d99a152238e79deffdf7c1`;
- qualification JSON SHA-256:
  `597e8fa42f2d608a0108abb687f05d336bace2b75768d83aa3181c1b7e719df0`;
- environment wrapper SHA-256:
  `49319205794e9c9f96a16e8bcfe21d618596ae3afd94fa65c429782c3a1a52a3`;
- qualification analyzer SHA-256:
  `bd38102ad23ac972544964796921d3a367019cb5f5b9ffbad0447d405887cec4`;
- Rust environment SHA-256:
  `854569f3ab6337cfa87d42bbbef7bfb0cec20d823afc3b9c8c3138713a496116`.
