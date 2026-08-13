# E7a iterative logical deletion — round 22 checkpoint

Status: **DEVELOPMENT EXACT-EQUALITY PASS / CONTINUATION AUTHORIZED / NOT DEPLOYED**

## Outcome

Claude continued the behavior-preserving reduction from accepted round 14 through round 22. The
seven fixed fields of the single-valued `YamoOpeningPolicy` record were inlined one at a time, then
the empty record and its never-read plumbing were deleted.

Head candidate:
`claude_1/e7a-incremental-simplification/candidate-r22-delete-opening-policy-record.rs`

- bytes: 56,651;
- SHA-256: `2943ad840ccaf2332ab515ab768aa8c97bac2de894a7eda6228b92ea5f0707cc`;
- reduction from the initial 62,278-byte equivalent: 5,627 bytes;
- reduction from exact live E7a: 6,169 bytes.

Every round has a pre-generation contract, exact anchor-checked builder, byte-identical rebuild,
optimized compile, clean empty-input behavior, ten exact semantic fixtures, and exact frozen live
parity on 25 games / 7,234 command lines. No identifier renaming, formatting, compression, or
Arena mutation occurred.

## Accumulated development checkpoint

Round 22 was compared with exact live E7a on the same consumed design used for round 13:

- 43 official-generator maps starting at seed 9,854,000;
- both seats;
- six opponent families;
- 516 paired tasks total.

Result: `DEVELOPMENT_EXACT_EQUALITY_PASS`.

- Different terminal tasks: 0/516.
- Mean paired delta / bootstrap lower bound: 0 / 0.
- All six family means and both seat means: 0.
- Catastrophes: 19 baseline / 19 candidate.
- Negative-margin mass: 4,138 / 4,138.
- Training coverage and median delay: 516/516 and 0 turns.
- Maximum period-2 episode: 244 / 244.
- Candidate p95 latency ratio: 1.02094; maximum 7.12 ms.
- Critical and unclassified issues: zero.

Evidence JSON:
`local_codex_1/e7a-iterative-logical-deletion/candidate-r22-delete-opening-policy-record-development.json`

Evidence SHA-256:
`bed4bc677c17fcb32fb07969303ee19866b71bab8b66c39161f8e9d62b71d903`

Panel TSV SHA-256:
`59433f8c6650d476f627dbbd2ba90802fd4f727d7a3004f00f7396343a154d24`

## Decisions

The next untouched range is deferred until the current fixed/dead-code cascade reaches its
terminal source. This avoids spending a one-shot range on a candidate that will immediately be
superseded. Round 13's existing untouched exact-equality result remains prior evidence, but is not
misrepresented as qualifying round 22.

The constant-false `15<=0||` disjunct may be folded in its own declared round. Unused derived impls
are also legitimate dead-code deletion rather than formatting, subject to exact token-only edits
and the full per-round gates. They must be split by trait: current `Debug` derives in one round and
`Hash` on `PlantKind` in another. The current source contains 12 `Debug` tokens—the earlier count
of 13 included the now-deleted `YamoOpeningPolicy` record.

## Provenance observations

The offline packet is consistently bound to the frozen audit. In game `897833625`, the audit's
summary histogram reports one more CHOP and one fewer MOVE than the hash-pinned baseline output.
Because online replay comparison and the packet agree on all 7,234 raw command lines, this is a
summary/taxonomy discrepancy, not a parity difference.

The host-only online evaluator and packet builder eagerly import the credential-reading Arena
module. This is recorded as tooling debt, not a blocker: those tools inherently call the Arena,
while the delegated offline evaluator is credential-free. Future cloud replay-decoder reuse should
split pure decoding from the Arena client and lazy-load credentials.

## Arena decision

This source is smaller but behavior-exact, so expected rating gain is zero. The mature live agent
remains unchanged under the no-churn rule.
