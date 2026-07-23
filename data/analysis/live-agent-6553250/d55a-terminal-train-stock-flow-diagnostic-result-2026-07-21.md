# D55a terminal TRAIN stock-flow diagnostic — result (2026-07-21)

## Verdict

**Select resource-specific LEMON renewable/source acquisition as the next prospective mechanism.**
Of 732 cells blocked before worker three, 668 (91.26%) cannot close the full bill even after adding
all carried currency and currently ripe matching fruit. LEMON has a deposited deficit in 540/732
(73.77%), 31.15 percentage points above PLUM, satisfying both frozen dominance thresholds.

This is consumed-map stock-flow diagnosis only. It does not evaluate value/support or authorize a
candidate/platform action.

## Integrity

- The diagnostic contains 1,280 unique complete cells.
- Every pre-existing field reproduces D54a A exactly; common-field mismatches are zero.
- Every TRAIN attempt partition remains exact.
- The run completes in 17.87 s at 19.08 effective CPU cores.
- Eighteen runner tests and three analyzer tests pass.

The first analyzer invocation stopped while mapping `standing_*` to the emitted
`final_standing_*` columns and wrote no result. Only that field-name mapping changed; raw data,
classification order, thresholds, and decision logic remained frozen.

## Readiness hierarchy

| Next target | Cells | Deposited ready | Carry closes | Ripe closes | Source unresolved |
|---:|---:|---:|---:|---:|---:|
| worker 2 | 224 | 0 | 0 | 64 (28.57%) | 160 (71.43%) |
| worker 3 | 732 | 0 | 4 (0.55%) | 60 (8.20%) | **668 (91.26%)** |
| worker 4 | 153 | 0 | 0 | 4 (2.61%) | 149 (97.39%) |

The binding target-three branch therefore selects source acquisition, not retry timing, banking,
or merely redirecting workers to already-ripe stock.

## Target-three resource decomposition

| Resource | Deposited deficit | Mean deficit | Still short after carry + ripe stock |
|---|---:|---:|---:|
| LEMON | **540/732 (73.77%)** | 4.940 | **408/732 (55.74%)** |
| PLUM | 312/732 (42.62%) | 1.443 | 248/732 (33.88%) |
| IRON | 208/732 (28.42%) | 0.683 | 204/732 (27.87%) |
| APPLE | 32/732 (4.37%) | 0.093 | 0/732 |

Exact post-stock shortage patterns are led by LEMON only (328 cells), PLUM only (132), PLUM+IRON
(92), no remaining per-resource shortage despite failing jointly at earlier stages (64),
LEMON+IRON (56), IRON only (36), PLUM+LEMON+IRON (20), and PLUM+LEMON (4).

The model plants a mean 26.32 BANANA and 10.55 APPLE trees in blocked target-three cells, versus
only 2.26 LEMON and 4.36 PLUM. Mean harvested yield is likewise 56.87 BANANA, 33.46 APPLE, 9.52
LEMON, and 14.49 PLUM. Universal planting therefore masks a commodity mismatch: production is
renewable but poorly aligned with the exact hybrid-worker bill.

## Next constraint

D56 may add one LEMON source-builder only while funding worker three or four. Its target source
floor must be coefficient-free: `ceil(next LEMON cost / 3)`, one full three-fruit cycle of capacity.
The builder may plant carried LEMON or acquire one from deposited/ripe stock while the bill is not
yet affordable. It must preserve V5's shared ledger, exact bill transaction, roles, specs, caps,
farm caps, and all other target logic.

Because PLUM and IRON remain meaningful secondary shortages, D56 must rerun the full workforce
conjunction. If LEMON production activates but workforce still fails, close the one-resource branch
and advance to a full exact deficit-vector source allocator; do not tune the LEMON floor.

## Evidence

- protocol SHA-256:
  `f3a9abf5d3932c38632ce1f10029d01fb54506b593a666321e0b721a4cd7bb91`;
- diagnostic matrix SHA-256:
  `59240f763c285c5961be0eea417b5a66ad5e049ccb076f7835caeb67fdb766fa`;
- result SHA-256:
  `eca4391b6f39400ad4683972268971ccfd2b00227a6c7f15255b5fec4782067c`;
- runner SHA-256:
  `6cb143cff5e329ce70c8c6468a6e2663268cd2d83794f66155f8109ac80eed40`;
- unchanged V5 strategy SHA-256:
  `f5ec11f3ec8b480e82bbbc6c39e7caa77efdb2a678e0d5a190eaf0035c8e098d`;
- analyzer SHA-256:
  `62b589a2aaaa8be9da8f407053f902f50cf5909797cd632fc90938c003f42c82`.
