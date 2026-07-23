# Three-worker macro controller — deployability and field result, 2026-07-19

## Verdict

**Reject universal direct transfer of the exact `NorxondorThreeWorkerSilver` controller.  Stage 1
passes completely, but Stage 2A fails three of four frozen gates.  Do not run Stage 2B and do not
submit this source to the arena.**

This is a strategy-transfer failure, not an implementation, size, runtime, compiler, or platform
failure.  The exact 62,725-byte resident remains unchanged as agent `6560353`.

## Standalone qualification

The behavior-preserving standalone source is only 21,798 bytes, SHA-256
`69237902e54232cdf31ef8e8bc0e6c25066a4c152bde36479ffb8e1ee92f8377`.

- Rust 2021 standalone compilation: pass;
- source and sidecar hash: pass;
- ten 300-turn protocol streams: byte-identical stdout and zero stderr;
- seeds 0--29, both seats, eight local models: 480/480 complete matches and 131,347/131,347
  command vectors identical to the research strategy;
- all 480 local matches ended with exactly three workers;
- weighted mean decision time 0.227 ms, maximum per-match p95 0.926 ms, and absolute maximum
  15.213 ms, versus frozen 5/50 ms limits.

Code size is therefore not the plateau.  The previous 100k concern disappears for this compact
architecture, and the earlier 209--279 ms Monte Carlo runtime cannot be attributed to protocol or
controller overhead.

## Frozen Stage 2A result

All ten `TestSession/play` games compiled and completed.  Source hashes were exact and replay
enrichment found no diagnostic output.  TestSession maps are unpaired, so per-opponent row
differences are descriptive; the predeclared aggregate gates still decide the experiment.

| Measure | Resident control | Three-worker candidate | Delta / gate | Pass |
|---|---:|---:|---:|:---:|
| Mean own score | 245.4 | 150.0 | -95.4, required >=0 | no |
| Mean opponent score | 342.4 | 277.2 | -65.2 | descriptive |
| Mean margin | -97.0 | -127.2 | -30.2, required >=-10 | no |
| Mean wood | 56.0 | 29.0 | -27.0 | descriptive |
| Mean fruit | 21.4 | 34.0 | +12.6 | descriptive |
| Wins | 1/5 | 0/5 | -1 | descriptive |
| Reached worker three | 0/5 | 3/5 | required >=4/5 | no |
| Valid games | 5/5 | 5/5 | required 10/10 total | yes |

The unpaired bootstrap 95% interval is [-189.0, +1.2] for own-score delta and [-157.2, +94.0]
for margin delta.  Those wide intervals do not change the frozen rejection.

## Per-opponent mechanism rows

| Opponent | Candidate score | Opponent score | Margin | Workers | Successful candidate TRAIN turns |
|---|---:|---:|---:|---:|---|
| delineate | 224 | 469 | -245 | 3 | 4, 77 |
| wala | 233 | 498 | -265 | 3 | 1, 98 |
| norxondor | 194 | 240 | -46 | 3 | 20, 84 |
| Escdemon | 44 | 91 | -47 | 2 | 20 |
| laconic | 55 | 88 | -33 | 2 | 1 |

The branch has two distinct failures:

1. **Funding deadlock.** Against Escdemon and laconic, both workers remain in exclusive deficit
   funding for the rest of the game.  Terminal inventories remain short of the fixed third-worker
   floor (especially LEMON), own wood is only 4/8, and scores collapse to 44/55.  The candidate
   emits no invalid TRAIN; it simply never becomes affordable.
2. **Late scale without field control.** In the other three games worker three arrives only at
   turns 77--98 (median 84).  Own output recovers to 194--233, but delineate and wala reach 469/498.
   The exact Silver continuation does not reproduce the renewable-production or suppression
   relationship that made its synthetic terminal teacher valuable.

At a higher abstraction, all 480 generated-map/local-model matches reached worker three while
only 3/5 exact field games did.  That is direct evidence that local qualification confounds map
distribution and opponent interaction.  It also independently confirms the earlier proxy audits:
the old continuation zoo is not a credible Legend transfer judge.

## Next experiment

Freeze and run an **exact-field-map model-gap decomposition** before designing another controller.
Reconstruct the five candidate TestSession initial maps, run the exact resident and exact
three-worker policy against all eight frozen local opponents on each map, and compare local
workforce/score ranges with the observed field outcome.

- If local models also miss worker three on the Escdemon/laconic maps, official map/resource
  distribution is the first repair target.
- If local models nearly always fund worker three there, opponent interaction/model coverage is
  the dominant failure and generated-map optimization must stop serving as a transfer gate.
- If actual own score lies outside the local eight-model range broadly, the next representation
  must be evaluated on exact official-map/replay-derived scenarios before any policy search.

No threshold or talent cap is tuned from these five games.  The field rows are diagnosis data and
may never become an acceptance holdout.

## Evidence

- `norxondor-three-worker-controlled-field-protocol-2026-07-19.md`;
- `norxondor-three-worker-standalone-qualification-2026-07-19.json`;
- `norxondor-three-worker-parity-0-29.tsv`;
- `norxondor-three-worker-stage2a-result-2026-07-19.json`;
- `data/panels/norxondor-three-worker-stage2a-top5-20260719.json`;
- exact candidate and SHA sidecar in `cgauto/submissions/`.

