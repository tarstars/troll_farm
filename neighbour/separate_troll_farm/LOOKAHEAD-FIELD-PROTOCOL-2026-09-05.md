# Persistent-horizon planner: fresh real-agent protocol

Local development supports opening this screen, not publication: 176/5/11 versus V439's
173/5/14 across the eight consumed maps, no map-level point regressions, zero command/runtime
failures. All 43,263 observed-state turns are packaged/readable-identical, worst 43.573 ms.
Interactive startup covers 320 open-stdin launches, correct first outputs, worst 3.772 ms.
The exact uninstrumented-source A/A and current full suite must complete before any game request.

Compare exact V439 SHA `7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`
with persistent-horizon SHA `9f01587b4f71b8e5bbbe15e86a69aac274fe1ac476725951e6bf67db304b1c5d`.
The candidate is 92,430 UTF-16 units. No source edits during either field stage.

`freeze_lookahead_field.py` reads the current division table and freezes actual agent identities
at ranks 7, 8, 20, 40, 60, plus rank 7 in the opposite seat. Each stage contains six independent
seed blocks, three in each seat, with both programs paired against the same adaptive opponent
and initial state. Candidate/baseline request order alternates. The confirmation stage reverses
the seats and uses distinct unopened seeds. Exact formulas and identities are in its two immutable
plan files under project working storage. Freeze both before requesting either stage.

Screen: at most twelve unranked requests, one collector, no automatic retry of a POST or ambiguous
completion. Advance only with at least one additional match point, no lost baseline win against
the rank-seven/eight identities, no margin deterioration on a majority of blocks, and zero
deployment/protocol failures. A tie does not advance this tested configuration; it is not proof
that the true effect is zero. Keep the small-sample limitation explicit.

Confirmation: open its twelve requests only after the screen passes. Require at least one
additional match point again, no lost target-rank baseline win, no majority of worse-margin
blocks and zero deployment/protocol failures. Do not tune on either stage and retain its label
as a holdout. Failed runs remain in the denominator. Ambiguity stops the collector for read-only
recovery, not reissue. Verify seed echo, physical seat, exact opponent identity and initial input
hash for every pair; use official ranks for outcomes, not score ordering alone.

Reports must include per-stage and per-opponent W/D/L and points, both scores, margin, failures,
seat results and shared-map paired uncertainty. The fixed small opponent sample cannot establish
a rank conversion or quantify generalization over unseen policies. A passing finalist may proceed
to a separately guarded, single exact publication; it does not establish seventh place. Success
still requires the mature exact-agent top-seven rollout and later confirmation in `EVALUATION.md`.
