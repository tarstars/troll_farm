# D159a current-resident all-finished effect refresh — result

Date: 2026-07-23  
Verdict: **the midgame anti-compounding signature independently replicates; collect a small
field-native bounded-response A/B bank before training another controller or selector.**

## Outcome

The authorized read-only pull returned 200/200 finished games. Every row belongs to exact resident
agent `6561795`; all 80 exact D23 control IDs are present once, leaving 120 non-D23 games in the
independent suffix. There are zero fetch failures, duplicate IDs, identity mismatches, or unknown
replay-diff updates. The source remains submission `41015603`, 62,725 bytes, SHA-256
`a8eb3b2b...b884e55`.

The platform snapshot was rank **40**, score **22.26**. This is an observational ladder read, not a
policy effect: the resident did not change.

The frozen suffix gate passes all four conditions:

| Frozen condition | Suffix result | Gate |
|---|---:|:---:|
| Catastrophic losses (`margin <= -100`) | 13/120 = **10.83%** | pass |
| Share of negative-margin mass | **57.84%** | pass |
| Distinct catastrophic opponents | **12** | pass |
| Catastrophic opponent final-wood gap | **+48.64** | pass |

No game was created, no reserved map was touched, no candidate was built, and no submission or
resident mutation occurred.

## Cohort result

| Cohort | W-T-L | Mean margin | Median | Bootstrap 95% CI | Catastrophes | Tail mass |
|---|---:|---:|---:|---:|---:|---:|
| Exact D23 IDs | 42-0-38 | +2.64 | +4.5 | [-19.40,+22.15] | 7/80 | 61.12% |
| Independent suffix | 55-1-64 | +1.02 | -1.5 | [-14.47,+16.45] | 13/120 | 57.84% |
| All exact resident | 97-1-102 | +1.67 | -1.0 | [-10.62,+13.47] | 20/200 | 59.15% |

The wide intervals warn against treating replay mixture margin as a precise ladder estimate. The
mechanism is much more stable than the mean: the historical and suffix cohorts both put roughly
three fifths of total downside in a small catastrophic tail.

One game has a known penalty-style mismatch between official score and inventory reconstruction.
Both values and all effect telemetry are present. The frozen protocol requires presence, not exact
inventory reconstruction, so the mismatch is retained as a diagnostic and does not alter the
integrity decision.

## Analysis at different abstraction levels

### Temporal dynamics

The resident usually earns a real opening lead and then loses it. In the suffix, **52/64 terminal
losses (81.25%)** have a positive resident score margin at turn 100; those reversals span 24
opponents. Ordinary losses average +23.94 at turn 100, remain +24.14 at turn 150, cross to -5.15 by
turn 225, and reach -42.17 at turn 300. Catastrophes average +23.62 at turn 100 and +7.62 at turn
150, then collapse to -45.46 at turn 200 and -75.00 at turn 225. The causal boundary is midgame,
not the first move.

### Economy and workforce

The resident finishes with exactly two workers in all 120 suffix games. Among losses, 37/64
opponents finish with at least three workers; opponent workforce is +0.75 higher in losses than
wins. This confirms a scale gap but does not prove that an isolated third-worker command is good.
Earlier forced-worker experiments failed because funding, renewable supply, job allocation, and
termination were not changed coherently.

### Interaction and renewable production

Suffix wins contact 53.3% of opponent crops; losses contact only 33.2%, a **-20.15 percentage-point**
gap. Catastrophic opponents collect 73.31 wood from their planted crops, **+51.12** versus
non-catastrophic games, and create about **19.78** more crops. Yet our score in catastrophes is
216—higher than our suffix average 187.93—while opponent score explodes to 375.46. The tail is
primarily failure to contain an opponent production loop, not simple collapse of our own economy.

### Statistical and causal interpretation

The signature repeats outside D23 across twelve catastrophic opponents, so it is not one player
name or one small batch. Replay association still cannot choose an intervention: strong workforce,
planting, and wood are mutually reinforcing consequences. The next experiment must create paired
causal variation while retaining the exact resident before and after a finite intervention.

### Project-history interpretation

- D32 already rejects permanent turn-75 farming on official common maps.
- D36 shows short resident overlays have positive hindsight value but insufficient scale and no
  TRAIN action.
- D29/D30 show generated-map selectors shift badly on official terrain.
- Direct worker patches, crop-only retunes, first-move search, and resident MOVE Monte Carlo are
  closed.
- D158 proves that a controller evaluated over D40 fallback is not evidence of improvement over
  the live resident.

Therefore the replicated mechanism does not authorize repeating any of those implementations.

## Attack-angle matrix

Each axis is scored 1 (weak) to 5 (strong): suffix replication (`R`), resident-relative upside
(`U`), resident-preserving testability (`T`), field fidelity (`F`), implementation tractability
(`I`), and tail safety (`S`). Ranking is the frozen unweighted total, then `R`, then `T`.

| Rank | Attack angle | R/U/T/F/I/S | Total | Adjudication |
|---:|---|---:|---:|---|
| 1 | Field-native bounded midgame probe bank | 5/4/5/5/3/5 | **27** | Open D160 design |
| 2 | Resident-anchored integrated scale response | 5/5/4/4/3/4 | **25** | Primary option content |
| 3 | Field-native counterfactual value dataset | 4/4/5/5/2/5 | **25** | Product of successful probes |
| 4 | Resident-fallback recurrent macro controller | 5/5/5/3/2/4 | **24** | Later; rebuild exact fallback first |
| 5 | Tail-triggered safe portfolio | 5/4/5/4/3/2 | **23** | Defer until an option has causal value |
| 6 | Integrated orchard-interception response | 5/4/4/4/3/3 | **23** | Component, never crop-only retune |
| 7 | Opponent-archetype portfolio | 3/3/5/5/3/3 | **22** | Too broad/volatile for name selector |
| 8 | Opening or first-move selector | 1/2/5/4/4/4 | **20** | Closed by midgame timing evidence |
| 9 | Online single-MOVE Monte Carlo | 2/2/5/3/2/4 | **18** | Closed at +0.508 and 92.85 ms p95 |
| 10 | Unanchored end-to-end PPO | 3/5/1/3/2/1 | **15** | Closed without exact-resident anchor |

## Next experiment

Open D160 as a **design-and-small-causal-panel study**, not a submission:

1. retain exact resident behavior except for one finite midgame response;
2. compare a small, semantically distinct bank that jointly controls funding/TRAIN, renewable
   planting, worker roles, interception, and an explicit return-to-resident boundary;
3. use common official TestSession maps and exact A/B identity checks;
4. require positive paired value, own-score protection, tail protection, and consistency across
   opponents before expanding the panel; and
5. use successful paired rows as field-native counterfactual labels. If no response clears the
   small causal gate, close this option vocabulary before any PPO or selector fit.

Platform authorization makes this worthwhile, but D159 itself does not authorize writes. D160
must freeze its panel, source variants, and stopping gates before the first game is created.

## Evidence

- raw replay census SHA-256: `97dc82a...df443`;
- deterministic result JSON SHA-256: `bd3fe457...965ac`;
- analyzer SHA-256: `325f8c95...ae68`;
- parser/protocol lock: `d159a-current-resident-all-finished-effect-refresh-lock.json`;
- focused tests: 9/9 pass.
