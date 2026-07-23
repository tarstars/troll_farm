# D149b state-conditioned joint ranker cross-fit — frozen protocol

Date: 2026-07-23  
Status: frozen after D149a's exact-repeat closure, before any D149b fit

## Hypothesis

D149a's proposal ranker sees only 379 action-delta features. Rust inspection confirms that these
contain proposal semantics plus interactions with turn, decision ordinal, crop count, candidate
counts, and worker ordinal, but not the separate 64-state vector. That state contains 56 global
economy features plus normalized turn, boundary count, crop count, remaining intervention budget,
and previous intervention kind. The second proposal is explicitly conditional on the first-created
state, yet D149a's ranker cannot use that information.

Change only the ranker input. Concatenate the same 64 state features to each legal proposal and use
`443 -> 16 -> 1`. Retain the 16-dimensional winning embedding and unchanged `84 -> 8 -> 1` gate.
Total size becomes exactly 7,810 parameters, an increase of 1,024 weights. No stage-specific head,
extra width, threshold calibration, alternate labels, or extra evidence is allowed.

## Frozen execution and gates

Reuse D149a exactly:

- the same 909 targets, 1,654 on-policy groups, eight map folds, and off-policy exclusions;
- seed pairs `(14901,14951)` through `(14904,14954)`;
- 60/80 epochs, batch 128, Adam `1e-3`, weight decay `1e-4`;
- fixed zero gate threshold, equal act/wait mass, and inverse task-group weighting;
- eight leave-one-fold-out fits per pair with ten forked workers and two threads each;
- byte-identical full selection repeat; and
- every D149a rank, gate, fold, joint-decision, and inactive-prefix acceptance threshold unchanged.

Use D149a's unchanged selection order. An eligible exact repeat permits two deterministic all-fold
fits; require identical canonical hashes, exactly 7,810 finite parameters, then save one checkpoint.

## Decision boundary

Passing opens separately frozen prospective evaluation on untouched maps
`9,844,200--9,844,215`. Failure closes exact-best-pair one-hot imitation on this corpus: do not try
another width or stage split. The next hypothesis must change target information, most plausibly by
using D148 population returns to create value/near-tie labels or by collecting broader joint
counterfactual features.

D149b cannot read or generate reserved maps, integrate Rust, qualify or submit a candidate, change
the resident, or interact with Arena.
