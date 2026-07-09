# Ownership corpus — collection log

## Batch 1 (2026-07-09) — baseline, PARTIAL (collector died on API overload), salvaged by controller

**Probe:** `data/analysis/map-value-ownership/baseline-probe.min.rs` (66,993 B) — current
champion-line tree (splitclaims + ownership telemetry), DEBUG=true, emits `@TFOWN`. Built by the
collector before it died. Behaviorally = our live baseline (diagnostic verified EQUAL:32).

**What landed:** the collector (agent ad5cc124) built the probe and collected games vs plcc
(6480966) and mikdiet (6480914), got only 2 vs kurigen (6480824), then died on an Anthropic
API "Overloaded" error before aggregating/committing. Controller salvaged the aggregation
locally (no API): filtered to clean baseline games (`@TFOWN` present, `@TFPRESS` absent — this
excludes both old non-ownership probes AND the gate's in-flight pressurefarm games), joined
win/loss from the `.log` files, wrote `corpus/baseline_corpus.csv`.

**Corpus so far: 36 labeled baseline games (8W / 28L).**
- plcc: 3W/14L · mikdiet: 5W/12L · kurigen: 0W/2L (thin — resume needed)
- Far from the 20W+20L/class target; wins are the bottleneck (we lose most games vs these
  19-20-tier opponents, so ~60-80 games/class needed to bank 20 wins).

## ★ First-look finding — the exposed-value→loss signal is WEAK/ABSENT in aggregate

Mean exposed value, wins vs losses (t150):
- `own_half_exposed`: **WIN 67.6 vs LOSS 55.6** — REVERSED (wins have MORE, not less)
- `created_exposed`: WIN 6.5 vs LOSS 5.6 — reversed
- `created_exposed` @t225: WIN 3.0 vs LOSS 4.1 — weakly in-hypothesis, tiny

The ownership hypothesis (high exposed value → we donate it → we lose) does NOT hold in the
aggregate here; at t150 it's reversed. **Likely confound:** exposed-value counts positively
correlate with *having a big active farm/operation*, which correlates with *winning* — so the
metric conflates "we have lots of value in play" with "value at risk," masking any donation
effect. This matches the diagnostic's own caveat ("own_half_exposed high even in the one win;
the model is not a standalone win predictor") — now confirmed with 8 wins, not 1.

**Implication for the goal (prove/kill ownership-aware play):** this is a CAUTION flag, not a
kill. It says (a) the signal pressurefarm keys on is confounded with farm-size, so the clamp
risks firing in *winning* big-farm states — exactly the efficacy risk the code reviewer
flagged; (b) don't expect the aggregate AUROC to separate cleanly. The DECISIVE test remains
pressurefarm's behavior (gate + arena), not this correlation. But if the gate shows the clamp
suppressing farm in winning states AND the arena is neutral/negative, this corpus is the
mechanism why → kill.

## Resume plan (when API stable; budget permitting, after the pressurefarm gate)
- Finish kurigen; push all three toward 20W+20L (wins are the bottleneck).
- Then AUROC by phase (loss=1, win=0) over own_half_exposed / created_exposed / opp_share /
  not_ours_share / composite — expected weak per the above; that itself is a finding.
- Add the pressurefarm candidate corpus (its gate games carry `@TFOWN`+`@TFPRESS`) for a
  baseline-vs-governor metric-shift comparison.
