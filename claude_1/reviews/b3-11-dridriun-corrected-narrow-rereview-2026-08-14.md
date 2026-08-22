# A-4 — B3.11 Dridriun postmortem corrected narrow re-review

- **Reviewer:** `claude_1`, on the VM · **Date (real UTC):** 2026-08-14
- **Task:** `20260731-dridriun-fruit-control-postmortem`; iteration-3 item **A-4**
- **Subject:** `local_codex_1`'s corrected handoff `20260731T134500Z`, game `896352129`
- **Verdict: CONCUR — the correction holds and the conclusion stays measurement-only.**
- Read-only. No re-derivation, no new measurement, no capability, target, threshold or Arena
  action.

## Separation

Author `local_codex_1`, dormant since 2026-08-06; I have never touched this postmortem. An earlier
`chatgpt_1` re-review exists but that agent is unreachable and its dispositions are
`RECORDED / UNREPLICATED` — this is the execution re-review.

## 1. Pinned hashes — both match on disk

| artifact | pinned sha256 (16) | on disk |
|---|---|---|
| compact JSON `…dridriun-fruit-control-postmortem-result-2026-07-31.json` | `c0ca3ce9bfb86cc5` | **match** |
| human report `….md` | `399b347a84b6fea8` | **match** |

## 2. "The opponent harvested zero resident-created apples" — confirmed, three independent ways

```
resident_door_apples.opponent_harvests                       = 0
resident_door_apples.actual_opponent_capture                 = False
boundaries.opponent_harvest_of_resident_apples_observed       = False
```

Three separate fields in the compact agree, and the last is stated as a *boundary* rather than a
measurement — the record itself refuses to let the zero be read as anything more.

## 3. "Capture reachable but not realized" — both halves confirmed

**Reachable:** the harvest-capable opponent unit 1 (`movement_speed 1, carry 1, harvest_power 1,
chop 1`) sits at raw BFS / ETA `[3, 2, 3, 3]` on the post-PLANT states and `[3, 3, 3, 3]` on the
first-ripe states. A few turns away, with the capability to take the fruit.

**Not realized:** `actual_opponent_capture = False`, and `opponent_harvests = 0`.

Also confirmed: the handoff withdraws an earlier "mixed 2/1" ETA label. The compact carries no 1s
in either ripe-cycle vector, so the withdrawal is reflected in the data and not merely announced.

**This pairing is the whole finding**, and it is the kind that is easy to over-read: the
opportunity existed and was not taken *in this one game*. That is not evidence the opponent cannot
take it, nor that contesting it is worth anything.

## 4. "Measurement-only" — confirmed, and the record enforces it structurally

`verdict = NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`, with an explicit decision block:

```
read_only_existing_corpus_precheck_may_be_proposed = True
source_or_policy_change_authorized                 = False
runner_or_panel_authorized                         = False
candidate_or_platform_action_authorized            = False
```

and boundaries:

```
opponent_harvests_are_observed_not_causal_savings      = True
resident_destroyed_fruit_stock_is_not_independent_turn_value = True
one_game_establishes_frequency_or_value                = False
existing_broad_failed_interventions_may_not_be_repackaged = True
```

**No capability change, no target, no threshold** — as required. The last boundary is the one
worth quoting forward: a narrowed precheck must not become a vehicle for re-proposing the broad
interventions that already failed (Phase 21, D173a/b, B3.7, B3.10 remain closed).

## 5. Supporting counts reconcile

| handoff claim | compact |
|---|---|
| harvest accounting `83 / 83 / 83 / 0` | `83` commands, `83` successful, `0` failed-or-zero-gain |
| first generation: 25 pre-contact commands = 25 confirmed units | `25` and `25` |
| resident CHOP `84 commands / 82 successes` | `84` / `82` |
| eight first-contact + eight joint-removal + 22 ripe CHOP rows | `8` + `8` + `22` = **38** |

## What I did NOT verify

The handoff states that **a direct trajectory reconstruction compares all 38 rows field-exact to
the compact**. I verified the **row counts** (8 + 8 + 22 = 38) but not field-exactness against an
independent reconstruction — that is re-derivation and outside A-4's narrow scope. **I neither
assert nor dispute it.** Recording it so my CONCUR is not later read as having reproduced the
appendix row by row.

## Scope compliance

No re-derivation, no new measurement, no replay, analyzer run, simulation, source, candidate,
TestSession, submission, restore or Arena action. Only `claude_1/**` and my message namespace
written.
