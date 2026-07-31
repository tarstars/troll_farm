# N7 dead-accretion removal plan — result

Verdict: **`DEPLOYMENT_ALREADY_SLIM`**.

The four families are dead from the exact live construction chain, but the correct
maintenance action is to leave the sacred source untouched. All four are already absent
from the 62,725-byte source used by the live submission. Its additional deletion ceiling
is therefore exactly **0 bytes (0%)**.

## Exact construction chain

`main()` constructs `SecureOrchardBot::new()`, which wraps
`YamoBot::tuned_carry_regeneration_transit_idle_harvest()`. The inner constructor leaves
`scarce_farming=false`, `scarce_plan=None`, and all opponent-crop controls off. The outer
constructor leaves `task_market_enabled=false` and `banana_factory_enabled=false`.
Specialized constructors can turn those families on for experiments, but `main()` never
calls them. This independently reproduces H13's live-dead conclusion.

## Artifact comparison

| Artifact | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| Sacred development/library source | 6,024 | 275,377 | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| D171a exact control snapshot | 6,024 | 275,377 | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| Pre-slim submission ancestor | 1 | 90,547 | `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9` |
| Current live deploy | 1 | 62,725 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |

The sacred source and D171a snapshot are byte-identical. `cgauto/api_submit.py` defaults
to the current live deploy.

| Family | Reachable from `main()` | Sacred occurrences | Pre-slim | Live deploy | Non-live consumers |
|---|---:|---:|---:|---:|---|
| `ScarceIntent` | no | 45 | 45 | **0** | embedded tests, exact snapshot, copied experiment variants |
| banana factory | no | 306 | **0** | **0** | ownership/economy runner and embedded tests |
| task market | no | 28 | **0** | **0** | ownership/economy runner and embedded tests |
| opponent-crop scoring | no | 121 | **0** | **0** | crop-priority, continuation, ownership, harvest-contact runners and tests |

Banana factory, task market, and opponent-crop scoring were already excluded from the
90,547-byte pre-slim ancestor. `cgauto/slim_live_source.py` explicitly specializes the
fixed-off control flow and removes `ScarceIntent`/`ScarcePlan` plus other compiler-dead
items. It reduces the ancestor by 27,822 bytes, but that total is not a Scarce-only
measurement: it includes many unrelated items and fragments.

## Why the sacred source is not a deletion target

The sacred file is not merely deployment input:

- `rust/src/lib.rs` exposes it as `troll_farm::resident_policy`;
- 23 Rust runners import it directly by path, in addition to the library inclusion;
- 11 Rust files contain `resident_policy` API uses;
- ownership/economy and crop runners directly call specialized task-market,
  banana-factory, and opponent-crop constructors or telemetry;
- embedded source tests exercise the disabled families;
- the exact D171a snapshot is used as a later-panel control fixture.

Deleting from the sacred file would change its binding hash, break byte identity with the
snapshot, alter a public research API, and invalidate historical compile/test assumptions.
Live deadness is not enough authority for that migration.

## Size bound and disposition

The gross sacred-to-live difference is 212,652 bytes (77.2221%), but it includes
minification, tests, public research constructors, unrelated dead items, and fixed-policy
specialization. It is only a loose upper bound and cannot be attributed to these four
families. The only decision-relevant deploy bound is:

> additional live-deploy removal = **0 / 62,725 bytes = 0%**

Keep the live deploy and its submit pointer unchanged. Keep the sacred source and D171a
snapshot byte-exact. Keep historical runners and submission artifacts for
reproducibility. N7 needs no cleanup patch and no successor.

If maintainability later justifies a separate owner-authorized migration, create a new
versioned non-sacred runtime module from the slim artifact, migrate active consumers one
at a time with API/command/hash parity, and retain the sacred source and snapshot as exact
fixtures. Do not clean the sacred source in place.

No source, formatter, deletion, regeneration, compile, test, game, map, package,
candidate, submission, or Arena action occurred.
