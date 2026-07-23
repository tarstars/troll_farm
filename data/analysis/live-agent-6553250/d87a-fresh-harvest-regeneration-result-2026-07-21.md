# D87a fresh-harvest regeneration commitment — result (2026-07-21)

## Decision

**Reject the candidate and keep confirmation maps `9,914,016--9,914,031` sealed.**

The intervention activates broadly and passes every integrity and activation gate, but fails all
material value and safety gates. Remembering every resident-selected natural-tree HARVEST as an
immediate regeneration commitment creates plants that the candidate never later harvests. It
therefore spends liquid fruit and worker time on a conversion loop that loses wood and frequently
donates value to the opponent.

## Reproducibility

- Frozen protocol: `d87a-fresh-harvest-regeneration-protocol-2026-07-21.md`, SHA-256
  `b76bc2870b279f39e764a0799ff6541669ab4db00d6a9cdb21652a080ccf30d6`.
- Repeat A and B: 512 rows each, SHA-256
  `73f3752369f2ac7f85bc66a70155597b5f1468376bd000d32f0a0f5a5733226b`; the sorted files are
  byte-identical.
- Analyzer: `cgauto/analyze_d87a_fresh_harvest_regeneration.py`, SHA-256
  `749e362eb4b32dd7a9f3e32201ac728260ee41d4f305e13f6b7245597691957a`.
- Analyzer tests: `tests/test_analyze_d87a_fresh_harvest_regeneration.py`, SHA-256
  `ca3eaf75606e83f98f8b4d0dc1e9602aaab339d9aa77f9b5e1037add5fa9de5e`; 3/3 pass.
- Source under test: `rust/src/bin/yamo_orchard_live.rs`, SHA-256
  `62946d06d42dc8ebbbd4ee3c8f2bcf0bf6087b7431fcc79d0afb6008d2b885bf`; all 9/9 bin tests
  pass. The research switch is disabled in the default constructor.
- Harness: `rust/src/bin/ownership_aware_complete_economy.rs`, SHA-256
  `f59c4f4f3c7786856eacc6d7360bdea5446eefea2e8acd4ab2c7779a2a8154c5`; all 18/18 bin tests
  pass.
- Machine-readable result: `d87a-fresh-harvest-regeneration-result.json`, SHA-256
  `fcd682538a8ca082203ae1e0d60752becd196b3246fe51b5a670e75cef2658ff`.

The first harness repeat exposed nondeterministic debug serialization of an unordered state set.
That instrumentation-only defect was repaired by sorting the set before hashing; the prospective
maps, policy, intervention, outcomes, and gates were not changed. The repaired A/B run is exact.

## Integrity and activation

All 512 rows form the preregistered 256 resident/candidate pairs over 16 maps, both seats, and all
eight opponent families. Games are complete or explicitly stalled; command parsing is valid;
fruit and wood provenance are both 100% assigned; and worker counts match within every pair.

There are zero candidate/shadow mismatches before the first eligible fresh-HARVEST commitment.
All 144 inactive tasks are exact in action hash, canonical state hash, and terminal result. The
candidate activates in 112 tasks across both seats and all eight opponents, creates 273 valid
commitments, and completes all 273 requested replants. Thus this is a test of the intended
mechanism, not a failed activation or accounting artifact.

## Paired value

| Cohort | n | Mean margin delta | Mean own score delta | Mean opponent score delta | Mean wood delta | Mean plants delta | Mean own-crop harvest delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| All pairs | 256 | -22.383 | -11.668 | +10.715 | -3.008 | +1.691 | 0.000 |
| Active | 112 | -51.161 | -26.670 | +24.491 | -6.875 | +3.866 | 0.000 |
| Sparse, 1--2 commitments | 65 | -45.738 | -26.585 | +19.154 | -6.831 | +3.000 | 0.000 |
| Sustained, 3+ commitments | 47 | -58.660 | -26.787 | +31.872 | -6.936 | +5.064 | 0.000 |

Only 12 active tasks improve, two tie, and 98 regress. Active deltas have tenth percentile -117,
minimum -252, and maximum +196. The map-cluster normal 95% interval for overall mean margin is
`[-37.596, -7.170]`.

Every active opponent-family mean is negative: `sched_bot` is least harmful at -4.071, followed
by `silver_boss` at -17.714; adaptive Gold is worst at -104.500. Catastrophic losses
(`margin <= -100`) rise from 36 to 50 and negative-margin mass rises from 7,890 to 10,919, a
1.3839 ratio.

## Gate result and interpretation

The candidate passes crop creation and positive added-plant gates only. It fails overall and
active value, confidence interval, win/regression balance, family robustness, tail safety,
catastrophe, negative-mass, wood-preservation, and own-crop-harvest gates.

The key causal observation is that 273 new crops lead to exactly zero extra own-crop harvests.
The resident's existing regeneration commitment was designed as a plant-to-wood conversion path,
not as a renewable orchard task. Connecting a fresh HARVEST to that state machine therefore
cannot reproduce yaichi's economy.

Do not tune species, cell choice, turn, or commitment lifetime on these consumed maps. The next
iteration must reconstruct yaichi's full per-unit task grammar from public replay `MSG` telemetry:
bank natural fruit, bootstrap protected crops from the shack, maintain mature own crops by
HARVEST-to-PLANT, and keep the trained worker on a separate wood/logistics role. No candidate,
TestSession, submission, resident replacement, or Arena write is authorized by D87.
