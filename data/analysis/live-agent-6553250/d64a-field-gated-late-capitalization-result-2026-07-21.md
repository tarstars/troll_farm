# D64a field-gated late-capitalization result (2026-07-21)

## Verdict

**Formally invalid on one unconditional substrate-safety gate; every admissible directional result
also rejects this action/selector pairing.** Four fresh D40 control tasks finish with only one
worker, so the preregistered requirement that the field-gated policy retain at least two workers in
every task fails. Those four tasks are ineligible for the post-turn-100 intervention and are
terminally identical under all policies, but the gate was unconditional and is not waived.

The remaining results are therefore diagnostic, not promotable value evidence. They are decisive
enough to prevent an immediate retry: suppressing D40's pending late third-worker plan loses about
68 margin on eligible tasks, while a two-arm hindsight oracle exposes less than two points of mean
headroom.

## Exact execution and integrity

- Two independent 4-policy x 256-task matrices are byte-identical, SHA-256
  `3ef63ac5245ae1fa83ee9290f8c1a6bffeb3e8c4fe37bee3137e184745f78576`.
- All 1,024 rows are present for 16 fresh maps, both seats, and eight opponent families.
- Eligibility, decision turn, state hash, classifier score, and support diagnostics match exactly
  across policies before divergence.
- Every ineligible task is terminally identical across policies.
- Illegal commands, provenance failures, deposit-prediction failures, worker-cap failures,
  nonfinite features, action-accounting failures, and reward-identity failures are all zero.
- The field-gated policy creates a crop in 256/256 tasks and never exceeds three workers.

## The failed safety invariant

The field-gated policy retains at least two workers in 252/256 tasks, not 256/256. The four misses
are both seats of seeds 9,830,002 and 9,830,014 against `resident`. Exact D40 also finishes with one
worker on the same four task keys, with the same action/state hashes:

| Seed | Block | Seats | Own crops per seat | Margins |
|---:|---|---|---:|---:|
| 9,830,002 | development | 0, 1 | 44, 44 | -140, -148 |
| 9,830,014 | validation | 0, 1 | 31, 35 | -123, -136 |

All four start with a producer-bill shortage but no immediately deficit-reducing job: seed
9,830,002 lacks three PLUM and one LEMON; seed 9,830,014 lacks two PLUM. The starting worker
occupies the shack and the initial deficit audit selects no productive reduction. A narrow stock-
flow audit is required before altering D40.

## Support and selector activity (diagnostic)

The common pre-intervention cohort is large: 114 eligible tasks, split 56 development / 58
validation. Field-distance support is not the primary problem: 107/114 (93.86%) lie inside the
frozen held-agent RMS-z radius.

The fixed 0.5 classifier is nevertheless almost one-sided on D40:

| Block | Scale | Suppress |
|---|---:|---:|
| Development | 1 | 55 |
| Validation | 1 | 57 |
| Total | 2 | 112 |

Thus the activity conjunction fails. The observational classifier recognizes D40 as a mostly
non-scaling economy even though D40's complete funding plan makes scaling valuable.

## Action headroom (quarantined diagnostic)

Among 114 eligible tasks, the two-arm oracle selects normal D40 scale in 104 and permanent late
suppression in ten. Its mean gain over D40 is only **+1.904**, with strict gains in 10/114 = 8.77%.
Both preregistered headroom gates fail (+5.0 and 20%). A scale-versus-permanent-suppress latch is
therefore too coarse to justify Monte-Carlo/value learning on this D40 substrate even before
considering the classifier.

## Selector outcomes (quarantined diagnostic)

| Comparison | Eligible mean margin delta |
|---|---:|
| Field gate vs D40 | **-67.561** |
| Never late scale vs D40 | **-68.974** |
| Field gate vs never late scale | +1.412 |
| Field gate vs inverse selector | **-66.149** |

The field gate loses 58.456 own score and gives the opponent 9.105 points on the eligible cohort.
Its validation delta is -51.966, it adds ten catastrophic losses overall, and it agrees with the
two-arm oracle in only 12/114 tasks. Overall mean margin falls 30.086 points. Seven of eight
opponent families regress; only `resident` improves (+2.688 overall), while the worst regression is
-49.000 against `compact_gold`.

The inverse selector is close to D40 because it scales in 112/114 eligible states; this is not a
new candidate, just confirmation that the direction of the field behavior label is not a value
rule for D40.

## Multilevel conclusion

1. **Integrity:** the intervention and classifier implementation are exact and repeatable.
2. **Substrate safety:** D40 has a newly exposed symmetric one-worker tail, invalidating D64's
   universal workforce premise before value can pass.
3. **Distribution:** most D40 states are geometrically inside the field support radius, but the
   classifier score distribution is strongly shifted toward no-scale.
4. **Causality:** behavior prediction does not imply action value. Top policies that do not later
   scale are running different complete recipes; forcing D40 to abandon its already-coupled funding
   plan destroys production.
5. **Action abstraction:** permanent scale versus permanent suppression is too coarse. Even its
   hindsight oracle has little headroom.
6. **Learning:** do not open the proposed narrow Monte-Carlo selector here, because the oracle gate
   itself fails. Any future MC action must preserve productive funding and vary timing/specification
   locally rather than cancel capitalization for the rest of the game.

## Decision

Honor the invalid branch: quarantine D64 value and audit only the violated worker-two invariant.
Freeze a small replay-stock-flow diagnostic on the four symmetric failures and same-map successful
controls. If a coefficient-free transaction invariant can repair worker two, validate it on new
maps before reopening any causal workforce experiment. Do not tune the classifier threshold,
exempt the four failures post hoc, reuse these seeds for selection, construct a candidate, or take
any platform action.

## Reproducibility

```text
563a8c4cf4447db50699dfab7cc8789384abb2dc77646a41e7176b8f41a331ad  d64a-field-gated-late-capitalization-protocol-2026-07-21.md
89144ab75a55fba17bbed18975f2f8fa636310a2e4e5ea2650f228ea155e67d0  d64a-field-snapshot-model-2026-07-21.json
114c6eac1520ec574dd0eb23bd9816a291e25a9873d953048ad0c28f55babec7  rust/src/d64a_snapshot_model_generated.rs
382d17da7fc38aa8501696e8ea881c3e64a2770987babf10bc115dbf4ced40d7  rust/src/bin/d64_field_gated_capitalization.rs
ac7cbb034c52fac05e829a80e93a13c6f0d295aeb052f396ae0626d5c74f9b12  cgauto/analyze_d64a_field_gated_capitalization.py
3ef63ac5245ae1fa83ee9290f8c1a6bffeb3e8c4fe37bee3137e184745f78576  each repeated matrix
aa3eed8c08fa0330644a29cb00217648667a2373286dc189d439e7530f140d19  d64a-field-gated-late-capitalization-result.json
```

