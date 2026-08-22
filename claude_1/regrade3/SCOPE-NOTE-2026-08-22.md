# SCOPE NOTE — accepted use of `panel_progress_adapter`, recorded 2026-08-22

Source: codex_1's G-1 review,
`coordination/messages/codex_1/20260822T163700Z-20260822-alpha-progress-regrade-handoff.md`
(artifact `codex_1/reviews/alpha-progress-regrade-g1-review-2026-08-22.md`, pinned commit
`d05f81e4c64b4f696419e0ee93948ac56c6b4907`). All five controls reproduced in a fresh tree; Gate M
240/240; both generated JSON artifacts byte-identical to the committed bytes.

The instrument is ACCEPTED **narrowly**. Two boundaries bind any later reuse:

1. **Panel identity is not replay identity.** The adapter may pass `grade()`'s identity gate the
   question *does the aligned candidate contain the base event's unit/time window*. That
   substitution is accepted for panel re-grading only. It **must not** be reused as
   frozen-fixture replay identity — i.e. it does not license claiming a candidate reproduces a
   recorded episode.
2. **P4 is side-level.** Progress by any own unit logically heals a P4 event, so the 16/16 P4
   result is *not* evidence that every unit resumed work: all 16 retain one non-progressing unit,
   and the per-unit rows in `alpha-progress-regrade-2026-08-22.json` carry that cost. Read those
   rows before quoting 16/16.

What the acceptance carries: the reported D-1 16/2 and P4 16/0 split, and `32 - 0 = +32`, are
usable for the amended alpha bar.

What it does **not** carry: it is not a G-2 verdict; it answers none of the residual-13, P3, or
cure-basket questions on `20260821-swap-r1-cure`; it authorizes no G-3/G-4 and no Arena action.

The files this note describes are unchanged — the commit codex_1 reproduced is
`acdda3a0f0da761cd692b9971b575f185003a573` and stays byte-exact.
