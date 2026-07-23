# D125a fit-activity-calibrated q6 — fit result

Date: 2026-07-22  
Portfolio decision: **close the old robust seed selector before fresh validation**

D125 converts D124's useful band into a deterministic training-only threshold. For each exact
D119 model, the midpoint between the 215th and 216th per-task maximum gate logits activates 215 of
256 fit tasks (83.984%). Two complete fit-selection executions are byte-identical. Three of four
calibrated models pass all structural and fit-policy gates.

| Seed | Calibrated offset | Fit mean | Minimum fold | Worst family | Proposal regret | Eligible |
|---:|---:|---:|---:|---:|---:|:---:|
| 11901 | -0.03358 | +5.543 | +3.414 | -4.000 | 16.864 | no |
| 11902 | -0.02695 | +6.133 | **+5.484** | -2.813 | 17.235 | yes |
| 11903 | -0.10122 | **+7.746** | +5.391 | **+0.625** | **16.659** | yes |
| 11904 | -0.04066 | +5.797 | +4.320 | +2.688 | 16.982 | yes |

The unchanged lexicographic robust key selects seed11902 because its minimum fit fold exceeds
seed11903 by only `0.094`. That priority discards much larger advantages for seed11903 in mean
(`+1.613`), worst family (`+3.438`), and proposal regret (`0.576` lower). Existing D124 development
evidence independently makes the mismatch actionable: seed11902 has no feasible fine-grid point;
at offsets `-0.05` and `0.00` it reaches only `+1.579` and `+1.686` on the retired aggregate,
whereas seed11903 owns two stable feasible points.

The fresh range `9,843,780--9,843,795` remains unopened. Although the frozen D125 protocol permits
collection after exact selection, spending it on a controller already rejected by the designated
development panel is not profitable. This is not a failure of 84% quantile calibration; it is a
failure of the old seed selector, whose first lexicographic coordinate is too sensitive to a tiny
two-fold difference.

Next retain the exact calibration rule and choose among fit-eligible seeds by the structural metric
that the D117--D119 sequence identified as the bottleneck: minimum mean proposal regret, with
higher within-ten coverage and fixed seed order only as ties. Freeze that single change as D126,
repeat it exactly, and open the same untouched validation range only if it selects an eligible
controller.

Fit lock SHA-256: `ea56bbbf3859eed255bee4bfdcf2a2c10fbb1499cd61d07176fbaf5c1e32ada3`  
Repeated fit result SHA-256: `515a2ed60194627bd28faff06e611a77b04c241f3e43f19d181a01d5a0d34b68`
