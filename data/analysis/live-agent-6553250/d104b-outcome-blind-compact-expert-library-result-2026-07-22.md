# D104b outcome-blind compact expert library — result

Date: 2026-07-22  
Decision: **fail; close coverage-only subset compression**

## Outcome

The frozen proposal-only greedy procedure selected seven of the 64 D98 experts before any terminal
outcome was loaded:

`four_11, four_12, four_50, four_40, four_21, four_48, four_53`.

Their exact decimal coefficient payload is 12,303 bytes. The subset passes every prospective
selection gate: it exposes 6.642 unique noncontrol proposals per D97 root on average, never fewer
than five, supplies a joint proposal at every root, and spans all jobs, all observed provenance
classes, both seats, all opponent families, and reversed role order. Selection reruns identically,
the lock predates value access, and every integrity check passes.

## Value audit

After the subset lock, its deduplicated proposal union gains `+25.348` mean margin over D40. It adds
`+15.773` own score, removes `9.574` opponent score, improves 203/240 rooted tasks, preserves 100%
crop creation and D40's 91.41% worker-three rate, and gains at least `+15.156` against every
opponent family. Joint proposals are selected at 189 roots and strictly beat the complete
best-single oracle at 81.

The result nevertheless fails three frozen gates:

- it retains 79.561% of D104a's union gain versus the required 80%;
- it is `-3.063` behind the complete best-single oracle rather than at least `+2` ahead; and
- the selected value-maximizing rows do not contain reversed worker-role order.

The decisive miss is not coverage or basic value. Hard subset pruning removes complementary joint
proposals: D104a's complete bank was `+3.883` beyond best-single, while the compact union is
`-3.063`. No longer, alternate, or outcome-favorable subset is evaluated after this result.

## Next implication

Close coverage-only expert deletion. Preserve the full 64-expert proposal basis and compress its
representation instead. Per-expert positive scaling does not affect within-expert argmax, so a
prospective low-bit integer quantization audit can reduce 9,792 coefficients from 39,168 raw f32
bytes to roughly 4.9--9.8 kB without deliberately discarding any expert. Quantization fidelity
must be locked without terminal outcomes before causal value is inspected.

This result does not authorize a learner, candidate, platform action, submission, or resident
change.
