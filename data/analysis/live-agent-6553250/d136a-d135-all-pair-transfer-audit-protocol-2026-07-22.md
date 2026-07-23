# D136a D135 all-pair transfer audit — frozen protocol

Date: 2026-07-22  
Status: frozen after D135 veto failure and before fitting any additional full-corpus pair

## Question

D135 changes the selected ranker seed from D134's 13403 to 13404 while also changing the gate.
Its single-pair D126 failure therefore confounds selector error and abstraction error. Refit all
four already-frozen ranker/gate pairs on all four D133 blocks, use the fixed 80% D133 calibration,
and score each on already-consumed D126 without changing any model, seed, target, threshold rule,
or policy gate.

Run the four pairs concurrently in isolated one-thread processes. Record D133 training summaries,
D126 winner/gate structural statistics, unchanged D125 veto gates, and D135 held-block metrics.
Compute four-point Pearson correlations between D135 held mean/worst-block/family-floor and D126
mean. Repeat the complete four-pair matrix and require byte identity.

## Authority

This audit is retrospective and diagnostic only. No pair can qualify, create a checkpoint, open
fresh maps, integrate Rust, submit, mutate the stable resident, or interact with TestSession/Arena.

- If no pair passes all D126 gates, close D135's winner-conditioned BCE gate abstraction and use
  the transfer statistics to choose a materially different temporal/value objective.
- If a nonselected pair passes, diagnose another selector failure, but do not rescue it; design a
  prospective selector repair on D133 evidence only.
