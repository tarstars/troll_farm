# A-3 — N5 corrected narrow re-review

- **Reviewer:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-14
- **Task:** `20260730-n5-endgame-opponent-plant-contest`; iteration-3 item **A-3**
- **Subject:** `local_codex_1`'s corrected handoff `20260731T131500Z`
- **Verdict: CONCUR — the correction preserves `NO_MATERIAL_CONTEST_OPPORTUNITY`.**
- Read-only. No re-derivation, no new measurement, no simulation, candidate or Arena action.

## Separation

The author is `local_codex_1`, dormant since 2026-08-06. I have never touched the N5 analyzer,
its tests or its result. An earlier re-review by `chatgpt_1` exists
(`chatgpt_1/n5-endgame-opponent-plant-contest-corrected-rereview-2026-08-06.md`) but that agent is
unreachable and its dispositions are `RECORDED / UNREPLICATED` by standing ruling — **this is the
execution re-review, and it reproduces rather than relays.**

## What I checked, and how

A re-review that reads the handoff's own summary confirms the handoff against itself. The
corrected hashes are pinned in the message, so the load-bearing questions are whether the bytes on
disk still match them and whether the twelve tests actually pass here.

### 1. Pinned hashes — all match on disk

| artifact | pinned sha256 (16) | on disk |
|---|---|---|
| `cgauto/endgame_opponent_plant_contest.py` | `0d4668b974b99d0a` | **match** |
| `tests/test_endgame_opponent_plant_contest.py` | `c3fb025e1f431170` | **match** |
| `data/analysis/…/n5-endgame-opponent-plant-contest-result.json` | `3a701cb5f816a878` | **match** |

The result also records `source.frozen_input_manifest_sha256 =
53ee5cf3347fbc72dcd1021369cb2b41ce48eb6c3ca22fc9981f7abf14a2b26f`, identical to the
382-occurrence manifest the handoff names, with `frozen_manifest_hash: true` and
`frozen_manifest_inputs_unchanged: true`, and coverage `382 requested / 382 decoded`.

### 2. Blocker 1 — literal post-birth ETA: **corrected**

`subject_eta_at_birth` (`cgauto/endgame_opponent_plant_contest.py:425-426`) opens with

```python
at_birth = game.states[birth_turn]
```

— the literal post-birth state, which is what the original review required. It is called once at
`:508` with `birth_turn`, so there is no second path reading a pre-birth state.

### 3. Blocker 2 — twelve tests: **present and passing**

`grep -c "def test_"` returns **12**, and `pytest` reports **12 passed**. The count is not merely
asserted in the handoff; both the file and the run agree.

### 4. The primary value is unchanged

| quantity | handoff | result JSON |
|---|---|---|
| deny-plus-capture ceiling, all resident games | `11.991735537190083` | **identical** |
| CI low | `8.727272727272727` | **identical** |
| CI high | `15.760330578512397` | **identical** |
| verdict | `NO_MATERIAL_CONTEST_OPPORTUNITY` | **identical** |

The verdict's basis is visible and conservative: `parameters.material_margin = 20.0`,
`gates.ci_upper_lt_20 = true` (15.76 < 20) and `gates.ci_lower_ge_20 = false`. **The entire
confidence interval sits below the material gate**, so the verdict does not depend on which end of
the interval one reads — which is the right shape for a "no opportunity" finding.

### 5. The correction's stated side effects reproduce

The handoff says the literal post-birth read changes resident ETA-0 from 5 to 0 and
reachable-within-remaining from 368 to 366. The result carries
`cohorts.resident.subject_eta_zero_targets = 0` and
`subject_reachable_within_remaining_targets = 366`. Both match. (The `yamo` cohort still shows
`subject_eta_zero_targets = 5`; the handoff's "5→0" is specifically the resident cohort, and
reading it as a global figure would be wrong.)

## One claim I did not independently verify, and why

The handoff states that **both removed reachable targets have zero opponent yield**. Confirming
that requires per-target yield attribution, which is re-derivation and therefore outside A-3's
narrow scope. **I am not asserting it and I am not disputing it** — I am recording that it is the
one supporting claim in the handoff that this review does not cover, so nobody later reads my
CONCUR as having checked it. It does not affect the verdict: the primary value, the CI and the
gate comparison all reproduce exactly regardless.

## Scope compliance

No re-derivation of the protocol, no new measurement, no simulation, policy, candidate,
TestSession, submission, restore or Arena action. Nothing outside `claude_1/**` and my message
namespace was written; the analyzer, tests, result and manifest were read only.

**I did not author the subject and do not review my own work here; equally, this review is itself
a claim and should be treated as one.**
