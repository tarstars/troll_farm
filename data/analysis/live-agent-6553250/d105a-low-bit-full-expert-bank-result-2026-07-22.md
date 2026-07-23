# D105a low-bit full-expert bank — result

Date: 2026-07-22  
Decision: **pass; freeze four-bit proposal bank and open D105b fresh-map controller preflight**

## Outcome-blind selection

Four-bit symmetric per-expert quantization passes every frozen fidelity gate, so the selector locks
it immediately and does not inspect six- or eight-bit proposal fidelity. The immutable lock was
written before D97 terminal arms, baselines, or the D104a value report were opened.

The four-bit bank exactly reproduces 13,489/15,360 = 87.82% of full-precision expert/root proposal
identities. Per-root recall of the exact noncontrol union averages 90.62%, never falls below 69.23%,
and has 78.83% mean Jaccard similarity. All 15,360 proposals are valid paired D97 arms.

Quantization does not collapse support. It exposes 17.596 unique noncontrol proposals per root on
average, versus 16.642 at full precision, never fewer than eight, with a joint proposal at every
root. Forty-eight experts remain active in at least 25% of roots, and the union retains all jobs,
provenance classes, seats, opponent families, and reversed role order.

The 9,792 signed coefficients require 4,896 packed bytes or 6,120 conservative base85 bytes. The
plain audit TSV is 26,119 bytes; that text is not the intended submission representation. One- and
twenty-worker selected proposal matrices are byte-identical. The selected run takes 23.86 seconds
with one worker and 2.54 seconds with twenty workers, about 9.4x faster on this workload.

## Frozen value audit

After the lock, the quantized proposal union gains `+32.445` mean margin over D40 and captures
88.04% of D97's complete joint-catalog oracle. It adds `+21.410` own score, removes `11.035`
opponent score, and strictly improves 225/240 rooted tasks. All opponent families gain at least
`+18.875`; crop creation remains 100% and worker-three reach remains exactly 91.41%.

Joint proposals are selected at 155/240 roots and strictly beat the complete best-single oracle at
112. Their mean incremental margin over best-single is `+4.508`, exceeding full precision's
`+3.883`. Every integrity and value gate passes.

The quantized union's `+0.586` advantage over full precision is not evidence that rounding is a
better policy. Both figures are hindsight unions on the same consumed panel, and quantization
changes some available arms. The warranted conclusion is narrower and stronger: four-bit packing
preserves the full bank's proposal breadth and coordination headroom under the size budget.

## Next implication

Freeze the four-bit bank and D104 proposal ABI. D105b must now test a small recurrent authority
controller on fresh maps without terminal fitting: can current and short-history field signals
select among deduplicated quantized proposals, preserve D40 control when uncertain, and generate
broad, mechanically safe interventions? PPO or another optimizer opens only after that interface
shows prospective activity and learnable held signal.

No candidate, platform action, submission, or resident change was made.
