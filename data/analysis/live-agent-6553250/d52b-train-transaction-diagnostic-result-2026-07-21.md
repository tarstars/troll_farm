# D52b TRAIN transaction diagnostic — result (2026-07-21)

## Verdict

**Require exact TRAIN-bill reservation through higher-priority actions; do not add a new shack
rule.** Every failed worker-three/four TRAIN attempt is explained by a preceding PICK removing
required currency. The frozen 80% budget-cause discriminator passes at 100%; shack-inclusive and
unexplained rates are both zero.

This is consumed-map transaction telemetry only. It does not change D52a's rejection and supplies
no score, support, candidate, or platform conclusion.

## Integrity

- The diagnostic contains an exact 160 x 8 grid with 1,280 unique cells.
- Every pre-existing field matches D52a A in all 1,280 cells; instrumentation did not alter policy
  behavior.
- Every row and every target-workforce aggregate satisfies attempts = successes + the four
  mutually exclusive failure categories.
- The run completes in 16.56 s at 19.68 effective CPU cores.
- Fifteen runner tests and four analyzer tests pass.

## Attribution

| TRAIN target | Attempts | Successes | Failures | Shack only | Budget only | Both | Other |
|---:|---:|---:|---:|---:|---:|---:|---:|
| worker 2 | 13,460 | 948 | 12,512 | 468 | 12,044 | 0 | 0 |
| worker 3 | 5,394 | 252 | 5,142 | 0 | 5,142 | 0 | 0 |
| worker 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 |

Counts are attempts, not unique cells: after an invalidated TRAIN, V3 often repeats the same
decision on later turns. For the binding worker-three/four pool, 5,142/5,142 failures are budget
only. The pooled success rate is 4.74% per attempt because the controller repeatedly emits TRAIN
while a same-turn PICK spends one reserved unit before TRAIN priority resolves.

The 468 worker-two shack failures equal the matrix's 468 immediate opening TRAIN commands. They do
not explain final worker-two failure: the worker eventually evacuates and all 468 immediate-opening
cells reach worker two. D52b therefore does not authorize adding explicit evacuation to this
scheduler.

## Causal interpretation

V3 checks affordability at decision time, then passes `pending_cost=None` to production whenever
TRAIN is currently affordable. `v2_pick_seed` consequently treats every deposited fruit as
spendable. PICK resolves before TRAIN, takes one PLUM/LEMON/APPLE, and invalidates the exact bill.
Two producer slots create more opportunities for that PICK, explaining D52a's otherwise anomalous
one-producer advantage.

The next eligible change is singular: when a TRAIN command is emitted, retain its exact current
cost as an intra-turn reservation and allow PICK only from per-resource surplus. Deficits, worker
specs, caps, role counts, target ordering, fallbacks, planting, and shack behavior must remain
unchanged. D53 must rerun the full D52 activation conjunction and require zero post-PICK budget
failures before support opens.

## Evidence

- protocol SHA-256:
  `d7fd21f6fa3a3107792d82079d5f88dcd757d1c8862611c784b2614ddd81ad7e`;
- diagnostic matrix SHA-256:
  `cca5ce8d910af069963215330216493f9dc648e617e280b1a1c2da8cca2ecddb`;
- diagnostic result SHA-256:
  `9b4913fd19b243f4b37bbdf558901dd822e9d329e0b2457ca9ed62cde4cc69e6`;
- runner SHA-256:
  `6df3732778f97663e830a84b407c92694477576fdd4c46196d9ba54bc01a622e`;
- unchanged V3 strategy SHA-256:
  `d13dea27b559e531d7fc53dc316768d2cb30e91e1064dd46f46c2e05fb645b78`;
- analyzer SHA-256:
  `1fee7ccf9b6ec61a62a0b09193e6d25ebd44b673a43ee0221a708d21dbc2016a`.
