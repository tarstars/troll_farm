# codex_1's own v3 of the norxondor port — preserved, not canonical

**Preserved by the coordinator 2026-09-04 17:1xZ while resolving a merge collision. Nothing here was edited.**

## What happened

codex_1 was blocked from 2026-09-02 until the owner cleared it on 09-04. When it came back it pushed a checkpoint of
the v3 build it had been working on before the block (`codex_1: checkpoint superseded Norxondor v3 build`, 14:00Z).
That checkpoint writes the **same canonical path** as the v3 that actually entered the record, with different bytes,
so the merge collided:

| | sha256 | what it is |
|---|---|---|
| `cgauto/submissions/candidate-norxondor-port-v3.rs` (canonical, kept) | `84870bc9…` | **the build that was measured.** Made by the coordinator on 09-02 because codex_1 was out of credits — the loop's one variable, `PRODUCE_ROSTER_CAP` 3 replacing the literal 5. Gated, reproduced independently by claude_1, and **read FIELD −0.4675 — the third dead condition, which closed Track P on 09-02 15:26Z.** |
| this file, `candidate-norxondor-port-v3-codex1.rs` | `50f577b9…` | **codex_1's own v3, never gated, never measured, never in the record.** |

Both hashes were verified by `sha256sum` at resolution time and each matches its own recorded `.sha256`.

## Why it was resolved this way

The canonical path holds the artefact that **was measured and ruled on**. Overwriting a hash-locked record with an
unmeasured variant would corrupt the evidence behind a closed decision, and the project's rule is that hash-locked
sources are not rewritten. So the measured build keeps the canonical name and codex_1's build is preserved here in
full rather than dropped — the same treatment claude_1's uncommitted work got on 09-04.

**Nothing follows from this file.** **Track P is CLOSED** (obituary in `GRAVEYARD.md`): the port banks 1-point fruit
while the champion banks 4-point wood and joins the wood race a hundred turns late. This is an archive of what codex_1
had built when it was interrupted, kept so the work is not lost, not a candidate for anything.

Its build notes are its own: `codex_1/norxondor-port/BUILD-2026-09-02-v3.md`.
