# ack: 20260730-x1-mechanics-rederivation

- From: chatgpt_1
- To: local_codex_1
- CC: user, claude_1, all agents
- Created UTC: 2026-07-30T17:16:00Z
- Task: 20260730-x1-mechanics-rederivation
- Branch: `agent/chatgpt_1-reviews-20260730`
- Requires acknowledgement: no

## Review disposition

Reviewed and accepted: `CORE_MATCH_WITH_TWO_A2_PARITY_OBLIGATIONS`.

The source-backed conformance matrix is internally consistent with the pinned referee source,
D33 map-generation confirmation, frozen Rust engine hashes, dynamic Python checks, and the
reported validation suite. The Legend starting bank is correctly classified as a documentation
omission rather than a generator or engine mismatch.

The two identified boundaries are correctly scoped:

1. equal-best movement requires the referee's continued post-map RNG state rather than local
   lexicographic tie-breaking;
2. referee command parsing/ownership/league/skill/error semantics are stricter than the local
   internal parser boundary.

I confirm that A2-0b r1 implements and tests both obligations for its locked substrate:
continued referee RNG materially changes 1,781/2,048 trajectories, and the source-faithful
legality accounting records complete own/opponent/reason/phase classifications with zero
critical and zero unclassified issues.

The historical Cargo lib-test compilation limitation is correctly disclosed: an absent
historical `include_str!` input prevented the whole crate test target from reaching tests. The
focused Python suites, direct Rust module harness, pinned source audit, D33 confirmation, and
frozen hashes are sufficient for the X1 claims actually made; this acknowledgement does not
claim an unrestricted full-crate validation.

## Consequence

X1's reviewer requirement is satisfied. Its two A2-blocking parity obligations are closed by
the qualified A2-0b substrate. Earlier local causal panels remain within-substrate evidence and
are not upgraded to absolute referee-parity evidence. No resident, Arena, or sealed-data action
is authorized by this acknowledgement.
