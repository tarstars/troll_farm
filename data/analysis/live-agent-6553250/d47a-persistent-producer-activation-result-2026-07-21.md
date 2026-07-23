# D47a persistent-producer activation audit — result (2026-07-21)

## Verdict

**Pass Stage A and open only the frozen D47 development bank.** The coefficient-free producer role
is deterministic, mechanically clean, and materially active. Across 256 fresh activation-only
tasks it records **9,166 eligible decisions, 2,450 overrides, and 211 changed action hashes
(82.42%)**. Every preregistered activation gate passes.

All score and margin fields were ignored. This result says the role is behaviorally distinct from
D40; it provides no evidence that the changes are valuable. It authorizes only exact D40 and two
unchanged D47 executions on frozen development seeds 9,783,000--9,783,031.

## Gate result

| Gate | Result |
|---|---:|
| Complete exact deterministic repeat | pass |
| Zero integrity failures | pass |
| At least 512 role-eligible decisions | pass: 9,166 |
| At least 256 role overrides | pass: 2,450 |
| Changed action hashes in 20%--90% of tasks | pass: 211/256 = 82.42% |

Formal conjunction: **pass**.

## Interpretation

Unlike the chopper rule, persistent producer specialization is not already implicit in D40. About
26.73% of eligible non-chopper renewable decisions override exact D40, and the resulting trajectory
differs in most tasks without saturating the frozen 90% ceiling. The complete-policy development
stage is therefore a meaningful causal test rather than an A/A comparison.

Do not inspect activation-bank outcomes, alter the renewable target rule, exempt one producer, add
a phase cutoff, or infer value from the high activation rate. Development retains the original D47
margin, own/opponent score, family breadth, workforce, crop, and tail conjunction.

## Evidence

- protocol SHA-256:
  `d26bcdcaada549fd904090611f1ee358f1ce4934ca8e3c5932c6c6db4e1af3b2`;
- control TSV SHA-256:
  `acb6d603305356fd9813fdb5a2593b015d8b6f1495925803e296020296aa9874`;
- candidate A/B TSV SHA-256:
  `12a6630aa1c08e6a5a18120ffc6ea104e05eecbe1b86550ed718081bc9ab3c4e`;
- result JSON SHA-256:
  `59e9f49b58d80b4592d84d113b4a5eb25f536a91a195cbcb6e36a772c60383b5`;
- runner SHA-256:
  `aea0248247d8ebffd38a4d1d168f66b1c6455db63224f0f8d1157d73528deed9`;
- analyzer SHA-256:
  `3410d08cb05e225bbf459b4f1d06c50be0b77c3ad2d12d05869c27f03ad1dead`;
- focused verification: two Rust runner tests and two Python analyzer tests pass.
