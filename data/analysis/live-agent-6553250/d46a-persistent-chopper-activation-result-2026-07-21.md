# D46a persistent-chopper activation audit — result (2026-07-21)

## Verdict

**Reject D46 before value evaluation and keep both fresh value banks sealed.** The fixed role rule
is mechanically exact and highly eligible, but it is behaviorally identical to D40. Across all 512
quarantined tasks it records **11,525 role-eligible decisions, zero overrides, and zero changed
action hashes**. The frozen minimums were 512 eligible decisions, 256 overrides, and action-hash
changes in 20%--90% of tasks.

No score, margin, own-score, opponent-score, workforce, crop, or tail outcome from this quarantined
bank was summarized or used. Seeds 9,780,000--9,780,031 and 9,781,000--9,781,031 remain untouched.
Do not alter the designated-worker rule or inspect D46 value on another bank.

## Mechanical audit

- Exact D40 control, D46 candidate A, and D46 candidate B each complete all 512 tasks.
- Candidate A and B are byte-identical.
- There are zero illegal-command, provenance, relevant-deposit-prediction, role-integrity,
  worker-cap, reward-identity, or action-count failures.
- Every D40 control role counter is zero.
- Candidate eligibility is broad: 22.51 eligible decisions per task on average.
- Every eligible choice is already D40 rank zero, so the candidate never changes a command.

## Interpretation

D40 does not erase the trained chopper's job kind in the way D45a's generic scoring surface made
plausible. Whenever the designated maximum-chop worker is in the rate branch and has a legal
`FELL_BANK` candidate, exact D40 already ranks a `FELL_BANK` action first. A persistent-chopper
override therefore cannot improve D40 because the proposed behavior is already implicit in the
teacher.

This localizes the remaining structural question away from the maximum-chop worker. D45a's broad
post-funding fell sensitivity must arise from decisions involving other workers, other target
choices, or states without an available fell job. Independent D35 role evidence identifies the
coherent team as producer/producer/chopper, with RENEW and FELL accounting for roughly 94% of
non-idle activity. D47 should therefore test the complementary coefficient-free role rule rather
than modify D46: after the third worker exists, each non-designated-chopper rate worker takes its
best legal provenance-ordered `RENEW` job. First run an activation-only audit; expose fresh value
maps only if the rule makes enough nontrivial changes.

## Gate result

| Gate | Result |
|---|---:|
| Complete exact deterministic repeat | pass |
| Zero integrity failures | pass |
| At least 512 eligible decisions | pass: 11,525 |
| At least 256 role overrides | **fail: 0** |
| Changed action hashes in 20%--90% of tasks | **fail: 0/512** |

Formal conjunction: **fail**.

## Evidence

- protocol SHA-256:
  `eca41e6e85edcea6ee0aa0e7d5bed3bb1cb6ef327ecc471c7b148fc1748a8d53`;
- quarantine amendment SHA-256:
  `c3834dd7b56194fe57a98e21c354d36ce925857fb9891966ca9fc414e085b139`;
- control TSV SHA-256:
  `8803fb92a40d770f4e44fb84d6fa9f20cf38da0d751688e040ecd90ee4f84d50`;
- candidate A/B TSV SHA-256:
  `ac3a304f12f6626a7cc21712ffc02469582becbb91d05847a52a776942865e5a`;
- result JSON SHA-256:
  `becc62a8af7ade1b724a4310ff2a6f042183a4771c0880a3be7c9882f42208ad`;
- runner SHA-256:
  `d48e5066cbdcdefd33df1e43034163b37bd2811c70a300588958a9ffcef716f4`;
- analyzer SHA-256:
  `95047f7f8bf25f3a48c827aba36e6fd81d8a3b0687f5125e9f1631db8c3225d6`;
- focused verification: two Rust runner tests and three Python analyzer tests pass.
