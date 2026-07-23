# D48a complete-policy economic-bonus surface — result (2026-07-21)

## Verdict

**Reject the three-scale surface and do not open cross-entropy search.** The implementation is
exact, deterministic, safe, and outcome-sensitive, but only two of six perturbations activate in
the frozen 5%--95% corridor. Banking is completely flat at zero and double scale; doubled
provenance is also an exact no-op; zero renewable scale changes only 3/64 tasks. The surface is too
saturated and one-sided for sample-efficient continuous search.

Do not select `provenance_zero` from its descriptive consumed-map result, prune banking, change the
perturbation amplitudes, or initialize CEM from an observed arm. No fresh map, model, candidate, or
platform gate opens.

## Exactness and activation

- Both 7 x 64 matrices complete in about ten seconds and are byte-identical.
- The `(1,1,1)` anchor matches every D40 prefix terminal field, action count, action hash, and state
  hash exactly.
- All 448 rows have zero mechanical, arithmetic, finite-value, or worker-cap failures.
- Active directions: `provenance_zero` at 60/64 tasks and `renew_double` at 58/64.
- Inactive directions: `provenance_double` 0/64, `renew_zero` 3/64, and both bank directions 0/64.
- Every perturbation preserves worker two, worker three, and crop rates at 100%, 93.75%, and 100%.

The perturbation means span 40.406 points and two of three semantic pairs differ by at least two,
so literal bonus calibration can change whole games. It nevertheless fails both identifiability
gates: banking has no active direction and only two of six total directions activate.

## Interpretation

D40's fixed bonuses define broad priority regimes rather than a smooth local surface. Once a bonus
is large enough, increasing it does nothing; removing it can jump almost every trajectory. A
Gaussian/CEM search over these coordinates would spend most evaluations in plateaus and estimate
unstable boundaries from common-map discontinuities. This closes continuous calibration of the
three literal bonus scales.

The next structural variable is assignment order, not another score weight. D40 allocates free
workers sequentially by ascending unit ID, so the trained chopper is usually last and receives only
targets left after producers reserve theirs. D46 proves it still finds a `FELL_BANK`, but not that
it chooses before competing renewable workers. D35's factorized joint oracle independently shows
that coordinated target allocation has value. D49 should move only the designated maximum-chop
worker to the front of each simultaneously free post-funding batch while preserving exact D40
actions, targets, reservations, and relative order for every other worker. Begin with activation
before fresh value evidence.

## Evidence

- protocol SHA-256:
  `4f3691dbc83cd9c0791719791de6518bb884034fabc59bc67fe151ff0a57580e`;
- policy catalog SHA-256:
  `8d6f1aaff77a3a4fb2c7bd5d71307a19895b05f2fab1d0166241200d2e8fe2d6`;
- duplicate matrix SHA-256:
  `48f0c619754aa83f519e6c654c6dfa82b9eca7c444a521e305c5849a2279abc6`;
- result JSON SHA-256:
  `a5ed881840f81bf84f948a7f8997898ac7f7d32960fab9ed1fad530bd51c7861`;
- runner SHA-256:
  `776fb39aaf7b57f1b1a826af7dd19235464007383e2f99716b6f26055d6c4343`;
- analyzer SHA-256:
  `3ce3b3e00208709705d0fbba0c8a03b4849124e33daab41388db655704595e5d`;
- focused verification: two Rust runner tests and three catalog/analyzer tests pass.
