# D171a — oscillation breaker: bounded fix for the memoryless detour tie-break

Status: FROZEN protocol, authored 2026-07-28 (Fable), from the B3.4 diagnosis
(`scratchpad b34-oscillation-diagnosis-report.md`; findings preserved in ledger vol 2).
Execute exactly; no threshold, arming, or scope change after any outcome is seen.
Classification: execution-class waste-cut (coverage-gap repair of an existing defense).
Expected effect is SMALL — the gates below are sized for that honestly.

## Root cause being fixed (from the diagnosis)

`resolve_move_conflicts_with_priority_and_forbidden`
(`rust/src/bin/yamo_orchard_live.rs:1440–1520`; detour tie-break `:1505–1519`):
candidate generators recompute targets fresh each turn with zero memory; when the natural
step is blocked by an own unit treated as reserved, the detour's
`min_by_key((BFS_dist, Cell))` can tie between "retreat" and "go around", broken by
incidental lexicographic Cell order — and regenerates the identical choice every turn.
17/18 real episodes: a teammate parked ≥85% of the run (11/18 at the own shack door on
the wood loop). The existing `force_unique_door_clear` defense is gated on
`unique_shack_door()` and never fires on 2–4-door maps.

## The fix (exact scope; nothing else may change)

Wire a per-unit short memory into the ALREADY-EXISTING, unwired
`forbidden_for_non_priority` parameter of that same function: each unit remembers the
cell it occupied two turns ago; after **3 confirmed reversals** (A→B→A→B pattern on the
same two cells with an unchanged target), that remembered cell becomes forbidden for the
unit's non-priority move resolution on the next turn, breaking the tie toward "around".
Disarm on target change or net progress (BFS distance to target decreases). Edit ONLY the
formatted dev copy (`rust/src/bin/yamo_orchard_live.rs`): the function body plus one
small per-unit state field; no other function, constant, or module may change. Produce
the slim candidate via the existing pruning pipeline; checksum sidecars for both forms.
Focused unit tests: reversal counting, arming exactly at 3, forbidden application,
disarm-on-progress, and no effect when no reversal pattern exists.

## Panel and baselines

- Fresh maps: seeds **9,853,000–9,853,127** (128 maps; before lock, grep both ledger
  volumes for `9,853` overlaps and verify sealed ranges untouched — abort on any hit)
  × the 8-family opponent panel × both seats = **2,048 paired episodes** vs exact
  resident control (paired = same map/seat/opponent).
- Historical replay check: for the 18 diagnosed episode games, replay the official
  prefixes with the candidate where the established replay machinery permits; the
  oscillation detector (B3.2 criteria: same-two-cell runs ≥10 turns) must confirm the
  runs break in **≥ 14/18**.

## Integrity gates (all before value)

Inactive episodes (breaker never armed) byte-exact vs control; command purity (diffs
confined to move commands of armed units); crop/workforce/reward accounting paired;
1-vs-20-thread byte identity; `LC_ALL=C`; the diff to the dev copy reviewed against the
scope rule (function + state field only).

## Value/mechanism gates (frozen)

- **Mechanism (primary):** fresh-panel same-two-cell runs ≥10 turns reduced **≥ 80%**
  vs control (per-game counts), AND no increase in runs of length 5–9 (no displacement),
  AND the ≥14/18 historical confirmation above.
- **Value (non-regression + activated check):** overall paired mean ≥ **0.0** with
  map-clustered 95% CI lower bound ≥ **−0.5**; activated-subset (games where the breaker
  fired) paired mean ≥ **+1.0**; worst family ≥ **−1.0**; catastrophes ≤ control;
  negative-margin mass ≤ 1.05 × control.
- **Verdict:** all pass → **QUALIFIED** — build the slim candidate artifact
  (checksummed) and STOP at the arena gate (owner authorization required for any
  submission; a qualified waste-cut may also simply wait for a natural resubmission
  occasion). Any gate fails → **CLOSED** — record; no tuning of the reversal floor,
  memory depth, or disarm rule; the diagnosis remains valid as documentation.

## Prohibitions

No edits outside the declared scope; no constant tuning elsewhere in the resident; no
fresh ranges beyond the declared one; no consumed-panel training/selection (this
experiment uses none); no arena/platform/YT action; do not modify the live submission
artifact or `api_submit.py` default.

## Outputs (house convention)

`d171a-oscillation-breaker-{lock,result-2026-07-28.md,result.json}`; the candidate pair
(formatted + slim + sha256 sidecars) under `cgauto/submissions/` named
`candidate-agent6561795-oscillation-breaker.{rs,min.rs}` ONLY if QUALIFIED; runner
extensions as needed; bulk rows external
(`artifacts/experiments/d171a-oscillation-breaker/`). Ledger entry on completion.
