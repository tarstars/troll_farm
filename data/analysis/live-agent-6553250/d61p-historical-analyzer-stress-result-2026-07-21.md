# D61p historical analyzer stress result (2026-07-21)

## Verdict

**Pass.** The D61p open-field analyzer completed every one of the 1,302 consumed historical
official replays without an exception. It is ready to analyze a current snapshot after separately
authorized collection and passed snapshot QA.

This result is infrastructure evidence only. It does not update any field hypothesis, select a
controller, weaken D62's renewable-safety invariant, open confirmation, or authorize platform
activity.

## Exact integrity result

| Measure | Result |
|---|---:|
| Indexed games | 1,302 |
| Raw replay / trajectory pairs missing | 0 |
| Successful game analyses | 1,302 / 1,302 |
| Resolved official turns | 361,755 |
| Player schedulers reconstructed | 2,604 |
| Crop-provenance reconstructions | 1,302 |
| Unknown diff updates | 0 |
| Final-inventory mismatches | 0 |
| Worker/TRAIN or scheduler assertion failures | 0 |
| Pseudo-resident seat 0 / seat 1 | 668 / 634 |

All nine frozen gates passed. The corpus spans one through 300 resolved turns and one through seven
final workers per player, so the pass is not confined to normal 300-turn/two-worker games.

The arbitrary, outcome-blind pseudo-resident side created no crop in 50 historical games. That is
deliberately not classified as a renewable-safety failure: the consumed field corpus has no
counterfactual feasibility label. This independently exercises the semantic distinction made after
the D62 tail audit.

## Parallel execution

The frozen 20-process run measured:

| Measure | Result |
|---|---:|
| Wall time | 11.528 s |
| Parent-plus-child CPU time | 215.594 s |
| Effective CPU cores | 18.703 |
| Throughput | 112.947 games/s |

This resolves the practical capacity concern for the analysis stage: process-based replay decoding
uses almost the full requested 20-core pool. The future network collector remains intentionally
rate-limited; only the offline parse and analysis stages are parallel.

## Reproducibility

Invocation:

```text
.venv/bin/python cgauto/audit_d61p_analyzer_historical.py \
  --output data/analysis/live-agent-6553250/d61p-historical-analyzer-stress-2026-07-21.json \
  --jobs 20
```

Frozen hashes:

```text
7d6e7d6d496ce2348934a84485fe7b697dbf77c18c9876bca62622104a7bd8ed  d61p-historical-analyzer-stress-protocol-2026-07-21.md
52ee717537d3954b2aedef467b7ffc96338545e39ad4cdd1a6d5085e2cbb067c  cgauto/audit_d61p_analyzer_historical.py
e9ed056c7d5ba1595bc52a563a917d785807219788c8473901d3ee8e242b71df  cgauto/analyze_d61p_field_snapshot.py
84b4c08f370f35fab8b0023bcf2aeb21c91c837bc5207fa56cf0a964111e8a37  data/processed/games.jsonl
1dbf5b7a4199eadc9e1029d3d73c4f185fa56fd6ac4a764afe42cc98d2b0060e  sorted game-ID stream
8a26fee88d5335222106380f2525ad2f76ae6e22a4091a91b85a48874f80a01d  d61p-historical-analyzer-stress-2026-07-21.json
```

## Next action

The infrastructure chain is now exhausted as a source of uncertainty. The next discriminating
evidence is the already frozen passive current-field snapshot: resident agent 6561795, current
top-20 Legend sources, exact QA/splitting, then this open-only analysis. Collection still requires
explicit user authorization. TestSession, Arena, submission, and confirmation remain separately
sealed.

