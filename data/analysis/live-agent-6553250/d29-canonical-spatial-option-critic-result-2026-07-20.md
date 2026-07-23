# D29 canonical spatial option critic — result (2026-07-20)

## Verdict

**Pass.**  The frozen 7,017-parameter spatial option critic passed every crossed-development and
untouched-confirmation gate.  On the 120-map prospective partition it selected permanent
`ownership2` in 40.99% of cells, achieved 88.56% positive-cell precision, and improved the
seed-clustered terminal margin by **+35.225** (95% normal CI `[27.874, 42.576]`) over the exact
warmed resident.  All eight opponent means and all six untouched 20-map-block means were
positive.  This authorizes compact-deployment engineering under a separately frozen protocol; it
does not authorize an Arena submission.

## Integrity and reproducibility

- Smoke joined 80/80 independently generated spatial/scalar/label cells with zero root,
  reached-cut, plane-shape, plane-hash, or orientation mismatch.  The two 80-row spatial exports
  were byte-identical (SHA-256 `81af145c1bc8ce1f87d0e07e0f93cb89f218525dcda9f883fb7ab6b6b4b1ec90`).
- Development joined all 9,600 cells from seeds 53,000--53,599, both seats, and eight opponents.
  It had zero missing/unexpected cells, zero duplicate/missing branches, zero root mismatch, and
  zero bad spatial hash or canonical orientation.
- The sole selectable evaluation was the preregistered 42-fold crossing of six unseen 100-map
  blocks with seven unseen structural opponent families.  Two complete executions emitted
  byte-identical prediction artifacts, SHA-256
  `c36e996c0c7081b0c38280a14a10987de1aebcadaec833a5bfc81dd5366e9a9a`.
- Only after that exact repeat passed was the full-development checkpoint written.  Its SHA-256 is
  `765e3bc5707ced9053a76d2735232e873003baccff6500bd8c1377b3c28721c9`.
- Confirmation joined all 1,920 cells from untouched seeds 53,600--53,719 with the same zero-error
  integrity checks and evaluated that checkpoint without a refit.

## Results at several levels

### Statistical level

| Metric | Crossed development, 600 maps | Prospective confirmation, 120 maps |
|---|---:|---:|
| Switch rate | 41.15% | 40.99% |
| Positive-cell precision | 80.05% | 88.56% |
| Seed-clustered margin delta | +30.252 | +35.225 |
| 5%-trimmed margin delta | +27.028 | +32.442 |
| 95% lower confidence bound | +27.124 | +27.874 |
| Positive / tied / negative seed means | 412 / 114 / 74 | 87 / 27 / 6 |
| Hindsight positive-option value captured | 57.07% | 68.04% |
| Resident-relative own-score delta | +43.132 | +46.524 |

The confirmation point estimate improved rather than regressed, while its switch rate stayed
within 0.17 percentage point of development.  This is strong evidence against the D25 failure
being repaired by a narrow threshold accident.

### Robustness level

Development opponent deltas ranged from +16.132 (`gold_adaptive`) to +59.408 (`printer_bot`);
confirmation ranged from +25.508 to +62.904.  Development's six 100-map block means ranged from
+25.607 to +35.180.  Confirmation's six 20-map block means were +34.463, +32.600, +38.181,
+23.334, +39.663, and +43.109.  Thus neither an opponent-family cell nor a chronological map
block carries the aggregate gain.

Tail behavior also improved.  On confirmation, catastrophic frequency fell from 15.94% for the
resident to 9.32% for the selector, and total negative-margin mass fell from 59,375 to 40,790
(ratio 0.687).  The worst confirmation seed mean was -18.25, but only six of 120 seed means were
negative.

### Policy level

The result supports a genuine macro option rather than permanent replacement of the resident.
The model rejects farming in roughly three fifths of turn-75 states and captures over two thirds
of the prospective hindsight-positive value in the remainder.  The resident remains the fallback
and supplies the exact first 74 turns in both branches.

### Representation and mechanism level

D25 showed that scalar trajectory summaries carried signal but generalized at only 73.23%
precision under simultaneous unseen-map/unseen-family validation.  D29 combines those same 426
observable scalars with a canonical 36 x 11 x 22 raw spatial state, increases the map sample five
fold, and estimates the conditional 25th percentile rather than a mean-plus-buffer.  The 88.56%
prospective precision shows that this package resolves much of the missing context.  It does not
identify how much causal credit belongs separately to the spatial planes, larger sample, or
quantile objective; those are deliberately not post-result ablations of the selected model.

D27--D28 remain relevant: cold-return penalties made short farm pulses poor, whereas D29 chooses a
terminal farm commitment and never pays a return transition.  The learned option therefore fits
the diagnosed policy-state discontinuity rather than contradicting it.

### Transfer and engineering level

The evidence is exact in the local referee and robust across generated maps and seven structural
families, but those opponents are still proxies rather than the current Legend field.  The model
also requires 426 history scalars, 36 spatial planes, inference weights, and the complete cold
`ownership2` policy alongside a 62,725-byte resident.  Numerical preservation, turn-75 live-state
parity, latency, and the 100,000-byte source cap are therefore real remaining gates, not packaging
details.

## Disposition

Open D29a compact deployment under
`d29a-compact-spatial-option-deployment-protocol-2026-07-20.md`.  Do not change the model,
threshold, turn, fallback, option, or confirmation evidence.  A complete D29a pass may open a
small controlled field-transfer experiment; it still does not itself authorize Arena submission.

## Frozen artifacts

- protocol SHA-256: `c63c526ec4b75b162689410ed6fc49cd119c3bf494a153843da525cd98a98083`;
- spatial exporter SHA-256: `d057ed19d241bcf3ffebc18d71ebc81856793f4bec500d0beb2f49364e465dc0`;
- trainer/evaluator SHA-256: `942a69611c757c4ddb33bfcfe3076e065790a142364a0ae5b983a99f56fa43f5`;
- development result SHA-256: `ee941a86042b0461763f61efc413b5191cc33295daaea50803835f2ad9e2dab3`;
- confirmation result SHA-256: `7b40435256b6b41eacf6c6de6c64c5a534bb4469947d35dcc0829dd2432ef24c`;
- confirmation prediction SHA-256: `61dc47ef310d12454679b89f9c56a8fc3a05d2341d9fb562871f255a2acdf19f`.
