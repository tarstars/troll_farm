# D51a workforce-history opponent population — result (2026-07-21)

## Verdict

**Reject D51 before support evaluation.** The state/history triggers are exact, deterministic, and
behavior-changing whenever reached, but the three field-supported early controllers reach worker
three in only 2,462/8,960 switch cells (27.48%). Consequently only 2,461 cells change their
checkpoint/terminal signature (27.47%), below the frozen 35% activation floor.

All score, distance, coverage, cohort, opponent, and support outcomes are formally ignored. No
fresh data or platform action occurred.

## Mechanical result

- Both 160 x 64 matrices contain 10,240 unique cells and are byte-identical.
- All eight anchors reproduce their current-substrate catalog rows exactly after mapping only the
  model label.
- Every one of 8,960 switch cells preserves its early controller's exact first command.
- All 2,462 recorded switches satisfy their frozen third-worker/history predicate; there are zero
  trigger-integrity failures.
- All 56 switch policies trigger on at least 16 maps, passing the per-policy breadth floor.
- 2,461/2,462 triggered cells change trajectory, showing that the late controllers are not inert.
- The binding failure is global reach: 6,498/8,960 cells never reach a switch.

The two runs completed in 2:21 and 2:17 wall time at about 19.2--19.7 effective CPU cores.

## Interpretation

D51 localizes the failure before the proposed transition. The early `LegendFieldProxyV2`
controllers emit common rich-field TRAIN specs, but under closed-loop interaction they fail to
complete the third-worker funding path on roughly three quarters of cells. A workforce-relative
clock cannot repair a workforce state that never arrives.

This unifies three earlier findings:

1. field replays show later workers are funded by multiple continuing producer cycles;
2. D37/D38 fail when renewable work and exact TRAIN-currency funding are not jointly scheduled;
   D40 succeeds only after composing deficit priority, shack evacuation, and work conservation;
3. D49 shows that coordinated reservation matters but persistent predicted deposits become stale
   under opponent interference.

The next eligible architecture is therefore not another whole-controller switch. It is a
procedural factorized job allocator that owns funding and production from the opening, uses
hybrid-capable workers, reallocates at job boundaries, and transactionally revalidates reserved
TRAIN currency. Only after that scheduler broadly reaches worker three should opponent-support or
policy-value fields open.

## Analyzer quarantine disclosure

The first analyzer invocation compared the deliberately different anchor labels and produced
1,280 false mismatches. More importantly, it continued into support scoring despite the genuine
activation failure. That accidental JSON is preserved and quarantined by SHA-256; none of its
support fields were used here or in the next hypothesis.

The corrected analyzer implements the protocol's label mapping, stops immediately on the failed
activation conjunction, and explicitly marks all outcomes ignored. No threshold or raw run was
changed.

## Gate result

| Gate | Result |
|---|---:|
| Complete byte-exact repeat | pass |
| Eight exact anchors | pass |
| Exact early openings | pass |
| Trigger integrity | pass: 0 failures |
| At least 45 policies trigger on >=16 maps | pass: 56 |
| At least 35% switch cells change | **fail: 2,461/8,960 = 27.47%** |

Formal activation conjunction: **fail**. Support gates were not evaluated.

## Evidence

- protocol SHA-256:
  `99e87ea222d3762f368979274190d38ffe44c7e48ba52ef7dbfe201de8857224`;
- A/B matrix SHA-256:
  `fcfbd3553c2d953cb55842407300319abf62d3b8c7f16d69cf3e1c6af955aa47`;
- corrected activation result SHA-256:
  `6ba443b5058acb5fdf2069391bd171deacc4741ac46719d8e876c187deb4b4c8`;
- quarantine note SHA-256:
  `59896a1a1ee20809a122ef6f5fbab4ad6ad42b505e2235ec12b84a77e4ac3b4f`;
- quarantined accidental JSON SHA-256:
  `e3b545deaae72df7ff89668039cb53325bafc03700845ae873655d5f81187a7d`;
- runner SHA-256:
  `74dc0cca758f2e97902662a62656555ce790ec6b4aceaa225c37ae4b056bc3e4`;
- corrected analyzer SHA-256:
  `678c1955344fcce5ea30d842fe6df3f8a23e2baa30ebeb7ce81564cb5c609f71`;
- focused verification: 13 Rust runner tests and four Python analyzer tests pass.
