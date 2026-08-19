# σ for PAIRED arena nights — re-measure note (2026-08-19, integrator)

**Why this exists:** the cure-C night's honesty clause flagged it — the
measured round-to-round spread of the PAIRED differences (0.976) came in far
below the planning value (2.123 = 1.501·√2 built from unpaired per-read σ).
Pairing adjacent windows cancels ladder drift better than the plan assumed.
The M-1 rule said "gross disagreement = re-measure σ, never a license to pick
the flattering number" — this is that re-measure, as a proposal for the OWNER.

## The measurement, with its honest uncertainty

- Data: the five paired differences of the cure-C night (+1.3, +0.2, +0.4,
  +0.6, +2.6), subject pair cure-C vs `98628e98…`.
- Empirical pair SD = **0.976** — but with only 4 degrees of freedom its own
  95% confidence interval is **[0.59, 2.81]**: five pairs genuinely cannot pin
  the noise level. The truth could still be close to the old planning value.
- Caveat carried from the night: pair 5 (+2.6) overlapped a visible ladder
  event (league grew 162→172); with pair 5 excluded the remaining four pairs
  have SD ≈ 0.48 — even less certain (df=3) but pointing the same direction.

## What the winner bar would look like (context, not a decision)

| assumed pair σ | bar at n=5 pairs | bar at n=10 pairs |
|---|---:|---:|
| 0.976 (tonight's point estimate) | 0.86 | 0.61 |
| **1.5 (proposed provisional)** | **1.32** | **0.93** |
| 2.123 (current planning value) | 1.86 | 1.32 |

## Proposal to the owner (M-1 amendment, needs your ruling)

1. **Adopt a provisional paired-design σ_pair = 1.5** — deliberately ABOVE the
   point estimate (0.976) because five pairs can't be trusted to set it, and
   comfortably inside the estimate's CI; it keeps the materiality floor (1.0)
   binding as the value bar.
2. **Pool forward:** every future paired night's differences join a running
   pooled estimate (this note is the ledger for it); at pooled df ≥ 9 the
   provisional 1.5 is replaced by the pooled value, whatever it says.
3. Unpaired σ = 1.501 per read stays untouched for single-arm reads.

Practical meaning if adopted: a night like yesterday's (+1.02 mean) would sit
just under a 1.32 winner bar at n=5 — still the owner's judgment call — and a
one-block extension (n=10, bar 0.93) would have been DECISIVE rather than
still-ambiguous. Faster verdicts, same honesty.

- Status: PROPOSAL — no rule changes until the owner rules. Filed as an
  owner-queue item; the numbers above are reproducible from the night ledger
  (`local_claude_1/cure-c-night-2026-08-18.md`).
