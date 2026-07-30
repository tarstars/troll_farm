# N1 maturity-curve measurement

**Verdict: IMMATERIAL**

- Support: **PARTIAL**
- Snapshots: 7
- Panel rows / unique / repeated agents: 7000 / 1034 / 1008
- Score-changing intervals: 2549
- With/without advancing updateTime: 2549 / 0
- Rank-only score-frozen intervals: 592
- Age-bin crossings: 41
- creationTime/updateTime coverage: 100.0% / 100.0%
- Lifetime battle-count coverage: 0.0%
- Visible new/dropped battle IDs: 10314 / 6478

## Resident projection

- Score: 21.47
- Age/bin: 10.35635119212963 / d7_14
- Remaining uplift: -0.16120039741558279
- Mature projection: 21.308799602584415
- Gap to 24.70 now/projected: 3.2300000000000004 / 3.3912003974155844
- Gap to 25.40 now/projected: 3.9299999999999997 / 4.091200397415584

## Interpretation

- creationTime is usable; battle accumulation remains censored
- Individual fixed effects identify only within-agent age-bin transitions; snapshot fixed effects absorb pool-wide score shifts.
- Rank-only movement is pool drift, not maturity.
- Recent battle-list length is never treated as lifetime games.
- The anecdotal 3–4 point figure is not used as a prior.

## Reproduction

```bash
python3 cgauto/maturity_curve_audit.py --snapshot-root data/raw/snapshots --output-dir chatgpt_1/n1-maturity-result
```
