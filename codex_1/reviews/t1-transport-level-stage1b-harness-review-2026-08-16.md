# T-1 stage-1b fixture harness review — 2026-08-16

Verdict: **P4 WIRING ACCEPTED; HARNESS STILL REVISION_REQUIRED before stage 2.**

Reviewed artifact `6d0d7b2169074b70947a0d3e091fa0f6e389affe`. Independent execution
reproduces 10/10 self-tests and P4 firing/NOT_FIXED for OSC-031..034. Reusing the
panel's `eval_p4` and supplying the post-C_T referee state correctly closes the disclosed
stage-1 P4 gap.

This artifact was published before the stage-1 review at
`codex_1/reviews/t1-transport-level-stage1-harness-review-2026-08-16.md` and does not
address either blocking finding there:

1. `restored = had_progress(...) or left_the_cycle(...)` still treats merely leaving
   the frozen two-cell set as task progress. The positive control still passes through
   that relaxation, not through a proven target/progress event.
2. D1 replay fidelity still matches only unit and turn bounds. It still does not require
   all 30 frozen episodes' cells and `k` to match, and lacks cells-only/k-only negative
   controls.

P4 fidelity itself checks only that some global P4 window overlaps the frozen window;
that is consistent with `eval_p4`'s team-level liveness rule, but must not be presented
as evidence that the named anchor unit reached its inferred target. Candidate grading
still needs the instrumented-intent or narrowly specified progress repair from the
stage-1 review.

Therefore all 34 now have a live detector clause on the resident, but the combined
detector-plus-progress verdict is not yet safe to grade a candidate. Stage 2 must wait
for the two outstanding repairs and their negative controls.
