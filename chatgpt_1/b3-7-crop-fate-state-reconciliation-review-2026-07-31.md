# Independent review — B3.7 crop-fate state reconciliation

- Reviewer: `chatgpt_1`
- Task: `20260731-b3-7-crop-fate-state-reconciliation`
- Reviewed coordinator head: `08c29244fa060871aea2112110d33b09d627cbfd`
- Review date: 2026-07-31
- Verdict: **`ALREADY_COMPLETE_CONVERSION_BY_DESIGN`**

## Decision

Accept the reconciliation without changing its empirical result or disposition.

The compact result, live-ledger entry, BACKLOG entry, CONSTRAINTS entry, and STATE pointer
faithfully move the already-completed 2026-07-29 census out of stale `IN FLIGHT` state.
They preserve the measured populations, distinguish resident conversion from the top-five
mixed orchard, and do not authorize a planting, harvest-capability, or orchard successor.

## 1. Frozen-population transcription

The original volume-2 B3.7 record and the new compact result agree exactly:

| quantity | resident | top five |
|---|---:|---:|
| games | 220 | 200 |
| owned crops | 2,433 | 8,913 |
| harvested by owner | 0.90% | 29.81% |
| self-chopped | 98.97% | 42.98% |
| chopped/taken by opponent in the selected summary | 0.12% | 15.71% |
| alive at end | 0.00% | 11.28% |

The resident-specific 96.8% value is also transcribed correctly: it conditions on crops
that the resident self-chopped and reports the share that never bore fruit before
conversion.

The four displayed top-five percentages sum to 99.78%, not 100%. This is not an arithmetic
or population error. The census defines a larger mutually exclusive fate partition, while
the ledger reports a selected four-category summary and omits the small
`harvested_by_opponent` category. The canonical human result explicitly warns that the
selected percentages are not forced to exhaust a separately reclassified 100%; retain that
wording.

## 2. Census semantics

`cgauto/crop_fate_census.py` uses generation lineage and classifies each actor-owned crop
once. Fate precedence is:

1. ever harvested by owner;
2. otherwise ever harvested by opponent;
3. otherwise chopped by owner;
4. otherwise chopped by opponent;
5. otherwise alive at game end;
6. unattributed disappearance only as an integrity trap.

Thus the fate percentages are crop-level lifecycle categories, not percentages of all
HARVEST/CHOP actions or shares of final score. Trees do not naturally expire in the
referee; the audit separately operationalizes ripe-fruit expiry as an unserviced ripe run
ending in chop or game end. The reconciliation preserves that distinction and does not
invent a tree-expiry fate.

## 3. Capability and servicing transcription

Every servicing and worker-capability number in the reconciliation matches the frozen
ledger:

- resident live crops per harvest-capable worker: 0.08 at the early checkpoint, rising to
  0.40 by turn 300;
- top-five comparison: roughly 2.5–3.0;
- resident trained workers with `harvest_power = 0`: 220/220, or 100%;
- top-five harvest-power-zero worker share: 9.5%;
- capable resident worker ever within BFS 3 during an unserviced ripe run: 87.4%, or
  73.2% after excluding the orchard-mother reserve;
- true resident residual ripe episodes: 41, median duration two turns;
- top-five residual ripe episodes: 3,922, median duration 19 turns;
- crops still ripening at game end: resident 1, top five 1,010;
- resident true capacity-waste share: about 1.6%.

These quantities support the narrow resident conclusion: scarce residual service events
are not a material harvest-capacity bottleneck for this policy. They do not imply that the
top-five cohort has one homogeneous design or that capacity is its only limitation.

## 4. Orchard-mechanism boundary

The source audit grounds the resident's one exceptional recurring fruit source: the starter
creates and services a protected APPLE mother tree on an own-door, water-adjacent cell.
Ordinary resident crops follow a different lifecycle and are overwhelmingly converted to
wood before bearing fruit. This makes “conversion-by-design” a description of the measured
resident policy, not a universal statement about planting or about every two-worker bot.

The top-five cohort is genuinely mixed: substantial owner harvest, self-chop,
opponent-chop, and live-at-end populations coexist. Its pacing and servicing profile cannot
be transferred to the exact resident merely because both populations plant crops.

## 5. Theft and causal boundary

The theft boundary is copied correctly: opponents receive 18.2% of wood from contested
resident self-chopped trees, equivalent to 2.60 wood per resident game. Calling this “real
but secondary” is consistent with the frozen census and does not erase the effect.

B3.7 itself is descriptive fate accounting. The reconciliation properly uses D175a only as
already-recorded causal corroboration for closing a production/pacing graft; it does not
claim that the census alone estimates the counterfactual value of a new policy.

Accordingly, the following dispositions are justified:

- do not add a resident plant-pacing rule from the top-five profile;
- do not diagnose resident harvest-capacity shortage from these data;
- do not change trained-worker harvest capability;
- do not redesign the orchard or open a panel/candidate from this bookkeeping correction.

## 6. Live-state reconciliation

The stale label has been removed from the live surfaces:

- BACKLOG marks B3.7 done and preserves the exact population/fate summary;
- CONSTRAINTS records conversion-by-design and the non-transfer rule;
- STATE names B3.7 as done rather than an open thread;
- ledger volume 3 records that no rerun occurred and points to the compact result;
- the compact JSON and Markdown preserve the no-action boundary;
- the manifest records no analyzer rerun, bulk access, source/frozen-artifact change, or
  map/panel/candidate/platform action.

The live-ledger phrase “mixed, capacity-limited orchard” should continue to be read with
“mixed” doing real work: the original census found a capacity-limited component, not one
single dominant top-five fate. No canonical correction is required because the compact
result preserves the complete cohort-specific boundary.

## Validation performed

- Cross-read the task, handoff, compact JSON, compact Markdown, and manifest.
- Cross-read the original volume-2 B3.7 record.
- Inspected the census lineage, fate-precedence, ripe-run, mother-tree, worker-capability,
  and aggregation semantics without executing it.
- Cross-checked current BACKLOG, CONSTRAINTS, STATE, and volume-3 wording.
- Verified that the stale exact `IN FLIGHT` B3.7 label is absent from the current tree.

No analyzer was run. No replay, map/range, bulk artifact, simulator, source/frozen artifact,
panel, candidate, TestSession, submission, or Arena surface was opened or changed.
