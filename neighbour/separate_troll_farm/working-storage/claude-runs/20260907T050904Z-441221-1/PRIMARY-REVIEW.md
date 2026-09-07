# Primary review — 2026-09-07

Exact candidate f07c76f19d3f4ff83d04b75532892ea1aca134e8cf4dd031a4f77fcd65c52c2a
is not a finalist. Independent actualRust1.90 compile/test:34 pass,0 fail.
Parsed192 unique map/seat/opponent pairs, all192 baseline command arrays match
gap20260906T210944Z-3184968-1. Baseline167/6/19=170, candidate146/1/45=146.5;
issues1 vs0. Compact independently counted81598UTF16. Production hashes unchanged.

Mean own-score231.34896 vs160.88021. Wood42.44792 vs36.51042 accounts for23.75
of the70.46875-point loss. Fruit-score61.55729 vs14.83854 accounts for46.71875.
This decomposition, not raw command counts, establishes the larger fruit deficit.
The reported311 vs11239 harvest counts are ring metrics, not all-map totals.

Timber implementation supports real legal hp0/cc1 cycles in fixtures and activates
in the full192 panel. However, the report's "known-map ablation" is NOT an actual
known development map: test opening(false) manually constructs an11x11 open board,
six trees, artificial stocks and no ore, with a passive opponent. +15 is synthetic
fixture evidence only. No seed-map generator/archive is invoked. Required real-map
mechanism ablation remains missing. Do not repeat this labeling or remove that limit.

Source jobs_for still prices only immediately present fruit and one harvest/drop
trip. CHOP values delivered wood without pricing lost future harvests. Existing
grove ownership prevents premature timber felling but does not preserve profitable
natural fruit assets. All six hire specs have hp<=1; four have hp0. These are testable
causal hypotheses, not established explanations of every loss. Next batch should
reproduce a fruit-production loss in an unmodified known-map adaptive trajectory,
then implement recurring fruit service/retention and workforce valuation together.

16-stream JSON reports4312turns,0differences,original maximum0.935ms. Inspected
corrected tool now rejects blank/EOF/exit/stderr. Its selector only bounds waiting
for first byte; readline can still block on a partial line, and stderr.read precedes
wait timeout. This is not fully bounded protocol certification. No need for another
audit-only batch: use existing robust runner when a finalist is certified.
