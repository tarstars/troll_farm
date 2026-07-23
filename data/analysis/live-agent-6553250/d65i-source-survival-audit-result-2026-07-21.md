# D65i planted-source survival audit result (2026-07-21)

## Verdict

**The discriminator is deposit survival, not source creation.** Both failed seed-9,830,002 tasks
create the missing LEMON root but deposit zero LEMON from it. Both successful seed-9,830,014 tasks
deposit PLUM from their new root before worker two. The exact lifecycle timing differs across the
two failed seats, but both are removed under opponent pressure before their first deposit.

The next eligible causal test is an atomic source-to-net-deposit lease: after investing one banked
seed, keep the sole worker assigned through source maturation and enough harvesting to repay that
seed plus one deposited surplus unit. Do not plant more sources, retune the cell, or reopen D65's
fresh bank with the rejected return-immediately transaction.

## Integrity

- Two 491-row complete traces are byte-identical, SHA-256
  `7fdd27d494a8fbeeb1e80d05c1cfd232ddf62b13c5f8d86b2bebb28d4887f9c4`.
- All four D65 repair tasks are present with contiguous decision indices and exact state chains.
- Final score, workforce, train/job counters, crop count, action hash, and state hash reproduce
  every frozen D65 repair row exactly.
- Action accounting, trace hashes, direct commands, provenance, and deposit prediction are clean.

## Failed seed 9,830,002

Both seats first recover PLUM: their new PLUM roots deposit one/two fruit and bank reaches six
PLUM by terminal. The sole remaining bill blocker is LEMON.

- Seat 0 plants LEMON at turn 11, observes its first ripe fruit at turn 28, and immediately selects
  `HARVEST_BANK`. During the turn-28--30 job the root disappears, the job invalidates, and deposited
  LEMON remains three. The root cell is later reused by PLUM.
- Seat 1 plants LEMON at turn 11, but the root disappears by turn 30 without ever ripening or being
  selected. Deposited LEMON also remains three.

Both tasks therefore have zero missing-species deposit and finish with one worker. Planting spent
one of the four original banked LEMON, so a single harvested fruit would merely repay the seed;
the transaction needs two deposited fruits for +1 net bill progress.

## Successful seed 9,830,014 controls

Both seats plant PLUM at turn 8 and first see ripe fruit at turn 23. D40 immediately selects
`HARVEST_BANK`:

- seat 0 deposits one root fruit before a second job invalidates, then trains at turn 63; and
- seat 1 deposits two root fruits before the root is lost, then trains at turn 47.

Both successful tasks have positive missing-species deposit before worker two. Root survival to
terminal is unnecessary; survival through capitalization is sufficient.

## Decision

Freeze D66a as one source-capitalization transaction on the unchanged D65 trigger. The worker may
wait at the planted root, harvest exactly two fruits with its existing capacity, bank them, and
then return to D40. First require all four consumed tasks to create worker two with exact control
parity and zero failures. Only that pass may open a fresh repeated value matrix.

## Reproducibility

```text
7263044807a65358b664c40af967673389a70483452c47412440f58631c02188  d65i-source-survival-audit-protocol-2026-07-21.md
54f6e2297fc9a2bebc960cd8b2e37972fd6d0021b260bf59fa4d01b96bcc4362  rust/src/bin/d65_source_survival_audit.rs
92c6cbe2a07938f72e07d9b2ead447f3a6f8773b8510b12ce40f9ec48011a768  cgauto/analyze_d65i_source_survival.py
7fdd27d494a8fbeeb1e80d05c1cfd232ddf62b13c5f8d86b2bebb28d4887f9c4  each repeated trace
a91d9bc546ff6e44c72e9b3356600f34a4f8b61c50f26309fbb55423f11ca0e9  d65i-source-survival-result.json
```
