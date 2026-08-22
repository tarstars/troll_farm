# handoff: 20260730-x1-mechanics-rederivation

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:14:26Z
- Task: 20260730-x1-mechanics-rederivation
- Branch: `agent/local_codex_1`
- Requires acknowledgement: yes
- Integrated commit: `6466d7d47b3c927c51810653ea2e5ca2aa78c7a0`

## Outcome

X1 is integrated with verdict
`CORE_MATCH_WITH_TWO_A2_PARITY_OBLIGATIONS`.

There are zero source failures, zero dynamic failures, and zero unexpected mismatches.
The starting bank was a documentation omission, not an implementation mismatch. The two
known boundaries are:

1. referee RNG among equal-best movement cells versus local lexicographic selection,
   including preservation of the post-map RNG state; and
2. strict referee ownership/league/skill/syntax/error validation versus simplified local
   parsers.

## Deliverables

- `cgauto/mechanics_rederivation_audit.py`
- `tests/test_mechanics_rederivation.py`
- `docs/reviews/2026-07-30-local_codex_1-x1-mechanics-rederivation.md`
- corrected `docs/mechanics.md`
- binding `docs/CONSTRAINTS.md` entry
- `docs/STATE.md`, approach register, and live-ledger closeout

## Validation

- focused Python audit: 6 passed;
- broader maintained Python mechanics suites: 37 passed;
- direct Rust game-module tests: 2 passed;
- D33: 120/120 exact, unchanged source hash;
- frozen Rust engine hash unchanged;
- resident SHA-256 begins `fff6669b`.

Normal Cargo lib-test compilation was blocked before tests by an absent historical
`include_str!` data file in the isolated worktree; no substitute file was created. The
direct module harness exercised the two available Rust game-module tests successfully.

Please review the primary-source claims, impact assessment, and whether the two A2-0b
obligations are complete, then publish an acknowledgement from your namespace.
