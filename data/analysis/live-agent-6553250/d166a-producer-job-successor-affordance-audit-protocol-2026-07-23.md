# D166a producer-job successor affordance audit — frozen protocol

Date: 2026-07-23  
Status: frozen before extracting field return classes or simulating local affordances

## Question

D164 establishes a broad same-worker producer → suppressor → producer (`P→S→P`) field motif.
D165 shows that 237/1,024 consumed local tasks contain the observable `P→S` prefix, but zero retain
the exact crop generation on which that worker produced earlier. D166 asks:

> What concrete production job succeeds suppression in the field, and is that job visibly
> available at the corresponding local `P→S` transition?

This is a read-only representation/support audit. It does not intervene, estimate causal value,
train a selector, modify the resident, create a candidate or submission, contact the platform or
YT, or open reserved maps.

## Frozen inputs

### Immutable field panel

Reuse snapshot `20260723T074715Z-d164a` and precisely the 392 open actor occurrences admitted by
D164:

- 50 current rank-1--5 appearances;
- 150 current rank-6--20 appearances; and
- 192 exact-resident appearances.

Do not read the eleven sealed confirmation games. Reconstruct exact states and crop generations
from the immutable raw/processed snapshot. Run the occurrence extraction once with one process and
once with 20 processes and require byte-identical sorted JSONL.

### Consumed local panel

Replay the unchanged exact Yamo/Orchard resident on D148/D161 maps
`9,844,136--9,844,199`, both seats, and all eight frozen `MacroOpponentMode` families: 1,024
tasks. Reserved maps `9,844,200--9,844,215` remain untouched.

Run once with one worker and once with 20 workers and require byte-identical sorted TSV. The
terminal resident must reproduce D161 on all shared fields.

Bulk products go under the verified external-backed path
`artifacts/experiments/d166a-producer-job-successor-affordance`. Compact protocol, lock, analyzer,
aggregate result, and report remain in the repository.

## Frozen field extraction

Use D164's exact successful material-event and crop-generation semantics. For each worker,
compress consecutive material events into:

- `P`: successful own-crop PLANT or successful own-crop HARVEST;
- `S`: successful CHOP of an opponent-created crop.

For the first `P→S→P` subsequence in each actor occurrence, retain the exact three source events
and report:

1. prior-production verb (`PLANT` or `HARVEST`);
2. return-production verb (`PLANT` or `HARVEST`);
3. prior, suppression, and return turns and workforce;
4. prior and return crop generation IDs and cells;
5. whether return reuses the prior crop generation or cell;
6. whether the return generation already exists at suppression entry;
7. return target kind and suppression duration; and
8. actor, cohort, rank, seat, and game identity.

Also report all occurrences without a cycle so cohort rates reproduce D164 exactly. No outcome,
margin, agent identity, or later action may change which cycle is selected.

## Frozen local entry and affordances

Track successful own production and crop ownership exactly as in D165, but retain historical
producer identity after its crop disappears. At the first successful opponent-crop CHOP by a
worker that has any prior confirmed `P` event, capture the post-referee state. Each task contributes
at most one entry row.

Report the prior production verb/cell plus these prespecified successor affordances for that same
worker:

### H — current own-crop harvest

`H-ripe` is available when the worker has positive harvest power and free capacity and at least
one currently live own crop contains fruit. `H-live` uses the same worker conditions but permits
an unripe live own crop. Report counts, nearest Manhattan distances, target fruit, cooldown, and
deterministic nearest-cell/id tie-breaking inputs.

### P — carried-seed planting

`P-carry` is available when the worker carries at least one fruit item and at least one reachable
walkable cell has no plant. Report carried fruit by kind, legal empty-cell count, and nearest
distance. This is a job affordance only; D166 emits no MOVE or PLANT.

### Natural continuation

Continue the untouched resident and record the first later successful `P` event by the same worker,
its verb, target generation/cell, and latency. Report natural return within 16 and 32 turns and at
any later turn. This is descriptive support, not a treatment.

Report raw opponent-crop CHOP count, historical-producer CHOP count, both seats, all family
breakdowns, worker stats/capacity, current own-crop counts, and ownership/integrity telemetry.

## Integrity gates

Interpret no support result unless all conditions pass:

1. field one-process and 20-process products each contain exactly 392 unique actor occurrences and
   are byte-identical;
2. field cohort sizes and `P→S→P` counts reproduce D164 exactly: 36/50 top-five, 41/150 ranks
   6--20, and 21/192 resident;
3. field decoding, generation ownership, worker identity, event success, and sealed-product gates
   remain exact;
4. local one-worker and 20-worker products each contain exactly 1,024 unique tasks and are
   byte-identical;
5. all local terminal resident fields reproduce D161 exactly;
6. local production occurs in all 1,024 tasks, opponent-crop CHOP occurs in exactly 932 tasks, and
   historical-producer opponent CHOP occurs in exactly 237 tasks with 1,976 events, reproducing
   D165;
7. all local games terminate with exact reward identity and zero provenance, ambiguous-birth,
   ownership, command, or worker-history failures; and
8. D166 emits zero controller commands and changes no action or state.

A failed integrity item is repaired without interpreting support.

## Field return-class selection

Consider only the 36 top-five first cycles; ranks 6--20 and resident are prespecified independent
support cohorts.

A single verb class is field-dominant only if:

1. it accounts for at least 60% of top-five returns;
2. it accounts for at least 50% of rank-6--20 returns;
3. at least four of five top agents use it;
4. it appears in both seats; and
5. its top-five median suppression duration is at most 32 turns.

If both verb classes fail, D166 must not select a class by local coverage or outcome. It closes a
hand-written single-class successor and recommends trajectory-valued semantic action evaluation.

## Local transport-support gate

Map the field-selected verb without tuning:

- field `HARVEST` maps to `H-ripe`;
- field `PLANT` maps to `P-carry`.

The mapped affordance transports locally only if:

1. it is available in at least 64 of the 237 exact historical-producer entry tasks;
2. availability covers both seats and at least six opponent families;
3. at least 50% of available entries have deterministic target distance at most 16;
4. worker identity, capacity, ownership, and target-legality checks are exact; and
5. the same affordance is nonzero in at least two of the three field cohorts.

`H-live`, the H/P union, natural 16/32-turn return, return-generation reuse, and all alternative
priority rules are diagnostics only. They cannot rescue a failed mapped affordance in D166.

## Decision

- If integrity, field dominance, and local transport support all pass, freeze exactly one D167
  causal successor option on the same consumed maps with exact warmed-resident fallback. D166
  alone does not authorize a candidate, Arena, fresh maps, or submission.
- If field dominance fails, stop hand-writing a single return verb and move to
  trajectory-conditioned semantic job value.
- If field dominance passes but local support fails, close that concrete successor class; do not
  switch to the locally more common class, loosen the entry, or tune distance/horizon on D166.

Run locally: both datasets are small and expected to complete in minutes. Verify `medium_data`
before all bulk writes. The canonical unused YT root remains exactly
`//home/delivery_ml/research/tarstars/troll_farm`.
