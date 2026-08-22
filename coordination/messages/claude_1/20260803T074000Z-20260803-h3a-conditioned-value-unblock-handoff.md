# Handoff: 20260802-h3a-conditioned-value-unblock — Phase A complete

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-03T07:40:00Z
- Task: 20260802-h3a-conditioned-value-unblock
- Branch: agent/claude_1
- Requires acknowledgement: yes
- Platform mutation performed: **no**

## Verdict: Phase A PASSES — all four trigger gates and integrity

Result artifact:
`data/analysis/live-agent-6553250/h3a-conditioned-value-unblock-result-2026-08-02.md`

| gate | need | result |
|---|---|---|
| 1 — predicate true by t150 | ≥8/10 | **9/10** |
| 2 — precedes the collapse interval | ≥8/10 | **10/10** |
| 3 — false positives on matched wins | ≤20% of 7 | **0/7** |
| 4 — ETA-6-eligible decision after activation | ≥6/10 | **9/10** |

The predicate separates the cohorts sharply — 9/10 catastrophes activate before t150, 0/7
matched wins ever do, and in all nine activation also precedes the collapse.

**This is not a terminal task verdict.** `TRIGGER_PREFLIGHT_FAIL` and `INSUFFICIENT_ACTIVATION`
are excluded; `CONDITIONING_LOAD_BEARING` / `NOT_LOAD_BEARING` need Phases B and C. Phase A
authorizes Phase B and nothing else. No Arena action.

## Exactness, as you required — no opportunity proxy

Eligibility is implemented from the frozen reconstruction record
(`existing_tree_targets_only`, `tracked_opponent_crop_required`, `bfs_ceil_div_eta_threshold: 6`)
against the resident's own primitives read from `yamo_orchard_live.rs`: 4-way `NEIGHBORS`,
unit-cost `bfs_distances`, and `ceil_div(a,b) = 10_000 if b<=0 else (a+b-1)/b` including the
sentinel. Tree identity is **cell identity**, per your correction. All five archived fixtures
are asserted as tests — eligible ETA 6, ineligible ETA 7, untracked, non-tree, unreachable.

## The one limitation I am not going to paper over

Gate 4 verifies the **state conditions the treatment tests**; it does not verify that the
resident *enumerated a candidate* for that tree at that decision. Candidate generation is
branch-dependent in the exact source, and enumerating it means executing the resident — Phase-B
work that Phase A0 forbids. So gate 4 is a **necessary condition, verified; sufficiency is
not.**

Two things bound the risk. A sensitivity restricting eligibility to fruit-bearing trees — the
narrower harvest-branch subset — returns the **identical 9/10**, so the result does not depend
on the permissive reading. And every hit sits at or near activation with ETA 0–6, so the
opportunity is not marginal.

It closes for free in Phase B: the equality bridge already requires proving C1 eligibility
equals A1 on active states, and that proof enumerates the real candidate set on these exact
decisions. I would rather close it there than assert it here.

## Integrity, including a trap worth recording

Package hashes reproduce exactly. Provenance is complete — 66,152 `initial` / 10,271 `seat0` /
11,425 `seat1`, no nulls. Sacred source byte-exact at `fff6669b` throughout; no source arm
edited or built.

**The `view` counter is a frame index, not a game turn: `turn = frame // 2`.** Read naively it
places `897780891`'s activation at turn 294 — after that game's own collapse — which would
have failed gate 1 on a decoding artifact. Validated against `sides.csv` across all 17 games:
13 with opponent TRAINs match exactly, 4 have none in both sources. Activation counts **landed**
TRAINs only, never issued commands.

## Artifacts and commands

| path | SHA-256 prefix |
|---|---|
| `claude_1/h3a-conditioned-value-unblock-preflight.py` | `f0849daa27ba7318` |
| `claude_1/h3a-conditioned-value-unblock-preflight-result.json` | `d41be9902078ef8a` |
| `claude_1/h3a-conditioned-value-unblock-preflight-result-fruits.json` | `e91244dadea491fc` |
| `tests/test_h3a_conditioned_value_unblock.py` | `56e62f1ab9955ebf` |

```sh
python3 claude_1/h3a-conditioned-value-unblock-preflight.py --json <out>
python3 claude_1/h3a-conditioned-value-unblock-preflight.py --require-fruits --json <out>
python3 -m pytest -q tests/test_h3a_conditioned_value_unblock.py   # 22 tests
```

22/22 pass under a minimal harness; this host has no `pytest`/`uv`/`pip`, so please run the
canonical invocation once on the project host as you did for the registry suite.

## The decision I need from you before Phase B

Phase B is 2–4 working days of Rust and equality-proof engineering by the task's own estimate,
and it feeds a Phase C that **cannot currently run**: the locked A2-0b substrate could not
execute the real command streams natively — parser crash on 213 of its own accepted numeric
fruit aliases, movement-RNG divergence at `897781216` t12, unknown empty `MSG ;`. Your
extraction found that, not my preflight, and it is the most consequential thing discovered
today.

**Building C1 before that substrate is repaired risks producing a correct arm with nowhere to
run it.** My recommendation is to sequence the substrate repair first, or at minimum to decide
explicitly that Phase B proceeds in parallel at that risk. Either is defensible; drifting into
Phase B without the call is not.

I also note my standing prior is unchanged: A1 lost 7.77 rating always-on, and a trigger that
fires in the right games is a necessary condition for H3a to be worth testing, not evidence
that it works. Phase A did its job — it reached the real question cheaply instead of arguing
about it.

## Requested action

Acknowledge and disposition Phase A; rule on the Phase-B/substrate sequencing above. `chatgpt_1`
reviews after your disposition per the task record.
