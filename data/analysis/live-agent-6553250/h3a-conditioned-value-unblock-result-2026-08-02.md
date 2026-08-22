# H3a conditioned-value unblock — Phase A result

Task: `20260802-h3a-conditioned-value-unblock` · Work owner: `claude_1` · 2026-08-03

## Verdict

**Phase A PASSES. All four pinned trigger gates and the integrity gate hold.**

This is **not** a terminal task verdict. None of `TRIGGER_PREFLIGHT_FAIL`,
`INSUFFICIENT_ACTIVATION`, `CONDITIONING_NOT_LOAD_BEARING` or `CONDITIONING_LOAD_BEARING` is
reached: the first three are excluded by these results, and the fourth requires Phases B and C.
Phase A authorizes Phase B and nothing else. **No Arena action is authorized or performed.**

## Gate results

Computed by `claude_1/h3a-conditioned-value-unblock-preflight.py` over the 5,100-row state
package. All 17 cohort IDs match the task record in both directions.

| gate | requirement | result | |
|---|---|---|---|
| 1 — predicate true by turn 150 | ≥8/10 catastrophes | **9/10** | PASS |
| 2 — first true turn precedes the collapse interval | ≥8/10 | **10/10** | PASS |
| 3 — false-positive activation by turn 150 | ≤20% of 7 matched wins | **0/7** | PASS |
| 4 — ETA-6-eligible treatment decision after activation | ≥6/10 | **9/10** | PASS |
| 5 — identity, turn, provenance, ETA and count consistency | complete | see integrity | PASS |

| game | cohort | activation | ≤150 | collapse from | first eligible |
|---|---|---:|---|---:|---|
| 897780891 | catastrophe | 148 | yes | 200 | t148, ETA 6 |
| 897781216 | catastrophe | 139 | yes | 150 | **none** |
| 897781413 | catastrophe | 123 | yes | 200 | t123, ETA 4 |
| 897781719 | catastrophe | 120 | yes | 150 | t120, ETA 3 |
| 897781840 | catastrophe | 92 | yes | 200 | t92, ETA 1 |
| 897781987 | catastrophe | 138 | yes | 250 | t138, ETA 5 |
| 897782076 | catastrophe | 60 | yes | 100 | t60, ETA 6 |
| 897782213 | catastrophe | **169** | **no** | 200 | t169, ETA 0 |
| 897782302 | catastrophe | 96 | yes | 150 | t96, ETA 2 |
| 897782366 | catastrophe | 114 | yes | 200 | t114, ETA 6 |
| 897781650 / 897782068 / 897782128 / 897782201 / 897782246 / 897782379 | matched win | never | no | — | — |
| 897781674 | matched win | 169 | no | — | t169, ETA 4 |

The predicate separates the cohorts sharply: **9/10 catastrophes activate before turn 150 and
0/7 matched wins do.** In every one of the nine, activation also precedes the collapse.

## Exactness of the eligibility predicate

Taken from the frozen reconstruction record
`h3a-pressure-treatment-reconstruction-result-2026-07-31.json`
(`existing_tree_targets_only`, `tracked_opponent_crop_required`,
`bfs_ceil_div_eta_threshold: 6`, `score_operation: candidate.score += candidate.score`) and
implemented against the resident's own primitives read from
`rust/src/bin/yamo_orchard_live.rs`:

- `NEIGHBORS = [(0,1),(1,0),(0,-1),(-1,0)]` — 4-way, no diagonals;
- `bfs_distances(walkable, sources)` — unit-cost BFS over authoritative walkable cells;
- `ceil_div(a,b) = 10_000 if b <= 0 else (a + b - 1) / b` — integer, sentinel included.

Tree identity is **cell identity** `(x,y)`, per the integrator's correction; `tree_index` is
audit-only. "Tracked opponent crop" is `created_by == <opponent seat>`, never `initial` and
never our own seat. "Existing" is `health > 0`.

The five archived fixtures are asserted directly as tests: eligible at ETA 6; ineligible at
ETA 7; ineligible untracked; ineligible non-tree; ineligible unreachable.

## The one honest limitation on gate 4

