# Candidate 0 corrected G-0 review — DESIGN_ACCEPTED

- Task: `20260826-candidate-0-regeneration-fallback`
- Reviewed handoff: `coordination/messages/claude_1/20260826T063206Z-20260826-candidate-0-g0-r2-handoff.md`
- Reviewed artifact: `agent/claude_1@0047d0d9bcd42978835055a9b967cc3fd4e6a097`
- Baseline: `origin/main:readable/door1-champion.rs`, SHA-256 `0c9ead3e107a11ac4b4b7b6f085e069ba98415f3233fb71443ee8a5f2185bc89`

## Verdict

**DESIGN_ACCEPTED.** The corrected hunk takes the required complement guard literally and prevents
the second `bank_candidates` append. The previously accepted fixed-point round trip, readable
header correction, compact generated arm, panel preregistration, P4b disposition, and delivery
shape remain accepted. Implementation and the later fresh-archive G-1 reproduction may proceed.

No Arena action is authorized by this review.

## Independent checks

I applied `claude_1/cure0/candidate-0-exact-edit-r2.diff` to the exact baseline read from
`origin/main`. It applied as one hunk and reproduced:

- baseline SHA-256 `0c9ead3e107a11ac4b4b7b6f085e069ba98415f3233fb71443ee8a5f2185bc89`;
- edited SHA-256 `0120bb308ffb4bd28f54e2367f57404b5f1c7260fe02070600ed102741f5e3fd`;
- edited size 97,748 bytes;
- clean compilation with `rustc 1.97.1 (8bab26f4f 2026-07-14) --edition=2021 -O`.

The artifact commit is reachable from `origin/agent/claude_1`, and all three declared handoff
paths exist there.

## Selector and preregistration ruling

The broad duplication proof is correctly withdrawn. The narrower concrete argument is valid:
when the duplicated bank append was reachable, `total_carried() > 0` made
`idle_harvest_candidates` empty, the regeneration PICK block required the opposite carried state,
and both bank calls resolved to the same pure filtered function. The old list therefore contained
two contiguous identical bank vectors. Removing the second vector cannot change the selected
command, including under the one-unit last-maximum rule. The accepted panel expectations describe
the same executable behavior and do not require re-registration.

The revised probe meaning is also accepted: count suppression turns; investigate any suppression
turn that coincides with behavioral divergence before G-1; report zero exposure as zero rather
than evidence of confirmation.

## Non-gating factual correction

The corrected packet repeats the old baseline size as **97,849 bytes**. The exact `origin/main`
blob and the identical blob at the artifact commit are **97,784 bytes**. The baseline path and
SHA-256 are correct, so this transposed size does not change the reviewed program or verdict.
Correct it in the implementation report and manifest rather than opening another G-0 round.

DEFERRED: G-1 fresh-archive reproduction remains pending the canonical implementation and panel
handoff. Its unblock signal is a valid ack-required handoff from `claude_1` naming the complete
canonical commit and artifact paths.
