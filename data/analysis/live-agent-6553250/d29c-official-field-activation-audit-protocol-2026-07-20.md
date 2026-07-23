# D29c official-field activation audit — frozen protocol (2026-07-20)

## Question and boundary

Does the frozen D29b selector produce a plausible, non-collapsed decision distribution when its
exact live parser and feature history are applied to actual current-resident Arena trajectories?

This is a read-only transfer-sanity audit.  It does not estimate the unobserved `ownership2`
counterfactual, tune the model, authorize submission, start games, or change the resident.

## Frozen identities and sample

- Resident agent `6561795`, submission `41015603`.
- Candidate source SHA-256
  `f074a553804a638d32cf97fe6e2e3cd2c718c4205ad79d6dfb2d6c7dde21c528`.
- Frozen critic payload SHA-256
  `acf192cf6b2225de01b12e0507120866f20c7b2e8296a026aa85dfae288be87f`.
- Strict activation threshold `raw > +4.0` and two-own-worker support guard.
- Use exactly the first 80 audited game IDs in
  `d29b-pretransfer-resident-checkpoint-2026-07-20.json`.

Fetch only those finished game results.  Decode logical states from official replay diffs and
recorded command context.  Serialize turns 1 through 75 through the same static-map/turn protocol
used by the compiled one-file candidate, normalized to the resident's seat.  Run an independent
Rust diagnostic containing the exact live history, feature, and frozen critic code.

## Readiness and transfer-sanity gates

The audit passes only if:

1. all 80 requested games belong to the expected resident and fetch without error;
2. at least 60 games reach the turn-75 decision boundary;
3. every included replay has zero unknown diff updates and a complete 1/25/50/75 history;
4. every prediction is finite and every turn-75 root has exactly two own workers;
5. both decisions occur at least ten times; and
6. activation rate is between 17% and 67%, a fixed +/-25 percentage-point transfer corridor around
   D29b's fresh generated-field activation rate of 42.135%.

No outcome subgroup can override a failed readiness or activation gate.  A pass only preserves
eligibility for the already-frozen controlled transfer.  A failure closes the transfer until a new
representation hypothesis is preregistered.

## Diagnostic analysis

Report raw/normalized prediction quantiles, activation by seat and opponent, actual resident
win/loss/catastrophe composition, and prediction distance from the `+4` boundary.  These are
descriptive because the farm branch was not played.  In particular, correlation between a switch
and the observed resident outcome is not evidence of option value.

The model, threshold, worker guard, source, transfer thresholds, and sample cannot be changed after
reading these 80 games.