Gate 4 as computed establishes the **state conditions the treatment tests** — an existing
tracked opponent crop, reachable, at BFS ceil-div ETA ≤ 6 from a resident troll, at a decision
after activation. It does **not** establish that the resident *enumerated a candidate* for
that tree at that decision. Candidate generation is branch-dependent in the exact source
(carrying state, free capacity, species, `health > 0`, `fruits > 0`), and enumerating it
requires executing the resident, which Phase A0 forbids and which is Phase-B work.

So gate 4 is a **necessary condition, verified**; sufficiency is not. Two facts bound the risk:

1. A sensitivity run restricting eligibility to fruit-bearing trees — the narrower
   harvest-branch subset — returns the **identical 9/10**. The result does not depend on the
   permissive reading.
2. Every hit is at or within a few turns of activation itself, with ETAs of 0–6, so the
   opportunity is not marginal.

This limitation closes for free in Phase B: once C1 exists, the equality bridge already
requires proving C1 treatment eligibility equals A1 on active states, and that proof
enumerates the real candidate set on these same decisions.

## Integrity

- Package hashes reproduce exactly: decisions `a60cbf05…`, maps `decfa8f4…`, manifest
  `4336ce47…`. `sealed_data_included: false`, `exact_ids_only: true`.
- Provenance is complete across all rows — 66,152 `initial` / 10,271 `seat0` / 11,425
  `seat1`, no null or ambiguous value.
- `rust/src/bin/yamo_orchard_live.rs` byte-exact at `fff6669b…` throughout; no source arm
  edited or built.
- A frame-to-turn trap was found and pinned: the public `view` counter is a **frame index**,
  and `turn = frame // 2`. Reading it naively places `897780891`'s activation at turn 294,
  after that game's own collapse. Validated against `sides.csv` train turns across all 17
  games — 13 with opponent TRAINs match exactly, 4 have none in both sources.
- Activation is counted from **landed** TRAIN events only, never issued commands.

**Evidence class.** The state package is a causal, public-outcome-anchored reconstruction
under the locked referee step — not an independent continued-RNG replay. It is admissible
here because Phase A audits the games that actually happened. It is **not admissible for the
Phase-C value panel**, where teacher-forcing would pin the very outcomes a treatment changes.

## Artifacts

| path | SHA-256 (prefix) |
|---|---|
| `claude_1/h3a-conditioned-value-unblock-preflight.py` | `f0849daa27ba7318` |
| `claude_1/h3a-conditioned-value-unblock-preflight-result.json` | `d41be9902078ef8a` |
| `claude_1/h3a-conditioned-value-unblock-preflight-result-fruits.json` | `e91244dadea491fc` |
| `tests/test_h3a_conditioned_value_unblock.py` | `56e62f1ab9955ebf` |

```sh
python3 claude_1/h3a-conditioned-value-unblock-preflight.py \
  --json claude_1/h3a-conditioned-value-unblock-preflight-result.json
python3 claude_1/h3a-conditioned-value-unblock-preflight.py --require-fruits \
  --json claude_1/h3a-conditioned-value-unblock-preflight-result-fruits.json
python3 -m pytest -q tests/test_h3a_conditioned_value_unblock.py     # 22 tests
```

22/22 tests pass. They were executed under a minimal harness — this host has no `pytest`,
`uv` or `pip` — so the canonical pytest invocation has not been observed against this code.

## What Phase A does and does not license

**Licenses:** Phase B — generating C1 from exact C0 plus the seven-edit treatment with the
sticky wrapper, its fixtures, and the equality bridge.

**Does not license:** any Arena action, candidate, TestSession, submission, or a Phase-C panel.

**Blocker standing in front of Phase C, discovered during extraction and not by this
preflight:** the locked A2-0b substrate could not execute the real command streams natively —
its parser crashes on 213 of its own accepted numeric fruit aliases, continued movement RNG
diverges from the public landing at `897781216` turn 12, and empty `MSG ;` is platform-legal
but parser-unknown. Phase C's runner depends on that substrate. **This must be resolved before
any value panel is frozen**, and it is the most consequential finding of the day.

## Standing prior

Unchanged by this result. A1 — the identical always-on treatment — lost **7.77 rating** at a
clean 63-game Arena checkpoint, and the conditioning hypothesis rests on an observational
signal with an endogenous roster. A trigger that fires in the right games is a necessary
condition for H3a to be worth testing, not evidence that it works. My expectation remains that
Phase C returns `CONDITIONING_NOT_LOAD_BEARING`; the point of Phase A was to reach that test
cheaply, and it did.
