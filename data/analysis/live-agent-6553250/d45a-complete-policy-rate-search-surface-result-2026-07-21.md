# D45a complete-policy rate-search surface — result (2026-07-21)

## Verdict

**Reject the frozen 32-parameter surface and do not open cross-entropy search.** The implementation
is exact, deterministic, safe, and strongly outcome-sensitive, but only **10 of 16** perturbations
fall inside the required 5%--95% task-activation band versus 12 required. The conjunction fails on
that sole gate.

This is not a rejection of whole-game policy search as an abstraction. It says the frozen vector
contains saturated/dead directions and one overly broad direction, so optimizing all 32 coordinates
would waste samples and permit non-identifiable parameters. Per protocol, do not reduce the vector
post hoc, alter amplitudes, or choose one of the descriptively strong arms. No model, candidate, or
platform gate opens.

## Integrity and exact anchor

- Both 17 × 64 matrices complete and are byte-identical, each with SHA-256
  `ef52c454979a786dceed064de8bc0ae3a499030a987d301a05a5fe567f39502a`.
- The zero vector matches the 64-row D40 prefix in every terminal field, action-plane count,
  action hash, and state hash: zero parity failures.
- All 1,088 rows have zero illegal commands, provenance failures, prediction failures, worker
  overflow, or decision loops.
- Every perturbation retains worker two in 100%, worker three in 93.75%, and crops in at least
  98.44% of tasks. The fixed D40 funding/workforce mechanics are therefore preserved.

## Surface result

The zero policy averages +23.188 margin on this consumed four-map slice. Perturbation means span
**-21.078 to +59.438**, an 80.516-point range; six lie above zero and seven below it. Six of eight
plus/minus pairs differ by at least two margin points, so the surface changes complete outcomes,
not only action hashes.

Activation fails because:

- both `bank` directions and positive opponent-owner bias reproduce zero exactly;
- `mine_minus` changes 1/64 tasks and `mine_plus` changes 3/64, below 5%; and
- `workers_fell_minus` changes 62/64 tasks (96.875%), above the 95% ceiling.

The ten qualifying active directions include both fell signs, both harvest signs, negative
opponent ownership, both renew signs, both turn×renew signs, and positive workers×fell.

## Mechanism observations

These consumed-map outcomes cannot select a vector, but they do identify the structural control
surface. Job-kind and workforce/phase interactions materially change both own production and
opponent suppression while the workforce ladder remains fixed. Bank and mine coordinates are
largely irrelevant in the tested generic linear form; opponent ownership is already saturated in
D40's lexicographic prior.

The strongest directional differences are workers×fell (80.516), fell (59.063), renew (43.078),
and turn×renew (8.609). This is consistent with independent top-bot archaeology and D40's own
worker specifications: the third trained unit is a `(2,2,0,2)` chopper, yet D40 sends every worker
through one generic rate ordering after funding completes.

## Next hypothesis

Do not salvage D45 by searching a post-result subset. Replace the linear surface with one
coefficient-free structural hypothesis defined independently by role semantics: after the third
worker is trained, the maximum-chop worker persistently takes the best legal `FELL_BANK` job under
the existing D40 provenance order, falling back exactly to D40 when no fell job exists. Other
workers and all TRAIN/deficit/evacuation decisions remain unchanged.

This D46 role policy should be frozen once, run prospectively against exact D40 on fresh official
maps, and require margin, opponent breadth, workforce, crop, and tail gates. It is a state-machine
role allocation, not a selected D45 coefficient.

## Evidence

- protocol SHA-256:
  `185d99a54b9d9283c43301f7ca104b3367d80addcf8ea2671b07c3a7fc8660ab`;
- parameter catalog SHA-256:
  `be42c39ba3cb16ba9c9538b84611272172efc6f8e737947506e65b7ccf93409e`;
- result JSON SHA-256:
  `856490a309df74cedbde091dfa0c6b509f1f88eb28e01970f899462b9d8b6b63`;
- evaluator SHA-256:
  `d8686e96926deeb205df8f40014ce54ced81a126ca18fcc040a4c1c3097ff5de`;
- analyzer SHA-256:
  `eef39864de10ba64e57ea92092a15ff6926ac0da55efa7c1f856919aaf4979cb`;
- focused verification: two Rust evaluator tests and four catalog/analyzer tests pass.
