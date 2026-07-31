# Owner-directed far-denial no-return Arena execution

Date: 2026-07-31
Task: `20260731-owner-far-denial-no-return-arena`
Phase: **submitted; first Arena checkpoint identity/runtime clean**

## Candidate

- Source:
  `cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs`
- Size: 63,033 bytes
- SHA-256: `307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd`
- Generator SHA-256:
  `06e3ecd199b478e71224b9ed7f9a8794defd57d8787a594ea152caf5031e3eac`
- Sacred resident SHA-256 remains:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

The change uses terrain BFS from a tree to the nearest own shack door. At distance ≤3,
the existing return/drop behavior is unchanged. At distance >3, while the tree species is
the initial `typeToCut` focus and the opponent has at most two trolls:

- the chop candidate excludes the return/drop leg and wood value;
- a full-capacity troll may continue issuing CHOP;
- lethal overflow wood is discarded by the referee rather than causing a bank return.

All non-focus trees, later phases, near trees, fruit banking, ordinary wood production,
and endgame behavior retain the resident path.

## Validation

- Fail-closed generator reconstructs the exact resident SHA `a8eb3b2b…` before applying
  two function replacements and the announcement label.
- Focused tests: 2 passed. The compiled exact candidate emits a bank-directed MOVE for a
  full troll on a focus tree at BFS 3 and `CHOP` at BFS 4.
- Four unsealed local seeds (`1300–1303`) × both seats against `ringfix3` complete without
  stderr/runtime failure.
- Exact candidate compiles under Rust 2021 release optimization and is below the platform
  100,000-byte gate.

## Platform preflight

- Arena room remains resident agent `6561795`, rank 45/113, score 21.9.
- The 20 latest resident battle records all identify submission `41015603`.
- The IDE-saved draft SHA is `51380661…`, not the resident source. This is classified as
  unsent editor state because Arena identity and every sampled battle remain the exact
  resident agent/submission. The API submission uses a fresh generated session and does
  not rely on that draft.

The owner explicitly directed this unqualified candidate to Arena. Exactly one candidate
submission was made:

- TestSession submission response: `41070584`;
- new candidate agent: `6585578`;
- first discovery: ten queued battles, all initially `done=false`;
- previous ranked row remained resident agent `6561795` at 21.9 while the queue started.

No second candidate or control submission is in flight.

## First Arena checkpoint

The submission-scoped reader fetched 20/20 finished results for exact agent/submission
`6585578`/`41070584`:

- identity clean, 20 parsed, zero pending, zero runtime validity signals;
- fresh score 18.22, rank 86/113;
- 3/20 catastrophic games (15.0%), negative mass 502.

This is a fresh 20-game validity checkpoint, not a mature comparison to the resident's
21.9 row. The candidate stays in flight; there is no restore or second submission.

## 95-game maturity checkpoint

The exact submission-scoped reader later fetched 95 finished results with one pending:

- identity clean, 95 parsed, zero runtime validity signals;
- score 20.14, rank 57/113 in the checkpoint; the room rounded to 20.2 at rank 56/113;
- 12/95 catastrophic games (12.6%), negative mass 2,819.

The row is rising but remains below the resident's mature 21.9 baseline. The candidate
continues maturing; there is no restore or second submission.
