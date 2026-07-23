# D41b exact-prior residual actor — frozen preflight protocol (2026-07-21)

## Question and authorization

D41a proves that the 44-feature observation is sufficient but its independent tiny MLP cannot
reproduce D40's branchwise tuple ordering. D41b asks whether an exact deterministic prior can
preserve the complete D40 policy closed-loop and provide a compact zero-residual initialization for
later outcome learning.

This protocol authorizes the exact-prior/rank implementation, a zero-initialized residual actor,
development evaluation, an exact repeat, source/parameter measurement, tests, and written analysis.
It does **not** authorize nonzero residual training, PPO, confirmation maps, candidate construction,
TestSession, submission, or Arena.

## Frozen actor

For every legal candidate, reconstruct D40's exact branch-dependent ordering from the already
exported action ID and 44 features. Preserve Rust's tuple semantics, including `(x, y)` rather than
row-major spatial ordering and `None < Some` for optional cells. Assign rank zero to the selected
candidate and increasing integer ranks to the remaining candidates. In the deficit branch,
positive-reduction candidates use the frozen D40 tuple and all nonpositive candidates follow in
ascending stable action-ID order. In evacuation, non-idle candidates use the frozen tuple and idle
follows. TRAIN's selected goal ranks first and the two alternatives follow by plane/action ID. The
rate branch uses its frozen tuple for the entire candidate set. Stable action ID is the final total
order tie break in every branch; it cannot alter D40's selected action because action IDs are unique.

The future actor interface is

`logit(candidate) = -temperature * prior_rank(candidate) + residual(candidate)`.

For this preflight, residuals are identically zero and evaluation uses masked argmax, so temperature
is any positive finite constant and cannot affect the selected action. Reserve the residual model
shape `44 -> 16 -> 1` with ReLU, 737 parameters. Initialize its final layer to zero; earlier-layer
initialization is irrelevant to this deterministic preflight. PPO temperature, optimizer, entropy,
critic, reward, and schedule remain deliberately unspecified until D41b passes.

## Data and comparisons

- D41a validation maps 9,710,000--9,710,031 are consumed diagnostic data and may be used only for
  the already-recorded 85,047-decision sufficiency result.
- Evaluate closed-loop on development maps **9,711,000--9,711,031**, both seats and the same eight
  opponents: 512 episodes.
- Compare against the D40 TSV frozen before D41a training, including score, workforce, crops,
  integrity counters, action hash, and state hash for every task.
- Repeat the exact-prior run independently on the same development grid.
- Confirmation maps 9,720,000--9,720,031 remain sealed.

## Gates

D41b passes only if all hold:

1. exact-prior selection equals the independent Rust D40 label on every development decision and
   in every branch;
2. all 512 terminal rows match the frozen D40 baseline on action/state hashes, scores, workforce,
   crop creation, and integrity counters;
3. the independent repeat has identical decision counts, per-branch counts, action hashes, state
   hashes, and terminal metrics;
4. invalid direct commands, provenance failures, relevant deposit-prediction failures, decision
   loops, candidate overflows, and worker-cap errors are zero;
5. zero-residual argmax equals exact-prior argmax for every visited decision;
6. residual actor size is exactly 737 parameters, at most 2,948 float32 bytes or 737 int8 bytes; and
7. the standalone exact-prior plus residual-inference kernel is projected at no more than 10,000
   source bytes, leaving deployment headroom under the 100k submission limit.

A pass opens one separately preregistered residual-PPO development experiment. A failure closes
this anchor and requires either missing-order repair or direct D40 deployment analysis. No threshold
or ordering change is allowed after development execution begins.

## Compute and preservation

Run locally: this is a deterministic CPU comparison over roughly 85k decisions per replica. YT
startup is not economical. Preserve the protocol, implementation, tests, both run summaries,
terminal comparison, hashes, elapsed time, and final verdict.
